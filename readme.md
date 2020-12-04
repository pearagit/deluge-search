# deluge-tool

A command line tool to search, move, and label your deluge torrents using FZF.

Requires FZF to be installed and in your PATH.

## Usage

```
Usage: deluge-search [OPTIONS] COMMAND [ARGS]...

Options:
  --quiet           Don't print the selected torrent
  --filter TEXT     triple semicolon separated list of filter values in the
                    format key=value

  --set-label TEXT  set the label of the results
  --help            Show this message and exit.

Commands:
  fzf
  move-torrents
  torrents
```
