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
print("successfully started")

@client.event
async def on_voice_state_update(member, before, after):
    if member.guild.id != 864475338340171786:  # ビト森ID
        return
    role = member.guild.get_role(935073171462307881)  # in a vc
    if before.channel is None and after.channel is not None:
        await member.add_roles(role)
        return
    if before.channel is not None and after.channel is None:
        await member.remove_roles(role)
        return

@client.event
async def on_message(message):
    if message.channel.id == 930839018671837184:  # バトスタチャット
        return

    if message.channel.id == 930767329137143839:  # バトスタ対戦表
        if message.author.bot:
            return
        await message.delete(delay=1)
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
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(ran_audio[ran_int]), volume=0.2)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p kbbtime" or message.content == "s.kbbtime":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("kbbtime.mp3"), volume=0.2)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p kansei" or message.content == "s.kansei":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        ran_int = random.randint(1, 2)
        ran_audio = {1: "kansei.mp3", 2: "kansei_2.mp3"}
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(ran_audio[ran_int]), volume=0.2)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p count" or message.content == "s.count":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        ran_int = random.randint(1, 2)
        ran_audio = {1: "countdown.mp3", 2: "countdown_2.mp3"}
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(ran_audio[ran_int]), volume=0.2)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p bunka" or message.content == "s.bunka":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("bunka.mp3"), volume=0.2)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p esh" or message.content == "s.esh":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        ran_int = random.randint(1, 2)
        ran_audio = {1: "esh.mp3", 2: "esh_2.mp3"}
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(ran_audio[ran_int]), volume=0.4)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p msn" or message.content == "s.msn":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("msn.mp3"), volume=0.4)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p olala" or message.content == "s.olala":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("olala.mp3"), volume=0.4)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p dismuch" or message.content == "s.dismuch":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        ran_int = random.randint(1, 4)
        ran_audio = {1: "dismuch.mp3", 2: "dismuch_2.mp3", 3: "dismuch_3.mp3", 4: "dismuch_4.mp3"}
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(ran_audio[ran_int]), volume=1)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.help":
        await message.delete(delay=1)
        await message.channel.send("コマンド一覧\n`s.join` コマンドを打った人が居るVCチャンネルに接続\n`s.leave` VCチャンネルから切断\n`s.p count or s.count` 321beatboxの音声\n`s.p time or s.time` timeの音声\n`s.p kbbtime or s.kbbtime` 歓声無しtimeの音声 音源：KBB\n`s.p kansei or s.kansei` 歓声\n`s.p bunka or s.bunka` 文化の人の音声\n`s.p esh or s.esh` eshの音声\n`s.p msn or s.msn` make some noiseの音声\n`s.p olala or s.olala` olalaの音声")
        await message.channel.send("make some noise bot開発者：tari3210 #9924")
        return

    if message.content.startswith("s.c") and "s.c90" not in message.content and "s.cancel" not in message.content and "s.check" not in message.content:
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        names = [(j) for j in message.content.split()]
        names.remove("s.c")
        if len(names) == 0:
            await message.delete(delay=1)
            audio = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio("countdown.mp3"), volume=0.5)
            await message.channel.send("3, 2, 1, Beatbox!", delete_after=10)
            message.guild.voice_client.play(audio)
            await sleep(7)
            embed = Embed(title="1:00", color=0x00ff00)
            sent_message = await message.channel.send(embed=embed)
            counter = 50
            color = 0x00ff00
            for i in range(5):
                await sleep(9.9)
                embed = Embed(title=f"{counter}", color=color)
                await sent_message.edit(embed=embed)
                counter -= 10
                if i == 1:
                    color = 0xffff00
                elif i == 3:
                    color = 0xff0000
            await sleep(9.9)
            embed = Embed(title="TIME!")
            await sent_message.edit(embed=embed)
            await sent_message.delete(delay=5)
            audio = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio("time.mp3"), volume=0.5)
            message.guild.voice_client.play(audio)
            await sleep(3)
            audio = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio("msn.mp3"), volume=0.5)
            message.guild.voice_client.play(audio)

        elif len(names) == 2 or len(names) == 3:
            round_count = 1
            if len(names) == 3:
                round_count = int(names[2])
                embed = Embed(title="再開コマンド", description=f"Round{names[2]}から再開します")
                await message.channel.send(embed=embed)
                del names[2]
                if round_count % 2 == 0:
                    names.reverse()
            audio = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio("countdown.mp3"), volume=0.5)
            await message.channel.send("3, 2, 1, Beatbox!", delete_after=10)
            message.guild.voice_client.play(audio)
            await sleep(7)
            embed = Embed(title="1:00", description=f"Round{round_count} {names[0]}", color=0x00ff00)
            sent_message = await message.channel.send(embed=embed)
            while round_count < 5:
                timeout = 9.9
                counter = 50
                color = 0x00ff00
                for i in range(7):
                    def check(reaction, user):
                        id_manage = 904368977092964352  # ビト森杯運営
                        roles = user.roles
                        id_list = [role.id for role in roles]
                        return id_manage in id_list and str(reaction.emoji) == '⏭️'
                    try:
                        await client.wait_for('reaction_add', timeout=timeout, check=check)
                    except asyncio.TimeoutError:
                        if counter == -10:
                            await message.channel.send("Error: timeout\nタイマーを停止しました")
                            return
                        embed = Embed(title=f"{counter}", description=f"Round{round_count} {names[0]}", color=color)
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
                                embed = Embed(title="0", description=f"Round4 {names[0]}", color=color)
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
                    embed = Embed(title="1:00", description=f"Round{round_count} {names[0]}", color=0x00ff00)
                    sent_message = await message.channel.send(embed=embed)
            audio = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio("time.mp3"), volume=0.2)
            message.guild.voice_client.play(audio)
            await sleep(3)
            audio = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio("msn.mp3"), volume=0.5)
            message.guild.voice_client.play(audio)
            embed = Embed(title="投票箱", description=f"1⃣ {names[0]}\n2⃣ {names[1]}")
            channel_judge = message.guild.get_channel(912714891444518943)  # 審査員会議室
            poll = await channel_judge.send(embed=embed)
            await poll.add_reaction("1⃣")
            await poll.add_reaction("2⃣")
            await message.delete(delay=1)
        else:
            await message.channel.send("Error: 入力方法が間違っています。")
        return

    if message.content.startswith("s.bj"):
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        names = [(j) for j in message.content.split()]
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
        embed = Embed(title="90", description=f"Round{round_count} {names[0]}", color=0x00ff00)
        sent_message = await message.channel.send(embed=embed)
        while round_count < 5:
            timeout = 10
            counter = 80
            color = 0x00ff00
            while True:
                def check(reaction, user):
                    return user.bot is False and str(reaction.emoji) == '⏭️'
                try:
                    await client.wait_for('reaction_add', timeout=timeout, check=check)
                except asyncio.TimeoutError:
                    if counter == -10:
                        await message.channel.send("Error: timeout\nタイマーを停止しました")
                        return
                    embed = Embed(title=f"{counter}", description=f"Round{round_count} {names[0]}", color=color)
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
                            embed = Embed(title="0", description=f"Round4 {names[0]}", color=color)
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
                embed = Embed(title="90", description=f"Round{round_count} {names[0]}", color=0x00ff00)
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
        names = [(j) for j in message.content.replace('s.battle', '').split()]
        count = 1
        if len(names) == 3:
            try:
                count = int(names[2])
            except ValueError:
                pass
            if 2 <= count <= 4 and len(names) == 3:
                embed = Embed(title="再開コマンド", description=f"Round{count}から再開します。\n\n※意図していない場合、`s.leave`と入力してbotを停止した後、再度入力してください。")
                await message.channel.send(embed=embed)
                del names[2]
        while len(names) != 2:
            await message.channel.send("Error: 入力方法が間違っています。\n\n`cancelと入力するとキャンセルできます`\nもう一度入力してください：")

            def check(m):
                return m.channel == message.channel and m.author == message.author

            try:
                msg2 = await client.wait_for('message', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await message.channel.send("Error: timeout")
                return
            if msg2.content == "cancel":
                await message.channel.send("キャンセルしました。")
                return
            if msg2.content.startswith("s.battle"):
                return
            names = [(j) for j in msg2.content.replace('s.battle', '').split()]
        embed = Embed(title=f"{names[0]}さん `1st` vs {names[1]}さん `2nd`", description="1分・2ラウンドずつ\n1 minute, 2 rounds each\n\n▶️を押してスタート")
        before_start = await message.channel.send(embed=embed)
        await before_start.add_reaction("▶️")
        await before_start.add_reaction("❌")
        stamps = ["▶️", "❌"]

        def check(reaction, user):
            return user == message.author and str(reaction.emoji) in stamps and reaction.message == before_start

        try:
            reaction, _ = await client.wait_for('reaction_add', timeout=600, check=check)
        except asyncio.TimeoutError:
            await before_start.delete()
            await message.channel.send("Error: timeout")
            return
        await before_start.clear_reactions()
        if reaction.emoji == "❌":
            await before_start.delete()
            return
        embed = Embed(title="Are you ready??")
        sent_message = await message.channel.send(embed=embed)
        stage_channel = client.get_channel(931462636019802123)  # ステージ
        try:
            await stage_channel.connect(reconnect=True)
        except discord.errors.ClientException:
            pass
        VoiceClient = message.guild.voice_client
        me = message.guild.me
        try:
            await me.edit(suppress=False)
        except AttributeError:
            pass
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("battle_start.mp3"), volume=0.4)
        message.guild.voice_client.play(audio)
        await sleep(11)
        connect = VoiceClient.is_connected()
        if connect is False:
            await message.channel.send("Error: 接続が失われたため、タイマーを停止しました\nlost connection")
            return
        embed = Embed(title="3, 2, 1, Beatbox!")
        await sent_message.edit(embed=embed)
        await sleep(3)
        while count <= 4:
            embed = Embed(title="1:00", description=f"Round{count} {names[1 - count % 2]}\n\n{names[0]} vs {names[1]}", color=0x00ff00)
            await sent_message.edit(embed=embed)
            counter = 50
            color = 0x00ff00
            for i in range(5):
                await sleep(9.9)
                embed = Embed(title=f"{counter}", description=f"Round{count} {names[1 - count % 2]}\n\n{names[0]} vs {names[1]}", color=color)
                await sent_message.edit(embed=embed)
                counter -= 10
                connect = VoiceClient.is_connected()
                if connect is False:
                    await message.channel.send("Error: 接続が失われたため、タイマーを停止しました\nlost connection")
                    return
                if i == 1:
                    color = 0xffff00
                elif i == 3:
                    color = 0xff0000
            await sleep(9.9)
            if count <= 3:
                audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(f"round{count + 1}switch.mp3", volume=1.5))
                connect = VoiceClient.is_connected()
                if connect is False:
                    await message.channel.send("Error: 接続が失われたため、タイマーを停止しました\nlost connection")
                    return
                message.guild.voice_client.play(audio)
                embed = Embed(title="TIME!", description=f"Round{count + 1} {names[count % 2]}\nSWITCH!\n\n{names[0]} vs {names[1]}")
                await sent_message.edit(embed=embed)
                await sleep(3)
            count += 1
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("time.mp3"), volume=0.2)
        if random.randint(1, 10) == 1:
            audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("time_3.mp3"), volume=0.3)
            message.guild.voice_client.play(audio)
            embed = Embed(title="投票箱", description=f"`1st:`{names[0]}\n`2nd:`{names[1]}\n\nぜひ気に入ったBeatboxerさんに1票をあげてみてください。\n※集計は行いません。botの動作はこれにて終了です。")
            role_vc = message.guild.get_role(935073171462307881)  # in a vc
            await sent_message.edit(role_vc.mention, embed=embed)
            await sent_message.add_reaction("1⃣")
            await sent_message.add_reaction("2⃣")
            await sleep(8)
            await sent_message.add_reaction("🦁")
            await sent_message.edit(f"{role_vc.mention}\nなああああああああああああああああああああああああああああああああああああああああああああああああああ", embed=embed)
            return
        message.guild.voice_client.play(audio)
        embed = Embed(title="投票箱", description=f"`1st:`{names[0]}\n`2nd:`{names[1]}\n\nぜひ気に入ったBeatboxerさんに1票をあげてみてください。\n※集計は行いません。botの動作はこれにて終了です。")
        role_vc = message.guild.get_role(935073171462307881)  # in a vc
        await sent_message.edit(role_vc.mention, embed=embed)
        await sent_message.add_reaction("1⃣")
        await sent_message.add_reaction("2⃣")
        await sent_message.add_reaction("🔥")
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("msn.mp3"), volume=0.5)
        await sleep(3)
        message.guild.voice_client.play(audio)
        await sent_message.edit(f"{role_vc.mention}\nmake some noise for the battle!\ncome on!!", embed=embed)
        return

    if message.content == "s.start":
        await message.channel.send("処理中...")
        stage_channel = client.get_channel(931462636019802123)  # ステージ
        role_vc = message.guild.get_role(935073171462307881)  # in a vc
        bbx_mic = client.get_channel(931781522808262756)  # bbxマイク設定
        chat = client.get_channel(930839018671837184)  # バトスタチャット
        scheduled_events = message.guild.scheduled_events
        await chat.send(f"{role_vc.mention}\nチャット欄はこちら")
        if len(scheduled_events) == 1 and scheduled_events[0].name == "battle stadium":
            try:
                await scheduled_events[0].start()
            except discord.errors.HTTPException:
                pass
        else:
            try:
                await stage_channel.create_instance(topic="battle stadium")
            except discord.errors.HTTPException:
                pass
        try:
            await stage_channel.connect(reconnect=True)
        except discord.errors.ClientException:
            pass
        me = message.guild.me
        await me.edit(suppress=False)
        channel0 = client.get_channel(930767329137143839)  # 対戦表
        await channel0.purge()
        role = message.guild.get_role(930368130906218526)  # battle stadium
        role_member = role.members
        for member in role_member:
            await member.remove_roles(role)
        channel1 = client.get_channel(930446820839157820)  # 参加
        button = Button(label="Entry", style=discord.ButtonStyle.primary, emoji="✅")

        async def button_callback(interaction):
            role = interaction.guild.get_role(930368130906218526)  # battle stadium
            await interaction.user.add_roles(role)
            description = interaction.user.display_name
            if interaction.user.is_on_mobile():
                description += "\n\n※バトルを始める際、speakerになった後、ミュート以外画面操作を一切行わないでください\nDiscordバグにより音声が一切入らなくなります"
            embed = Embed(title="受付完了 entry completed", description=description)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await message.channel.send(f"エントリー完了：{interaction.user.display_name}", delete_after=3)
            await sleep(3)
            embed = Embed(title=":warning:", description="バトルを始める際、speakerになった後、ミュート以外画面操作を一切行わないでください\nDiscordバグにより音声が一切入らなくなります", color=0xffff00)
            await chat.send(interaction.user.mention, embed=embed, delete_after=20)
        button.callback = button_callback
        view = View(timeout=None)
        view.add_item(button)
        embed = Embed(title="Entry", description="下のボタンを押してエントリー！\npress button to entry")
        entry_button = await channel1.send(role_vc.mention, embed=embed, view=view)
        await message.channel.send("処理完了")
        embed = Embed(title="受付開始", description=f"ただいまより参加受付を開始します。\n{channel1.mention}にてエントリーを行ってください。\nentry now accepting at {channel1.mention}", color=0x00bfff)
        await message.channel.send(embed=embed)
        await channel1.send(f"エントリー後に、 {bbx_mic.mention} を確認して、マイク設定を行ってください。", delete_after=60)
        await sleep(30)
        embed = Embed(title="あと30秒で締め切ります", color=0xffff00)
        await message.channel.send(embed=embed)
        await channel1.send(f"{role_vc.mention}\nボタンを押してエントリー！\npress button to entry", delete_after=30)
        await sleep(20)
        embed = Embed(title="締め切り10秒前", color=0xff0000)
        await message.channel.send(embed=embed)
        await sleep(10)
        await entry_button.delete()
        await message.channel.send("参加受付を締め切りました。\nentry closed\n\n処理中... しばらくお待ちください")
        role_member = role.members
        playerlist = [member.display_name for member in role_member]
        random.shuffle(playerlist)
        if len(playerlist) < 2:
            embed = Embed(title="Error", description="参加者が不足しています。", color=0xff0000)
            await message.channel.send(embed=embed)
            return
        counter = 1
        counter2 = 0
        dt_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        date = str(dt_now.strftime('%m月%d日 %H:%M')) + " JST"
        if date[3] == "0":
            date = date[:3] + date[4:]
        if date[0] == "0":
            date = date[1:]
        embed = Embed(title="抽選結果", description=f"{date}", color=0xff9900)
        while counter2 + 2 <= len(playerlist):
            embed.add_field(name=f"Match{counter}", value=f"{playerlist[counter2]} `1st` vs {playerlist[counter2 + 1]} `2nd`", inline=False)
            counter += 1
            counter2 += 2
        if len(playerlist) % 2 == 1:
            double_pl = message.guild.get_member_named(playerlist[0])
            if double_pl is None:
                double_pl = playerlist[0]
            else:
                double_pl = double_pl.mention
            await message.channel.send(f"----------------------------------------\n\n参加人数が奇数でした。\n{playerlist[0]}さんの対戦が2回行われます。")
            await channel0.send(f"参加人数が奇数でした。\n{double_pl}さんの対戦が2回行われます。")
            embed.add_field(name=f"Match{counter}", value=f"{playerlist[-1]} `1st` vs {playerlist[0]} `2nd`", inline=False)
        await message.channel.send(embed=embed)
        embed.title = "対戦カード"
        await channel0.send(role_vc.mention, embed=embed)
        await channel0.send(f"{role.mention}\n\n{bbx_mic.mention} を確認して、マイク設定を行ってからの参加をお願いします。\n\n※スマホユーザーの方へ\nspeakerになった後、ミュート以外画面操作を一切行わないでください\nDiscordバグにより音声が一切入らなくなります")
        return

    if message.content == "s.stage":
        await message.delete(delay=1)
        stage_channel = client.get_channel(931462636019802123)  # ステージ
        try:
            await stage_channel.create_instance(topic="battle stadium")
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
        scheduled_events = message.guild.scheduled_events
        if len(scheduled_events) == 1 and scheduled_events[0].status == "active":
            await scheduled_events[0].complete()
        channel0 = client.get_channel(930767329137143839)  # 対戦表
        await channel0.purge()
        role = message.guild.get_role(930368130906218526)  # battle stadium
        role_member = role.members
        for member in role_member:
            await member.remove_roles(role)
        stage = client.get_channel(931462636019802123)  # ステージ
        try:
            instance = await stage.fetch_instance()
        except discord.errors.NotFound:
            pass
        else:
            await instance.delete()
        return

    if "s." not in message.content:
        if message.author.bot:
            return
        elif message.channel.id == 930447365536612353:  # バトスタbot
            await message.delete(delay=1)
        return

client.run("ODk2NjUyNzgzMzQ2OTE3Mzk2.YWKO-g.PbWqRCFnvgd0YGAOMAHNqDKNQAU")
