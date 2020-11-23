import os


from .client import DelugeClient


def main():
    client_args = {
        "host": os.environ.get("DELUGE_RPC_HOST"),
        "port": int(os.environ.get("DELUGE_RPC_PORT")),
        "username": os.environ.get("DELUGE_RPC_USERNAME"),
        "password": os.environ.get("DELUGE_RPC_PASSWORD"),
    }
    tool = DelugeClient(client_args)
    tool.get_torrents()


if __name__ == "__main__":
    main()
