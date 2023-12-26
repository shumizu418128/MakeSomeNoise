from discord import ButtonStyle
from discord.ui import Button, View

# NOTE: ビト森杯運営機能搭載ファイル

# trueになっているボタンを表示 (falseは非表示)


async def get_view(
    contact: bool = False,
    call_admin: bool = False,
    submission_content: bool = False,
    cancel: bool = False,
    entry_bitomori: bool = False,
    entry_exhibition: bool = False,
    entry: bool = False,
    replace: bool = False
):
    view = View(timeout=None)

    button_contact = Button(
        label="お問い合わせチャンネル作成",
        style=ButtonStyle.primary,
        custom_id="button_contact",
        emoji="📝"
    )
    button_call_admin = Button(
        label="運営に問い合わせ",
        style=ButtonStyle.primary,
        custom_id="button_call_admin",
        emoji="📩"
    )
    button_submission_content = Button(
        label="エントリー状況照会",
        style=ButtonStyle.gray,
        custom_id="button_submission_content",
        emoji="🔍"
    )
    button_cancel = Button(
        label="エントリーキャンセル",
        style=ButtonStyle.red,
        custom_id="button_cancel",
        emoji="❌"
    )
    button_entry_bitomori = Button(
        style=ButtonStyle.green,
        label="ビト森杯エントリー",
        custom_id="button_entry_bitomori",
        emoji="🏆"
    )
    button_entry_exhibition = Button(
        style=ButtonStyle.green,
        label="OLEBエントリー",
        custom_id="button_entry_exhibition",
        emoji="⚔️"
    )
    # 問い合わせスレッド作成
    if contact:
        view.add_item(button_contact)

    # 運営呼び出し
    if call_admin:
        view.add_item(button_call_admin)

    # エントリー状況照会
    if submission_content:
        view.add_item(button_submission_content)

    # キャンセル
    if cancel:
        view.add_item(button_cancel)

    # ビト森杯エントリー
    if entry_bitomori or entry:
        view.add_item(button_entry_bitomori)

    # OLEBエントリー
    if entry_exhibition or entry:
        view.add_item(button_entry_exhibition)

    # entry = entry_bitomori and entry_exhibition

    # 繰り上げ出場
    button_accept_replace = Button(
        style=ButtonStyle.green,
        label="ビト森杯に出場する",
        custom_id="button_accept_replace",
        emoji="✅"
    )
    if replace:
        view.add_item(button_accept_replace)
        view.add_item(button_cancel)
        view.add_item(button_call_admin)
    return view
