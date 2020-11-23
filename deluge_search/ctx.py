import click

from .client import DelugeClient


class Context:
    def __init__(self, app_name: str, client: DelugeClient):
        self.app_name = app_name
        if not self.app_name:
            raise ValueError("app_name must not be empty")
        self.config_dir = click.get_app_dir(self.app_name)

        self.client = client
