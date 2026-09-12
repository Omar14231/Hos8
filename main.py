import os
from threading import Thread
from flask import Flask, jsonify
import discord
from discord.ext import commands

# 1. إعداد خادم Flask
app = Flask(__name__)
chat_history = {}

@app.route('/', methods=['GET', 'HEAD'])
def health_check():
    return "OK", 200

@app.route('/get_messages/<job_id>', methods=['GET'])
def get_messages(job_id):
    return jsonify(chat_history.get(job_id, []))

# 2. تعريف البوت (يجب أن يكون هنا قبل الاستدعاءات)
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

CHANNEL_ID = 1547629102830452746

# 3. معالجة الأحداث والرسائل
@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.channel.id == CHANNEL_ID and message.author.bot:
        lines = [line.strip() for line in message.content.split('\n') if line.strip()]
        if len(lines) >= 2:
            try:
                if ':' in lines[0]:
                    player_name, text_msg = lines[0].split(':', 1)
                    player_name = player_name.strip()
                    text_msg = text_msg.strip()
                else:
                    return

                if '/' in lines[1]:
                    ids = lines[1].split('/', 1)
                    job_id = ids[1].strip()
                else:
                    return

                if job_id not in chat_history:
                    chat_history[job_id] = []

                chat_history[job_id].append({
                    "player": player_name,
                    "message": text_msg
                })
                print(f"Recorded message for {job_id}: [{player_name}]: {text_msg}")
            except Exception as e:
                print(f"Error parsing message: {e}")
                
    await bot.process_commands(message)

# 4. تشغيل خادم الويب والبوت
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    bot.run(os.environ.get('DISCORD_TOKEN'))
