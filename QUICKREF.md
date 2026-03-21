# Kimi CLI Quick Reference

## Web & Search
```bash
/get <url>                    # Scrape webpage
/get --map <url>              # Map site URLs
/get --crawl <url>            # Crawl multiple pages
/get --extract <url>          # Extract structured data

/search <query>               # Web search
/search <query> --scrape      # Search + fetch top 3

/ask <question>               # Quick answer
/ask --deep <question>        # Research mode
/ask --reason <question>      # Step-by-step
```

## Documentation
```bash
/docs <library> <query>       # Query Context7 docs
/docs react useEffect
/docs pandas DataFrame
```

## Reasoning & Execution
```bash
/think <problem>              # Sequential reasoning
/think --store <k> <v>        # Save thought
/think --recall <k>           # Load thought

/do <intent>                  # Execute task
/do <intent> --explain        # Preview plan

/run <workflow>               # Run workflow
/run --list                   # List workflows
/run <wf> --dry-run           # Validate only

/check <execution-id>         # Check status
/check --recent 10            # List recent
```

## GitHub
```bash
/gh issues list [repo]        # List issues
/gh issues get <n>            # Get issue
/gh issues create <title>     # Create issue

/gh prs list [repo]           # List PRs
/gh prs get <n>               # Get PR
/gh prs merge <n>             # Merge PR

/gh repos list                # List repos
/gh repos get <o/r>           # Get repo

/gh branches list <o/r>       # List branches
/gh branches create <o/r/b>   # Create branch
```

## Linear
```bash
/linear issues list           # List issues
/linear issues get <id>       # Get issue
/linear issues create <t>     # Create issue

/linear teams list            # List teams
/linear projects list         # List projects
/linear cycles list           # List cycles
```

## System
```bash
/session save <n> [msg]       # Save session
/session load <n>             # Load session
/session list                 # List sessions
/session delete <n>           # Delete session

/config list                  # List config
/config get <k>               # Get value
/config set <k> <v>           # Set value
/config delete <k>            # Delete key

/help                         # Show help
/help <command>               # Command help
```
