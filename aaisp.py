#!/usr/bin/env python3

# Core
import json
import logging
from urllib.parse import urljoin
# Third-party
import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout, \
    RequestException

# =========================================================================== #

logging.basicConfig(level=logging.INFO)

# =========================================================================== #

class CredentialsMissingError(Exception):
    pass
class APIError(Exception):
    pass

# =========================================================================== #

class AAISP:

    FORMAT_RAW    = 0
    FORMAT_MBYTES = 1
    FORMAT_GBYTES = 2
    FORMAT_MBITS  = 3
    FORMAT_GBITS  = 4

    # ----------------------------------------------------------------------- #

    def __init__(self, username, password):
        self.base_url = "https://chaos2.aa.net.uk/broadband/"
        self.username = username
        self.password = password
        self.params   = {
            'control_login': self.username,
            'control_password': self.password
        }
        self.stored_info = {}

    # ----------------------------------------------------------------------- #

    def _format_bytes(self, bytes_num: int, unit_format: int,
                      precision: int = 1) -> float:
        """
        Formats bit and byte counts in more useful units (Gbit/s, MB, etc.)

        Args:
            bytes_num[int]: The byte count to be formatted.
            unit_format[int]: The format flag specifying the desired unit.
            precision[int]: How many maximum decimal places to round it to.

        Returns:
            The byte count, formatted and rounded according to the arguments.
        """
        if unit_format == self.FORMAT_MBYTES:
            return round(bytes_num / 10000000, precision)
        elif unit_format == self.FORMAT_GBYTES:
            return round(bytes_num / 1000000000, precision)
        elif unit_format == self.FORMAT_MBITS:
            return round(bytes_num / 1000000, precision)
        elif unit_format == self.FORMAT_GBITS:
            return round(bytes_num / 1000000000, precision)
        else:
            return round(bytes_num, precision)

    # ----------------------------------------------------------------------- #

    def _get(self, endpoint: str, params: dict) -> dict:
        """
        Performs a CHAOS API request using the GET method.

        CHAOS API responses are in JSON format, and include the requested
        information with the key name matching the endpoint requested.

        Args:
            endpoint[str]: The CHAOS command to execute.
            params[dict]: Parameters or arguments for the CHAOS command.

        Returns:
            A dict containing the requested information from the API.
        """
        if not self.username or not self.password:
            logging.error("Username or password were not supplied!")
            raise CredentialsMissingError()
        
        full_url = urljoin(self.base_url, endpoint)
        
        if params:
            params.update(self.params)
        else:
            params = self.params

        try:
            response = requests.get(full_url, params=params)
            response.raise_for_status() 

            try:
                json_data = response.json()
                requested_info = json_data.get(endpoint)

                if not requested_info:
                    logging.debug("Couldn't find data dict in JSON response")
                    return None

                return requested_info

            except json.JSONDecodeError:
                logging.error("Response is not in JSON format.")

        except HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
        except ConnectionError as conn_err:
            logging.error(f"Error connecting: {conn_err}")
        except Timeout as timeout_err:
            logging.error(f"Timeout error: {timeout_err}")
        except RequestException as err:
            logging.error(f"Error: {err}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")

    # ----------------------------------------------------------------------- #

    def _get_info_attrib(self, service_id: int, key: str) -> str:
        """
        Retrieves an attribute for a specified line.

        If line information is cached, the attribute value will be retrieved
        from the cache. If not, an API request will be issued to retrieve the
        line information.

        Args:
            service_id[int]: The 5-digit numerical ID for the line.
            key[str]: The name of the attribute to be retrieved.

        Returns:
            str: The requested attribute value.
        """
        if service_id not in self.stored_info:
            logging.debug(f"Info not retrieved already for SID {service_id}!")
            self.info()
        else:
            logging.debug(f"Cached info available for SID {service_id}")

        value = self.stored_info[service_id].get(key)
        if not value:
            logging.error(f"Couldn't find {key} in response JSON!")
            raise APIError()

        return value

    # ----------------------------------------------------------------------- #

    def info(self) -> list:
        """
        Invokes the CHAOS 'info' command to retrieve all services and their
        respective information.

        Returns:
            A list containing a dict for each present service.
        """
        logging.debug(f"Retrieving all service info for user '{self.username}'")
        info = self._get('info', None)
        for service in info:
            self.stored_info[int(service['ID'])] = service
        return info

    # ----------------------------------------------------------------------- #
    
    def services(self) -> list:
        """
        Retrieves all service IDs for the given account.

        Returns:
            A list containing all service IDs, as integers.
        """
        if not self.stored_info:
            self.info()
        return list(self.stored_info.keys())
        
    # ----------------------------------------------------------------------- #

    def tx_rate(self, service_id: int, unit_format: int = 0,
                precision: int = 1) -> int:
        """
        Retrieves the TX (download) rate for a specified service.

        Args:
            service_id[int]: The 5-digit numerical ID for the line.
            unit_format[int]: A flag to specify the unit format desired.
            precision[int]: Maximum amount of decimal places.

        Returns:
            The TX (download) rate in bytes.
        """
        logging.debug("Retrieving TX rate for service {service_id}")
        rate = int(self._get_info_attrib(service_id, 'tx_rate'))
        return self._format_bytes(rate, unit_format, precision)
        
    # ----------------------------------------------------------------------- #

    def rx_rate(self, service_id: int, unit_format: int = 0,
                precision: int = 1) -> int:
        """
        Retrieves the RX (upload) rate for the specified line.

        Args:
            service_id[int]: The 5-digit numerical ID for the line.
            unit_format[int]: A flag to specify the unit format desired.
            precision[int]: Maximum amount of decimal places.

        Returns:
            The RX (upload) rate in bytes.
        """
        logging.debug("Retrieving RX rate for service {service_id}")
        rate = int(self._get_info_attrib(service_id, 'rx_rate'))
        return self._format_bytes(rate, unit_format, precision)
        
    # ----------------------------------------------------------------------- #

    def usage_remaining(self, service_id: int, unit_format: int = 0,
                        precision: int = 1) -> int:
        """
        Retrieves the quota usage remaining for the specified line.

        Args:
            service_id[int]: The 5-digit numerical ID for the line.
            unit_format[int]: A flag to specify the unit format desired.
            precision[int]: Maximum amount of decimal places.

        Returns:
            The quota remaining, in bytes.
        """

        logging.debug("Retrieving usage remaining for service {service_id}")
        remaining = int(self._get_info_attrib(service_id, 'quota_remaining'))
        return self._format_bytes(remaining, unit_format, precision)

    # ----------------------------------------------------------------------- #

    def usage_used(self, service_id: int, unit_format: int = 0,
                   precision: int = 1) -> int:
        """
        Retrieves the quota usage used for the specified line.

        Args:
            service_id[int]: The 5-digit numerical ID for the line.
            unit_format[int]: A flag to specify the unit format desired.
            precision[int]: Maximum amount of decimal places.

        Returns:
            The quota used, in bytes.
        """
        logging.debug("Retrieving usage used for service {service_id}")
        remaining  = int(self._get_info_attrib(service_id, 'quota_remaining'))
        total = int(self._get_info_attrib(service_id, 'quota_monthly'))
        return self._format_bytes(total - remaining, unit_format, precision)

    # ----------------------------------------------------------------------- #

    def login(self, service_id: int) -> str:
        """
        Retrieves the login string for the line.

        Args:
            service_id[int]: The 5-digit numerical ID for the line.

        Returns:
            The login username/string for the line.
        """
        logging.debug("Retrieving login for service {service_id}")
        return self._get_info_attrib(service_id, 'login')


# =========================================================================== #
