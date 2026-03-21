'use strict';

const { spawn } = require('child_process');
const fs = require('fs').promises;
const path = require('path');
const os = require('os');

const SESSION_DIR = path.join(os.homedir(), '.kimi', 'sessions');

/**
 * Parse command-line arguments with strict validation
 * Supports: --flag, --key=value, -f, positional args
 * Stops parsing at -- (remaining become positional)
 */
function parseArgs(argv, opts = {}) {
  const result = {
    positional: [],
    options: {},
    flags: {},
    raw: argv
  };

  const { 
    strings = [],      // Options that expect string values
    booleans = [],     // Flags (no value)
    integers = [],     // Options that expect integer values
    required = []      // Required positional count
  } = opts;

  let i = 0;
  while (i < argv.length) {
    const arg = argv[i];

    if (arg === '--') {
      result.positional.push(...argv.slice(i + 1));
      break;
    }

    if (arg.startsWith('--')) {
      const eq = arg.indexOf('=');
      if (eq !== -1) {
        const key = arg.slice(2, eq);
        const val = arg.slice(eq + 1);
        
        if (integers.includes(key)) {
          const n = parseInt(val, 10);
          if (isNaN(n)) throw new Error(`--${key} must be a number, got: ${val}`);
          result.options[key] = n;
        } else {
          result.options[key] = val;
        }
      } else {
        const key = arg.slice(2);
        result.flags[key] = true;
      }
      i++;
    } else if (arg.startsWith('-') && arg.length > 1) {
      // Short flags: -abc becomes flags a, b, c
      const flags = arg.slice(1).split('');
      flags.forEach(f => result.flags[f] = true);
      i++;
    } else {
      result.positional.push(arg);
      i++;
    }
  }

  // Validate required positionals
  if (required.length > 0) {
    for (const r of required) {
      if (result.positional.length < r) {
        throw new Error(`Missing required argument #${r}`);
      }
    }
  }

  return result;
}

/**
 * Require a positional argument at index, throw if missing
 */
function requirePositional(args, index, name) {
  const val = args.positional[index];
  if (val === undefined || val === null) {
    throw new Error(`${name} is required`);
  }
  return val;
}

/**
 * Require at least N positional arguments
 */
function requireAtLeastN(args, n, name) {
  if (args.positional.length < n) {
    throw new Error(`${name} requires at least ${n} argument(s)`);
  }
}

/**
 * Validate URL is http(s), return URL object
 */
function validateUrl(str, name = 'URL') {
  try {
    const url = new URL(str);
    if (!['http:', 'https:'].includes(url.protocol)) {
      throw new Error(`${name} must use http or https protocol`);
    }
    return url;
  } catch (err) {
    if (err.message.includes('protocol')) throw err;
    throw new Error(`Invalid ${name}: ${str}`);
  }
}

/**
 * Validate integer with range
 */
function validateInt(str, name, { min, max } = {}) {
  const n = parseInt(str, 10);
  if (isNaN(n)) throw new Error(`${name} must be an integer, got: ${str}`);
  if (min !== undefined && n < min) throw new Error(`${name} must be >= ${min}`);
  if (max !== undefined && n > max) throw new Error(`${name} must be <= ${max}`);
  return n;
}

/**
 * Read JSON from string or @file path
 * Returns parsed object or throws
 */
async function readJson(input, name = 'JSON') {
  if (!input) throw new Error(`${name} input is empty`);
  
  let content;
  if (input.startsWith('@')) {
    const filePath = input.slice(1);
    try {
      content = await fs.readFile(filePath, 'utf8');
    } catch (err) {
      throw new Error(`Cannot read ${name} file ${filePath}: ${err.message}`);
    }
  } else {
    content = input;
  }
  
  try {
    return JSON.parse(content);
  } catch (err) {
    throw new Error(`Invalid ${name} JSON: ${err.message}`);
  }
}

/**
 * Call an MCP tool with timeout and error handling
 */
