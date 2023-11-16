# from pprint import pprint
from typing import Any

from anymail.signals import AnymailInboundEvent
from dateutil.parser import ParserError, parse

from journal.accounts.models import Account
from journal.entries.models import Entry


def handle_inbound(
    sender: Any, event: AnymailInboundEvent, esp_name: str, **kwargs: Any
) -> None:
    message = event.message
    if message is None:
        print("No message")
        return None

    # TODO: parse message.text to remove prompt text

    try:
        entry_datetime = parse(message.subject, fuzzy_with_tokens=True)[0]  # type: ignore
    except ParserError:
        print("Bad date parse")
        return None

    username = message.to[0].username
    if "." not in username:
        print("Username missing period.")
        return None

    account_id = username.split(".")[1]
    try:
        account = Account.objects.active().get(id=account_id)
    except Account.DoesNotExist:
        print(f"No active account ID: {account_id}")
        return None

    Entry.objects.create(
        body=message.text,
        when=entry_datetime.date(),
        user=account.user,
    )
