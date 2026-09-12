@bot.event
async def on_message(message):
    # التأكد من الروم المحددة وأن الرسالة قادمة من الويب هوك (Bot)
    if message.channel.id == CHANNEL_ID and message.author.bot:
        lines = [line.strip() for line in message.content.split('\n') if line.strip()]
        if len(lines) >= 2:
            try:
                # البحث عن النقطتين : للتقسيم بغض النظر عن المسافات
                if ':' in lines[0]:
                    player_name, text_msg = lines[0].split(':', 1)
                    player_name = player_name.strip()
                    text_msg = text_msg.strip()
                else:
                    return

                # البحث عن / لتقسيم PlaceId و JobId
                if '/' in lines[1]:
                    ids = lines[1].split('/', 1)
                    map_id = ids[0].strip()
                    job_id = ids[1].strip()
                else:
                    return

                if job_id not in chat_history:
                    chat_history[job_id] = []

                # إضافة الرسالة لقائمة السيرفر
                chat_history[job_id].append({
                    "player": player_name,
                    "message": text_msg
                })
                print(f"Recorded message for {job_id}: [{player_name}]: {text_msg}")
            except Exception as e:
                print(f"Error parsing message: {e}")
                
    await bot.process_commands(message)
