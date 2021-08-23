# ePread

Touch-friendly, distraction-free, ePub reader for desktop.

- Both Touch-friendly and Keyboard-driven.
- Distraction-free and minimal UI.
- Dark mode.
- User-injectable CSS.
- User-injectable JavaScript.
- System tray icon to, optionally, close to.

Also
- Remembers the last opened page and other preferences (position in page, dark mode, zoom, etc) per ePub file.
- And supports forgetting everything about the book before quitting.

Written in Python 3 using Qt 5 (PyQt5) and QtWebEngine (Blink-based, the same web engine as Chrome).

You can launch it from the GUI or CLI.


## Installation

1. Install the dependencies; they are: `python3` and `git` using your system's package manager, and `PyQt5` and `PyQtWebEngine` from PyPI.

    On a Debian or Ubuntu system, they are installed with:

    ```
    sudo apt install python3-pip git
    ```

    Then

    ```
    python3 -m pip install --user --upgrade pip
    python3 -m pip install --user --upgrade PyQt5 PyQtWebEngine
    ```

2. Install ePread:

    If you want to install to the user only (no root needed):

    ```
    mkdir -p ~/.local/bin
    git clone --depth 1 https://github.com/noureddin/epread ~/.epread
    ln -s ~/.epread/epread ~/.local/bin/
    ln -s ~/.epread/epread.desktop ~/.local/share/applications/
    ```

## Update

If you followed the steps in the Installation section exactly, you could update ePread with the following command:

```
cd ~/.epread && git pull
```

## Uninstallation

If you followed the steps in the Installation section exactly, you could uninstall ePread with the following command:

```
rm ~/.local/bin/epread ~/.local/share/applications/epread.desktop ~/.epread -fr
```


## Keyboard Interface

(Also check the file: `~/.local/share/epread/keys`, and modify it as you see fit.)

- `Ctrl+Q`, `Ctrl+W`, or `Ctrl+F4`: exit
- `Right Arrow`: next page
- `Left Arrow`: previous page
- `Alt+Home`: First page (usually the cover)
- `Alt+End`: Last page (usually the end cover)
- `Alt+Left` or `Ctrl+H`: back (if you followed an internal link)
- `Alt+Right` or `Ctrl+L`: forward (if you followed an internal link)
- `Ctrl++`: zoom in
- `Ctrl+-`: zoom out
- `Ctrl+0`: reset zoom
- `Shift+Ctrl+I`: invert colors
- `Shift+Ctrl+S`: show custom css dialog
- `Ctrl+F` or `/`: show find in page dialog
- `F3` or `Ctrl+G`: find next
- `Shift+F3` or `Shift+Ctrl+G`: find previous
- `Shift+Ctrl+H`: clear matches
- `Shift+Ctrl+M`: close to the system tray icon
- `Ctrl+P`: save current page as PDF 


## License

Apache License, Version 2.

Copyright 2021 Noureddin.
