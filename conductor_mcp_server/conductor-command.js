#!/usr/bin/env node
/**
 * Conductor MCP Command - Intent-Aware Orchestration
 * Usage: /conductor <action> [options]
 * 
 * Actions:
 *   intent <description>     - Execute intent with automatic tool orchestration
 *   route <task>             - Route task to best single tool
 *   workflow <file>          - Execute workflow from JSON file
 *   explain <intent>         - Explain planning decisions without executing
 *   status <plan_id>         - Get execution status
 *   context <action>         - Manage context sessions (store/retrieve/merge/clear)
 *   learn <plan_id>          - Save successful workflow as template
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const action = args[0];
const params = args.slice(1);

function runMcpTool(server, tool, argsObj) {
  const argsJson = JSON.stringify(argsObj).replace(/"/g, '\\"');
  const cmd = `echo "${argsJson}" | npx -y @anthropic-ai/mcp-tool ${server} ${tool}`;
  try {
    const result = execSync(cmd, { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'inherit'] });
    console.log(result);
  } catch (e) {
    console.error(`Error running ${tool}:`, e.message);
    process.exit(1);
  }
}

function showHelp() {
  console.log(`
🎼 Conductor - Intent-Aware Orchestration

Automatically routes intents to the right tools and orchestrates workflows.

Usage: /conductor <action> [arguments]

Actions:
  intent <description> [options]     Execute intent with auto tool selection
    Options: --tech=react,node --priority=speed|accuracy --context='{"key":"val"}'
    
  route <task>                       Route to single best tool (no execution)
    Options: --output=quick|detailed
    
  workflow <file.json>               Execute workflow from JSON definition
    File format: {"steps": [{"tool": "...", "inputs": {...}}]}
    
  explain <intent>                   Show tool selection reasoning
    Options: --tech=... --context='{"key":"val"}'
    
  status <plan_id>                   Check execution status
    
  context <session_id> <action>      Manage context
    Actions: store, retrieve, merge, clear
    Options: --data='{"key":"val"}' (for store/merge)
    
  learn <plan_id> --rating=0.9       Save successful workflow as template
    Options: --tags=tag1,tag2

Examples:
  /conductor intent "Research best auth libraries for Node.js"
  /conductor intent "Debug React performance issue" --tech=react,typescript
  /conductor route "Find FastAPI documentation"
  /conductor explain "Implement OAuth2 in Python"
  /conductor context my_session store --data='{"token":"abc123"}'
  /conductor learn plan_abc123 --rating=0.95 --tags=auth,nodejs

Workflow JSON Format:
  {
    "steps": [
      {
        "tool": "brave",
        "inputs": {"query": "..."},
        "parallel": true
      },
      {
        "tool": "perplexity",
        "inputs": {"messages": [{"role":"user","content":"..."}]},
        "depends_on": [0]
      }
    ],
    "synthesis_mode": "merge"
  }
`);
}

if (!action || action === '--help' || action === '-h') {
  showHelp();
  process.exit(0);
}

// Parse options
const options = {};
const positional = [];
for (let i = 0; i < params.length; i++) {
  const arg = params[i];
  if (arg.startsWith('--')) {
    const [key, value] = arg.slice(2).split('=');
    options[key] = value || true;
  } else {
    positional.push(arg);
  }
}

// Parse tech stack if provided
function parseTechStack() {
  return options.tech ? options.tech.split(',') : [];
}

// Parse context if provided
function parseContext() {
  if (options.context) {
    try {
      return JSON.parse(options.context);
    } catch (e) {
      console.error('Error: Invalid context JSON');
      process.exit(1);
    }
  }
  return {};
}

switch (action) {
  case 'intent': {
    const description = positional.join(' ');
    if (!description) {
      console.error('Error: Intent description required');
      process.exit(1);
    }
    
    const techStack = parseTechStack();
    const context = parseContext();
    
    const args = {
      intent: description,
      context: {
        ...context,
        ...(techStack.length > 0 && { tech_stack: techStack }),
        ...(options.priority && { priority: options.priority })
      }
    };
    
    runMcpTool('conductor', 'intent_to_execution', args);
    break;
  }

  case 'route': {
    const task = positional.join(' ');
    if (!task) {
      console.error('Error: Task description required');
      process.exit(1);
    }
    
    const args = {
      task: task,
      required_output: options.output || 'detailed'
    };
    
    runMcpTool('conductor', 'auto_route', args);
    break;
  }

  case 'workflow': {
    const filePath = positional[0];
    if (!filePath) {
      console.error('Error: Workflow JSON file required');
      process.exit(1);
    }
    
    if (!fs.existsSync(filePath)) {
      console.error(`Error: File not found: ${filePath}`);
      process.exit(1);
    }
    
    let workflow;
    try {
      workflow = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
    } catch (e) {
      console.error('Error: Invalid JSON in workflow file');
      process.exit(1);
    }
    
    const args = {
      steps: workflow.steps,
      synthesis_mode: workflow.synthesis_mode || 'merge',
      workflow_id: workflow.id || path.basename(filePath, '.json')
    };
    
    runMcpTool('conductor', 'workflow_orchestrate', args);
    break;
  }

  case 'explain': {
    const intent = positional.join(' ');
    if (!intent) {
      console.error('Error: Intent description required');
      process.exit(1);
    }
    
    const techStack = parseTechStack();
    const context = parseContext();
    
    const args = {
      intent: intent,
      context: {
        ...context,
        ...(techStack.length > 0 && { tech_stack: techStack })
      }
    };
    
    runMcpTool('conductor', 'explain_plan', args);
    break;
  }

  case 'status': {
    const planId = positional[0];
    if (!planId) {
      console.error('Error: Plan ID required');
      process.exit(1);
    }
    
    runMcpTool('conductor', 'get_execution_status', { plan_id: planId });
    break;
  }

  case 'context': {
    const sessionId = positional[0];
    const contextAction = positional[1];
    
    if (!sessionId || !contextAction) {
      console.error('Error: Session ID and action required');
      console.error('Usage: /conductor context <session_id> <store|retrieve|merge|clear>');
      process.exit(1);
    }
    
    const validActions = ['store', 'retrieve', 'merge', 'clear'];
    if (!validActions.includes(contextAction)) {
      console.error(`Error: Invalid action. Valid: ${validActions.join(', ')}`);
      process.exit(1);
    }
    
    const args = {
      session_id: sessionId,
      action: contextAction
    };
    
    if ((contextAction === 'store' || contextAction === 'merge') && options.data) {
      try {
        args.data = JSON.parse(options.data);
      } catch (e) {
        console.error('Error: Invalid data JSON');
        process.exit(1);
      }
    }
    
    runMcpTool('conductor', 'context_preservation', args);
    break;
  }

  case 'learn': {
    const planId = positional[0];
    if (!planId) {
      console.error('Error: Plan ID required');
      process.exit(1);
    }
    
    if (!options.rating) {
      console.error('Error: --rating required (0.0-1.0)');
      process.exit(1);
    }
    
    const args = {
      plan_id: planId,
      success_rating: parseFloat(options.rating)
    };
    
    if (options.tags) {
      args.tags = options.tags.split(',');
    }
    
    runMcpTool('conductor', 'learn_workflow', args);
    break;
  }

  default:
    console.error(`Unknown action: ${action}`);
    showHelp();
    process.exit(1);
}
