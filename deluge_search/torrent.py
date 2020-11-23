class Torrent:
    def __init__(self, id, torrent_data={}):
        self.id = id.decode("utf-8")

        if not torrent_data["name"]:
            raise ValueError("invalid torrent, no name")

        for key in torrent_data:
            setattr(self, key, torrent_data[key])

    def print(self):
        torrent_data = self.__dict__
        for key in torrent_data:
            print(f"{key}: {torrent_data[key]}")
