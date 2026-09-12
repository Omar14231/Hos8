import discord
from discord.ext import commands
import os
from flask import Flask, jsonify
from threading import Thread

app = Flask(__name__)
chat_history = {} # تخزين الرسائل بناءً على ID السيرفر

# مسار HTTP ليقرأ منه سكريبت روبلوكس الرسائل
@app.route('/get_messages/<job_id>')
def get_messages(job_id):
    return jsonify(chat_history.get(job_id, []))

# مسار أساسي لخداع Render ليبقي المشروع يعمل كـ Web Service
@app.route('/')
def home():
    return "Server is running!"

def run_http():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

CHANNEL_ID = 1547629102830452746

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")

@bot.event
async def on_message(message):
    # التأكد أن الرسالة جاءت من الويب هوك وفي الروم المحددة
    if message.author.bot and message.channel.id == CHANNEL_ID:
        lines = message.content.split('\n')
        if len(lines) >= 2:
            try:
                # تفكيك صيغة الويب هوك: "الاسم : النص"
                header = lines[0].split(' : ', 1)
                # تفكيك: "ID_Map/ID_Server"
                ids = lines[1].split('/')
                
                if len(header) == 2 and len(ids) == 2:
                    player_name = header[0].strip()
                    text_msg = header[1].strip()
                    map_id = ids[0].strip()
                    job_id = ids[1].strip()
                    
                    if job_id not in chat_history:
                        chat_history[job_id] = []
                    
                    # حفظ الرسالة في السجل الأبدي للسيرفر
                    chat_history[job_id].append({
                        "player": player_name,
                        "message": text_msg
                    })
            except Exception as e:
                pass
                
    await bot.process_commands(message)

if __name__ == "__main__":
    Thread(target=run_http).start()
    # تأكد من وضع DISCORD_TOKEN في إعدادات Environment Variables في Render
    bot.run(os.environ.get('DISCORD_TOKEN'))

