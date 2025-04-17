# Snapify 📸

A lightweight, asynchronous Python script to download Snapchat Stories for one or more users—either as a one‑off or continuously in monitor mode. Media files are neatly organized into per‑user subfolders.

---

## Features

- **Multi‑user support**: Specify multiple Snapchat usernames via a comma‑separated list.
- **One‑off downloads**: Fetch all current public Story media for given users.
- **Monitor mode**: Continuously poll for new media at a configurable interval.
- **Per‑user folders**: Automatically create subdirectories for each username under your base download directory.
- **Persistent state**: Tracks downloaded URLs in a JSON file to avoid re‑downloading.
- **Colored, tabulated output**: Visual feedback with `pystyle` and `tabulate` for easy monitoring and logs.

## Prerequisites

- **Python**: 3.8 or newer
- **Pip**: For installing dependencies

Install required packages:

```bash
pip install aiohttp aiofiles pystyle tabulate
```

> Alternatively, you can create a `requirements.txt`:
>
> ```txt
> aiohttp
> aiofiles
> pystyle
> tabulate
> ```
>
> and run:
>
> ```bash
> pip install -r requirements.txt
> ```

## Usage

Clone or download this repository and run:

```bash
python snapify.py -u user1,user2,... [options]
```

### Arguments

| Flag            | Description                                                                                 | Default        |
|-----------------|---------------------------------------------------------------------------------------------|----------------|
| `-u, --user`    | **(Required)** Comma‑separated Snapchat username(s) to fetch.                                | —              |
| `-d, --directory` | Base directory to store downloads. Subfolders are created per user.                       | `snap_media`   |
| `-m, --monitor` | Enable continuous monitoring mode (runs until interrupted).                                 | off            |
| `--interval`    | Polling interval in minutes when running in monitor mode.                                   | `2`            |
| `--json`        | Path to JSON state file tracking downloaded URLs.                                           | `autoposts.json` |
| `--debug`       | Enable debug logs (prints each downloaded file path in real time).                          | off            |

### Examples

1. **One‑off download** of user `loren` into default folder:

   ```bash
   python snapify.py -u loren
   ```

2. **Download multiple users** (`alice`, `bob`) into a custom folder:

   ```bash
   python snapify.py -u alice,bob -d my_snaps
   ```

   This creates:
   ```text
   my_snaps/
   ├── alice/
   │   └── <media files>
   └── bob/
       └── <media files>
   ```

3. **Monitor mode** every 5 minutes, with debug output:

   ```bash
   python snapify.py -u alice,bob -m --interval 5 --debug
   ```

4. **Custom JSON state file**:

   ```bash
   python snapify.py -u alice -m --json state.json
   ```

## JSON State File

By default, downloads are tracked in `autoposts.json`. The format is:

```json
{
  "alice": [
    "https://cf-st.sc-cdn.net/d/...",
    "https://cf-st.sc-cdn.net/d/..."
  ],
  "bob": [
    "https://cf-st.sc-cdn.net/d/..."
  ]
}
```

Change the `--json` path to customize its location or filename.

## Troubleshooting

- **Missing dependencies**: Ensure all packages are installed (`aiohttp`, `aiofiles`, `pystyle`, `tabulate`).
- **No story data found**: Make sure the username is correct and the story is public.
- **Permission errors**: Check that your user has write access to the download directory.

## Contributing

Feel free to submit issues or pull requests for enhancements—such as notification hooks, alternative output formats, or GUI wrappers.

## License

MIT © Snapify

