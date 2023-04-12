import asyncio
import datetime
import random
from asyncio import sleep

import discord
from discord import Embed
from discord.ui import Button, View

intents = discord.Intents.all()  # デフォルトのIntentsオブジェクトを生成
intents.typing = False  # typingを受け取らないように
client = discord.Client(intents=intents)
print(f"Make Some Noise! (server): {discord.__version__}")


@client.event
async def on_voice_state_update(member, before, after):
    if member.id == 412082841829113877 or member.bot:  # tari3210
        return
    try:
        vc_role = member.guild.get_role(935073171462307881)  # in a vc
        if before.channel is None and bool(after.channel):
            embed = Embed(title="BEATBOXをもっと楽しむために",
                          description="", color=0x0081f0)
            embed.add_field(name=f"Let's show your 💜❤💙💚 with `{member.display_name}`!",
                            value="ビト森のすべての仲間たちと、\nもっとBEATBOXを好きになれる。\nそんなあたたかい雰囲気作りに、\nぜひ、ご協力をお願いします。")
            embed.set_footer(
                text="We love beatbox, We are beatbox family\nあつまれ！ビートボックスの森", icon_url=member.guild.icon.url)
            await after.channel.send(f"{member.mention} チャットはこちら chat is here", embed=embed, delete_after=60)
            await member.add_roles(vc_role)
        if bool(before.channel) and after.channel is None:
            await member.remove_roles(vc_role)
    except Exception:
        return


@client.event
async def on_member_join(member):
    channel = client.get_channel(864475338340171791)  # 全体チャット
    embed_discord = Embed(
        title="Discordの使い方", description="https://note.com/me1o_crew/n/nf2971acd1f1a")
    embed = Embed(title="GBBの最新情報はこちら", color=0xF0632F)
    embed.add_field(name="GBBINFO-JPN 日本非公式情報サイト",
                    value="https://gbbinfo-jpn.jimdofree.com/")
    embed.add_field(name="swissbeatbox 公式instagram",
                    value="https://www.instagram.com/swissbeatbox/")
    await channel.send(f"{member.mention}\nあつまれ！ビートボックスの森 へようこそ！", embeds=[embed_discord, embed])
    events = channel.guild.scheduled_events
    events_exist = []
    for event in events:
        if event.status in [discord.EventStatus.scheduled, discord.EventStatus.active]:
            events_exist.append(event)
    if bool(events_exist) is False:
        return
    closest_event = events_exist[0]
    for event in events_exist:
        if event.start_time < closest_event.start_time:
            closest_event = event
    await sleep(1)
    await channel.send(closest_event.url)


