import os
import subprocess
import uuid
import json

import click
from shell import shell

from .client import DelugeClient
from .ctx import Context
from .torrent import Torrent


@click.group()
@click.pass_context
@click.option(
    "--set-label",
    default=None,
    help="set the label of the results",
)
@click.option(
    "--quiet",
    default=False,
    help="Don't print the selected torrent",
)
def cli(click_ctx, set_label: str, quiet: bool):
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
            "set_label": set_label,
            "quiet": quiet,
        },
    )


@cli.command()
@click.pass_context
@click.argument("query", default="")
def fuzzy(click_ctx, query: str):
    ctx: Context = click_ctx.obj
    results = ctx.client.fuzzy_search(query)
    process_results(ctx, results)


@cli.command(epilog="filters in the format of `key=value`")
@click.pass_context
@click.argument("filters", nargs=-1)
def filter(click_ctx, filters: str):
    ctx: Context = click_ctx.obj
    filter = {}
    for filter_str in filters:
        filter_parts = filter_str.split("=")
        filter[filter_parts[0]] = filter_parts[1]
    results = ctx.client.filter(filter)

    process_results(click_ctx, results)


def process_results(ctx: Context, results: list[Torrent]):

    if not len(results):
        click.echo("Your search did not match any results.")
        exit(1)

    print_results(ctx, results)

    label = ctx.settings["set_label"]
    if not label:
        return

    ensure_label(ctx, label)
    set_results_label(ctx, results, label)


def print_results(ctx: Context, results: list[Torrent]):
    if not ctx.settings["quiet"]:
        results_json = []
        for result in results:
            results_json.append(result.__dict__)
        # output_filename = f"/tmp/deluge-search-{uuid.uuid4()}.tmp"
        # output_file = open(output_filename, "w")

        # output_file.write(json.dumps(results_json))
        # output_file.close()
        subprocess.call(f"echo '{json.dumps(results_json)}' | jq .[]", shell=True)
        # print(shell(f'echo "{json_str}" | jq --indent 2 -C').output())
        # click.echo(jq.compile(".").input(json_str).text())
        # click.echo(json.dumps(results_json, indent=2))

    # if not ctx.settings["output"]:
    #     for result in results:
    #         result.print()
    # elif ctx.settings["output"] == "json":
    #     results_json = []
    #     for result in results:
    #         results_json.append(result.__dict__)
    #     click.echo(json.dumps(results_json, indent=2))
    # elif ctx.settings["output"] == "paths":
    #     for result in results:
    #         click.echo(result.file_path)


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
