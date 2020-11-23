import uuid
import subprocess
import os
from typing import Optional

from shell import shell
from deluge_client import DelugeRPCClient

from .torrent import Torrent


def filter_torrent(torrent, filter_dict):
    torrent_dict = torrent.__dict__
    for filter_key in filter_dict:
        filter_value = str(filter_dict[filter_key])
        torrent_value = str(torrent_dict[filter_key])
        if torrent_value != filter_value:
            return False
    return True


class DelugeClient:
    def __init__(self, host="", port=58846, username="", password=""):
        self.filter = {}
        self.rpc = DelugeRPCClient(
            host,
            port,
            username,
            password,
        )
        self.rpc.connect()
        if not self.rpc.connected:
            raise RuntimeError("Failed to connect to deluge rpc")

    def get_labels(self):
        labels = []
        results = self.rpc.call("label.get_labels")
        for result in results:
            labels.append(result.decode("utf-8"))
        return labels

    def search(self, filter_dict={}) -> list[Torrent]:
        results = []
        keys = ["name", "label", "progress", "save_path"]
        for filter_key in filter_dict.keys():
            if not filter_key in keys:
                keys.append(filter_key)

        torrents = self.rpc.call(
            "core.get_torrents_status",
            {},
            keys,
        )
        for id in torrents:
            torrent_data = {}
            for (key, value) in torrents[id].items():
                data_key = key.decode("utf-8")
                data_value = value

                try:
                    data_value = value.decode("utf-8")
                except (UnicodeDecodeError, AttributeError):
                    pass

                torrent_data[data_key] = data_value

            results.append(Torrent(id, torrent_data))

        return list(filter(lambda x: filter_torrent(x, filter_dict), results))

    def fuzzy_select(self, results: list[Torrent], query="") -> list[Torrent]:
        lines = []
        for result in results:
            lines.append(f"{result.id};;;{result.name};;;label: {result.label}")
        search_uuid = uuid.uuid4()
        search_filename = f"/tmp/deluge-search-{search_uuid}.tmp"
        output_filename = f"{search_filename}.out"
        search_file = open(search_filename, "w")
        search_file.write("\n".join(lines))
        search_file.close()
        cmd = f'cat {search_filename} | fzf --multi --delimiter=";;;" --with-nth=2.. --nth=1 --query="{query}" > {output_filename}'
        subprocess.call(cmd, shell=True)

        output_file = open(output_filename, "r")
        output = output_file.read()
        os.remove(search_filename)
        os.remove(output_filename)

        selected_ids = []
        selected_torrents = []
        output_lines = output.split("\n")
        for output_line in output_lines:
            selected_ids.append(output_line.split(";;;")[0])

        for selected_id in selected_ids:
            for result in results:
                if result.id == selected_id:
                    selected_torrents.append(result)

        return selected_torrents
