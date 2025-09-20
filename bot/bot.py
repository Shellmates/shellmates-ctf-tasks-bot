import os
import logging
import discord
from discord.ext import commands, tasks
from discord import app_commands
from dotenv import load_dotenv
from datetime import datetime
from storage import add_task, get_user_tasks, get_all_tasks, mark_task_done

# ----------------------------
# Setup
# ----------------------------
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
REMINDER_CHANNEL_ID = int(os.getenv("REMINDER_CHANNEL_ID", 0))

if not TOKEN:
    raise RuntimeError("Set DISCORD_TOKEN in .env")

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
logging.basicConfig(level=logging.DEBUG)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ----------------------------
# Modal for adding tasks
# ----------------------------
class TaskModal(discord.ui.Modal, title="Add a Task"):
    task_title = discord.ui.TextInput(
        label="Task Title",
        placeholder="Enter your task",
        required=True,
        max_length=100
    )
    due_date = discord.ui.TextInput(
        label="Due Date",
        placeholder="YYYY-MM-DD",
        required=True
    )

    def __init__(self, user):
        super().__init__()
        self.user = user

    async def on_submit(self, interaction: discord.Interaction):
        try:
            due_date_obj = datetime.strptime(str(self.due_date), "%Y-%m-%d").date()
        except ValueError:
            await interaction.response.send_message("❌ Invalid date format. Use YYYY-MM-DD.", ephemeral=True)
            return

        if due_date_obj < datetime.utcnow().date():
            await interaction.response.send_message("⚠️ Due date cannot be in the past.", ephemeral=True)
            return

        task = add_task(str(self.task_title), self.user.id, due_date_obj)
        await interaction.response.send_message(
            f"✅ Task added: **{task['title']}** (due {task['due_date']})",
            ephemeral=True
        )

# ----------------------------
# Dropdown for marking tasks done
# ----------------------------
class TaskSelect(discord.ui.Select):
    def __init__(self, user):
        tasks = get_user_tasks(user.id)

        options = [
            discord.SelectOption(
                label=t["title"],
                description=f"Due: {t['due_date']} (ID: {t['id']})",
                value=str(t["id"])
            )
            for t in tasks
        ]

        if not options:
            options = [discord.SelectOption(label="No tasks available", value="none")]

        super().__init__(
            placeholder="Choose a task to mark as done",
            min_values=1,
            max_values=1,
            options=options
        )
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "none":
            await interaction.response.send_message("❌ You have no tasks to complete.", ephemeral=True)
            return

        task_id = int(self.values[0])
        success, message = mark_task_done(task_id, self.user.id)
        await interaction.response.send_message(message, ephemeral=True)


class TaskSelectView(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=60)
        self.add_item(TaskSelect(user))


# ----------------------------
# Slash Commands
# ----------------------------
@bot.tree.command(name="task_add", description="Add a new task using a form")
async def task_add(interaction: discord.Interaction):
    modal = TaskModal(interaction.user)
    await interaction.response.send_modal(modal)

@bot.tree.command(name="tasks_my", description="List your pending tasks")
async def tasks_my(interaction: discord.Interaction):
    user_tasks = get_user_tasks(interaction.user.id)
    if not user_tasks:
        await interaction.response.send_message("You have no pending tasks.", ephemeral=True)
        return
    embed = discord.Embed(title=f"{interaction.user.name}'s tasks", color=discord.Color.blue())
    for t in user_tasks:
        embed.add_field(name=t["title"], value=f"Due: {t['due_date']} | ID: {t['id']}", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="tasks_all", description="List all server-wide tasks")
async def tasks_all(interaction: discord.Interaction):
    all_tasks = get_all_tasks()
    if not all_tasks:
        await interaction.response.send_message("No tasks found.", ephemeral=True)
        return
    embed = discord.Embed(title="All Tasks", color=discord.Color.green())
    for t in all_tasks:
        status = "✅ Done" if t["status"] == "done" else "⌛ Pending"
        embed.add_field(
            name=t["title"],
            value=f"Due: {t['due_date']} | Assigned: <@{t['assignee']}> | Status: {status}",
            inline=False
        )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="task_done", description="Mark one of your tasks as done")
async def task_done(interaction: discord.Interaction):
    user_tasks = get_user_tasks(interaction.user.id)
    if not user_tasks:
        await interaction.response.send_message("❌ You have no pending tasks.", ephemeral=True)
        return

    view = TaskSelectView(interaction.user)
    await interaction.response.send_message("Select a task to mark as done:", view=view, ephemeral=True)


# ----------------------------
# Reminder System
# ----------------------------
@tasks.loop(minutes=1)
async def task_reminder_loop():
    today = datetime.utcnow().date()
    tasks = get_all_tasks()

    for t in tasks:
        if t["status"] != "pending" or t["reminded"]:
            continue
        due_date = datetime.strptime(t["due_date"], "%Y-%m-%d").date()
        days_left = (due_date - today).days

        if days_left <= 1:
            user = await bot.fetch_user(t["assignee"])
            reminder_message = f"⏰ Reminder: Your task **{t['title']}** is due on **{t['due_date']}**!"
            try:
                await user.send(reminder_message)
            except discord.Forbidden:
                if REMINDER_CHANNEL_ID:
                    channel = bot.get_channel(REMINDER_CHANNEL_ID)
                    if channel:
                        await channel.send(f"{user.mention} {reminder_message}")
            t["reminded"] = True
    # save updates
    from storage import save_tasks
    save_tasks(tasks)

# ----------------------------
# Lifecycle Events
# ----------------------------
async def setup_hook():
    await bot.tree.sync()
    print("✅ Synced slash commands")
    task_reminder_loop.start()

bot.setup_hook = setup_hook

@bot.event
async def on_ready():
    print(f"Bot ready: {bot.user} (id: {bot.user.id})")

# ----------------------------
# Run Bot
# ----------------------------
if __name__ == "__main__":
    bot.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)
