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



## Details For Tasks Discord Bot Core

- Interactivity can be via commands or Discord UI.

- `/tasks create`
  - Shows a UI for the user to create a task.
  - User can select **title**, **description**, **deadline**, and **priority**.

- `/tasks assign`
  - Admins and managers only.
  - Assign a task to a user or multiple users.
  - UI similar to `/tasks create` with an additional input for selecting assignees.

- `/tasks my`
  - Returns a list of tasks assigned to the user.

- `/tasks done`
  - Changes status of a task from **ongoing** to **done**.

- `/tasks cancel`
  - Allows the user to cancel their own task.

- `/tasks filter [user?]`
  - Returns a list of tasks for a specific user.
  - If no user is provided, returns a summary of all users with the number of tasks each has.

- `/tasks remind [user] [task]`
  - Sends a reminder DM to the user.
  - Can also send reminders in the Discord channel.
  - Tasks can be scheduled to automatically remind users after a set duration.

- `/tasks config [time] [task?] [user?]`
  - Controls how much time before the user is reminded about a task.
  - If no task is provided, sets a default reminder time for all tasks for the user.
  - The user option allows admins to set a custom reminder time for a specific user.



## Backend and Database Tasks
- Models
    - user: username, roles, defaultReminderTime
    - task: title, desc, assignees, status, priority, deadline

- Function: function will be exported from you script and used by the second dev
    - create_task(userId, title, description?, deadline?, priority?) -> returns task object
    - assign_task(taskId, assigneeIds) -> returns updated task object
    - mark_task_done(taskId, doneById) -> returns updated task object
    - cancel_task(taskId, cancelledById) -> returns updated task object
    - get_task(taskId) -> returns task object
    - list_tasks(filter?) -> returns array of task objects
    - send_task_reminder(taskId, userId?, channelId?) -> returns reminder object
    - configure_task_reminder(userId?, taskId?, timeBefore?) -> returns updated reminder config

- Features
    - expose some llm agent with some personalty to the bot, so he can send messages to threaten (xD) or be nice with the users
    - rate limit to stop spamming


