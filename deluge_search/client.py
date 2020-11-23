import uuid
import subprocess
import os

from shell import shell
from deluge_client import DelugeRPCClient

from .torrent import Torrent


class DelugeClient:
    def __init__(self, host="", port=58846, username="", password=""):
        self.client = DelugeRPCClient(
            host,
            port,
            username,
            password,
        )
        self.client.connect()
        if not self.client.connected:
            raise RuntimeError("Failed to connect to deluge rpc")

    def get_torrents(self, keys=[]) -> list[Torrent]:
        torrents = []

        if "name" in keys:
            keys.remove("name")

        torrents_status = self.client.call(
            "core.get_torrents_status", {}, ["name"] + keys
        )
        for id in torrents_status:
            torrent_data = {}
            for (key, value) in torrents_status[id].items():
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

    def fuzzy_search(self, query, completed=True) -> bool:
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
            return False

        for torrent in torrents:
            if torrent.id == selected_id:
                selected_torrent = torrent

        selected_torrent.print()
        return True
