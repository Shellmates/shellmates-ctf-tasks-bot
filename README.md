# Discord Task Manager Bot

## Project Overview

The **Task Manager Bot** is a lightweight yet powerful Discord bot designed to help teams organize and track their work inside a Discord server.\
It allows members to create tasks, assign them, set deadlines, and get reminders—all without leaving Discord.

---

## Core Features

### Task Management

- Create tasks with `/task add`.
- List tasks with `/tasks my` (personal) or `/tasks all` (server-wide).
- Mark tasks as done with `/task done`.
- Assign tasks to yourself or other members.

### Reminders & Deadlines

- Get notified before due dates.
- Weekly summary of all pending tasks posted in a channel.
- Deadline alerts (e.g., "Task X is due tomorrow").

### Roles & Permissions

- **Managers**: Can assign tasks to members, mark any task done.
- **Members**: Can only mark their own tasks done (unless manager).

---

## Quality of Life Features

- **Interactivity**: Buttons & dropdowns for marking tasks done or editing due dates.
- **Slash Commands**: `/tasks my`, `/tasks all`, `/tasks due`.
- **Personalization**: Optional DM reminders for assigned tasks.
- **Per-User Lists**: Keep personal task lists separate from team tasks.
- **UI Enhancements**: Rich embeds with task details (title, assignee, due date, status).
- **Status Indicators**: done, pending, overdue.

---

## Stretch Goals (Nice to Have)

- **Personality Layer**: Friendly nudges or encouragement via LLM integration.
- **Kanban View**: Simple web dashboard showing tasks in columns (To Do / In Progress / Done).
- **Integrations**: Export tasks to Google Calendar or Trello.
- **Archiving**: Store completed tasks in DB for long-term progress tracking.

---

## Tech Stack

- **Bot Framework**: Discord.py (interactions, slash commands, buttons).
- **Database**: MongoDB (tasks, assignments, reminders, archives).
- *(Optional)* Web frontend for Kanban view (React).

---

## Suggested Folder Structure

```
task-manager-bot/
├── backend/
│   ├── api/
│   ├── database/
│   │   └── mongo_config.py
│   ├── main.py
│   ├── requirements.txt
│   └── .env
├── bot/
│   ├── cogs/
│   ├── utils/
│   ├── bot.py
│   └── requirements.txt
├── docs/
├── .env.example
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

## Required Environment Variables

| Variable        | Description                      |
| --------------- | -------------------------------- |
| `DISCORD_TOKEN` | Discord bot authentication token |
| `MONGO_URI`     | MongoDB connection string        |
| `MONGO_DB_NAME` | Database name                    |

