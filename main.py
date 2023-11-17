import os
import random
from asyncio import sleep
from datetime import datetime, time, timedelta, timezone

import discord
from discord import (Client, Embed, EventStatus, File, Intents, Interaction,
                     Member, Message, PrivacyLevel, VoiceState)
from discord.errors import ClientException
from discord.ext import tasks

from battle_stadium import battle, start
from button_callback import (button_call_admin, button_cancel, button_contact,
                             button_entry, button_entry_confirm)
from gbb_countdown import gbb_countdown
from keep_alive import keep_alive
from natural_language import natural_language
from search_next_event import search_next_event

TOKEN = os.environ['DISCORD_BOT_TOKEN']
intents = Intents.all()  # デフォルトのIntentsオブジェクトを生成
intents.typing = False  # typingを受け取らないように
client = Client(intents=intents)
print(f"Make Some Noise! (server): {discord.__version__}")

JST = timezone(timedelta(hours=9))
PM9 = time(21, 0, tzinfo=JST)


@tasks.loop(time=PM9)
async def advertise():
    channel = client.get_channel(864475338340171791)  # 全体チャット
    # 次のイベント
    next_event = await search_next_event(channel.guild.scheduled_events)
    if bool(next_event) and next_event.name == "BATTLE STADIUM":  # バトスタの場合
        # gif
        await channel.send(file=File(f"battle_stadium_{random.randint(1, 3)}.gif"))
    await channel.send(next_event.url)  # 次のイベントのURL送信
    dt_now = datetime.now(JST)  # 現在時刻

    # バトスタ開始まで35分以内の場合
    if next_event.name == "BATTLE STADIUM" and next_event.start_time - dt_now < timedelta(minutes=35):
        await sleep(29 * 60)  # 29分待機
        embed = Embed(title="BATTLE STADIUM 開始ボタン",
                      description="▶️を押すとバトスタを開始します")
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
            await battle_stadium_start.clear_reactions()
        except TimeoutError:  # 10分経過ならさよなら
            await battle_stadium_start.clear_reactions()
            return
        if reaction.emoji == "❌":  # ❌ならさよなら
            await battle_stadium_start.delete()
        await start(client)
    return


@client.event
async def on_ready():  # 起動時に動作する処理
    advertise.start()  # バトスタ宣伝
    return


@client.event
async def on_interaction(interaction: Interaction):
    custom_id = interaction.data["custom_id"]

    # interaction通知
    embed = Embed(
        title=custom_id,
        description=f"{interaction.user.mention}\n{interaction.message.jump_url}",
        color=0x00bfff
    )
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.display_avatar.url
    )
    bot_channel = interaction.guild.get_channel(
        897784178958008322  # bot用チャット
    )
    await bot_channel.send(f"{interaction.user.id}", embed=embed)

    ##############################
    # 参加者が押すボタン
    ##############################

    # ビト森杯エントリー
    if custom_id == "button_entry":
        await button_entry(interaction)

    # お問い合わせ
    if custom_id == "button_contact":
        await button_contact(interaction)

    # 運営呼び出し
    if custom_id == "button_call_admin":
        await button_call_admin(interaction)

    # キャンセル
    if custom_id == "button_cancel":
        await button_cancel(interaction)

    # エントリー状況照会
    if custom_id == "button_entry_confirm":
        await button_entry_confirm(interaction)


@client.event
async def on_voice_state_update(member: Member, before: VoiceState, after: VoiceState):
    if member.id == 412082841829113877 or member.bot:  # tari3210
        return
    try:
        vc_role = member.guild.get_role(935073171462307881)  # in a vc
        if bool(before.channel) and after.channel is None:  # チャンネルから退出
            await member.remove_roles(vc_role)
        # チャンネルに参加
        elif before.channel != after.channel and bool(after.channel):
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
    if bool(next_event):
        await sleep(1)
        await channel.send(next_event.url)


@client.event
async def on_message(message: Message):
    # バトスタ対戦表、バトスタチャット
    if message.author.bot or message.content.startswith("l.") or message.channel.id in [930767329137143839, 930839018671837184]:
        return
    # s.から始まらない場合(コマンドではない場合)
    if not message.content.startswith("s."):
        await natural_language(message)
        return

    if message.content == "s.test":
        await message.channel.send(f"{str(client.user)}\n{discord.__version__}")
        return

    # VS参加・退出
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

    ##############################
    # バトスタコマンド
    ##############################

    if message.content.startswith("s.battle"):
        await battle(message.content, client)
        return

    if message.content == "s.start":
        await start(client)
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

    # 今週末のバトスタを設定（2週間後ではない）
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
