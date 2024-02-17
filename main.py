import os
import random
from asyncio import sleep
from datetime import datetime, timedelta, timezone

import discord
from discord import (ChannelType, Client, Embed, EventStatus, File, Intents,
                     Interaction, Member, Message, PrivacyLevel, VoiceState)
from discord.errors import ClientException

from advertise import advertise
from battle_stadium import battle, start
from button_admin_callback import (button_admin_cancel,
                                   button_admin_create_thread,
                                   button_admin_entry,
                                   button_admin_submission_content)
from button_callback import (button_accept_replace, button_call_admin,
                             button_cancel, button_contact, button_entry,
                             button_submission_content)
from button_view import get_view
from contact import (contact_start, search_contact)
from daily_work import daily_work_AM9, daily_work_PM10
from gbb import countdown
from keep_alive import keep_alive
from natural_language import natural_language
from search_next_event import search_next_event

# NOTE: ビト森杯運営機能搭載ファイル
TOKEN = os.environ['DISCORD_BOT_TOKEN']
intents = Intents.all()  # デフォルトのIntentsオブジェクトを生成
intents.typing = False  # typingを受け取らないように
client = Client(intents=intents)
JST = timezone(timedelta(hours=9))

print(
    f"Make Some Noise! (server): {discord.__version__} {datetime.now(JST).strftime('%Y-%m-%d %H:%M:%S')}")


@client.event
async def on_ready():  # 起動時に動作する処理
    advertise.start(client)  # バトスタ宣伝、バトスタ開始ボタン
    # daily_work_PM10.start(client)  # ビト森杯定期作業 22:00
    # daily_work_AM9.start(client)  # ビト森杯定期作業 09:00
    return


@client.event
async def on_interaction(interaction: Interaction):
    bot_channel = interaction.guild.get_channel(
        897784178958008322  # bot用チャット
    )
    custom_id = interaction.data["custom_id"]

    # セレクトメニューの場合
    if custom_id.startswith("select"):
        await interaction.response.defer(ephemeral=True, thinking=True)
        value = interaction.data["values"][0]
        await interaction.followup.send(
            interaction.user.mention,
            file=File(f"{value}.jpg"),
            ephemeral=True
        )
        return

    # ボタンのカスタムIDに_がない場合、custom_id未設定のためreturn
    if "_" not in custom_id:
        return

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
    embed.timestamp = datetime.now(JST)

    # 問い合わせスレッドがあり、かつ該当interactionと別チャンネルなら、descriptionに追加
    thread = await search_contact(interaction.user)
    if bool(thread) and interaction.message.channel.id != thread.id:
        embed.description += f"\n\nthread: {thread.jump_url}"

    # モーダルの場合、提出内容を表示
    if custom_id.startswith("modal"):
        values_list = [
            f"- `{sub_component['custom_id']}:` {sub_component['value']}"
            for component in interaction.data['components']
            for sub_component in component['components']
        ]
        values = "\n".join(values_list)
        embed.add_field(name="提出内容", value=values)

    await bot_channel.send(f"{interaction.user.id}", embed=embed)

    ##############################
    # 運営専用ボタン
    ##############################

    role_check = interaction.user.get_role(904368977092964352)  # ビト森杯運営
    if bool(role_check):

        # ビト森杯エントリー
        if "entry" in custom_id:
            await button_admin_entry(interaction)

        # キャンセル
        if "cancel" in custom_id:
            await button_admin_cancel(interaction)

        # エントリー状況照会
        if "submission_content" in custom_id:
            await button_admin_submission_content(interaction)

        # 問い合わせスレッド作成
        if custom_id == "button_admin_create_thread":
            await button_admin_create_thread(interaction)
        return

    ##############################
    # 参加者が押すボタン
    ##############################

    # ビト森杯エントリー
    if custom_id.startswith("button_entry"):
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
    if custom_id == "button_submission_content":
        await button_submission_content(interaction)

    # 繰り上げエントリー
    if custom_id == "button_accept_replace":
        await button_accept_replace(interaction)


@client.event
async def on_voice_state_update(member: Member, before: VoiceState, after: VoiceState):
    if member.id == 412082841829113877 or member.bot:  # tari3210
        return
    try:
        vc_role = member.guild.get_role(935073171462307881)  # in a vc

        # チャンネルから退出
        if bool(before.channel) and after.channel is None:
            await member.remove_roles(vc_role)

        # チャンネルに参加
        elif before.channel != after.channel and bool(after.channel):
            embed = Embed(
                title="BEATBOXをもっと楽しむために",
                description="", color=0x0081f0
            )
            embed.add_field(
                name=f"Let's show your 💜❤💙💚 with {member.display_name}!",
                value="ビト森のすべての仲間たちと、\nもっとBEATBOXを好きになれる。\nそんなあたたかい雰囲気作りに、\nぜひ、ご協力をお願いします。"
            )
            embed.set_footer(
                text="We love beatbox, We are beatbox family\nあつまれ！ビートボックスの森",
                icon_url=member.guild.icon.url
            )
            if after.channel.id == 886099822770290748:  # リアタイ部屋
                content = f"{member.mention} チャットはこちら chat is here"

                # マイクオンの場合、通知する
                if after.self_mute is False:
                    content += f"\n{member.display_name}さんはマイクがONになっています。ミュートに設定を変更すると、聞き専参加が可能です。"

                # マイクオフの場合、オンにすることを推奨する
                elif after.self_mute is True:
                    content += f"\n{member.display_name}さんはマイクがOFFになっています。ぜひマイクをONにして、一緒に盛り上がりましょう！"

                await after.channel.send(content, embed=embed, delete_after=60)

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
    text = await countdown()  # GBBまでのカウントダウン
    embed.set_footer(text=text)
    await channel.send(f"{member.mention}\nあつまれ！ビートボックスの森 へようこそ！", embeds=[embed_discord, embed])
    next_event = await search_next_event(channel.guild.scheduled_events)
    if bool(next_event):
        await sleep(1)
        await channel.send(next_event.url)

    view = await get_view(entry=True, contact=True)
    await channel.send("第3回ビト森杯(Loop)・Online Loopstation Exhibition Battle", view=view)


