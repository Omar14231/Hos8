import discord
from discord.ext import commands
import os
from flask import Flask, jsonify, request
from threading import Thread

app = Flask(__name__)
chat_history = {} # تخزين الرسائل حسب JobId السيرفر

# مسار الفحص المخصص لـ UptimeRobot (يقبل HTTP Head & Get)
@app.route('/', methods=['GET', 'HEAD'])
def health_check():
    return "OK", 200

# مسار استرجاع الرسائل لسكريبت اللعبة
@app.route('/get_messages/<job_id>', methods=['GET'])
def get_messages(job_id):
    return jsonify(chat_history.get(job_id, []))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

CHANNEL_ID = 1547629102830452746

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot and message.channel.id == CHANNEL_ID:
        lines = message.content.split('\n')
        if len(lines) >= 2:
            try:
                header = lines[0].split(' : ', 1)
                ids = lines[1].split('/')
                
                if len(header) == 2 and len(ids) == 2:
                    player_name = header[0].strip()
                    text_msg = header[1].strip()
                    map_id = ids[0].strip()
                    job_id = ids[1].strip()
                    
                    if job_id not in chat_history:
                        chat_history[job_id] = []
                    
                    chat_history[job_id].append({
                        "player": player_name,
                        "message": text_msg
                    })
            except Exception:
                pass
                
    await bot.process_commands(message)

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # تشغيل خادم الويب في خلفية متوازية مع البوت
    Thread(target=run_flask, daemon=True).start()
    bot.run(os.environ.get('DISCORD_TOKEN'))
