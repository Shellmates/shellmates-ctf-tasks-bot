import os
import logging
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime

# ----------------------------
# Setup & Configuration
# ----------------------------
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
REMINDER_CHANNEL_ID = int(os.getenv("REMINDER_CHANNEL_ID", 0))  # 👈 optional fallback channel

if not TOKEN:
    raise RuntimeError("Set DISCORD_TOKEN in .env")

# Logging
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
logging.basicConfig(level=logging.DEBUG)

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Bot
bot = commands.Bot(command_prefix="!", intents=intents)

# ----------------------------
# Task Manager
# ----------------------------
tasks_data = []  

class MarkDoneView(discord.ui.View):
    def __init__(self, task_id, owner_id):
        super().__init__(timeout=None)
        self.task_id = task_id
        self.owner_id = owner_id

    @discord.ui.button(label="Mark done ✅", style=discord.ButtonStyle.green)
    async def mark_done(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message("This is not your task.", ephemeral=True)
            return
        for t in tasks_data:
            if t["id"] == self.task_id and t["status"] == "pending":
                t["status"] = "done"
                await interaction.response.edit_message(
                    content=f"✅ Task **{t['title']}** marked done.", 
                    view=None
                )
                return
        await interaction.response.send_message("Task not found or already done.", ephemeral=True)


# ----------------------------
# Slash Commands
# ----------------------------
@bot.tree.command(name="task_add", description="Add a new task with a title and due date")
@app_commands.describe(
    title="Short title of the task",
    due_date="Due date in format YYYY-MM-DD"
)
async def task_add(interaction: discord.Interaction, title: str, due_date: str):
    # ✅ Validate date format
    try:
        due_date_obj = datetime.strptime(due_date, "%Y-%m-%d").date()
    except ValueError:
        await interaction.response.send_message(
            "❌ Invalid date format. Please use `YYYY-MM-DD` (e.g., `2025-09-20`).",
            ephemeral=True
        )
        return

    # ✅ Check if due date is in the past
    if due_date_obj < datetime.utcnow().date():
        await interaction.response.send_message(
            "⚠️ The due date cannot be in the past.",
            ephemeral=True
        )
        return

    task_id = len(tasks_data) + 1
    tasks_data.append({
        "id": task_id,
        "title": title,
        "assignee": interaction.user.id,
        "due_date": str(due_date_obj),
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "reminded": False
    })
    view = MarkDoneView(task_id, interaction.user.id)
    await interaction.response.send_message(
        f"Task added: **{title}** (due: {due_date_obj})", 
        view=view
    )


@bot.tree.command(name="tasks_my", description="List your pending tasks")
async def tasks_my(interaction: discord.Interaction):
    user_tasks = [t for t in tasks_data if t["assignee"] == interaction.user.id and t["status"] == "pending"]
    if not user_tasks:
        await interaction.response.send_message("You have no pending tasks.")
        return
    embed = discord.Embed(title=f"{interaction.user.name}'s tasks", color=discord.Color.blue())
    for t in user_tasks:
        embed.add_field(name=t["title"], value=f"Due: {t['due_date']} | ID: {t['id']}", inline=False)
    await interaction.response.send_message(embed=embed)


# ----------------------------
# Reminder System
# ----------------------------
@tasks.loop(minutes=1)
async def task_reminder_loop():
    today = datetime.utcnow().date()
    for t in tasks_data:
        if t["status"] != "pending" or t["reminded"]:
            continue

        due_date = datetime.strptime(t["due_date"], "%Y-%m-%d").date()
        days_left = (due_date - today).days

        if days_left <= 1:  # today or tomorrow
            user = await bot.fetch_user(t["assignee"])
            reminder_message = f"⏰ Reminder: Your task **{t['title']}** is due on **{t['due_date']}**!"

            try:
                await user.send(reminder_message)
                print(f"Sent DM to {user.name} for task {t['id']}")
            except discord.Forbidden:
                print(f"Could not DM {user.name}, trying fallback channel...")
                if REMINDER_CHANNEL_ID:
                    channel = bot.get_channel(REMINDER_CHANNEL_ID)
                    if channel:
                        await channel.send(f"{user.mention} {reminder_message}")

            t["reminded"] = True  # avoid duplicate reminders


# ----------------------------
# Moderation & Events
# ----------------------------
@bot.event
async def on_member_join(member):
    try:
        await member.send(f"Welcome to the server, {member.name}!")
    except discord.Forbidden:
        print(f"Could not DM {member.name}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if "shit" or "fuck" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} - Don't use that word again!")
    await bot.process_commands(message)  


# ----------------------------
# Lifecycle Events
# ----------------------------
async def setup_hook():
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"❌ Failed syncing commands: {e}")

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


