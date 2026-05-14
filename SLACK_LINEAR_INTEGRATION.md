# Linear + Slack Integration (KIM-3)

## Status
- Linear item KIM-3 updated to In Progress
- Branch: feat/KIM-3-linear-slack-integration created
- mcp_config.json updated with Slack server entry (on branch)

## Official Linear Slack Integration
Linear has built-in Slack integration:
- Create issues from Slack messages
- Sync threads to Linear comments
- Enable in Linear settings > Integrations > Slack

## MCP Client Extension
To fully integrate in this Kimi CLI MCP client:
1. Add Slack MCP server to mcp_config.json (done)
2. Create kimi_mcp_client/servers/slack.py wrapper
3. Expose in KimiMCPClient
4. Add workflows e.g. slack_to_linear_issue()

## Next Steps
- Implement Slack server wrapper
- Test with Linear issue creation from Slack
- Update README and tests

Closes KIM-3