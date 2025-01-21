"""
Filter visitor implementation to extract filtering information
"""

from datetime import datetime
from typing import Any, Optional, Union

from kognitos.bdk.api import (FilterBinaryExpression, FilterBinaryOperator,
                              FilterExpressionVisitor, FilterUnaryExpression,
                              NounPhrase, NounPhrasesExpression,
                              TypeMismatchError, ValueExpression)
from kognitos.bdk.reflection import ConceptScalarType
from twilio.base import values

SENDER_NUMBER = NounPhrase.from_word_list(["sender", "number"])
RECIPIENT_NUMBER = NounPhrase.from_word_list(["recipient", "number"])
DATE_SENT = NounPhrase.from_word_list(["date", "sent"])


class SMSMessageFilter(FilterExpressionVisitor):
    """
    Extract filtering information from the expression
    """

    current_noun_phrase: Optional[NounPhrase] = None
    current_value: Optional[Any] = None

    recipient_number: Union[str, object] = values.unset
    sender_number: Union[str, object] = values.unset
    date_sent: Union[datetime, object] = values.unset
    date_sent_before: Union[datetime, object] = values.unset
    date_sent_after: Union[datetime, object] = values.unset

    def visit_binary_expression(self, expression: FilterBinaryExpression):
        expression.left.accept(self)
        expression.right.accept(self)

        if expression.operator == FilterBinaryOperator.EQUALS:
            if self.current_noun_phrase == SENDER_NUMBER:
                self.sender_number = str(self.current_value)
            elif self.current_noun_phrase == RECIPIENT_NUMBER:
                self.recipient_number = str(self.current_value)
            elif self.current_noun_phrase == DATE_SENT:
                if not isinstance(self.current_value, datetime):
                    raise TypeMismatchError("date_sent", ConceptScalarType.DATETIME)

                self.date_sent = self.current_value
        elif expression.operator == FilterBinaryOperator.GREATER_THAN:
            if self.current_noun_phrase == DATE_SENT:
                if not isinstance(self.current_value, datetime):
                    raise TypeMismatchError("date_sent", ConceptScalarType.DATETIME)

                self.date_sent_after = self.current_value
        elif expression.operator == FilterBinaryOperator.LESS_THAN:
            if self.current_noun_phrase == DATE_SENT:
                if not isinstance(self.current_value, datetime):
                    raise TypeMismatchError("date_sent", ConceptScalarType.DATETIME)

                self.date_sent_before = self.current_value
        elif expression.operator == FilterBinaryOperator.AND:
            pass
        else:
            raise ValueError(f"unsupported filtering operator: {expression.operator}")

    def visit_unary_expression(self, expression: FilterUnaryExpression):
        pass

    def visit_value(self, expression: ValueExpression):
        self.current_value = expression.value

    def visit_noun_phrases(self, expression: NounPhrasesExpression):
        if len(expression.noun_phrases) != 1:
            raise ValueError(
                f"unsupported filtering noun phrase: {expression.noun_phrases}"
            )

        if expression.noun_phrases[0] not in [
            SENDER_NUMBER,
            RECIPIENT_NUMBER,
            DATE_SENT,
        ]:
            raise ValueError(
                f"unsupported filtering noun phrase: {expression.noun_phrases}"
            )

        self.current_noun_phrase = expression.noun_phrases[0]
