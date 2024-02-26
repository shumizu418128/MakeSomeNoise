from datetime import datetime, timedelta, timezone

from discord import Embed, Interaction

import database
from contact import (contact_start, debug_log, get_submission_embed,
                     search_contact)
from entry import Modal_entry, entry_cancel
from database import get_worksheet

# NOTE: ビト森杯運営機能搭載ファイル
JST = timezone(timedelta(hours=9))
green = 0x00ff00
yellow = 0xffff00
red = 0xff0000
blue = 0x00bfff


# 両カテゴリーのエントリーを受け付ける
async def button_entry(interaction: Interaction):

    # エントリー開始時刻を定義 1月6日 22:00
    dt_now = datetime.now(JST)
    dt_entry_start = datetime(
        year=2024,
        month=1,
        day=6,
        hour=22,
        tzinfo=JST
    )
    # ビト森杯エントリー済みかどうか確認
    # ビト森杯はanyでキャンセル待ちも含む
    role_check = [
        any([
            interaction.user.get_role(database.ROLE_LOOP),
            interaction.user.get_role(database.ROLE_LOOP_RESERVE)
        ]),
        interaction.user.get_role(database.ROLE_OLEB)
    ]
    # エントリーカテゴリー取得
    category = interaction.data["custom_id"].replace("button_entry_", "")

    # localeを取得
    locale = str(interaction.locale)

    # 問い合わせスレッドがある場合はそこからlocaleを取得
    thread = await search_contact(member=interaction.user)
    if bool(thread):
        locale = thread.name.split("_")[1]

    # エントリー開始時刻確認（tari_2は除外）
    if dt_now < dt_entry_start and interaction.user.id != database.TARI_2:
        await interaction.response.send_message(
            f"{interaction.user.mention}\nビト森杯(Loop)・Online Loopstation Exhibition Battle\nエントリー受付開始は1月6日 22:00です。",
            ephemeral=True
        )
        return

    # ビト森杯エントリー済み
    if role_check[0] and category == "bitomori":
        embed = Embed(
            title="エントリー済み",
            description="ビト森杯\nすでにエントリー済みです。",
            color=red
        )
        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_avatar.url
        )
        await interaction.response.send_message(interaction.user.mention, embed=embed, ephemeral=True)
        return

    # エキシビションエントリー済み
    if role_check[1] and category == "exhibition":
        embed = Embed(
            title="エントリー済み",
            description="Online Loopstation Exhibition Battle\nすでにエントリー済みです。",
            color=red
        )
        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_avatar.url
        )
        await interaction.response.send_message(interaction.user.mention, embed=embed, ephemeral=True)
        return

    # 日本からのエントリー
    if locale == "ja":

        # 1回目のエントリーの場合
        if not any(role_check):
            await interaction.response.send_modal(Modal_entry(interaction.user.display_name, category))
            return

    # 以下モーダル送信しないのでdeferをかける
    await interaction.response.defer(ephemeral=True, thinking=True)
    """
    # 日本からの、2回目のエントリーの場合
    if locale == "ja":
        await entry_2nd(interaction, category)
        return"""

    # 海外からのエントリー
    thread = await search_contact(member=interaction.user, create=True, locale=str(interaction.locale))

    # 各種言語の文言
    available_langs = [
        "ko", "zh-TW", "zh-CN",
        "en-US", "en-GB", "es-ES", "pt-BR"
    ]
    # localeが利用可能言語に含まれていない場合は英語にする
    if locale not in available_langs:
        locale = "en-US"
    langs = {
        "en-US": f"Error: please contact us via {thread.jump_url}",
        "en-GB": f"Error: please contact us via {thread.jump_url}",
        "zh-TW": f"錯誤：請點一下 {thread.jump_url} 聯係我們",
        "zh-CN": f"错误：请点击 {thread.jump_url} 联系我们 ※此服务器仅以日英交流",
        "ko": f"문의는 {thread.jump_url} 로 보내주세요",
        "es-ES": f"Error: por favor contáctenos a través de {thread.jump_url}",
        "pt-BR": f"Erro: entre em contato conosco através de {thread.jump_url}"
    }
    description = langs[locale] + f"\nお手数ですが {thread.jump_url} までお問い合わせください。"

    # 一旦エラー文言を送信
    embed = Embed(
        title="contact required: access from overseas",
        description=description,
        color=red
    )
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.display_avatar.url
    )
    await interaction.followup.send(interaction.user.mention, embed=embed, ephemeral=True)

    # 問い合わせスレッドにリダイレクト
    await contact_start(client=interaction.client, member=interaction.user, entry_redirect=True)
    return


