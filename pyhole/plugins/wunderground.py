#   Copyright 2010-2015 Josh Kearney
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""Pyhole Wunderground Plugin"""

import pywunderground

from pyhole.core import plugin
from pyhole.core import utils


class Wunderground(plugin.Plugin):
    """Provide access to current weather data."""

    @plugin.hook_add_command("weather")
    @utils.spawn
    def weather(self, message, params=None, **kwargs):
        """Display current weather report (ex: .w [set] [<location>])"""
        wunderground = utils.get_config("Wunderground")
        api_key = wunderground.get("key")

        if params:
            location = params
            if location.startswith("set "):
                location = location[4:]
                utils.write_file(self.name, message.source, location)
                message.dispatch("Location information saved.")
        else:
            location = utils.read_file(self.name, message.source)
            if not location:
                message.dispatch(self.weather.__doc__)
                return

        try:
            w = pywunderground.request(api_key, ["conditions"], location)
        except Exception:
            message.dispatch("Unable to fetch Wunderground data.")
            return

        if "current_observation" in w:
            w = w["current_observation"]

            city = w["display_location"]["full"]
            zip_code = w["display_location"]["zip"]
            temp = w["temperature_string"]
            humidity = w["relative_humidity"]
            wind = w["wind_string"]
            condition = w["weather"]

            zip_code = "" if zip_code == "00000" else " %s" % zip_code
            humidity = "N/A%" if len(humidity) > 3 else humidity

            result = "%s%s: %s   Humidity: %s   Wind: %s   %s" % (city,
                                                                  zip_code,
                                                                  temp,
                                                                  humidity,
                                                                  wind,
                                                                  condition)
            message.dispatch(result)
        else:
            message.dispatch("Location not found: '%s'" % location)

    @plugin.hook_add_command("w")
    def alias_w(self, message, params=None, **kwargs):
        """Alias of weather."""
        self.weather(message, params, **kwargs)
