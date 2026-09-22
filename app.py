import os
import threading
import requests
import discord
from discord.ext import commands
from flask import Flask

# ==========================================
# 1. تطبيق Flask لإبقاء البوت حياً (Keep-Alive)
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 البوت يعمل بنجاح 24/7 للأبد!", 200

# ==========================================
# 2. إعدادات البوت وتحديد الملك
# ==========================================
KING_USERNAME = "adsqwertt_1"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

active_channel_id = None

@bot.event
async def on_ready():
    print(f"✅ تم تسجيل الدخول بنجاح باسم البوت: {bot.user.name}")

# ==========================================
# 3. محرك المحادثة الذكي (Gemini API)
# ==========================================
def ask_gemini(prompt: str) -> str:
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        return "⚠️ لم يتم إعداد GEMINI_API_KEY في متغيّرات البيئة (Render)."

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
    
    system_instruction = (
        "أنت مساعد ذكي ومحترم في سيرفر ديسكورد. وظيفتك الإجابة على أسئلة الأعضاء ومساعدتهم. "
        "يُمنع منعاً باتاً الإجابة أو تقديم أي معلومات خادشة للحياء، غير أخلاقية، ممنوعة، أو غير قانونية. "
        "حافظ دائماً على أسلوب محترم ومفيد وبسيط بالعربية."
    )
    
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": system_instruction + "\n\nسؤال المستخدم: " + prompt}]
            }
        ]
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "candidates" in data and len(data["candidates"]) > 0:
                return data["candidates"][0]["content"]["parts"][0]["text"]
        return "❌ تعذر الحصول على إجابة من Gemini حالياً."
    except Exception as e:
        return f"❌ حدث خطأ أثناء الاتصال بـ Gemini: {str(e)}"

# ==========================================
# 4. الأوامر والإداريات (خاصة بالملك adsqwertt_1)
# ==========================================
@bot.command(name="10")
async def start_channel_rule(ctx):
    global active_channel_id
    if str(ctx.author) != KING_USERNAME:
        await ctx.send("❌ هذا الأمر مخصص للملك فقط!")
        return

    active_channel_id = ctx.channel.id
    rules_text = (
        f"👑 **تم تفعيل الروم بنجاح بواسطة الملك ({KING_USERNAME})** 👑\n\n"
        "📜 **قوانين وتوجيهات الروم:**\n"
        "1️⃣ هذا الروم مخصص للدردشة والأسئلة والإجابات عبر الذكاء الاصطناعي (Gemini AI).\n"
        "2️⃣ يمكنك توليد الصور عن طريق كتابة: `!تخيل [وصف الصورة]`\n"
        "3️⃣ يُمنع منعاً باتاً طلب أي محتوى خادش، غير أخلاقي، أو غير قانوني.\n"
        "4️⃣ جميع الأوامر الإدارية محصورة للملك فقط."
    )
    await ctx.send(rules_text)

@bot.command(name="صنع_رتبة")
async def create_role(ctx, *, role_name: str):
    if str(ctx.author) != KING_USERNAME:
        await ctx.send("❌ هذا الأمر للملك فقط!")
        return
    role = await ctx.guild.create_role(name=role_name)
    await ctx.send(f"✅ تم إنشاء الرتبة: **{role.name}**")

@bot.command(name="صنع_روم")
async def create_channel(ctx, *, channel_name: str):
    if str(ctx.author) != KING_USERNAME:
        await ctx.send("❌ هذا الأمر للملك فقط!")
        return
    channel = await ctx.guild.create_text_channel(name=channel_name)
    await ctx.send(f"✅ تم إنشاء الروم: **#{channel.name}**")

@bot.command(name="تغيير_الصورة")
async def change_icon(ctx, url: str):
    if str(ctx.author) != KING_USERNAME:
        await ctx.send("❌ هذا الأمر للملك فقط!")
        return
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            await ctx.guild.edit(icon=res.content)
            await ctx.send("✅ تم تغيير صورة السيرفر بنجاح!")
        else:
            await ctx.send("❌ تعذر تحميل الصورة من الرابط.")
    except Exception as e:
        await ctx.send(f"❌ حدث خطأ: {str(e)}")

# ==========================================
# 5. أمر توليد الصور المباشر
# ==========================================
@bot.command(name="تخيل")
async def generate_image(ctx, *, prompt: str = None):
    if active_channel_id and ctx.channel.id != active_channel_id:
        return

    if not prompt:
        await ctx.send("❌ يرجى كتابة وصف للصورة، مثال: `!تخيل سيارة مستقبلية في الليل`")
        return

    msg = await ctx.send("🎨 **جاري توليد الصورة... يرجى الانتظار**")
    encoded_prompt = prompt.replace(" ", "%20")
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"

    try:
        res = requests.get(image_url, timeout=15)
        if res.status_code == 200:
            embed = discord.Embed(
                title="✨ تم إنشاء الصورة بنجاح",
                description=f"**الوصف:** {prompt}",
                color=discord.Color.blue()
            )
            embed.set_image(url=image_url)
            embed.set_footer(text=f"طلب بواسطة: {ctx.author.name}")
            await msg.delete()
            await ctx.send(embed=embed)
        else:
            await msg.edit(content="❌ حدث خطأ أثناء جلب الصورة.")
    except Exception as e:
        await msg.edit(content=f"❌ تعذر الاتصال بخدمة الصور: {str(e)}")

# ==========================================
# 6. التفاعل التلقائي مع الدردشة (Gemini AI)
# ==========================================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)

    if active_channel_id and message.channel.id == active_channel_id:
        if not message.content.startswith("!"):
            async with message.channel.typing():
                response = ask_gemini(message.content)
                await message.reply(response)

# ==========================================
# 7. تشغيل البوت في مسار (Thread) منفصل
# ==========================================
def run_bot():
    token = os.environ.get("DISCORD_TOKEN")
    if token:
        bot.run(token)
    else:
        print("❌ خطأ: لم يتم العثور على DISCORD_TOKEN!")

# تشغيل البوت تلقائياً عند بدء gunicorn
threading.Thread(target=run_bot, daemon=True).start()