@client.event
async def on_message(message: Message):
    # バトスタ対戦表、バトスタチャット
    if message.author.bot or message.content.startswith("l.") or message.channel.id in [930767329137143839, 930839018671837184]:
        return

    # s.から始まらない場合(コマンドではない場合)
    if not message.content.startswith("s."):
        await natural_language(message)
        if message.channel.id == 1035965200341401600:  # ビト森杯 お知らせ
            view = await get_view(entry=True, contact=True)
            await message.channel.send(view=view)
            view = await get_view(info=True)
            await message.channel.send("以下のセレクトメニューからも詳細情報を確認できます。", view=view)
        return

    if message.content == "s.test":
        await message.channel.send(f"{str(client.user)}\n{discord.__version__}")
        return

    if message.content == "s.admin":
        await message.delete(delay=1)
        view = await get_view(admin=True)
        await message.channel.send(f"{message.author.mention}\n運営専用ボタン ※1分後に削除されます", view=view, delete_after=60)
        return

    if message.content == "s.entry":
        await message.delete(delay=1)
        view = await get_view(entry=True, contact=True)
        await message.channel.send(view=view)
        view = await get_view(info=True)
        await message.channel.send("以下のセレクトメニューからも詳細情報を確認できます。", view=view)
        return

    if message.content == "s.oleb":
        await message.delete(delay=1)
        role_exhibition = message.guild.get_role(
            1171760161778581505  # エキシビション
        )
        oleb_member_names = [
            member.display_name for member in role_exhibition.members
        ]
        if len(oleb_member_names) < 2:
            await message.channel.send("参加者数が不足しています。")
            return

        random.shuffle(oleb_member_names)
        embed = Embed(
            title="Online Loopstation Exhibition Battle 対戦表",
            description="対戦表"
        )
        for i in range(0, len(oleb_member_names), 2):
            embed.add_field(
                name=f"{i//2+1}回戦",
                value=f"{oleb_member_names[i]} vs {oleb_member_names[i+1]}"
            )
        if len(oleb_member_names) % 2 == 1:
            embed.description += f"\n\n参加者{len(oleb_member_names)}名\nbye: {oleb_member_names[-1]}"

        await message.channel.send(embed=embed)
        return

    if message.content == "s.reset":
        await message.delete(delay=1)
        if message.channel.type != ChannelType.private_thread:
            return

        member_id = message.channel.name.split("_")[0]
        member = message.guild.get_member(int(member_id))
        await contact_start(client, member)
        return

    if message.content == "s.contact":
        role = message.guild.get_role(
            1036149651847524393  # ビト森杯
        )
        for member in role.members:
            thread = await search_contact(member)
            if thread is None:
                await contact_start(client, member, entry_redirect=True)
        return

    if message.content == "s.notice":

        # ビト森杯エントリー者のIDを取得
        role_bitomori = message.guild.get_role(
            1036149651847524393  # ビト森杯
        )
        role_exhibition = message.guild.get_role(
            1171760161778581505  # エキシビション
        )
        # 両方のメンバーの集合を取得
        members = set(role_bitomori.members + role_exhibition.members)

        # エントリー者全員にZoomリンクを通知
        for member in members:

            # 除外メンバー
            if member.id == 1173621407658299523 or member.id == 1042416484338630686:
                continue

            # スレッドを取得
            thread = await search_contact(member)
            if thread is None:
                await contact_start(client, member, entry_redirect=True)
                thread = await search_contact(member)

            embed = Embed(
                title="ビト森杯・Online Loopstation Exhibition Battle 共通Zoomリンク",
                description="ご参加ありがとうございます\n\n[当日使用するZoomリンクはこちらです](https://zoom.us/j/94689140157?pwd=djFGUUtYRUhvejVoWDd5VWo5VHVCdz09)\
                    \n\n[ノイズキャンセル設定方法](https://support.zoom.com/hc/ja/article?id=zm_kb&sysparm_article=KB0059995#h_01GZ2K7TDMTK8YCKCTQ4JJ2NWB)\
                    \n[ステレオ設定方法](https://support.zoom.com/hc/ja/article?id=zm_kb&sysparm_article=KB0063294#h_77f0b3d3-cdeb-4b6f-9e47-204b127e2059)"
            )
            embed.set_footer(
                text="※リンクは絶対に他人に教えないでください",
                icon_url=message.guild.icon.url
            )
            await thread.send(
                f"{member.mention}\n### リンクは絶対に他人に教えないでください",
                embed=embed
            )
            await thread.send("当日の注意事項はこちらをご確認ください。\nhttps://discord.com/channels/864475338340171786/1035965200341401600/1206598450288787466")
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
