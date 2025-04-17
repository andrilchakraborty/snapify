import argparse
import asyncio
import aiohttp
import aiofiles
import os
import re
import json
import sys
from datetime import datetime
from tabulate import tabulate
from pystyle import Center, Colors, Colorate, Write

# Title for the tool
TOOL_TITLE = "Snapify"


def load_autopost_data(json_path):
    if os.path.isfile(json_path):
        with open(json_path, 'r') as f:
            return json.load(f)
    return {}


def save_autopost_data(data, json_path):
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)


async def get_json(session, username):
    url = f"https://story.snapchat.com/@{username}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    async with session.get(url, headers=headers) as resp:
        if resp.status == 404:
            return None
        text = await resp.text()
        match = re.search(r"<script id=\"__NEXT_DATA__\" type=\"application/json\">(.+?)</script>", text)
        if not match:
            return None
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return None


async def download_media(session, url, save_dir, debug=False):
    os.makedirs(save_dir, exist_ok=True)
    fname = re.sub(r'[<>:"/\\|?*]', '', url.split('/')[-1])
    async with session.get(url) as resp:
        if resp.status == 200:
            ct = resp.headers.get('Content-Type', '')
            ext = '.jpg' if 'image' in ct else '.mp4' if 'video' in ct else ''
            path = os.path.join(save_dir, fname + ext)
            async with aiofiles.open(path, 'wb') as f:
                while chunk := await resp.content.read(1024):
                    await f.write(chunk)
            if debug:
                Write.Print(f"[DEBUG] Downloaded: {path}\n", Colors.green)
            return path
    return None


async def check_new_media(usernames, base_dir, data, json_path, debug):
    async with aiohttp.ClientSession() as session:
        table_rows = []
        for user in usernames:
            user_dir = os.path.join(base_dir, user)
            last = set(data.get(user, []))
            js = await get_json(session, user)
            if not js or 'props' not in js or 'pageProps' not in js['props']:
                Write.Print(f"{user}: No story data found.\n", Colors.red)
                continue
            snaps = js['props']['pageProps']['story'].get('snapList', [])
            media_urls = [s['snapUrls']['mediaUrl'] for s in snaps]
            new = [u for u in media_urls if u not in last]
            downloaded = []
            for url in new:
                path = await download_media(session, url, user_dir, debug)
                if path:
                    downloaded.append(path)
            data[user] = list(last.union(new))
            status_msg = f"{len(downloaded)} new" if downloaded else "0 new"
            color = Colors.green if downloaded else Colors.yellow
            Write.Print(f"{user}: {status_msg} media downloaded.\n", color)
            table_rows.append([user, len(new), datetime.now().strftime('%Y-%m-%d %H:%M:%S')])

        save_autopost_data(data, json_path)

        if table_rows:
            # Build and display table with title
            title = Center.XCenter(Colorate.Horizontal(Colors.cyan_to_blue, f" {TOOL_TITLE} " ))
            headers = [f"{TOOL_TITLE} User", "New Items", "Checked At"]
            table = tabulate(table_rows, headers=headers, tablefmt="fancy_grid", stralign="center")
            centered = Center.XCenter(Colorate.Vertical(Colors.green_to_white, table))
            print("\n" + title + "\n" + centered + "\n")


def main():
    # Print centered title
    print(Center.XCenter(Colorate.Vertical(Colors.green_to_white, f"*** {TOOL_TITLE} ***")))
    parser = argparse.ArgumentParser(prog=TOOL_TITLE.lower(), description="Download Snapchat stories")
    parser.add_argument(
        "-u", "--user",
        type=str,
        required=True,
        help="Comma-separated Snapchat username(s)"
    )
    parser.add_argument("-d", "--directory", default="snap_media", help="Base download directory")
    parser.add_argument("-m", "--monitor", action="store_true", help="Continuously monitor snapshots")
    parser.add_argument("--json", dest="jsonfile", default="autoposts.json", help="Autopost JSON state file")
    parser.add_argument("--interval", type=int, default=2, help="Monitor interval in minutes")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    args = parser.parse_args()

    usernames = [u.strip() for u in args.user.split(',') if u.strip()]
    if not usernames:
        Write.Print("No valid usernames provided.\n", Colors.red)
        sys.exit(1)

    data = load_autopost_data(args.jsonfile)

    if args.monitor:
        async def monitor_loop():
            try:
                while True:
                    await check_new_media(usernames, args.directory, data, args.jsonfile, args.debug)
                    next_time = datetime.now().strftime("%H:%M:%S")
                    Write.Print(f"Waiting {args.interval} minutes... [{next_time}]\n", Colors.yellow)
                    await asyncio.sleep(args.interval * 60)
            except asyncio.CancelledError:
                pass

        try:
            asyncio.run(monitor_loop())
        except KeyboardInterrupt:
            Write.Print("\nMonitor stopped by user.\n", Colors.red)
            sys.exit(0)
    else:
        asyncio.run(check_new_media(usernames, args.directory, data, args.jsonfile, args.debug))


if __name__ == '__main__':
    main()
