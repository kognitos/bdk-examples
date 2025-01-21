"""
SMS message dataclass
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Self

from kognitos.bdk.decorators import concept
from twilio.rest.api.v2010.account.message import MessageInstance


@concept(is_a="sms message")
@dataclass
class SMSMessage:
    """
    An SMS (Short Message Service) message. Represents a text communication sent over a cellular network,
    typically between mobile phones.

    Attributes:
        body: The text content of the message
        num_segments: The number of segments that make up the complete message. SMS message bodies that exceed
            the [character limit](https://www.twilio.com/docs/glossary/what-sms-character-limit) are segmented
            and charged as multiple messages. Note: For messages sent via a Messaging Service, `num_segments` is
            initially `0`, since a sender hasn't yet been assigned
        sender_number: The sender's phone number (in [E.164](https://en.wikipedia.org/wiki/E.164) format),
            [alphanumeric sender ID](https://www.twilio.com/docs/sms/quickstart),
            [Wireless SIM](https://www.twilio.com/docs/iot/wireless/programmable-wireless-send-machine-machine-sms-commands),
            [short code](https://www.twilio.com/en-us/messaging/channels/sms/short-codes), or
            [channel address](https://www.twilio.com/docs/messaging/channels) (e.g., `whatsapp:+15554449999`). For
            incoming messages, this is the number or channel address of the sender. For outgoing messages, this value
            is a Twilio phone number, alphanumeric sender ID, short code, or channel address from which the
            message is sent
        recipient_number: The recipient's phone number (in [E.164](https://en.wikipedia.org/wiki/E.164) format) or
            [channel address](https://www.twilio.com/docs/messaging/channels) (e.g. `whatsapp:+15552229999`)
        date_updated: The [RFC 2822](https://datatracker.ietf.org/doc/html/rfc2822#section-3.3) timestamp (in GMT) of
            when the Message resource was last updated
        price: The amount billed for the message in the currency specified by `price_unit`. The `price` is populated
            after the message has been sent/received, and may not be immediately availalble. View
            the [Pricing page](https://www.twilio.com/en-us/pricing) for more details.
        account_sid: The SID of the [Account](https://www.twilio.com/docs/iam/api/account) associated with
            the Message resource
        num_media: The number of media files associated with the Message resource.
        status: The status of the message, for more information about possible statuses see
            [Message Status](https://www.twilio.com/docs/messaging/api/message-resource#message-status-values)
        messaging_service_sid: The SID of the [Messaging Service](https://www.twilio.com/docs/messaging/api/service-resource)
            associated with the Message resource. A unique default value is assigned if a Messaging Service is not used.
        sid: The unique, Twilio-provided string that identifies the Message resource.
        date_sent: The [RFC 2822](https://datatracker.ietf.org/doc/html/rfc2822#section-3.3) timestamp (in GMT) of when
            the Message was sent. For an outgoing message, this is when Twilio sent the message. For an
             incoming message, this is when Twilio sent the HTTP request to your incoming message webhook URL.
        date_created: The [RFC 2822](https://datatracker.ietf.org/doc/html/rfc2822#section-3.3) timestamp (in GMT) of
            when the Message resource was created
        price_unit: The currency in which `price` is measured, in
            [ISO 4127](https://www.iso.org/iso/home/standards/currency_codes.htm) format (e.g. `usd`, `eur`, `jpy`).
        error_message: The description of the `error_code` if the Message `status` is `failed` or `undelivered`. If no
            error was encountered, the value is `null`.
        error_code: The [error code](https://www.twilio.com/docs/api/errors) returned if the Message `status` is
            `failed` or `undelivered`. If no error was encountered, the value is `null`.
    """

    sid: Optional[str]
    body: Optional[str]
    num_segments: Optional[str]
    sender_number: Optional[str]
    recipient_number: Optional[str]
    price: Optional[float]
    account_sid: str
    num_media: int
    status: Optional[str]
    messaging_service_sid: str
    date_sent: Optional[datetime]
    date_created: Optional[datetime]
    date_updated: Optional[datetime]
    price_unit: str

    error_code: Optional[int]
    error_message: Optional[str]

    @classmethod
    def from_message_instance(cls, message_instance: MessageInstance) -> Self:
        """
        Constructs an SMSMessage object from a given MessageInstance object.

        Arguments:
            message_instance (MessageInstance): The MessageInstance object to create the SMSMessage from.

        Returns:
            The newly created SMSMessage object.

        """
        return SMSMessage(
            sid=message_instance.sid,
            body=message_instance.body,
            num_segments=message_instance.num_segments,
            sender_number=message_instance.from_,
            recipient_number=message_instance.to,
            date_updated=message_instance.date_updated,
            price=message_instance.price,
            status=message_instance.status,
            messaging_service_sid=message_instance.messaging_service_sid,
            date_sent=message_instance.date_sent,
            date_created=message_instance.date_created,
            account_sid=message_instance.account_sid,
            num_media=message_instance.num_media,
            price_unit=message_instance.price_unit,
            error_code=message_instance.error_code,
            error_message=message_instance.error_message,
        )
