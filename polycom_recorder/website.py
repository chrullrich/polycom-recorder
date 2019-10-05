#!/usr/bin/env python3

import sys
import os
import glob
import subprocess
import datetime


PERSIST_DIR = "/usr/local/recorder/recordings"
PAGE_HEAD = """<!DOCTYPE html>
<head>
<title>Conference Recordings</title>
<style type="text/css">
body {
    font-family: sans-serif;
}
table {
    border-collapse: collapse;
}
td, th {
    padding-right: 1ex;
}
</style>
</head>
<body>
<h1>Conference Recordings</h1>
<table>
    <tr>
        <th>Date</th>
        <th>Time</th>
        <th>Duration</th>
        <th>Play</th>
        <th>Download</th>
    </tr>
"""

PAGE_FOOT = """</body>
</html>"""


def main():
    os.chdir(PERSIST_DIR)
    recordings = glob.glob("*.ogg")

    with open("index.html", "wt") as htmlfile:
        out = lambda text: print(text, file=htmlfile)

        out(PAGE_HEAD)
        for fn in reversed(sorted(recordings)):
            start_td = datetime.datetime.strptime(fn[10:25], "%Y%m%dT%H%M%S")
            duration = float(subprocess.check_output(["soxi", "-D", fn]))
            hours, minutes, seconds = int(duration // 3600), int(duration // 60 % 60), int(duration % 60)

            out("<tr>")
            out(f"<td>{start_td:%Y-%m-%d}</td>")
            out(f"<td>{start_td:%H:%M:%S}</td>")
            out(f"<td>{hours:02d}:{minutes:02d}:{seconds:02d}</td>")
            out(f'<td><audio controls="controls" preload="none" src="{fn}"></td>')
            out(f'<td><a href="{fn}" download="{fn}">Download</a></td>')
            out("</tr>")

        out(PAGE_FOOT)


if (__name__ == "__main__"):
    main()