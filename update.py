#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Loopia DNS update client

This application is for educational purposes only.
Do no evil, do not break local or internation laws!
By using this code, you take full responisbillity for your actions.
The author have granted code access for educational purposes and is
not liable for any missuse.
"""
__author__ = "Jonas Werme"
__copyright__ = "Copyright (c) 2021 Jonas Werme"
__credits__: list = ["nsahq"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Jonas Werme"
__email__ = "jonas[dot]werme[at]hoofbite[dot]com"
__status__ = "Prototype"

import xmlrpc.client
import sys

from requests import get

from config import yaml_config_to_dict
from logger import get_logger


def clean_records(config: dict, domain: str, subdomain: str, zone_records) -> int:
    """Remove all A records except the first one"""

    count = 0
    for record in zone_records:
        status = client.removeZoneRecord(
            config["username"],
            config["password"],
            domain,
            subdomain,
            record["record_id"],
        )

        if status == "OK":
            count += 1
        if count != len(zone_records):
            raise Exception("Unable to remove all zone records")

    return count


def get_ip():
    """Get public IP adress"""

    return get("https://api.ipify.org/").content.decode("utf8")

def get_ip6():
    """Get public IPv6 address"""

    return get("https://api6.ipify.org/").content.decode("utf8")


def get_records(config, domain: str, subdomain: str, record_type: list = ["A", "AAAA"]) -> list:
    """Get current records for a subdomain in a zone"""

    if not config or not domain:
        raise ValueError("Missing or invalid configuration parameters")

    try:
        zone_records: list = client.getZoneRecords(
            config["username"],
            config["password"],
            domain,
            subdomain
        )

        if "AUTH_ERROR" in zone_records:
            raise ConnectionError(
                "UNAUTHORIZED: Unable to authenticate. Please check your user/pass."
            )

        # Quit if API returns unknown error
        if "UNKNOWN_ERROR" in zone_records:
            raise ConnectionAbortedError(
                "UNKNOWN ERROR: Could not process request or requested (sub)domain does not exist"
                " in this account."
            )

        return [d for d in zone_records if d["type"] in record_type]

    except xmlrpc.client.Error:
        raise


def add_record(config: dict, domain: str, subdomain: str, ip: str, record_type: str = "A") -> bool:
    """Add a new A record to a subdomains in a zone"""

    if not config or not domain or not subdomain or ip == "":
        raise ValueError("Missing or invalid configuration parameters")

    new_record = {
        "priority": "",
        "rdata": ip,
        "type": record_type,
        "ttl": config.get("ttl", 3600),
    }

    try:
        status = client.addZoneRecord(
            config["username"],
            config["password"],
            domain,
            subdomain,
            new_record,
        )
        if status == "OK":
            return True

        raise Exception("Unable to add a new record")
    except xmlrpc.client.Error:
        raise


def update_record(config: dict, domain: str, subdomain: str, ip: str, record: dict) -> int:
    """Update an existing A record for a subdomain in a zone"""

    if record["rdata"] == ip and int(record["ttl"]) == int(config["ttl"]):
        return False
    new_record = {
        "priority": record["priority"],
        "record_id": record["record_id"],
        "rdata": ip,
        "type": record["type"],
        "ttl": config["ttl"],
    }

    try:
        status = client.updateZoneRecord(
            config["username"],
            config["password"],
            domain,
            subdomain,
            new_record,
        )

        if status == "OK":
            return True

        raise Exception("Unable to perform update action")

    except xmlrpc.client.Error:
        raise


if __name__ == "__main__":
    cfg_file = 'config.yml'
    if len(sys.argv) > 1:
        cfg_file = sys.argv[1]

    try:
        cfg = yaml_config_to_dict(expected_keys=["username", "password", "domain", "subdomains"], config_file=cfg_file)
        log = get_logger(
            name=__name__,
            log_level_console=cfg["log_level_console"],
            log_level_file=cfg["log_level_file"],
            log_file=cfg["log_file"]
        )

        log.debug("Configuration and logging initialized")

        client = xmlrpc.client.ServerProxy(uri="https://api.loopia.se/RPCSERV", encoding="utf-8")
        log.debug("Client initialized")

        ipv4 = get_ip()
        ipv6 = get_ip6()
        log.debug(f"Current public ip is {ipv4} / {ipv6}")

        for subdomain in cfg['subdomains']:
            for record_type in ["A", "AAAA"]:
                new_ip = ipv6 if record_type == "AAAA" else ipv4
                fqdn = cfg["domain"] if subdomain == "@" else f"{subdomain}.{cfg['domain']}"

                a_records = get_records(cfg, cfg['domain'], subdomain, record_type=[record_type])
                log.debug(f"Found {len(a_records)} {record_type} records in {fqdn}.")
                try:
                    if len(a_records) > 1:
                        count_removed = clean_records(cfg, cfg['domain'], subdomain, a_records[1:])
                        log.info(f"Cleaned up {count_removed} {record_type} records in {fqdn}")

                    elif len(a_records) == 0:
                        if add_record(cfg, cfg['domain'], subdomain, new_ip, record_type):
                            log.info(f"Added a new {record_type} record for {new_ip} in {fqdn}")
                        else:
                            log.critical(f"Unable to create {record_type} record in {fqdn}, exiting")
                            exit(2)

                    else:
                        if update_record(cfg, cfg['domain'], subdomain, new_ip, a_records[0]):
                            log.info(f"Updated the {record_type} record for {new_ip} in {fqdn}")
                        else:
                            log.info(f"A records for {fqdn} already up to date")
                except Exception as e:
                    log.critical(e)
                    raise
    except Exception as e:
        exit(f"{e}")
