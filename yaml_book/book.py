"""
YAML book implementation
"""

# pylint: disable=redefined-builtin
from __future__ import annotations

from io import StringIO
from typing import IO, Any, List, Optional, Self, Union

import yaml
from deepmerge import always_merger
from kognitos.bdk.api import NounPhrase
from kognitos.bdk.decorators import book, concept, procedure

YAMLValue = Union[str, int, float, bool, "YAMLConcept", List["YAMLValue"]]


@concept(is_a="yaml")
class YAMLConcept:
    """
    A concept used to hold a JSON value
    """

    value: Optional[dict] = None

    def __init__(self, value: Optional[dict]):
        self.value = value

    def to_bytes(self) -> bytes:
        """
        Serialize this concept into bytes
        """
        if self.value is None:
            return b""
        return yaml.safe_dump(self.value).encode("utf-8")

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        """
        Deserialize the concept from a byte stream
        """
        if not data:
            return cls(None)
        return cls(yaml.safe_load(data.decode("utf-8")))

    def to_stream(self) -> IO:
        """
        Serialize this concept into a stream
        """
        io = StringIO()
        yaml.safe_dump(self.value, io)
        return io

    @classmethod
    def from_stream(cls, io: IO) -> Self:
        """
        Deserialize the concept from a stream
        """
        return cls(yaml.safe_load(io))

    def has(self, key: str, case_sensitive: bool = True) -> bool:
        """
        Checks if the key exists in the yaml.

        Args:
            key (str): The key to check.
            case_sensitive (bool, optional): Determines whether the check is case-sensitive. Defaults to True.

        Returns:
            bool: True if the key is in the yaml, False otherwise.
        """
        if self.value is not None:
            if case_sensitive and key in self.value:
                return True
            if not case_sensitive and key.lower() in [
                value_key.lower() for value_key in self.value.keys()
            ]:
                return True

        return False

    def get(self, key: str, case_sensitive: bool = True) -> "YAMLValue":
        """
        Retrieve a value from the yaml concept by its key.

        Args:
            key (str): The key to look for in the yaml concept.
            case_sensitive (bool, optional): If True, the key lookup is case-sensitive.
                                             If False, the key lookup is case-insensitive.
                                             Defaults to True.

        Returns:
            The value associated with the provided key, wrapped appropriately.

        Raises:
            KeyError: If the key is not found in the YAMLConcept object.
        """

        def wrap(item: Any) -> YAMLValue:
            if isinstance(item, dict):
                return YAMLConcept(item)
            if isinstance(item, list):
                return [wrap(item) for item in item]

            return item

        if self.value is not None:
            if case_sensitive:
                if key in self.value:
                    return wrap(self.value[key])

                raise KeyError(key)

            if key.lower() in [value_key.lower() for value_key in self.value.keys()]:
                new_key = [
                    value_key
                    for value_key in self.value.keys()
                    if key.lower() == value_key.lower()
                ][0]
                return wrap(self.value[new_key])

            raise KeyError(key)

        raise KeyError(key)

    def set(self, key: str, value: YAMLValue, case_sensitive: bool = True):
        """
        Set a value in the yaml concept by its key.

        Args:
            key (str): The key to set in the yaml concept.
            value (YAMLValue): The value to associate with the provided key.
            case_sensitive (bool, optional): If True, the key lookup is case-sensitive.
                                             If False, the key lookup is case-insensitive.
                                             Defaults to True.

        Returns:
            YAMLConcept: The updated yaml concept object.

        Raises:
            KeyError: If the key is not found in the yaml concept and `case_sensitive` is False.
        """

        def unwrap(item: YAMLValue) -> Any:
            if isinstance(item, YAMLConcept):
                return item.value
            if isinstance(item, list):
                return [unwrap(item) for item in item]

            return item

        if self.value is not None:
            if case_sensitive:
                self.value[key] = unwrap(value)
                return self

            if key.lower() in [value_key.lower() for value_key in self.value.keys()]:
                new_key = [
                    value_key
                    for value_key in self.value.keys()
                    if key.lower() == value_key.lower()
                ][0]
                self.value[new_key] = unwrap(value)
                return self

            raise KeyError(key)
        raise KeyError(key)

    def delete(self, key: str, case_sensitive: bool = True):
        """
        Delete a value from the yaml concept by its key.

        Args:
            key (str): The key to look for in the YAMLConcept object.
            case_sensitive (bool, optional): If True, the key lookup is case-sensitive.
                                             If False, the key lookup is case-insensitive.
                                             Defaults to True.

        Raises:
            KeyError: If the key is not found in the YAMLConcept object.
        """

        def wrap(item: Any) -> Any:
            if isinstance(item, dict):
                return YAMLConcept(item)
            if isinstance(item, list):
                return [wrap(item) for item in item]

            return item

        if self.value is not None:
            if case_sensitive:
                if key in self.value:
                    self.value.pop(key)
                else:
                    raise KeyError(key)
            else:
                if key.lower() in [
                    value_key.lower() for value_key in self.value.keys()
                ]:
                    new_key = [
                        value_key
                        for value_key in self.value.keys()
                        if key.lower() == value_key.lower()
                    ][0]
                    self.value.pop(new_key)
                else:
                    raise KeyError(key)
        else:
            raise KeyError(key)


