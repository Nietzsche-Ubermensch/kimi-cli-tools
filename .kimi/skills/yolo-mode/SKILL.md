# Yolo Mode Skill

## Description
Enables autonomous execution mode for the Kimi CLI. When activated, the AI proceeds with actions without asking for user confirmation at each step, streamlining workflows for experienced users who trust the AI's judgment.

## Triggers

### Primary Triggers
- `/yolo` - Activate yolo mode for the current session
- `/yolo on` - Explicitly enable yolo mode
- `/yolo off` - Disable yolo mode

### Contextual Triggers
- User says "just do it" or "go ahead"
- User says "proceed without asking" or "don't ask for confirmation"
- User explicitly requests autonomous mode

## Behavior

### When Yolo Mode is ACTIVE
The AI will:
- Execute shell commands without confirmation prompts
- Write files without showing diffs first
- Make git commits/pushes when requested
- Install packages and dependencies automatically
- Delete files when necessary for cleanup
- Restart services/processes as needed
- Create/update GitHub resources (issues, PRs)

The AI will STILL ask for confirmation when:
- Deleting entire directories with important content
- Accessing files outside the working directory
- Operations requiring elevated (Administrator) privileges
- Destructive operations on production systems
- Accessing sensitive credential files

### When Yolo Mode is INACTIVE (default)
The AI will:
- Ask for confirmation before destructive operations
- Show file diffs before writing
- Prompt before executing shell commands
- Request explicit approval for git mutations

## Configuration

### Environment Variable
```bash
KIMI_YOLO_MODE=true  # Enable yolo mode globally
```

### Session State
Yolo mode can be toggled per session using the `/yolo` command.

## Usage Examples

### Enable Yolo Mode
```
/yolo
```
Response: "🚀 Yolo mode activated. I'll proceed with actions without confirmation."

### Disable Yolo Mode
```
/yolo off
```
Response: "🛑 Yolo mode deactivated. I'll ask for confirmation before actions."

### Check Status
```
/yolo status
```
Response: "Yolo mode is currently: ACTIVE/INACTIVE"

## Safety Guardrails

Even in yolo mode, the following protections remain:

1. **Path Restrictions**: Cannot access files outside working directory
2. **Git Safety**: Won't force-push or rewrite history unless explicitly requested
3. **Production Awareness**: Warns before operations on production-like environments
4. **Credential Protection**: Won't expose API keys or tokens in output
5. **Rate Limiting**: Respects API rate limits for external services

## Integration with Other Skills

### MCP Server Workflows
When yolo mode is active, MCP server operations proceed without intermediate confirmation:
- Linear issue creation happens immediately
- GitHub PRs are created without preview prompts
- Firecrawl extractions execute directly
- Browser automation proceeds without step-by-step approval

### Execution Chains
Multi-step workflows execute seamlessly:
```
User: "/yolo"
User: "Research Hacker News, extract top 3 stories, create Linear issue"
→ AI executes entire chain without interruption
```

## Best Practices

### When to Use Yolo Mode
- ✅ Repetitive development tasks
- ✅ Trusted automation workflows
- ✅ Rapid prototyping sessions
- ✅ Batch operations on test data

### When NOT to Use Yolo Mode
- ❌ Production system changes
- ❌ Irreversible data operations
- ❌ First-time exploration of a codebase
- ❌ Security-sensitive operations

## Related Commands

- `/mcp` - View MCP server status
- `/task` - Manage background tasks
- `/plan` - Enter plan mode (always asks for approval)
