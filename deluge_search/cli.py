import os
import subprocess
import uuid
import json

import click
from shell import shell

from .client import DelugeClient
from .ctx import Context
from .torrent import Torrent


def search(ctx: Context) -> list[Torrent]:
    filter_str = ctx.settings["filter_str"]
    filter = {}

    if filter_str:
        filter_list = filter_str.split(";;;")
        for filter_str in filter_list:
            filter_parts = filter_str.split("=")
            filter[filter_parts[0]] = filter_parts[1]

    return ctx.client.search(filter)


def process_results(ctx: Context, results: list[Torrent]):

    if not len(results):
        exit(1)

    print_results(ctx, results)

    label = ctx.settings["set_label"]
    if not label:
        return

    ensure_label(ctx, label)
    set_results_label(ctx, results, label)


def print_results(ctx: Context, results: list[Torrent]):
    if not ctx.settings["quiet"]:
        result_json = []
        for result in results:
            result_json.append(result.__dict__)
        tmp_filename = f"/tmp/deluge-search-{uuid.uuid4()}"
        tmp_file = open(tmp_filename, "w")
        tmp_file.write(json.dumps(result_json))
        tmp_file.close()
        subprocess.call(f"jq . {tmp_filename}", shell=True)
        os.remove(tmp_filename)


def ensure_label(ctx: Context, label: str):
    labels = ctx.client.get_labels()
    if label not in labels:
        if click.confirm(f"Label `{label}` does not exist. Do you want to create it?"):
            ctx.client.rpc.call("label.add", label)
        else:
            click.echo("Exiting without applying label.")
            exit(1)


def set_results_label(ctx: Context, results: list[Torrent], label: str):
    for result in results:
        click.echo(f"Applying label `{label}` to {result.name}.")
        ctx.client.rpc.call("label.set_torrent", result.id, label)
    click.echo(f"Label {label} applied.")


@click.group()
@click.pass_context
@click.option(
    "--quiet",
    is_flag=True,
    default=False,
    help="Don't print the selected torrent",
)
@click.option(
    "--filter",
    default="",
    help="triple semicolon separated list of filter values in the format key=value",
)
@click.option(
    "--set-label",
    default=None,
    help="set the label of the results",
)
def cli(click_ctx, quiet, filter, set_label: str):

    client = DelugeClient(
        os.environ.get("DELUGE_RPC_HOST"),
        int(os.environ.get("DELUGE_RPC_PORT")),
        os.environ.get("DELUGE_RPC_USERNAME"),
        os.environ.get("DELUGE_RPC_PASSWORD"),
    )
    click_ctx.obj = Context(
        "deluge-tool",
        client,
        {
            "quiet": quiet,
            "filter_str": filter,
            "set_label": set_label,
        },
    )


@cli.command()
@click.pass_context
def torrents(click_ctx):
    ctx: Context = click_ctx.obj
    results = search(ctx)
    process_results(ctx, results)


@cli.command()
@click.pass_context
@click.argument("query", default="")
def fzf(click_ctx, query: str):
    ctx: Context = click_ctx.obj
    results = search(ctx)
    results = ctx.client.fuzzy_select(results, query)
    process_results(ctx, results)