@book(name="YAML", icon="data/icon.svg")
class YAMLBook:
    """
    The YAML book simplifies interacting with YAML-formatted files, allowing you to open, read, and edit them while maintaining the correct structure and format.

    The YAML book is an easy-to-use book that allows you to interact with YAML-formatted files in a simple and
    straightforward way. YAML, which stands for "YAML Ain't Markup Language", is a language often used for
    configuration files and data exchange between languages with different data structures.

    With the YAML book, you can open, read, and edit YAML files just like you would with any standard document. It
    has features that ensure your modifications keep the correct YAML structure and format, preventing you from
    inadvertently damaging your files.

    Author:
        Kognitos, Inc.
    """

    @procedure("to get a (*yaml*'s property)")
    def get_property_by_name(
        self, yaml: YAMLConcept, property: str | NounPhrase
    ) -> (
        YAMLValue
    ):  # pylint: disable=procedure-return-unsupported-type # https://linear.app/kognitos/issue/KOG-8186/support-recursive-types-on-bdk-linter
        """
        Retrieve a property by name from a YAML concept

        Input Concepts:
            the yaml: The YAML concept
            the property: The name of the property that should be retrieved from the YAML

        Output Concepts:
            the yaml's property: The property that was retrieved from the YAML

        Example 1:
            Retrieve the Movies property using exact match on the name

            >>> get yaml's "Movies"

        Example 2:
            Retrieve the Movies property using natural language

            >>> get yaml's movies
        """
        if isinstance(property, str):
            return yaml.get(property)
        if isinstance(property, NounPhrase):
            for field_name in property.to_field_names():
                if yaml.has(field_name, case_sensitive=False):
                    return yaml.get(field_name, case_sensitive=False)

        raise ValueError(property)

    @procedure("to get a *yaml* as a (text)")
    def convert_to_text(self, yaml: YAMLConcept) -> str:
        """
        Convert a YAML concept into text

        Input Concepts:
            the yaml: The YAML concept

        Output Concepts:
            the text: The serialized YAML concept
        """
        return yaml.to_bytes().decode("utf-8")

    @procedure("to get a text as a (*yaml*)")
    def convert_from_text(self, text: str) -> YAMLConcept:
        """
        Convert a text into a YAML concept

        Input Concepts:
            the text: The text to be converted

        Output Concepts:
            the yaml: The YAML concept
        """
        return YAMLConcept.from_bytes(bytes(text, "utf-8"))

    @procedure("to set or change a (*yaml*)'s property to a value")
    def set_property_to_value(
        self,
        yaml: YAMLConcept,
        property: str | NounPhrase,
        value: YAMLValue,  # pylint: disable=procedure-argument-unsupported-type # https://linear.app/kognitos/issue/KOG-8186/support-recursive-types-on-bdk-linter
    ) -> YAMLConcept:
        """
        Change a property in a YAML concept to a specific text value

        Input Concepts:
            the yaml: The YAML concept which contains the property to be changed
            the yaml's property: The name of the property to be changed
            the value: The concept to be used as value for the property to be changed

        Output Concepts:
            the yaml: The updated YAML concept
        """
        if isinstance(property, str):
            yaml.set(property, value)
        elif isinstance(property, NounPhrase):
            for field_name in property.to_field_names():
                if yaml.has(field_name, case_sensitive=False):
                    yaml.set(field_name, value, case_sensitive=False)
                    break

        return yaml

    @procedure("to delete or remove a (*yaml*)'s property")
    def delete_property(
        self, yaml: YAMLConcept, property: str | NounPhrase
    ) -> YAMLConcept:
        """
        Remove a property in a YAML concept

        Input Concepts:
            the yaml: The YAML concept which contains the property to be removed
            the yaml's property: The name of the property to be removed

        Output Concepts:
            the yaml: The updated YAML concept
        """
        yaml.delete(property)

        return yaml

    @procedure("to get a *yaml* as a (file)")
    def convert_to_file(self, yaml: YAMLConcept) -> IO:
        """
        Convert a YAML concept into a file

        Input Concepts:
            the yaml: The YAML concept

        Output Concepts:
            the file: The file containing the serialized YAML concept
        """
        return yaml.to_stream()

    @procedure("to get a file as a (*yaml*)")
    def convert_from_file(self, file: IO) -> YAMLConcept:
        """
        Convert a file into a YAML concept

        Input Concepts:
            the file: The file that contains the serialized YAML concept

        Output Concepts:
            the yaml: The YAML concept
        """
        return YAMLConcept.from_stream(file)

    @procedure("to merge a (*yaml*) to another *yaml*")
    def merge(self, yaml: YAMLConcept, another_yaml: YAMLConcept) -> YAMLConcept:
        """
        Merge two YAML concepts into a YAML concept.

        Input Concepts:
            the yaml: The first YAML concept
            another yaml: The second YAML concept

        Output Concepts:
            the yaml: The YAML concept that has been merged
        """
        always_merger.merge(yaml.value, another_yaml.value)

        return yaml
