"""
Get song info.
"""
import shutil
import os
import mpd

from . import brainz
from . import util


def init(port=6600, server="localhost"):
    """Initialize mpd."""
    client = mpd.MPDClient()

    try:
        client.connect(server, port)
        return client

    except ConnectionRefusedError:
        print("error: Connection refused to mpd/mopidy.")
        os._exit(1)  # pylint: disable=W0212


def get_art(cache_dir, size, default_cover, client):
    """Get the album art."""
    song = client.currentsong()

    if len(song) < 2:
        print("album: Nothing currently playing.")
        if default_cover:
            shutil.copy(default_cover, cache_dir / "current.jpg")
            return

        util.bytes_to_file(util.default_album_art(), cache_dir / "current.jpg")
        return

    file_name = f"{song['artist']}_{song['album']}_{size}.jpg".replace("/", "")
    file_name = cache_dir / file_name

    if file_name.is_file():
        shutil.copy(file_name, cache_dir / "current.jpg")

    else:

        brainz.init()
        album_art = brainz.get_cover(song, size)

        if not album_art and default_cover:
            shutil.copy(default_cover, cache_dir / "current.jpg")
        elif not album_art and not default_cover:
            album_art = util.default_album_art()

        if album_art:
            util.bytes_to_file(album_art, cache_dir / "current.jpg")
            util.bytes_to_file(album_art, file_name)

    print(cache_dir / "current.jpg")
