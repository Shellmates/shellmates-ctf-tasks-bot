# Contributing Guidelines

## Commit Conventions

Use conventional commit messages:

```
feat: add team creation command
fix: resolve flag submission validation bug  
docs: update API endpoint documentation
refactor: reorganize bot command handlers
test: add unit tests for scoreboard endpoints
chore: update dependencies
```

**Types**: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`, `ci`

## Adding Dependencies


### Bot (Discord.py)
```bash
cd bot  
pip install <package>
pip freeze > requirements.txt
```

Always update the appropriate `requirements.txt` file when adding new packages.

## Issues

- Use clear, descriptive titles
- Provide steps to reproduce for bugs
- Include environment details (Python version, OS)
- Label appropriately: `bug`, `feature`, `enhancement`, `documentation`

## Pull Requests

1. Fork the repo and create feature branch: `git checkout -b feature/your-feature`
2. Make changes and commit with conventional messages
3. Update relevant documentation
4. Test your changes locally
5. Submit PR with clear description of changes
6. Link related issues using `Fixes #123`

**PR Title Format**: `feat: add team management commands`
