# modrinth_mod_update

Python script for updating your Minecraft mods from Modrinth. No external modules required.

### Features:

- Stores mod info as .json file (and detects if one already exists in the same folder as script)
- Checks for newer version from Modrinth and compares version to installed mods
- Downloads newer versions if detected
- SHA1 checksum for file integrity
- Supports command line arguments (*wow!*)

### Usage:

There are no external Python modules to install, only uses built-in libraries. Just install Python 3
on your computer, and run it through a terminal or command prompt. Has only been tested on Linux,
Python 3.13.5. I haven't tested on Windows or macOS, but should theoretically be platform independent.

You can use `mod_update.py --help` for the help message.

## Detecting and creating a `.json` file

This detects whether an existing `.json` file exists. If not, then it'll ask for what folder your mods
are in, and creates a `.json` file to cache for faster and easier use, and which you can specify the
name of in the command.

`python mod_update.py --detect mods.json`

You can even use paths like `/home/username/Downloads/mods.json` or even `~/Downloads/mods.json` to
specify your `.json` file! Really high tech, I know.

## Checking for updates

Assuming a `.json` file for your mods exists, you can specify it with the command below. It checks for
the mods present in the file, then checks Modrinth for a newer version. If newer ones are detected, it
downloads the file, verifies its integrity with a checksum, and replaces the old mod.

`python mod_update.py --check mods.json`

## Reporting bugs

Make a pull request at this repository's [GitHub Issues](https://github.com/Rerence1016/modrinth_mod_update/issues).
Provide a detailed description of:

- What you were trying to do
- What doesn't work
- Python version
- OS and version
- A screenshot or `.txt` of the error or bug