@client.event
async def on_message(message):
    if not message.content.startswith("s."):
        if message.author.bot or "https://gbbinfo-jpn.jimdofree.com/" in message.content:
            return
        # バトスタbot, バトスタ対戦表
        if message.channel.id in [930447365536612353, 930767329137143839]:
            if message.content.startswith("l."):
                return
            await message.delete(delay=1)
            return
        for word in ["💜❤💙💚", "brez", "ぶれず", "ブレズ", "愛", "sar", "oras"]:
            if word in message.content.lower():
                for stamp in ["💜", "❤", "💙", "💚"]:
                    await message.add_reaction(stamp)
        embed = Embed(title="GBBの最新情報はこちら", color=0xF0632F)
        embed.add_field(name="GBBINFO-JPN 日本非公式情報サイト",
                        value="https://gbbinfo-jpn.jimdofree.com/")
        embed.add_field(name="swissbeatbox 公式instagram",
                        value="https://www.instagram.com/swissbeatbox/")
        if "m!wc" in message.content.lower():
            await message.channel.send(embed=embed)
            await message.channel.send("**Wildcard結果・出場者一覧 はこちら**\nhttps://gbbinfo-jpn.jimdofree.com/20230222/")
        if message.channel.type == discord.ChannelType.text:
            emoji = random.choice(message.guild.emojis)
            await message.add_reaction(emoji)
            for word in ["gbb", "wildcard", "ワイカ", "ワイルドカード", "結果", "出場", "通過", "チケット", "ルール", "審査員", "ジャッジ", "日本人", "colaps"]:
                if word in message.content.lower():
                    if any(["?" in message.content, "？" in message.content]):
                        await message.reply("https://gbbinfo-jpn.jimdofree.com/")
                        await message.reply(embed=embed)
                    else:
                        await message.channel.send(embed=embed)
                    break
            await sleep(3600)
            try:
                await message.remove_reaction(emoji, message.guild.me)
            except Exception:
                pass

    if message.channel.id == 930839018671837184:  # バトスタチャット
        return

    if message.content == "s.test":
        await message.channel.send(f"{str(client.user)}\n{discord.__version__}")
        return

    if message.content == "s.join":
        await message.delete(delay=1)
        if message.author.voice is None:
            await message.channel.send("VCチャンネルに接続してから、もう一度お試しください。")
            return
        try:
            await message.author.voice.channel.connect(reconnect=True)
        except discord.errors.ClientException:
            await message.channel.send("既に接続しています。\nチャンネルを移動させたい場合、一度切断してからもう一度お試しください。")
            return
        else:
            await message.channel.send("接続しました。")
            return

    if message.content == "s.leave":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。")
            return
        await message.guild.voice_client.disconnect()
        await message.channel.send("切断しました。")
        return

    if message.content == "s.p time" or message.content == "s.time":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        ran_int = random.randint(1, 3)
        ran_audio = {1: "time.mp3", 2: "time_2.mp3", 3: "time_3.mp3"}
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(ran_audio[ran_int]), volume=0.2)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p kbbtime" or message.content == "s.kbbtime":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio("kbbtime.mp3"), volume=0.2)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p kansei" or message.content == "s.kansei":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        ran_int = random.randint(1, 2)
        ran_audio = {1: "kansei.mp3", 2: "kansei_2.mp3"}
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(ran_audio[ran_int]), volume=0.2)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p count" or message.content == "s.count":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        ran_int = random.randint(1, 2)
        ran_audio = {1: "countdown.mp3", 2: "countdown_2.mp3"}
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(ran_audio[ran_int]), volume=0.2)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p bunka" or message.content == "s.bunka":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio("bunka.mp3"), volume=0.2)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p esh" or message.content == "s.esh":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        ran_int = random.randint(1, 2)
        ran_audio = {1: "esh.mp3", 2: "esh_2.mp3"}
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(ran_audio[ran_int]), volume=0.4)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p msn" or message.content == "s.msn":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(f"msn_{random.randint(1, 3)}.mp3"), volume=0.4)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p olala" or message.content == "s.olala":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio("olala.mp3"), volume=0.4)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p dismuch" or message.content == "s.dismuch":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        ran_int = random.randint(1, 4)
        ran_audio = {1: "dismuch.mp3", 2: "dismuch_2.mp3",
                     3: "dismuch_3.mp3", 4: "dismuch_4.mp3"}
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(ran_audio[ran_int]), volume=1)
        message.guild.voice_client.play(audio)
        return

    if message.content.startswith("s.c") and "s.c90" not in message.content and "s.cancel" not in message.content and "s.check" not in message.content:
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        VoiceClient = message.guild.voice_client
        names = [(j) for j in message.content.replace('s.c', '').split()]
        if len(names) == 0:
            await message.delete(delay=1)
            audio = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio("countdown.mp3"), volume=0.5)
            embed = Embed(title="3, 2, 1, Beatbox!")
            sent_message = await message.channel.send(embed=embed)
            message.guild.voice_client.play(audio)
            await sleep(7)
            connect = VoiceClient.is_connected()
            if connect is False:
                await message.channel.send("Error: 接続が失われたため、タイマーを停止しました\nlost connection", delete_after=5)
                await sent_message.delete()
                return
            embed = Embed(title="1:00", color=0x00ff00)
            await sent_message.edit(embed=embed)
            counter = 50
            color = 0x00ff00
            for i in range(5):
                await sleep(9.9)
                embed = Embed(title=f"{counter}", color=color)
                await sent_message.edit(embed=embed)
                counter -= 10
                connect = VoiceClient.is_connected()
                if connect is False:
                    await message.channel.send("Error: 接続が失われたため、タイマーを停止しました\nlost connection", delete_after=5)
                    await sent_message.delete()
                    return
                if i == 1:
                    color = 0xffff00
                elif i == 3:
                    color = 0xff0000
            await sleep(9.9)
            embed = Embed(title="TIME!")
            await sent_message.edit(embed=embed, delete_after=10)
            audio = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio("time.mp3"), volume=0.5)
            message.guild.voice_client.play(audio)
            await sleep(3)
            audio = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio("msn.mp3"), volume=0.5)
            message.guild.voice_client.play(audio)
            return

        count = 1
        if len(names) == 3:
            try:
                count = int(names[2])
            except ValueError:
                pass
            if 2 <= count <= 4:
                embed = Embed(
                    title="再開コマンド", description=f"Round{count}から再開します。\n\n※意図していない場合、`s.leave`と入力してbotを停止した後、再度入力してください。")
                await message.channel.send(embed=embed, delete_after=60)
                del names[2]
        while len(names) != 2:
            await message.channel.send("Error: 入力方法が間違っています。\n\n`cancelと入力するとキャンセルできます`\nもう一度入力してください：", delete_after=60)

            def check(m):
                return m.channel == message.channel and m.author == message.author

            try:
                msg2 = await client.wait_for('message', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await message.channel.send("Error: timeout", delete_after=5)
                return
            if msg2.content.startswith("s.c"):
                return
            await msg2.delete(delay=5)
            if msg2.content == "cancel":
                await message.channel.send("キャンセルしました。", delete_after=5)
                return
            names = [(j)
                     for j in msg2.content.replace('s.c', '').split()]
        embed = Embed(title=f"1️⃣ {names[0]} vs {names[1]} 2️⃣",
                      description="1分・2ラウンドずつ\n1 minute, 2 rounds each\n\n▶️を押してスタート")
        before_start = await message.channel.send(embed=embed)
        await before_start.add_reaction("▶️")
        await before_start.add_reaction("❌")
        stamps = ["▶️", "❌"]

        def check(reaction, user):
            return user == message.author and reaction.emoji in stamps and reaction.message == before_start

        try:
            reaction, _ = await client.wait_for('reaction_add', timeout=600, check=check)
        except asyncio.TimeoutError:
            await message.channel.send("Error: timeout", delete_after=5)
            await before_start.delete()
            return
        if reaction.emoji == "❌":
            await before_start.delete()
            return
        if count % 2 == 0:
            names.reverse()
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio("countdown.mp3"), volume=0.5)
        embed = Embed(title="3, 2, 1, Beatbox!")
        sent_message = await message.channel.send(embed=embed)
        message.guild.voice_client.play(audio)
        await sleep(7)
        await before_start.delete()
        while count <= 4:
            embed = Embed(
                title="1:00", description=f"Round{count} {names[0]}", color=0x00ff00)
            await sent_message.edit(embed=embed)
            timeout = 9.9
            counter = 50
            color = 0x00ff00
            connect = VoiceClient.is_connected()
            if connect is False:
                await message.channel.send("Error: 接続が失われたため、タイマーを停止しました\nlost connection", delete_after=5)
                return
            while True:
                def check(reaction, user):
                    admin = user.get_role(904368977092964352)  # ビト森杯運営
                    return bool(admin) and reaction.emoji == '⏭️' and reaction.message == sent_message
                try:
                    await client.wait_for('reaction_add', timeout=timeout, check=check)
                except asyncio.TimeoutError:
                    connect = VoiceClient.is_connected()
                    if connect is False:
                        await message.channel.send("Error: 接続が失われたため、タイマーを停止しました\nlost connection", delete_after=5)
                        await sent_message.delete()
                        return
                    if counter == -10:
                        await message.channel.send("Error: timeout\nタイマーを停止しました", delete_after=5)
                        await sent_message.delete()
                        return
                    embed = Embed(
                        title=f"{counter}", description=f"Round{count} {names[0]}", color=color)
                    await sent_message.edit(embed=embed)
                    counter -= 10
                    if counter == 30:
                        color = 0xffff00
                    elif counter == 10:
                        color = 0xff0000
                    elif counter == 0:
                        color = 0x000000
                        await sent_message.add_reaction("⏭️")
                    elif counter == -10:
                        timeout = 60
                        if count == 4:
                            await sent_message.clear_reactions()
                            break
                else:
                    await sent_message.clear_reactions()
                    break
            names.reverse()
            count += 1
        embed = Embed(
            title="TIME!", description="make some noise for the battle!!")
        await sent_message.edit(embed=embed)
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio("time.mp3"), volume=0.2)
        message.guild.voice_client.play(audio)
        await sleep(3)
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio("msn.mp3"), volume=0.5)
        message.guild.voice_client.play(audio)
        await message.delete(delay=1)
        await sleep(3)
        embed = Embed(
            title="オーディエンス投票受付中", description="YouTube投票機能を利用して集計します")
        embed.add_field(name="※投票できないときは",
                        value="アプリの再起動をお試しください", inline=False)
        await sent_message.edit(embed=embed, delete_after=20)
        return

    if message.content.startswith("s.bj"):
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        names = [j for j in message.content.split()]
        names.remove("s.bj")
        round_count = 1
        if len(names) != 2:
            await message.channel.send("Error: 入力方法が間違っています。")
            return
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio("countdown.mp3"), volume=0.5)
        await message.channel.send("3, 2, 1, Beatbox!", delete_after=10)
        message.guild.voice_client.play(audio)
        await sleep(7)
        embed = Embed(
            title="90", description=f"Round{round_count} {names[0]}", color=0x00ff00)
        sent_message = await message.channel.send(embed=embed)
        while round_count < 5:
            timeout = 10
            counter = 80
            color = 0x00ff00
            while True:
                def check(reaction, user):
                    return user.bot is False and reaction.emoji == '⏭️'
                try:
                    await client.wait_for('reaction_add', timeout=timeout, check=check)
                except asyncio.TimeoutError:
                    if counter == -10:
                        await message.channel.send("Error: timeout\nタイマーを停止しました")
                        return
                    embed = Embed(
                        title=f"{counter}", description=f"Round{round_count} {names[0]}", color=color)
                    await sent_message.edit(embed=embed)
                    counter -= 10
                    if counter == 30:
                        color = 0xffff00
                    elif counter == 10:
                        color = 0xff0000
                    elif counter == 0:
                        color = 0x000000
                        await sent_message.add_reaction("⏭️")
                    elif counter == -10:
                        timeout = 30
                        if round_count == 4:
                            embed = Embed(
                                title="0", description=f"Round4 {names[0]}", color=color)
                            await sent_message.edit(embed=embed)
                            break
                else:
                    break
            embed = Embed(title="TIME!")
            await sent_message.edit(embed=embed)
            await sent_message.delete(delay=5)
            names.reverse()
            round_count += 1
            if round_count < 5:
                await message.channel.send("SWITCH!", delete_after=5)
                embed = Embed(
                    title="90", description=f"Round{round_count} {names[0]}", color=0x00ff00)
                sent_message = await message.channel.send(embed=embed)
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio("time.mp3"), volume=0.2)
        message.guild.voice_client.play(audio)
        await sleep(3)
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio("msn.mp3"), volume=0.5)
        message.guild.voice_client.play(audio)
        await message.delete(delay=1)
        return

    if message.content == "s.c90":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        embed = Embed(title="90", color=0x00ff00)
        sent_message = await message.channel.send(embed=embed)
        counter = 80
        color = 0x00ff00
        for i in range(8):
            await sleep(9.9)
            embed = Embed(title=f"{counter}", color=color)
            await sent_message.edit(embed=embed)
            counter -= 10
            if i == 4:
                color = 0xffff00
            elif i == 6:
                color = 0xff0000
        await sleep(9.9)
        embed = Embed(title="TIME!")
        await sent_message.edit(embed=embed)
        await sent_message.delete(delay=5)
        return

    if message.content.startswith("s.battle"):
        stage_channel = client.get_channel(931462636019802123)  # ステージ
        chat = stage_channel
        vc_role = message.guild.get_role(935073171462307881)  # in a vc
        pairing_channel = client.get_channel(930767329137143839)  # 対戦表
        entry_channel = client.get_channel(930446820839157820)  # 参加
        JST = datetime.timezone(datetime.timedelta(hours=9))
        embed_chat_info = Embed(title="チャット欄はこちら chat is here",
                                description=f"対戦表： {pairing_channel.mention}\nエントリー： {entry_channel.mention}\nBATTLEタイマー： {message.channel.mention}", color=0x00bfff)

        async def connection(VoiceClient):
            if VoiceClient.is_connected is False:
                embed = Embed(
                    title="Error", description="接続が失われたため、タイマーを停止しました\nlost connection", color=0xff0000)
                await message.channel.send(embed=embed)
                await chat.send(embed=embed)

        async def timer(time: float, msg: discord.Message, VoiceClient: discord.VoiceClient):
            await connection(VoiceClient)

            def check(reaction, user):
                return user == message.author and str(reaction.emoji) == '❌' and reaction.message == msg
            try:
                _, _ = await client.wait_for('reaction_add', timeout=time, check=check)
            except asyncio.TimeoutError:
                await connection(VoiceClient)
            else:
                try:
                    VoiceClient.stop()
                except Exception:
                    pass
                audio = discord.PCMVolumeTransformer(
                    discord.FFmpegPCMAudio(f"timer_stop.mp3"))
                message.guild.voice_client.play(audio)
                embed = Embed(
                    title="TIMER STOPPED", description="問題が発生したため、タイマーを停止しました\nまもなく、停止時のラウンドからバトルを再開します", color=0xff0000)
                await message.channel.send(embed=embed)
                await chat.send(embed=embed)
                return False

        await chat.send(embed=embed_chat_info)
        count = 0
        names = message.content.replace(
            " vs", "").replace('s.battle', '').split()
        while True:
            embed = Embed(title="処理中...")
            before_start = await message.channel.send(embed=embed)
            if len(names) == 2:
                count = 1
                embed = Embed(title="先攻・後攻の抽選を行います", description="抽選中...")
                await before_start.edit(embed=embed)
                random.shuffle(names)
                break
            if len(names) == 3:
                try:
                    count = int(names[2])
                except ValueError:
                    pass
                if 1 <= count <= 4:
                    embed = Embed(
                        title="再開コマンド", description=f"Round{count}から再開します。")
                    await message.channel.send(embed=embed)
                    await chat.send(embed=embed)
                    break
            embed = Embed(title="Error: 入力方法が間違っています",
                          description=f"入力内容：{names}\n\n`cancelと入力するとキャンセルできます`\n↓もう一度入力してください↓",  color=0xff0000)
            await message.channel.send(embed=embed)

            def check(m):
                return m.channel == message.channel and m.author == message.author
            try:
                msg = await client.wait_for('message', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await message.channel.send("Error: timeout")
                return
            if msg.content == "cancel":
                await message.channel.send("キャンセルしました。")
                return
            if msg.content.startswith("s.battle"):
                return
            names = msg.content.replace(" vs", "").split()
        embed = Embed(title=f"1️⃣ {names[0]} vs {names[1]} 2️⃣",
                      description="1分・2ラウンドずつ\n1 minute, 2 rounds each")
        embed.timestamp = datetime.datetime.now(JST)
        await before_start.edit(embed=embed)
        embed.description += f"\n\nBATTLEタイマーはこちら {message.channel.mention}"
        await chat.send(embed=embed)
        await before_start.add_reaction("▶️")
        await before_start.add_reaction("❌")

        def check(reaction, user):
            stamps = ["▶️", "❌"]
            return user == message.author and reaction.emoji in stamps and reaction.message == before_start
        reaction, _ = await client.wait_for('reaction_add', check=check)
        await before_start.clear_reactions()
        if reaction.emoji == "❌":
            await before_start.delete()
            return
        VoiceClient = await stage_channel.connect(reconnect=True)
        await message.guild.me.edit(suppress=False)
        embed = Embed(title="Are you ready??", color=0x00ff00)
        sent_message = await message.channel.send(embed=embed)
        await sent_message.add_reaction("❌")
        embed.description = f"BATTLEタイマーはこちら {message.channel.mention}"
        await chat.send(embed=embed)
        random_start = random.randint(1, 3)
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(f"BattleStart_{random_start}.mp3"), volume=0.4)
        message.guild.voice_client.play(audio)
        if random_start == 1:
            check_timer = await timer(9, sent_message, VoiceClient)
            if check_timer is False:
                return
        else:
            check_timer = await timer(11, sent_message, VoiceClient)
            if check_timer is False:
                return
        embed = Embed(title="🔥🔥 3, 2, 1, Beatbox! 🔥🔥", color=0xff0000)
        await sent_message.edit(embed=embed)
        embed.description = f"BATTLEタイマーはこちら {message.channel.mention}"
        await chat.send(embed=embed)
        check_timer = await timer(3, sent_message, VoiceClient)
        if check_timer is False:
            return
        stamps = {1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣"}

        while count <= 4:
            embed = Embed(
                title="1:00", description=f"Round {stamps[count]}  **{names[1 - count % 2]}**\n\n{names[0]} vs {names[1]}", color=0x00ff00)
            await sent_message.edit(embed=embed)
            counter = 50
            color = 0x00ff00
            for i in range(5):
                check_timer = await timer(9.9, sent_message, VoiceClient)
                if check_timer is False:
                    return
                embed = Embed(
                    title=f"{counter}", description=f"Round {stamps[count]}  **{names[1 - count % 2]}**\n\n{names[0]} vs {names[1]}", color=color)
                await sent_message.edit(embed=embed)
                counter -= 10
                if i == 1:
                    color = 0xffff00
                    embed = Embed(
                        title="音声バグが発生する場合があります", description=f"Beatboxerの音声が聞こえない場合、チャットにてお知らせください\n`タイマーを停止し、バトルを中断することがあります`\n\nBATTLEタイマーはこちら {message.channel.mention}", color=0xffff00)
                    await chat.send(embed=embed)
                elif i == 3:
                    color = 0xff0000
            check_timer = await timer(4.9, sent_message, VoiceClient)
            if check_timer is False:
                return
            embed = Embed(
                title="5", description=f"Round {stamps[count]}  **{names[1 - count % 2]}**\n\n{names[0]} vs {names[1]}", color=color)
            await sent_message.edit(embed=embed)
            check_timer = await timer(4.9, sent_message, VoiceClient)
            if check_timer is False:
                return
            if count <= 3:
                audio = discord.PCMVolumeTransformer(
                    discord.FFmpegPCMAudio(f"round{count + 1}switch_{random.randint(1, 3)}.mp3"), volume=2)
                message.guild.voice_client.play(audio)
                embed = Embed(
                    title="TIME!", description=f"Round {stamps[count + 1]}  **{names[count % 2]}**\nSWITCH!\n\n{names[0]} vs {names[1]}")
                await sent_message.edit(embed=embed)
                check_timer = await timer(3, sent_message, VoiceClient)
                if check_timer is False:
                    return
            count += 1
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(f"time_{random.randint(1, 2)}.mp3"), volume=0.3)
        pairing_channel = client.get_channel(930767329137143839)  # 対戦表
        await sent_message.delete()
        tari3210 = message.guild.get_member(412082841829113877)
        if random.randint(1, 20) == 1:
            audio = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio("time_fuga.mp3"), volume=0.4)
            message.guild.voice_client.play(audio)
            embed = Embed(
                title="投票箱", description=f"1️⃣ {names[0]}\n2️⃣ {names[1]}\n\nぜひ気に入ったBeatboxerさんに1票をあげてみてください。\n※集計は行いません。botの動作はこれにて終了です。")
            embed.set_footer(
                text=f"bot開発者: {str(tari3210)}", icon_url=tari3210.display_avatar.url)
            embed.timestamp = datetime.datetime.now(JST)
            await sleep(7)
            poll = await message.channel.send(f"{vc_role.mention}\nなあああああああああああああああああああああああああああああああああああああああああああああああああああああああああ！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！", embed=embed)
            await poll.add_reaction("1⃣")
            await poll.add_reaction("2⃣")
            await poll.add_reaction("🦁")
            await chat.send(embed=embed_chat_info)
            return
        message.guild.voice_client.play(audio)
        embed = Embed(
            title="投票箱", description=f"1️⃣ {names[0]}\n2️⃣ {names[1]}\n\nぜひ気に入ったBeatboxerさんに1票をあげてみてください。\n※集計は行いません。botの動作はこれにて終了です。")
        embed.set_footer(
            text=f"bot開発者: {str(tari3210)}", icon_url=tari3210.display_avatar.url)
        embed.timestamp = datetime.datetime.now(JST)
        poll = await message.channel.send(f"{vc_role.mention}\nmake some noise for the battle!\ncome on!!", embed=embed)
        await poll.add_reaction("1⃣")
        await poll.add_reaction("2⃣")
        await poll.add_reaction("🔥")
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(f"msn_{random.randint(1, 3)}.mp3"), volume=0.4)
        await sleep(4.0)
        message.guild.voice_client.play(audio)
        await chat.send(embed=embed_chat_info)
        return

    if message.content == "s.start":
        await message.channel.send("処理中...")
        stage_channel = client.get_channel(931462636019802123)  # ステージ
        chat = stage_channel
        vc_role = message.guild.get_role(935073171462307881)  # in a vc
        bbx_mic = client.get_channel(931781522808262756)  # bbxマイク設定
        pairing_channel = client.get_channel(930767329137143839)  # 対戦表
        bs_role = message.guild.get_role(930368130906218526)  # BATTLE STADIUM
        entry_channel = client.get_channel(930446820839157820)  # 参加
        scheduled_events = message.guild.scheduled_events
        embed_chat_info = Embed(title="チャット欄はこちら chat is here",
                                description=f"対戦表： {pairing_channel.mention}\nエントリー： {entry_channel.mention}\nBATTLEタイマー： {message.channel.mention}", color=0x00bfff)
        await chat.send(vc_role.mention, embed=embed_chat_info)
        try:
            for scheduled_event in scheduled_events:
                if scheduled_event.name == "BATTLE STADIUM":
                    await scheduled_event.start()
                    break
            await stage_channel.create_instance(topic="BATTLE STADIUM", send_notification=True)
        except Exception:
            pass
        try:
            await stage_channel.connect(reconnect=True)
        except discord.errors.ClientException:
            pass
        await message.guild.me.edit(suppress=False)
        await pairing_channel.purge()
        for member in bs_role.members:
            await member.remove_roles(bs_role)
        button = Button(
            label="Entry", style=discord.ButtonStyle.primary, emoji="✅")

        async def button_callback(interaction):
            await interaction.response.defer(ephemeral=True, thinking=False)
            await interaction.user.add_roles(bs_role)
            embed = Embed(title="受付完了 entry completed",
                          description=f"**注意事項**・ノイズキャンセル設定に問題がある方が非常に増えています。\n必ず {bbx_mic.mention} を確認して、マイク設定を行ってからの参加をお願いします。\n\n・Discordの音声バグが多発しています。発生した場合、バトルを中断し、途中のラウンドからバトルを再開することがあります。\n※音声バグ発生時の対応は状況によって異なります。ご了承ください。", color=0xffff00)
            await message.channel.send(f"エントリー完了：{interaction.user.display_name}", delete_after=3)
            await interaction.followup.send(embed=embed, ephemeral=True)

        button.callback = button_callback
        view = View()
        view.add_item(button)
        embed = Embed(
            title="Entry", description="下のボタンを押してエントリー！\npress button to entry")
        entry_button = await entry_channel.send(vc_role.mention, embed=embed, view=view)
        entry_button2 = await chat.send("このボタンからもエントリーできます", embed=embed, view=view)
        embed = Embed(
            title="受付開始", description=f"ただいまより参加受付を開始します。\n{entry_channel.mention}にてエントリーを行ってください。\nentry now accepting at {entry_channel.mention}", color=0x00bfff)
        await message.channel.send(embed=embed)
        await entry_channel.send(f"エントリー後に、 {bbx_mic.mention} を確認して、マイク設定を行ってください。", delete_after=60)
        await sleep(30)
        embed = Embed(title="あと30秒で締め切ります", color=0xffff00)
        await message.channel.send(embed=embed)
        await chat.send(embed=embed_chat_info)
        await entry_channel.send(f"{vc_role.mention}\nボタンを押してエントリー！\npress button to entry", delete_after=30)
        await sleep(20)
        embed = Embed(title="バトル中に、音声バグが発生する場合があります", description=f"Beatboxerの音声が聞こえない場合、チャットにてお知らせください\n`タイマーを停止し、バトルを中断することがあります`\n\nBATTLEタイマーはこちら {message.channel.mention}", color=0xffff00)
        await chat.send(embed=embed)
        embed = Embed(title="締め切り10秒前", color=0xff0000)
        await message.channel.send(embed=embed)
        await sleep(10)
        await entry_button.delete()
        await entry_button2.delete()
        await message.channel.send("参加受付を締め切りました。\nentry closed\n\n処理中... しばらくお待ちください")
        playerlist = [member.display_name.replace(
            "`", "").replace(" ", "-") for member in bs_role.members]
        if len(playerlist) < 2:
            embed = Embed(
                title="Error", description="参加者が不足しています。", color=0xff0000)
            await message.channel.send(embed=embed)
            return
        random.shuffle(playerlist)
        counter = 1
        counter2 = 0
        embed_pairing = Embed(
            title="抽選結果", description="先攻・後攻は、バトル直前に抽選を行います", color=0xff9900)
        while counter2 + 2 <= len(playerlist):
            embed.add_field(
                name=f"Match{counter}", value=f"{playerlist[counter2]} vs {playerlist[counter2 + 1]}", inline=False)
            counter += 1
            counter2 += 2
        if len(playerlist) % 2 == 1:
            double_pl = message.guild.get_member_named(playerlist[0])
            if double_pl is None:
                double_pl = playerlist[0]
            else:
                double_pl = double_pl.mention
            embed = Embed(title="参加人数が奇数でした", description=f"{playerlist[0]}さんの対戦が2回行われます\n\n※あと1人参加者が追加された場合、{playerlist[0]}さんと交代になります。", color=0xff9900)
            await message.channel.send(embed=embed)
            await pairing_channel.send(f"参加人数が奇数でした。\n{double_pl}さんの対戦が2回行われます。\n\n※あと1人参加者が追加された場合、{double_pl}さんと交代になります。")
            embed = Embed(
                title="参加人数が奇数でした", description=f"あと1人参加できます。ご希望の方はこのチャットにご記入ください。\n\n※参加者が追加された場合、{playerlist[0]}さんと交代になります。", color=0xff9900)
            await chat.send(embed=embed)
            embed_pairing.add_field(
                name=f"Match{counter}", value=f"{playerlist[-1]} vs {playerlist[0]}", inline=False)
        tari3210 = message.guild.get_member(412082841829113877)
        embed_pairing.set_footer(
            text=f"bot開発者: {str(tari3210)}", icon_url=tari3210.display_avatar.url)
        JST = datetime.timezone(datetime.timedelta(hours=9))
        embed_pairing.timestamp = datetime.datetime.now(JST)
        await message.channel.send(embed=embed_pairing)
        embed_pairing.title = "対戦カード"
        await pairing_channel.send(vc_role.mention, embed=embed_pairing)
        await pairing_channel.send(f"{bs_role.mention}\n\n{bbx_mic.mention} を確認して、マイク設定を行ってからの参加をお願いします。\n\n※スマホユーザーの方へ\nspeakerになった後、ミュート以外画面操作を一切行わないでください\nDiscordバグにより音声が一切入らなくなります")
        await chat.send(embeds=[embed_pairing, embed_chat_info])
        return

    if message.content == "s.stage":
        await message.delete(delay=1)
        stage_channel = client.get_channel(931462636019802123)  # ステージ
        try:
            await stage_channel.create_instance(topic="BATTLE STADIUM")
        except discord.errors.HTTPException:
            pass
        try:
            await stage_channel.connect(reconnect=True)
        except discord.errors.ClientException:
            pass
        me = message.guild.me
        await me.edit(suppress=False)
        return

    if message.content == "s.end":
        await message.delete(delay=1)
        pairing_channel = client.get_channel(930767329137143839)  # 対戦表
        bs_role = message.guild.get_role(930368130906218526)  # BATTLE STADIUM
        stage = client.get_channel(931462636019802123)  # ステージ
        scheduled_events = message.guild.scheduled_events
        for scheduled_event in scheduled_events:
            if scheduled_event.status == discord.ScheduledEventStatus.active and scheduled_event.name == "BATTLE STADIUM":
                await scheduled_event.complete()
        try:
            instance = await stage.fetch_instance()
        except Exception:
            pass
        else:
            await instance.delete()
        await pairing_channel.purge()
        for member in bs_role.members:
            await member.remove_roles(bs_role)
        return

    if message.content.startswith("s.bs"):
        await message.delete(delay=1)
        JST = datetime.timezone(datetime.timedelta(hours=9))
        dt_now = datetime.datetime.now(JST)
        sat = datetime.timedelta(days=6 - int(dt_now.strftime("%w")))
        start_time = datetime.datetime(
            dt_now.year, dt_now.month, dt_now.day, 21, 30, 0, 0, JST) + sat
        end_time = datetime.datetime(
            dt_now.year, dt_now.month, dt_now.day, 22, 30, 0, 0, JST) + sat
        stage = client.get_channel(931462636019802123)  # BATTLE STADIUM
        event = await message.guild.create_scheduled_event(name="BATTLE STADIUM", description="今週もやります！\nこのイベントの趣旨は「とにかくBeatboxバトルをすること」です。いつでも何回でも参加可能です。\nぜひご参加ください！\n観戦も可能です。観戦中、マイクがオンになることはありません。\n\n※エントリー受付・当日の進行はすべてbotが行います。\n※エントリー受付開始時間は、バトル開始1分前です。", start_time=start_time, end_time=end_time, channel=stage, privacy_level=discord.PrivacyLevel.guild_only)
        embed = Embed(title="BATTLE STADIUM 開催のお知らせ", description="```今週もやります！\nこのイベントの趣旨は「とにかくBeatboxバトルをすること」です。いつでも何回でも参加可能です。\nぜひご参加ください！\n観戦も可能です。観戦中、マイクがオンになることはありません。\n\n※エントリー受付・当日の進行はすべてbotが行います。\n※エントリー受付開始時間は、バトル開始1分前です。```", color=0x00bfff)
        embed.add_field(name="日時 date", value=start_time.strftime(
            '%m/%d 21:30 - 22:30 Japan time'), inline=False)
        embed.add_field(name="場所 place",
                        value=f'stage channel {stage.mention}', inline=False)
        await message.channel.send(embed=embed)
        await message.channel.send(event.url)
        return

client.run("ODk2NjUyNzgzMzQ2OTE3Mzk2.YWKO-g.PbWqRCFnvgd0YGAOMAHNqDKNQAU")
