import uuid
import subprocess
import os
from typing import Optional

from shell import shell
from deluge_client import DelugeRPCClient

from .torrent import Torrent


class DelugeClient:
    def __init__(self, host="", port=58846, username="", password=""):
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

    def get_torrents(self, keys=[]) -> list[Torrent]:
        torrents = []

        if "name" in keys:
            keys.remove("name")

        results = self.rpc.call("core.get_torrents_status", {}, ["name"] + keys)
        for id in results:
            torrent_data = {}
            for (key, value) in results[id].items():
                data_key = key.decode("utf-8")
                data_value = value

                try:
                    data_value = value.decode("utf-8")
                except (UnicodeDecodeError, AttributeError):
                    pass

                torrent_data[data_key] = data_value

            torrent = Torrent(id, torrent_data)
            torrents.append(torrent)

        return torrents

    def fuzzy_search(self, query, completed=True) -> Optional[Torrent]:
        torrents = self.get_torrents(["save_path", "progress"])
        lines = []
        for torrent in torrents:
            if completed and torrent.progress != 100.0:
                continue
            lines.append(f"{torrent.id};;;{torrent.name}")
        search_uuid = uuid.uuid4()
        search_filename = f"/tmp/deluge-search-{search_uuid}.tmp"
        output_filename = f"{search_filename}.out"
        search_file = open(search_filename, "w")
        search_file.write("\n".join(lines))
        search_file.close()
        cmd = f'cat {search_filename} | fzf --delimiter=";;;" --with-nth=2.. --query="{query}" > {output_filename}'
        subprocess.call(cmd, shell=True)

        output_file = open(output_filename, "r")
        output = output_file.read()
        os.remove(search_filename)
        os.remove(output_filename)
        selected_id = output.split(";;;")[0]

        if not selected_id:
            return None

        for torrent in torrents:
            if torrent.id == selected_id:
                selected_torrent = torrent

        return selected_torrent
