"""
A short description of the project.
"""

import logging
import os
from typing import Optional
from urllib.parse import quote

import requests
from kognitos.bdk.api import NounPhrase
from kognitos.bdk.decorators import book, config, connect, procedure
from requests import HTTPError

OPENWEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
DEFAULT_TIMEOUT = 30

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@book(name="Open Weather", icon="data/icon.svg")
class OpenWeatherBook:
    """
    OpenWeather book enables users to fetch real-time temperature data for any city worldwide via the OpenWeather API.

    OpenWeather provides comprehensive weather data services, including current, forecast, and historical weather
    information. Explore a wide range of APIs for solar radiation, road risk assessment, solar energy prediction,
    and more, with global coverage and user-friendly access. Ideal for developers and businesses seeking accurate and
    reliable weather insights.

    Author:
        Kognitos, Inc.
    """

    def __init__(self):
        """
        Initializes an instance of the class.
        """
        self._base_url = OPENWEATHER_BASE_URL
        self._api_key = None
        self._timeout = float(DEFAULT_TIMEOUT)

    @property
    @config(default_value=DEFAULT_TIMEOUT)
    def timeout(self) -> float:
        """
        Timeout in seconds when making API calls to OpenWeather
        """
        return self._timeout

    @timeout.setter
    def timeout(self, timeout: float):
        """
        Sets the timeout value in seconds.
        """
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self._timeout = timeout

    @connect(noun_phrase="api keys")
    def connect(self, api_key: str):
        """
        Authenticate to Open Weather API using the specified API key. You can obtain you own API key by visiting
        Open Weahter's website at https://openweathermap.org/appid.

        Arguments:
            api_key: The API key to be used for connecting

        Labels:
            api_key: API Key
        """
        api_key = os.getenv("API_KEY", api_key)
        test_url = f"{self._base_url}?appid={api_key}&q=London"
        response = requests.get(test_url, timeout=self._timeout)
        if response.status_code == 401:
            response_data = response.json()
            if "Invalid API key" in response_data.get("message", ""):
                raise ValueError("Invalid API key")

        self._api_key = api_key

    @procedure("to get the (current temperature) at a city")
    def current_temperature(
        self, city: NounPhrase, unit: Optional[NounPhrase] = NounPhrase("standard")
    ) -> float:
        """Fetch the current temperature for a specified city.

        Input Concepts:
            the city: The name of the city. Please refer to ISO 3166 for the state codes or country codes.
            the unit: Unit of measurement. standard, metric and imperial units are available. If you do
                not specify the units, standard units will be applied by default.

        Output Concepts:
            the current temperature: The current temperature in the specified units of measurement, or None if an error occurs.

        Example 1:
            Retrieve the current temperature at London

            >>> get the current temperature at London

        Example 2:
            Retrieve the current temperature at London in Celsius

            >>> get the current temperature at Buenos Aires with
            ...     the unit is metric
        """
        complete_url = f"{self._base_url}?appid={self._api_key}&q={quote(str(city))}&units={str(unit) if unit else 'standard'}"
        try:
            logger.info("retrieving temperature for %s", str(city))
            response = requests.get(complete_url, timeout=self._timeout)
            response.raise_for_status()

            weather_data = response.json()

            temperature = weather_data["main"]["temp"]
            return temperature
        except requests.Timeout:
            logger.error("request timed out")
            raise
        except (requests.RequestException, HTTPError) as e:
            logger.error("error occurred: %s", e)
            raise
