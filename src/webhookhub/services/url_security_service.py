import ipaddress
from urllib.parse import urlparse
import socket


def validate_webhook_hostname(hostname: str) -> None:
    try:
        addresses = socket.getaddrinfo(
            hostname,
            None,
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror:
        raise ValueError(
            "Webhook hostname could not be resolved"
        )

    for address in addresses:
        ip_address = address[4][0]

        ip = ipaddress.ip_address(ip_address)

        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        ):
            raise ValueError(
                "Webhook hostname resolves to a private or internal IP"
            )


def validate_webhook_url(url: str) -> None:
    parsed = urlparse(url)

    if parsed.scheme != "https":
        raise ValueError(
            "Webhook URL must use HTTPS"
        )

    if not parsed.hostname:
        raise ValueError(
            "Webhook URL must contain a hostname"
        )

    hostname = parsed.hostname.lower()

    if hostname == "localhost":
        raise ValueError(
            "Webhook URL cannot point to localhost"
        )

    try:
        ip = ipaddress.ip_address(hostname)
    except ValueError:
        validate_webhook_hostname(hostname)
        return

    if (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    ):
        raise ValueError(
            "Webhook URL cannot point to a private or internal IP"
        )