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
@click.option(
    "--quiet",
    "quiet",
    default=False,
    help="Don't print the selected torrent",
)
@click.argument("query", default="")
@click.argument("label", default="")
def fuzzy(click_ctx, completed, quiet, query, label):
    ctx: Context = click_ctx.obj
    torrent = ctx.client.fuzzy_search(query, completed)
    if not torrent:
        exit(1)
    if not quiet:
        torrent.print()

    if not label:
        return

    labels = ctx.client.get_labels()
    if label not in labels:
        if click.confirm(f"Label `{label}` does not exist. Do you want to create it?"):
            ctx.client.rpc.call("label.add", label)
        else:
            click.echo("Exiting without applying label.")
            exit(1)

    ctx.client.rpc.call("label.set_torrent", torrent.id, label)
