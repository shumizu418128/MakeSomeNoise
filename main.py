import asyncio
import os
import random
import re
from asyncio import sleep
from datetime import datetime, time, timedelta, timezone

import discord
from discord import (ChannelType, Client, Embed, EventStatus, FFmpegPCMAudio,
                     File, Intents, Member, Message, PCMVolumeTransformer,
                     PrivacyLevel, ScheduledEvent, VoiceState)
from discord.errors import ClientException
from discord.ext import tasks

from battle_stadium import battle, start
from keep_alive import keep_alive

TOKEN = os.environ['DISCORD_BOT_TOKEN']
intents = Intents.all()  # デフォルトのIntentsオブジェクトを生成
intents.typing = False  # typingを受け取らないように
client = Client(intents=intents)
print(f"Make Some Noise! (server): {discord.__version__}")

JST = timezone(timedelta(hours=9))
PM9 = time(21, 0, tzinfo=JST)


async def gbb_countdown():
    dt_gbb_start = datetime(2023, 10, 18, 13, 0)  # 2023/10/18 13:00
    dt_gbb_end = datetime(2023, 10, 22)  # 2023/10/22
    dt_gbb_start = dt_gbb_start.replace(tzinfo=JST)
    dt_gbb_end = dt_gbb_end.replace(tzinfo=JST)
    dt_now = datetime.now(JST)

    td_gbb = abs(dt_gbb_end - dt_now)  # GBB終了から現在の時間
    if dt_gbb_end > dt_now:  # GBB終了前なら
        td_gbb = abs(dt_gbb_start - dt_now)  # GBB開始から現在の時間

    m, s = divmod(td_gbb.seconds, 60)  # 秒を60で割った商と余りをm, sに代入
    h, m = divmod(m, 60)  # mを60で割った商と余りをh, mに代入

    if dt_gbb_start > dt_now:  # GBB開始前なら
        return f"GBB2023まであと{td_gbb.days}日{h}時間{m}分{s}.{td_gbb.microseconds}秒です。"

    elif dt_gbb_end > dt_now:  # GBB開催中なら
        return f"今日はGBB2023 {td_gbb.days + 1}日目です。"

    # GBB終了後なら
    return f"GBB2023は{td_gbb.days}日{h}時間{m}分{s}.{td_gbb.microseconds}秒前に開催されました。"


async def search_next_event(events: list[ScheduledEvent]):
    events_exist = []  # 予定されているイベント
    for event in events:  # 予定されているイベントをリストに追加
        if event.status in [EventStatus.scheduled, EventStatus.active]:
            events_exist.append(event)
    if bool(events_exist) is False:  # 予定されているイベントがない場合さよなら
        return
    closest_event = events_exist[0]
    for event in events_exist:  # 一番近いイベントを探す
        if event.start_time < closest_event.start_time:
            closest_event = event
    return closest_event


@tasks.loop(time=PM9)
async def advertise():
    channel = client.get_channel(864475338340171791)  # 全体チャット
    next_event = await search_next_event(channel.guild.scheduled_events)  # 次のイベント
    if next_event.name == "BATTLE STADIUM":  # バトスタの場合
        # gif
        await channel.send(file=File(f"battle_stadium_{random.randint(1, 3)}.gif"))
    await channel.send(next_event.url)  # 次のイベントのURL送信
    dt_now = datetime.now(JST)  # 現在時刻

    # バトスタ開始まで35分以内の場合
    if next_event.name == "BATTLE STADIUM" and next_event.start_time - dt_now < timedelta(minutes=35):
        await sleep(29 * 60)  # 29分待機
        embed = Embed(title="BATTLE STADIUM 開始ボタン",
                      description="▶️を押すとバトスタを開始します\n※s.startコマンドは不要です")
        bot_channel = client.get_channel(930447365536612353)  # バトスタbot
        battle_stadium_start = await bot_channel.send(embed=embed)
        await battle_stadium_start.add_reaction("▶️")
        await battle_stadium_start.add_reaction("❌")

        def check(reaction, user):
            stamps = ["▶️", "❌"]
            role_check = user.get_role(1096821566114902047)  # バトスタ運営
            return bool(role_check) and reaction.emoji in stamps and reaction.message == battle_stadium_start
        try:
            # 10分待機
            reaction, _ = await client.wait_for('reaction_add', check=check, timeout=600)
        except TimeoutError:  # 10分経過ならさよなら
            return
        await battle_stadium_start.clear_reactions()
        if reaction.emoji == "❌":  # ❌ならさよなら
            await battle_stadium_start.delete()
        await start(client)
    return


