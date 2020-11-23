import os

import click

from .client import DelugeClient
from .ctx import Context


@click.group()
@click.pass_context
def cli(click_ctx):

    client = DelugeClient(
        os.environ.get("DELUGE_RPC_HOST"),
        int(os.environ.get("DELUGE_RPC_PORT")),
        os.environ.get("DELUGE_RPC_USERNAME"),
        os.environ.get("DELUGE_RPC_PASSWORD"),
    )
    click_ctx.obj = Context("deluge-tool", client)


@cli.command()
@click.pass_context
@click.option(
    "--completed",
    "completed",
    flag_value=True,
    default=True,
    help="only search compeleted torrents",
)
@click.argument("query", default="")
def fuzzy(click_ctx, query, completed):
    ctx: Context = click_ctx.obj
    success = ctx.client.fuzzy_search(query, completed)
    if not success:
        exit(1)