async def button_contact(interaction: Interaction):
    await interaction.response.defer(ephemeral=True, thinking=True)

    # 問い合わせスレッドを取得or作成
    thread = await search_contact(member=interaction.user, create=True, locale=str(interaction.locale))
    embed = Embed(
        title="お問い合わせチャンネル作成",
        description=f"{thread.jump_url} までお問い合わせください。",
        color=blue
    )
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.display_avatar.url
    )
    await interaction.followup.send(interaction.user.mention, embed=embed, ephemeral=True)

    # 問い合わせ対応開始
    await contact_start(client=interaction.client, member=interaction.user)
    return


async def button_call_admin(interaction: Interaction):
    await interaction.response.defer(thinking=True)

    contact = interaction.client.get_channel(database.CHANNEL_CONTACT)
    admin = interaction.guild.get_role(database.ROLE_ADMIN)
    # しゃべってよし
    await contact.set_permissions(interaction.user, send_messages_in_threads=True)

    # 要件を書くよう案内
    embed = Embed(
        title="このチャンネルにご用件をご記入ください",
        description="運営が対応します",
        color=yellow
    )
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.display_avatar.url
    )
    await interaction.followup.send(interaction.user.mention, embed=embed)
    await interaction.channel.send("↓↓↓ このチャットにご記入ください ↓↓↓")

    # メッセージが来たら運営へ通知
    def check(m):
        return m.channel == interaction.channel and m.author == interaction.user

    msg = await interaction.client.wait_for('message', check=check)
    await msg.reply(
        f"{admin.mention}\n{interaction.user.display_name}さんからの問い合わせ",
        mention_author=False
    )
    # エントリー状況照会
    embed = await get_submission_embed(interaction.user)
    await interaction.channel.send(embed=embed)
    return


async def button_cancel(interaction: Interaction):

    # 応答タイミングが状況に応じて違うので、ここで応答を済ませる
    await interaction.response.send_message(f"{interaction.user.mention}\n処理中...", delete_after=2)

    role_check = [
        any([
            interaction.user.get_role(database.ROLE_LOOP),
            interaction.user.get_role(database.ROLE_LOOP_RESERVE)
        ]),
        interaction.user.get_role(database.ROLE_OLEB)
    ]
    emoji = ""

    # そもそもエントリーしてる？
    # どちらのロールも持っていない場合
    if any(role_check) is False:
        embed = Embed(
            title="エントリーキャンセル",
            description=f"Error: {interaction.user.display_name}さんはエントリーしていません。",
            color=red
        )
        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_avatar.url
        )
        await interaction.channel.send(embed=embed)
        return

    # エントリーカテゴリー 日本語、英語表記定義
    if role_check[0]:  # ビト森杯
        category = "bitomori"
        category_ja = "ビト森杯"
    if role_check[1]:  # エキシビション
        category = "exhibition"
        category_ja = "Online Loopstation Exhibition Battle"

    # 両方にエントリーしている場合
    if all(role_check):

        # キャンセルするカテゴリーを選択
        embed = Embed(
            title="エントリーキャンセル",
            description="どちらのエントリーをキャンセルしますか？\n🏆 ビト森杯\
                \n⚔️ Online Loopstation Exhibition Battle\n❌ このメッセージを削除する",
            color=yellow
        )
        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_avatar.url
        )
        notice = await interaction.channel.send(embed=embed)
        await notice.add_reaction("🏆")
        await notice.add_reaction("⚔️")
        await notice.add_reaction("❌")

        def check(reaction, user):
            return user == interaction.user and reaction.emoji in ["🏆", "⚔️", "❌"] and reaction.message == notice

        try:
            reaction, _ = await interaction.client.wait_for('reaction_add', check=check, timeout=60)

        # 60秒で処理中止
        except TimeoutError:
            await notice.delete()
            await interaction.channel.send("Error: Timeout\nもう1度お試しください")
            return

        # リアクションを消す
        await notice.clear_reactions()

        # ❌ならさよなら
        if reaction.emoji == "❌":
            return
        emoji = reaction.emoji

        # エントリーカテゴリー 日本語、英語表記定義
        if emoji == "🏆":  # ビト森杯
            category = "bitomori"
            category_ja = "ビト森杯"

        if emoji == "⚔️":  # エキシビション
            category = "exhibition"
            category_ja = "Online Loopstation Exhibition Battle"

    # キャンセル意思の最終確認
    embed = Embed(
        title="エントリーキャンセル",
        description=f"{category_ja}エントリーをキャンセルしますか？\n⭕ `OK`\n❌ このメッセージを削除する",
        color=yellow
    )
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.display_avatar.url
    )
    notice = await interaction.channel.send(embed=embed)
    await notice.add_reaction("⭕")
    await notice.add_reaction("❌")

    def check(reaction, user):
        return user == interaction.user and reaction.emoji in ["⭕", "❌"] and reaction.message == notice

    try:
        reaction, _ = await interaction.client.wait_for('reaction_add', timeout=10, check=check)

    # 10秒で処理中止
    except TimeoutError:
        await notice.delete()
        await interaction.channel.send("Error: Timeout\nもう1度お試しください")
        return

    await notice.clear_reactions()

    # ❌ならさよなら
    if reaction.emoji == "❌":
        await notice.delete(delay=1)
        return

    # cancel実行
    await entry_cancel(interaction.user, category)
    return