@client.event
async def on_ready():  # 起動時に動作する処理
    advertise.start()  # バトスタ宣伝
    return


@client.event
async def on_voice_state_update(member: Member, before: VoiceState, after: VoiceState):
    if member.id == 412082841829113877 or member.bot:  # tari3210
        return
    try:
        vc_role = member.guild.get_role(935073171462307881)  # in a vc
        if bool(before.channel) and after.channel is None:  # チャンネルから退出
            await member.remove_roles(vc_role)
        elif before.channel != after.channel and bool(after.channel):  # チャンネルに参加
            embed = Embed(title="BEATBOXをもっと楽しむために",
                          description="", color=0x0081f0)
            embed.add_field(name=f"Let's show your 💜❤💙💚 with `{member.display_name}`!",
                            value="ビト森のすべての仲間たちと、\nもっとBEATBOXを好きになれる。\nそんなあたたかい雰囲気作りに、\nぜひ、ご協力をお願いします。")
            embed.set_footer(
                text="We love beatbox, We are beatbox family\nあつまれ！ビートボックスの森", icon_url=member.guild.icon.url)
            if after.channel.id == 886099822770290748:  # リアタイ部屋
                await after.channel.send(f"{member.mention} チャットはこちら chat is here", embed=embed, delete_after=60)
            else:
                await after.channel.send(f"{member.mention} チャットはこちら chat is here", delete_after=60)
            await member.add_roles(vc_role)
    except Exception:
        return


@client.event
async def on_member_join(member: Member):
    channel = client.get_channel(864475338340171791)  # 全体チャット
    await sleep(2)
    embed_discord = Embed(
        title="Discordの使い方", description="https://note.com/me1o_crew/n/nf2971acd1f1a")
    embed = Embed(title="GBBの最新情報はこちら", color=0xF0632F)
    embed.add_field(name="GBBINFO-JPN 日本非公式情報サイト",
                    value="https://gbbinfo-jpn.jimdofree.com/")
    embed.add_field(name="swissbeatbox 公式instagram",
                    value="https://www.instagram.com/swissbeatbox/")
    text = await gbb_countdown()  # GBBまでのカウントダウン
    embed.set_footer(text=text)
    await channel.send(f"{member.mention}\nあつまれ！ビートボックスの森 へようこそ！", embeds=[embed_discord, embed])
    next_event = await search_next_event(channel.guild.scheduled_events)
    await sleep(1)
    await channel.send(next_event.url)


