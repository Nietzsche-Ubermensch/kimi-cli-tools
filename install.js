#!/usr/bin/env node
'use strict';

const fs = require('fs').promises;
const path = require('path');
const os = require('os');

const COMMANDS_DIR = path.join(__dirname, 'kimi-commands');
const TARGET_DIR = path.join(os.homedir(), '.kimi', 'commands');
const LIB_SOURCE = path.join(__dirname, 'lib');
const LIB_TARGET = path.join(os.homedir(), '.kimi', 'lib');

const COMMANDS = [
  'get', 'search', 'ask', 'docs',
  'think', 'do', 'run', 'check',
  'gh', 'linear',
  'session', 'config', 'help'
];

async function ensureDir(dir) {
  await fs.mkdir(dir, { recursive: true });
  console.log(`  ✓ ${dir}`);
}

async function copyFile(src, dest) {
  const content = await fs.readFile(src, 'utf-8');
  await fs.writeFile(dest, content, { mode: 0o755 });
}

async function install() {
  console.log('\n📦 Kimi CLI Command Installer\n');
  
  console.log('Creating directories:');
  await ensureDir(TARGET_DIR);
  await ensureDir(LIB_TARGET);
  
  console.log('\nInstalling commands:');
  for (const cmd of COMMANDS) {
    const src = path.join(COMMANDS_DIR, cmd);
    const dest = path.join(TARGET_DIR, cmd);
    
    try {
      await copyFile(src, dest);
      console.log(`  ✓ /${cmd}`);
    } catch (err) {
      console.log(`  ✗ /${cmd} - ${err.message}`);
    }
  }
  
  console.log('\nInstalling library:');
  const libFiles = ['utils.js'];
  for (const file of libFiles) {
    const src = path.join(LIB_SOURCE, file);
    const dest = path.join(LIB_TARGET, file);
    try {
      await copyFile(src, dest);
      console.log(`  ✓ lib/${file}`);
    } catch (err) {
      console.log(`  ✗ lib/${file} - ${err.message}`);
    }
  }
  
  console.log('\n' + '='.repeat(50));
  console.log('Installation complete!');
  console.log('\nAdd this to your shell profile:');
  console.log(`  export PATH="$HOME/.kimi/commands:$PATH"`);
  console.log('\nOr use commands directly:');
  console.log(`  ~/.kimi/commands/help`);
  console.log('='.repeat(50) + '\n');
}

install().catch(err => {
  console.error('Installation failed:', err.message);
  process.exit(1);
});