async def button_submission_content(interaction: Interaction):
    await interaction.response.send_message("処理中...", ephemeral=True)
    embed = await get_submission_embed(interaction.user)
    await interaction.channel.send(embed=embed)
    return


async def button_accept_replace(interaction: Interaction):
    await interaction.response.defer(thinking=True)
    role = interaction.guild.get_role(database.ROLE_LOOP)
    role_reserve = interaction.guild.get_role(database.ROLE_LOOP_RESERVE)
    contact = interaction.guild.get_channel(database.CHANNEL_CONTACT)

    # Google spreadsheet worksheet読み込み
    worksheet = await get_worksheet('エントリー名簿')

    # DBからユーザーIDで検索
    cell_id = await worksheet.find(f'{interaction.user.id}')
    if bool(cell_id):

        # 繰り上げ手続き締切が設定されているか確認
        cell_deadline = await worksheet.cell(row=cell_id.row, col=11)

    # 締切が設定されていない場合 or DBに名前がない場合、エラー通知
    if cell_deadline.value == "" or bool(cell_id) is False:

        # エラー内容
        if bool(cell_id) is False:
            description = "Error: DB検索結果なし"
        elif cell_deadline.value == "":
            description = "Error: DB繰り上げ手続き締め切りなし"

        # bot用チャットへ通知
        await debug_log(
            function_name="button_accept_replace",
            description=description,
            color=red,
            member=interaction.user
        )
        # 該当者へ通知
        embed = Embed(
            title="Error",
            description="運営が対処します。しばらくお待ちください。\n対処には数日かかる場合があります。",
            color=red
        )
        # しゃべってよし
        await contact.set_permissions(interaction.user, send_messages_in_threads=True)
        return

    # まず手続き完了通知
    embed = Embed(
        title="繰り上げ出場手続き完了",
        description="手続きが完了しました。ビト森杯ご参加ありがとうございます。\n\n※エントリー状況照会ボタンで確認できるまで、10秒ほどかかります。",
        color=green
    )
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.display_avatar.url
    )
    await interaction.followup.send(embed=embed)

    # ロール付け替え
    await interaction.user.remove_roles(role_reserve)
    await interaction.user.add_roles(role)

    # 出場可否を出場に変更
    await worksheet.update_cell(cell_id.row, 5, "出場")

    # 繰り上げ手続き締切を削除
    await worksheet.update_cell(cell_id.row, 11, "")

    # 時間を追記
    cell_time = await worksheet.cell(row=cell_id.row, col=9)
    await worksheet.update_cell(
        row=cell_time.row,
        col=cell_time.col,
        value=cell_time.value + " 繰り上げ: " +
        datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")
    )
    # bot用チャットへ通知
    await debug_log(
        function_name="button_accept_replace",
        description="繰り上げ出場手続き完了",
        color=blue,
        member=interaction.user
    )
    # memberを再取得
    member = interaction.guild.get_member(interaction.user.id)

    # 問い合わせを用意
    await contact_start(client=interaction.client, member=member, entry_redirect=True)
    return
