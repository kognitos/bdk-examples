"""
Twilio Book
"""

import logging
from typing import List, Optional

from kognitos.bdk.api import FilterExpression
from kognitos.bdk.decorators import book, connect, procedure
from twilio.rest import Client

from .sms_message import SMSMessage
from .sms_message_filter import SMSMessageFilter

logger = logging.getLogger(__name__)


@book(name="Twilio", icon="data/twilio.svg")
class TwilioBook:
    """
    Twilio book enables users to interact with and manage their communications via the Twilio API.

    Twilio provides a comprehensive communication platform, offering features such as SMS, voice calls, video, and chat. Ideal for businesses
    and developers seeking reliable and scalable communication solutions. The Twilio book ensures secure and seamless access to these services.

    Author:
        Kognitos, Inc.
    """

    def __init__(self):
        """
        Initializes an instance of the class.
        """
        self._account_sid = None
        self._auth_token = None

    @connect(noun_phrase="auth token method")
    def connect(self, account_sid: str, auth_token: str):
        """
        Establishes a connection to the Twilio API using the provided account SID and auth token.

        Args:
            account_sid (str): The Account SID from your Twilio account.
            auth_token (str): The Auth Token from your Twilio account.

        Labels:
            account_sid: Account SID
            auth_token: Auth Token
        """
        try:
            logger.info(
                "Attempting to connect to Twilio using Account SID %s", account_sid
            )
            client = Client(account_sid, auth_token)
            # verify the credentials by fetching the account details
            client.api.accounts(account_sid).fetch()

            self._auth_token = auth_token
            self._account_sid = account_sid

            logger.info("Connected to Twilio API successfully.")
        except Exception as e:
            logger.error("Could not connect to Twilio API: %s", str(e))
            raise ValueError(f"Could not connect to Twilio API: {str(e)}") from e

    @procedure("to send an *SMS* message")
    def send_sms_message(
        self, sender_number: str, recipient_number: str, message_body: str
    ) -> Optional[str]:
        """
        Sends an SMS message using the Twilio API.

        Input Concepts:
            the sender number: The Twilio phone number to send the message from
            the recipient number: The recipient's phone number
            the message body: The body of the SMS message to send

        Returns:
            The SID of the sent message if successful, otherwise None.

        Example 1:
            Send an SMS message

            >>> send an SMS message where
            >>>   the sender number is "+18004445555"
            >>>   the recipient number is "+18004446666"
            >>>   the message body is "Hello from Kognitos!"
        """
        client = Client(self._account_sid, self._auth_token)

        message = client.messages.create(
            body=message_body, from_=sender_number, to=recipient_number
        )
        return message.sid

    @procedure("to read some (*SMS* messages)")
    def read_sms_messages(
        self,
        offset: Optional[int],
        limit: Optional[int],
        filter_expression: Optional[FilterExpression],
    ) -> List[SMSMessage]:
        """
        Read some SMS messages using the Twilio API.

        Returns:
            A list of SMS messages that matches the specified filtering criteria

        Example 1:
            Retrieve SMS messages filtered by sender and recipient numbers

            >>> read some sms messages whose sender number is "+18004445555" and whose recipient number is "+18004446666"

        Example 2:
            Retrieve SMS messages filtered by the date in which they were sent

            >>> convert "2022-03-01T15:00:00Z" to a datetime
            >>> use the above as the message date
            >>> read some sms messages whose date sent is the message date

        Example 3:
            Retrieve SMS messages that were sent in the specified time period

            >>> convert "2022-03-01T15:00:00Z" to a datetime
            >>> use the above as the start date
            >>> convert "2022-03-03T15:00:00Z" to a datetime
            >>> use the above as the end date
            >>> read some sms messages whose date sent is after the start date and whose date sent is before the end date
        """
        client = Client(self._account_sid, self._auth_token)

        filter_visitor = SMSMessageFilter()

        if filter_expression is not None:
            filter_expression.accept(filter_visitor)

        messages = client.messages.list(
            to=filter_visitor.recipient_number,
            from_=filter_visitor.sender_number,
            date_sent=filter_visitor.date_sent,
            date_sent_before=filter_visitor.date_sent_before,
            date_sent_after=filter_visitor.date_sent_after,
        )

        if offset is not None:
            messages = messages[offset:]

        if limit is not None:
            messages = messages[:limit]

        return [SMSMessage.from_message_instance(message) for message in messages]
