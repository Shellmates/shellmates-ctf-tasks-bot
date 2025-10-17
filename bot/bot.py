import os
import sys
import logging
import discord
from discord.ext import commands, tasks
from discord import app_commands
from dotenv import load_dotenv
from datetime import datetime
from bson import ObjectId

# ----------------------------
# Path setup: make sure backend can be imported
# ----------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from api.tasks import create_task, get_task, list_tasks, assign_task, mark_task_done, cancel_task
from api.users import getorcreateuser

# ----------------------------
# Load environment variables
# ----------------------------
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

TOKEN = os.getenv("DISCORD_TOKEN")
REMINDER_CHANNEL_ID = int(os.getenv("REMINDER_CHANNEL_ID", 0))

if not TOKEN:
    raise RuntimeError("❌ Missing DISCORD_TOKEN in .env")

# ----------------------------
# Logging setup
# ----------------------------
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
#logging.basicConfig(level=logging.DEBUG)

# ----------------------------
# Bot setup
# ----------------------------
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
        placeholder="Enter your task title",
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

        # ✅ Make sure we register this Discord user in MongoDB
        dbuser = getorcreateuser(None, str(self.user.name))

        # ✅ Use the user's Discord ID so tasks_my can find it later
        task = create_task(
            dbuser,
            str(self.user.id),  # 👈 this fixes the problem
            str(self.task_title),
            f"Task added via Discord by {self.user.name}",
            "medium",
            str(due_date_obj)
        )

        await interaction.response.send_message(
            f"✅ Task created: **{task['title']}** (due {task['deadline']})",
            ephemeral=True
        )

# ----------------------------
# Slash Commands
# ----------------------------
@bot.tree.command(name="task_add", description="Add a new task using a form")
async def task_add(interaction: discord.Interaction):
    modal = TaskModal(interaction.user)
    await interaction.response.send_modal(modal)

@bot.tree.command(name="tasks_my", description="List your tasks from MongoDB")
async def tasks_my(interaction: discord.Interaction):

    dbuser = getorcreateuser(None, str(interaction.user.name))
    user_tasks = list_tasks(dbuser)

    if not user_tasks:
        await interaction.response.send_message("📭 You have no tasks.", ephemeral=True)
        return

    embed = discord.Embed(title=f"{interaction.user.name}'s Tasks", color=discord.Color.blurple())
    for t in user_tasks:
        embed.add_field(
            name=t["title"],
            value=f"Due: {t.get('deadline', 'N/A')} | Status: {t.get('status', 'Pending')}",
            inline=False
        )
    await interaction.response.send_message(embed=embed, ephemeral=True)




@bot.tree.command(name="task_assign", description="Assign a task to a user")
async def task_assign(interaction: discord.Interaction, task_id: str, assignee: discord.User):
    dbuser = getorcreateuser(None, str(interaction.user.name))
    result= assign_task(task_id, str(assignee.name), dbuser)
    
    if result:
        embed = discord.Embed(
            title="Task Assigned",
            description=f"Task '{result.get('title', 'Unknown')}' assigned to {assignee.name}",
            color=discord.Color.green()
        )
        embed.add_field(
            name="Due Date",
            value=result.get('deadline', 'N/A'),
            inline=True
        )
        embed.add_field(
            name="Status",
            value=result.get('status', 'Pending'),
            inline=True
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message(f"Failed to assign task", ephemeral=True)


@bot.tree.command(name="tasks_all", description="List all tasks from the database")
async def tasks_all(interaction: discord.Interaction):
    all_tasks = list_tasks(None)
    if not all_tasks:
        await interaction.response.send_message("📂 No tasks found in the database.", ephemeral=True)
        return

    embed = discord.Embed(title="All Tasks", color=discord.Color.green())
    for t in all_tasks:
        embed.add_field(
            name=t["title"],
            value=f"ID: {t.get('_id','')} By: {t.get('createdby_name', 'Unknown')} | Due: {t.get('deadline', 'N/A')} | Status: {t.get('status', 'Pending')}",
            inline=False
        )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="task_done", description="Mark one of your tasks as done")
async def task_done(interaction: discord.Interaction):
    dbuser = getorcreateuser(None, str(interaction.user.name))
    user_tasks = list_tasks(dbuser)

    if not user_tasks:
        await interaction.response.send_message("❌ You have no tasks to complete.", ephemeral=True)
        return

    # Create dropdown for user tasks
    options = [
        discord.SelectOption(label=t["title"], value=str(t["_id"])) for t in user_tasks
    ]

    class TaskSelect(discord.ui.Select):
        def __init__(self):
            super().__init__(
                placeholder="Select a task to mark as done",
                min_values=1,
                max_values=1,
                options=options
            )

        async def callback(self, interaction: discord.Interaction):
            selected_id = self.values[0]
            updated = mark_task_done(ObjectId(selected_id), dbuser)
            await interaction.response.send_message(
                f"✅ Task **{updated['title']}** marked as done!", ephemeral=True
            )

    view = discord.ui.View()
    view.add_item(TaskSelect())
    await interaction.response.send_message("Select a task to mark as done:", view=view, ephemeral=True)

# ----------------------------
# Task reminder loop
# ----------------------------
@tasks.loop(minutes=5)
async def task_reminder_loop():
    print("🔁 Checking for due tasks...")
    all_tasks = list_tasks(None)
    today = datetime.utcnow().date()

    for t in all_tasks:
        if t.get("status") != "Pending":
            continue

        deadline_str = t.get("deadline")
        if not deadline_str:
            continue

        try:
            deadline_date = datetime.strptime(deadline_str, "%Y-%m-%d").date()
        except Exception:
            continue

        days_left = (deadline_date - today).days
        if days_left == 1:
            reminder_msg = f"⏰ Reminder: Task **{t['title']}** is due tomorrow ({deadline_str})!"
            if REMINDER_CHANNEL_ID:
                channel = bot.get_channel(REMINDER_CHANNEL_ID)
                if channel:
                    await channel.send(reminder_msg)

# ----------------------------
# Lifecycle events
# ----------------------------
async def setup_hook():
    await bot.tree.sync()
    print("✅ Slash commands synced")
    task_reminder_loop.start()

bot.setup_hook = setup_hook

@bot.event
async def on_ready():
    print(f"🤖 Bot is online: {bot.user} (id: {bot.user.id})")

# ----------------------------
# Run bot
# ----------------------------
if __name__ == "__main__":
    bot.run(TOKEN)