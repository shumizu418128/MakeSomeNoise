import re
from datetime import datetime, timedelta, timezone

import gspread_asyncio
from discord import Embed, Interaction, Member, TextStyle
from discord.ui import Modal, TextInput
from oauth2client.service_account import ServiceAccountCredentials

from contact import contact_start, search_contact

# NOTE: ビト森杯運営機能搭載ファイル
re_hiragana = re.compile(r'^[ぁ-ゞ　 ー]+$')
JST = timezone(timedelta(hours=9))
green = 0x00ff00
yellow = 0xffff00
red = 0xff0000
blue = 0x00bfff

"""
Google spreadsheet
row = 縦 1, 2, 3, ...
col = 横 A, B, C, ...
"""


def get_credits():
    return ServiceAccountCredentials.from_json_keyfile_name(
        "makesomenoise-4cb78ac4f8b5.json",
        ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive',
         'https://www.googleapis.com/auth/spreadsheets'])


class modal_entry(Modal):  # self = Modal, category = "bitomori" or "exhibition"
    def __init__(self, display_name: str, category: str):
        super().__init__(title="エントリー受付", custom_id=f"modal_entry_{category}")

        self.add_item(
            TextInput(
                label="あなたの名前",
                placeholder="名前",
                default=display_name
            )
        )
        self.add_item(
            TextInput(
                label="あなたの名前の「よみがな」",
                placeholder="よみがな"
            )
        )
        self.add_item(
            TextInput(
                label="使用するデバイス（すべて記入）",
                placeholder="使用するデバイス",
                style=TextStyle.long
            )
        )
        self.add_item(
            TextInput(
                label="備考（任意回答）",
                placeholder="連絡事項など",
                style=TextStyle.long,
                required=False
            )
        )

    # TODO: 動作テスト
    # モーダル提出後の処理
    async def on_submit(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)
        category = self.custom_id.split("_")[1]  # "bitomori" or "exhibition"

        # 入力内容を取得
        name = self.children[0].value
        read = self.children[1].value
        device = self.children[2].value
        note = self.children[3].value
        if note == "":  # 備考が空欄の場合
            note = "なし"  # なしと記載

        # よみがなのひらがな判定
        if not re_hiragana.fullmatch(read):
            embed = Embed(
                title="❌ Error ❌",
                description=f"エントリーに失敗しました。\nよみがなは、**「ひらがな・伸ばし棒** `ー` **のみ」** で入力してください\
                    \n\n入力したよみがな：{read}",
                color=red
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # エントリー処理（初めてのエントリー前提）
        if category == "bitomori":
            await entry_bitomori(
                interaction=interaction,
                name=name,
                read=read,
                device=device,
                note=note
            )
        elif category == "exhibition":
            await entry_exhibition(
                interaction=interaction,
                name=name,
                read=read,
                device=device,
                note=note
            )


# TODO: 動作テスト
async def entry_bitomori(interaction: Interaction, name: str, read: str, device: str, note: str):
    role = interaction.guild.get_role(
        1036149651847524393  # ビト森杯
    )
    role_reserve = interaction.guild.get_role(
        1172542396597289093  # キャンセル待ち ビト森杯
    )
    bot_channel = interaction.guild.get_channel(
        897784178958008322  # bot用チャット
    )
    # ビト森杯エントリー済みかどうか確認
    role_check = [
        interaction.user.get_role(
            1036149651847524393  # ビト森杯
        ),
        interaction.user.get_role(
            1172542396597289093  # キャンセル待ち ビト森杯
        )
    ]
    if role_check[0]:  # ビト森杯エントリー済み
        embed = Embed(
            title="エントリー済み",
            description="既にエントリー済みです。",
            color=red
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        return
    if role_check[1]:  # ビト森杯キャンセル待ち登録済み
        embed = Embed(
            title="キャンセル待ち登録済み",
            description="既にキャンセル待ち登録済みです。",
            color=red
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        return

    # エントリー数が上限に達している or キャンセル待ちリストに人がいる場合
    if len(role.members) >= 16 or len(role_reserve.members) > 0:
        await interaction.user.add_roles(role_reserve)
        embed = Embed(
            title="キャンセル待ち登録",
            description="参加者数が上限に達しているため、キャンセル待ちリストに登録しました。\n\n",
            color=blue
        )
        entry_status = "キャンセル待ち"

    # エントリー受付完了通知
    else:
        await interaction.user.add_roles(role)
        embed = Embed(
            title="エントリー完了",
            description="エントリー受付完了しました。\n\n",
            color=green
        )
        entry_status = "出場"

    submission = f"受付内容\n- 名前: {name}\
        \n- よみがな: {read}\n- 出場可否: {entry_status}\n- デバイス: {device}\n- 備考: {note}"
    embed.description += submission
    await interaction.followup.send(embed=embed, ephemeral=True)

    # 一応bot_channelにも通知
    embed = Embed(
        title="modal_entry",
        description=submission,
        color=blue
    )
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.avatar.url
    )
    await bot_channel.send(f"{interaction.user.id}", embed=embed)

    # Google spreadsheet worksheet読み込み
    gc = gspread_asyncio.AsyncioGspreadClientManager(get_credits)
    agc = await gc.authorize()
    # https://docs.google.com/spreadsheets/d/1Bv9J7OohQHKI2qkYBMnIFNn7MHla8KyKTYTfghcmIRw/edit#gid=0
    workbook = await agc.open_by_key('1Bv9J7OohQHKI2qkYBMnIFNn7MHla8KyKTYTfghcmIRw')
    worksheet = await workbook.worksheet('BATTLEエントリー名簿')

    # エントリー数を更新
    num_entries = await worksheet.cell(row=3, col=1)
    num_entries.value = int(num_entries.value) + 1
    await worksheet.update_cell(row=3, col=1, value=num_entries.value)

    # エントリー情報を書き込み
    row = int(num_entries.value) + 1
    values = [
        name,
        read,
        entry_status,
        device,
        note,
        str(datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")),
        str(interaction.user.id)
    ]
    for col, value in zip(range(3, 10), values):
        await worksheet.update_cell(row=row, col=col, value=value)

    # ニックネームを更新
    await interaction.user.edit(nick=name)
    await contact_start(client=interaction.client, member=interaction.user, entry_redirect=True)


# TODO: 動作テスト
async def entry_exhibition(interaction: Interaction, name: str, read: str, device: str, note: str):
    role_exhibition = interaction.guild.get_role(
        1171760161778581505  # エキシビション
    )
    role_check = interaction.user.get_role(
        1171760161778581505  # エキシビション
    )
    bot_channel = interaction.guild.get_channel(
        897784178958008322  # bot用チャット
    )
    if role_check:  # エキシビションエントリー済み
        embed = Embed(
            title="エントリー済み",
            description="既にエントリー済みです。",
            color=red
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        return

    await interaction.user.add_roles(role_exhibition)
    embed = Embed(
        title="エントリー完了",
        description="エントリー受付完了しました。\n\n",
        color=green
    )
    submission = f"受付内容\n- 名前: {name}\
        \n- よみがな: {read}\n- デバイス: {device}\n- 備考: {note}"
    embed.description += submission
    await interaction.followup.send(embed=embed, ephemeral=True)

    # 一応bot_channelにも通知
    embed = Embed(
        title="modal_entry_exhibition",
        description=submission,
        color=blue
    )
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.avatar.url
    )
    await bot_channel.send(f"{interaction.user.id}", embed=embed)

    # Google spreadsheet worksheet読み込み
    gc = gspread_asyncio.AsyncioGspreadClientManager(get_credits)
    agc = await gc.authorize()
    # https://docs.google.com/spreadsheets/d/1Bv9J7OohQHKI2qkYBMnIFNn7MHla8KyKTYTfghcmIRw/edit#gid=0
    workbook = await agc.open_by_key('1Bv9J7OohQHKI2qkYBMnIFNn7MHla8KyKTYTfghcmIRw')
    worksheet = await workbook.worksheet('エキシビションエントリー名簿')

    # エントリー数を更新
    num_entries = await worksheet.cell(row=3, col=1)
    num_entries.value = int(num_entries.value) + 1
    await worksheet.update_cell(row=3, col=1, value=num_entries.value)

    # エントリー情報を書き込み
    row = int(num_entries.value) + 1
    values = [
        name,
        read,
        device,
        note,
        str(datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")),
        str(interaction.user.id)
    ]
    for col, value in zip(range(3, 9), values):
        await worksheet.update_cell(row=row, col=col, value=value)

    # ニックネームを更新
    await interaction.user.edit(nick=name)
    await contact_start(client=interaction.client, member=interaction.user, entry_redirect=True)


# TODO: 動作テスト
async def entry_cancel(member: Member):
    bot_channel = member.guild.get_channel(
        897784178958008322  # bot用チャット
    )
    tari3210 = member.guild.get_member(
        412082841829113877
    )
    # 問い合わせスレッドを取得
    thread = await search_contact(member=member)

    # キャンセル完了通知
    embed = Embed(
        title="エントリーキャンセル",
        description="ビト森杯エントリーキャンセル完了しました。",
        color=green
    )
    embed.timestamp = datetime.now(JST)
    await thread.send(member.mention, embed=embed)

    role_check = [
        member.get_role(
            1036149651847524393),  # ビト森杯
        member.get_role(
            1172542396597289093)   # キャンセル待ち ビト森杯
    ]

    # ロール削除
    if role_check[0]:  # ビト森杯
        role = member.guild.get_role(
            1036149651847524393  # ビト森杯
        )
        await member.remove_roles(role)
    if role_check[1]:  # キャンセル待ち ビト森杯
        role_reserve = member.guild.get_role(
            1172542396597289093  # キャンセル待ち ビト森杯
        )
        await member.remove_roles(role_reserve)

    # Google spreadsheet worksheet読み込み
    gc = gspread_asyncio.AsyncioGspreadClientManager(get_credits)
    agc = await gc.authorize()
    # https://docs.google.com/spreadsheets/d/1Bv9J7OohQHKI2qkYBMnIFNn7MHla8KyKTYTfghcmIRw/edit#gid=0
    workbook = await agc.open_by_key('1Bv9J7OohQHKI2qkYBMnIFNn7MHla8KyKTYTfghcmIRw')
    worksheet = await workbook.worksheet('BATTLEエントリー名簿')

    # DBから削除
    cell_id = await worksheet.find(f'{member.id}')
    if bool(cell_id):  # DB登録あり
        for i in range(3, 10):
            await worksheet.update_cell(cell_id.row, i, '')
    else:  # DB登録なし
        await bot_channel.send(f"{tari3210.mention}\nError: DB登録なし\nキャンセル作業中止\n\n{thread.jump_url}")
        return

    # 通知
    embed = Embed(
        title="エントリーキャンセル",
        description=thread.jump_url,
        color=blue
    )
    embed.set_author(
        name=member.display_name,
        icon_url=member.avatar.url
    )
    await bot_channel.send(embed=embed)