async function mcpCall(server, tool, params, opts = {}) {
  const { timeout = 60000, retries = 0 } = opts;
  const input = JSON.stringify(params);
  
  const attempt = async () => {
    return new Promise((resolve, reject) => {
      const child = spawn('npx', [
        '-y', '@anthropic-ai/mcp-tool',
        server, tool
      ], {
        stdio: ['pipe', 'pipe', 'pipe'],
        shell: false,
        timeout
      });
      
      let stdout = '';
      let stderr = '';
      let killed = false;
      
      const timer = setTimeout(() => {
        killed = true;
        child.kill('SIGTERM');
        reject(new Error(`MCP call timed out after ${timeout}ms`));
      }, timeout);
      
      child.stdin.write(input);
      child.stdin.end();
      
      child.stdout.on('data', (d) => { stdout += d.toString(); });
      child.stderr.on('data', (d) => { stderr += d.toString(); });
      
      child.on('close', (code, signal) => {
        clearTimeout(timer);
        
        if (killed) return; // Already rejected by timeout
        
        if (signal) {
          reject(new Error(`MCP call terminated by ${signal}`));
        } else if (code !== 0) {
          const err = stderr || `Exit code ${code}`;
          reject(new Error(`MCP error: ${err}`));
        } else {
          try {
            // Try to parse JSON, fallback to raw string
            const trimmed = stdout.trim();
            if (!trimmed) resolve(null);
            else if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
              resolve(JSON.parse(trimmed));
            } else {
              resolve(trimmed);
            }
          } catch {
            resolve(stdout.trim());
          }
        }
      });
      
      child.on('error', (err) => {
        clearTimeout(timer);
        reject(new Error(`Failed to spawn MCP tool: ${err.message}`));
      });
    });
  };
  
  // Try with retries
  let lastError;
  for (let i = 0; i <= retries; i++) {
    try {
      return await attempt();
    } catch (err) {
      lastError = err;
      if (i < retries) await new Promise(r => setTimeout(r, 1000 * (i + 1)));
    }
  }
  throw lastError;
}

/**
 * Format output consistently
 */
function formatOutput(data, opts = {}) {
  const { compact = false, raw = false } = opts;
  
  if (raw) {
    process.stdout.write(String(data));
    return;
  }
  
  if (data === null || data === undefined) {
    return;
  }
  
  if (typeof data === 'string') {
    process.stdout.write(data + (data.endsWith('\n') ? '' : '\n'));
    return;
  }
  
  // Handle MCP content format
  if (data.content && Array.isArray(data.content)) {
    data.content.forEach(c => {
      if (c.text) process.stdout.write(c.text + '\n');
    });
    return;
  }
  
  // Pretty print JSON
  const space = compact ? undefined : 2;
  process.stdout.write(JSON.stringify(data, null, space) + '\n');
}

/**
 * Ensure session directory exists
 */
async function ensureSessionDir() {
  try {
    await fs.mkdir(SESSION_DIR, { recursive: true });
  } catch {
    // Ignore errors
  }
  return SESSION_DIR;
}

/**
 * Sanitize session ID (alphanumeric, dash, underscore only)
 */
function sanitizeSessionId(id) {
  if (!id || typeof id !== 'string') {
    throw new Error('Session ID is required');
  }
  const sanitized = id.replace(/[^a-zA-Z0-9_-]/g, '');
  if (sanitized !== id) {
    throw new Error(`Session ID contains invalid characters. Use only: a-z, A-Z, 0-9, -, _`);
  }
  if (sanitized.length > 128) {
    throw new Error('Session ID too long (max 128 characters)');
  }
  return sanitized;
}

/**
 * General ID sanitizer (alphanumeric, dash, underscore, dot)
 */
function sanitizeId(id) {
  if (!id || typeof id !== 'string') {
    throw new Error('ID is required');
  }
  const sanitized = id.replace(/[^a-zA-Z0-9_.-]/g, '');
  if (sanitized !== id) {
    throw new Error(`ID contains invalid characters. Use only: a-z, A-Z, 0-9, -, _, .`);
  }
  if (sanitized.length > 256) {
    throw new Error('ID too long (max 256 characters)');
  }
  return sanitized;
}

/**
 * Sanitize GitHub repo ID (owner/repo format)
 */
function sanitizeRepoId(repoId) {
  if (!repoId || typeof repoId !== 'string') {
    throw new Error('Repository ID is required (format: owner/repo)');
  }
  
  const parts = repoId.split('/');
  if (parts.length !== 2) {
    throw new Error('Repository must be in format: owner/repo');
  }
  
  const owner = sanitizeId(parts[0]);
  const repo = sanitizeId(parts[1]);
  
  return `${owner}/${repo}`;
}

/**
 * Validate choice against allowed values
 */
function validateChoice(val, name, allowed) {
  if (!allowed.includes(val)) {
    throw new Error(`${name} must be one of: ${allowed.join(', ')}`);
  }
  return val;
}

/**
 * Read file or return null (does not throw)
 */
async function readFileSafe(filePath) {
  try {
    return await fs.readFile(filePath, 'utf8');
  } catch {
    return null;
  }
}

/**
 * Write file with parent directory creation
 */
async function writeFileSafe(filePath, content) {
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.writeFile(filePath, content);
}

/**
 * Fatal error - print to stderr and exit
 */
function fatal(msg, code = 1) {
  process.stderr.write(`Error: ${msg}\n`);
  process.exit(code);
}

module.exports = {
  parseArgs,
  requirePositional,
  requireAtLeastN,
  validateUrl,
  validateInt,
  validateChoice,
  readJson,
  mcpCall,
  formatOutput,
  ensureSessionDir,
  sanitizeSessionId,
  sanitizeId,
  sanitizeRepoId,
  readFileSafe,
  writeFileSafe,
  fatal
};
