"""Submodule containing the CLI command handlers."""

import logging
import sys
from main import MainApp as main_serivce
from authenticator import AuthenticatorService

def setup_logging():
    """Configure the logging."""
    logging.basicConfig(level=logging.DEBUG)


def main_service():
    """Handles the `mainservice` CLI command."""
    setup_logging()
    logging.info("Main service starting...")
    sys.exit(main_service().main(sys.argv))


def catalog_service():
    """Handles the `catalogservice` CLI command."""
    print("Catalog service")
    sys.exit(0)


def streamprovider_service():
    """Handles the `streamingservice` CLI command."""
    print("Streaming service")
    sys.exit(0)


def authentication_service():
    """Handles the `authenticationservice` CLI command."""
    print("Authentication service")
    return AuthenticatorService().main(sys.argv)


def client():
    """Handles the IceFlix client CLI command."""
    print("Starting IceFlix client...")
    sys.exit(0)