@client.event
async def on_message(message: Message):
    # バトスタ対戦表、バトスタチャット
    if message.author.bot or message.content.startswith("l.") or message.channel.id in [930767329137143839, 930839018671837184]:
        return
    # s.から始まらない場合(コマンドではない場合)
    if not message.content.startswith("s."):
        if "草" in message.content:
            emoji = message.guild.get_emoji(990222099744432198)  # 草
            await message.add_reaction(emoji)

        for word in ["💜❤💙💚", "brez", "ぶれず", "ブレズ", "愛", "sar", "oras", "かわいい", "カワイイ", "好", "impe", "いんぴ", "インピ", "ベッドタイムキャンディ"]:
            if word in message.content.lower():
                for stamp in ["💜", "❤", "💙", "💚"]:
                    await message.add_reaction(stamp)

        embed = Embed(title="GBBの最新情報はこちら",
                      description=">>> 以下のサイトにお探しの情報がない場合、\n__**未発表 もしくは 未定（そもそも決定すらしていない）**__\n可能性が非常に高いです。", color=0xF0632F)
        embed.add_field(name="GBBINFO-JPN 日本非公式情報サイト",
                        value="https://gbbinfo-jpn.jimdofree.com/")
        embed.add_field(name="swissbeatbox 公式instagram",
                        value="https://www.instagram.com/swissbeatbox/")
        text = await gbb_countdown()
        embed.set_footer(text=text)

        if "m!wc" in message.content.lower():
            await message.channel.send(embed=embed)
            await message.channel.send("[GBB 2023 Wildcard結果・出場者一覧 はこちら](https://gbbinfo-jpn.jimdofree.com/20230222/)")

        if message.channel.type in [ChannelType.text, ChannelType.forum, ChannelType.public_thread]:  # テキストチャンネルの場合
            emoji = random.choice(message.guild.emojis)
            if message.author.id in [891228765022195723, 886518627023613962]:  # Yuiにはbrezを
                emoji = message.guild.get_emoji(889877286055198731)  # brez
            if message.author.id in [887328590407032852, 870434043810971659]:  # 湯にはsaroを
                emoji = message.guild.get_emoji(889920546408661032)  # oras
            # maycoにはheliumを
            if message.author.id in [389427133099016193, 735099594010132480, 990630026275860540]:
                emoji = message.guild.get_emoji(890506350868721664)  # helium
            await message.add_reaction(emoji)

            url_check = re.search(
                r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+", message.content)
            if bool(url_check):
                return

            for word in ["gbb", "wildcard", "ワイカ", "ワイルドカード", "結果", "出場", "通過", "チケット", "ルール", "審査員", "ジャッジ", "日本人", "colaps"]:
                if word in message.content.lower():
                    if any(["?" in message.content, "？" in message.content]):
                        await message.reply("**GBB最新情報をお探しですか？**\n## ぜひこちらのサイトをご覧ください！\n\n[GBBINFO-JPN 日本非公式情報サイト](https://gbbinfo-jpn.jimdofree.com/)")
                        await message.reply(embed=embed)
                    else:
                        await message.channel.send(embed=embed)
                    break
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
        except ClientException:
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
        audio = PCMVolumeTransformer(
            FFmpegPCMAudio(ran_audio[ran_int]), volume=0.2)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p kbbtime" or message.content == "s.kbbtime":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        audio = PCMVolumeTransformer(FFmpegPCMAudio("kbbtime.mp3"), volume=0.2)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p kansei" or message.content == "s.kansei":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        ran_int = random.randint(1, 2)
        ran_audio = {1: "kansei.mp3", 2: "kansei_2.mp3"}
        audio = PCMVolumeTransformer(
            FFmpegPCMAudio(ran_audio[ran_int]), volume=0.2)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p count" or message.content == "s.count":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        ran_int = random.randint(1, 2)
        ran_audio = {1: "countdown.mp3", 2: "countdown_2.mp3"}
        audio = PCMVolumeTransformer(
            FFmpegPCMAudio(ran_audio[ran_int]), volume=0.2)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p bunka" or message.content == "s.bunka":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        audio = PCMVolumeTransformer(FFmpegPCMAudio("bunka.mp3"), volume=0.2)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p esh" or message.content == "s.esh":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        ran_int = random.randint(1, 2)
        ran_audio = {1: "esh.mp3", 2: "esh_2.mp3"}
        audio = PCMVolumeTransformer(
            FFmpegPCMAudio(ran_audio[ran_int]), volume=0.4)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p msn" or message.content == "s.msn":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        audio = PCMVolumeTransformer(FFmpegPCMAudio(
            f"msn_{random.randint(1, 3)}.mp3"), volume=0.4)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p olala" or message.content == "s.olala":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        audio = PCMVolumeTransformer(FFmpegPCMAudio("olala.mp3"), volume=0.4)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p dismuch" or message.content == "s.dismuch":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        ran_int = random.randint(1, 4)
        ran_audio = {1: "dismuch.mp3", 2: "dismuch_2.mp3",
                     3: "dismuch_3.mp3", 4: "dismuch_4.mp3"}
        audio = PCMVolumeTransformer(
            FFmpegPCMAudio(ran_audio[ran_int]), volume=1)
        message.guild.voice_client.play(audio)
        return

    ##############################
    # 60秒カウンター x4
    ##############################

    if message.content.startswith("s.c") and "s.c90" not in message.content and "s.cancel" not in message.content and "s.check" not in message.content:
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        voice_client = message.guild.voice_client
        names = [(j) for j in message.content.replace('s.c', '').split()]
        if len(names) == 0:
            await message.delete(delay=1)
            audio = PCMVolumeTransformer(
                FFmpegPCMAudio("countdown.mp3"), volume=0.5)
            embed = Embed(title="3, 2, 1, Beatbox!")
            sent_message = await message.channel.send(embed=embed)
            message.guild.voice_client.play(audio)
            await sleep(7)
            connect = voice_client.is_connected()
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
                connect = voice_client.is_connected()
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
            audio = PCMVolumeTransformer(
                FFmpegPCMAudio("time.mp3"), volume=0.5)
            message.guild.voice_client.play(audio)
            await sleep(3)
            audio = PCMVolumeTransformer(
                FFmpegPCMAudio("msn.mp3"), volume=0.5)
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
        audio = PCMVolumeTransformer(
            FFmpegPCMAudio("countdown.mp3"), volume=0.5)
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
            connect = voice_client.is_connected()
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
                    connect = voice_client.is_connected()
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
        audio = PCMVolumeTransformer(
            FFmpegPCMAudio("time.mp3"), volume=0.2)
        message.guild.voice_client.play(audio)
        await sleep(3)
        audio = PCMVolumeTransformer(
            FFmpegPCMAudio("msn.mp3"), volume=0.5)
        message.guild.voice_client.play(audio)
        await message.delete(delay=1)
        await sleep(3)
        embed = Embed(
            title="オーディエンス投票受付中", description="YouTube投票機能を利用して集計します")
        embed.add_field(name="※投票できないときは",
                        value="アプリの再起動をお試しください", inline=False)
        await sent_message.edit(embed=embed, delete_after=20)
        return

    ##############################
    # 90秒カウンター x4
    ##############################

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

    ##############################
    # バトスタコマンド
    ##############################

    if message.content.startswith("s.battle"):
        await battle(message.content, client)
        return

    if message.content == "s.start":
        await start(client)
        return

    if message.content == "s.stage":
        await message.delete(delay=1)
        stage_channel = client.get_channel(931462636019802123)  # ステージ
        try:
            await stage_channel.create_instance(topic="BATTLE STADIUM")
        except Exception:
            pass
        try:
            await stage_channel.connect(reconnect=True)
        except ClientException:
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
            if scheduled_event.status == EventStatus.active and scheduled_event.name == "BATTLE STADIUM":
                await scheduled_event.end()
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

    ##############################
    # バトスタ宣伝
    ##############################

    if message.content.startswith("s.bs"):
        general = message.guild.get_channel(864475338340171791)  # 全体チャット
        announce = message.guild.get_channel(885462548055461898)  # お知らせ
        await message.delete(delay=1)
        dt_now = datetime.now(JST)
        sat = timedelta(days=6 - int(dt_now.strftime("%w")))
        start_time = datetime(dt_now.year, dt_now.month,
                              dt_now.day, 21, 30, 0, 0, JST) + sat
        end_time = datetime(dt_now.year, dt_now.month,
                            dt_now.day, 22, 30, 0, 0, JST) + sat
        stage = client.get_channel(931462636019802123)  # BATTLE STADIUM
        event = await message.guild.create_scheduled_event(
            name="BATTLE STADIUM",
            description="【エキシビションBeatboxバトルイベント】\n今週もやります！いつでも何回でも参加可能です。\nぜひご参加ください！\n観戦も可能です。観戦中、マイクがオンになることはありません。\n\n※エントリー受付・当日の進行はすべてbotが行います。\n※エントリー受付開始時間は、バトル開始1分前です。",
            start_time=start_time,
            end_time=end_time,
            channel=stage,
            privacy_level=PrivacyLevel.guild_only)
        await announce.send(file=File(f"battle_stadium_{random.randint(1, 3)}.gif"))
        await announce.send(event.url)
        await general.send(file=File(f"battle_stadium_{random.randint(1, 3)}.gif"))
        await general.send(event.url)
        return

keep_alive()
try:
    client.run(TOKEN)
except Exception:
    os.system("kill 1")
