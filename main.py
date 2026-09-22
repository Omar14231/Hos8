import os
import threading
import aiohttp
import discord
from discord.ext import commands
from http.server import HTTPServer, BaseHTTPRequestHandler

# ==========================================
# 1. خادم HTTP خفيف لإبقاء البوت يعمل 24/7 على Render
# ==========================================
class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write("🤖 البوت يعمل بنجاح 24/7 بدون توقف!".encode('utf-8'))

def run_http_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), KeepAliveHandler)
    server.serve_forever()

threading.Thread(target=run_http_server, daemon=True).start()

# ==========================================
# 2. إعدادات البوت والتعرف على الملك
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
# 3. محرك محادثة Gemini AI (نظيف ومحترم)
# ==========================================
async def ask_gemini(prompt: str) -> str:
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        return "⚠️ لم يتم إضافة GEMINI_API_KEY في إعدادات البيئة (Render)."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
    
    # تعليمات الأمان والصلاحيات الأخلاقية الصارمة
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
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "candidates" in data and len(data["candidates"]) > 0:
                        return data["candidates"][0]["content"]["parts"][0]["text"]
                return "❌ تعذر الحصول على إجابة من Gemini حالياً."
    except Exception as e:
        return f"❌ حدث خطأ أثناء الاتصال بـ Gemini: {str(e)}"

# ==========================================
# 4. أمر التفعيل والأوامر الإدارية للملك
# ==========================================

@bot.command(name="10")
async def start_channel_rule(ctx):
    global active_channel_id
    
    # حصر الأمر للملك فقط
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
        "4️⃣ جميع الأوامر الإدارية (إنشاء رتب، رومات، أو تغيير الصورة) محصورة للملك فقط."
    )
    await ctx.send(rules_text)

# أوامر التحكم بالسيرفر للملك فقط
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
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    await ctx.guild.edit(icon=data)
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
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status == 200:
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
# 6. التفاعل التلقائي مع الرسائل (Gemini AI Chat)
# ==========================================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # معالجة الأوامر أولاً (مثل !10 أو !تخيل)
    await bot.process_commands(message)

    # إذا كانت الرسالة في الروم المحدد، وليست أمراً يبدأ بـ !
    if active_channel_id and message.channel.id == active_channel_id:
        if not message.content.startswith("!"):
            async with message.channel.typing():
                response = await ask_gemini(message.content)
                await message.reply(response)

# تشغيل البوت
token = os.environ.get("DISCORD_TOKEN")
if token:
    bot.run(token)
else:
    print("❌ خطأ: لم يتم العثور على DISCORD_TOKEN!")
