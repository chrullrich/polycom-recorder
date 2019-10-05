#!/usr/bin/env python3

import sys
import os
import subprocess
import signal
import tempfile
import shutil
import datetime
import selectors

from systemd import daemon


PERSIST_DIR = "/usr/local/recorder/recordings"
BUFFER_SIZE = 4 * 1024

AUDIODRIVER = "alsa"
AUDIODEV= "hw:1"
EFFECTS_FILE = os.path.join(os.path.dirname(__file__), "effects")

REC_OPTIONS = [
    "-q",               # no output
    "-t", "ogg",        # file format
    "-r", "44100",      # sample rate (sox does not go below with ogg)
    "--effects-file", EFFECTS_FILE,
]


quit = False
busy = False


class Interrupted(Exception):
    pass


def sigint(signum, stackframe):
    global quit
    quit = True

    # Interrupt select() if we are still waiting for rec to start recording.
    if (not busy):
        raise Interrupted()
    else:
        print("Recording is active, will exit once done.", file=sys.stderr)


def recording_duration(fn):
    return float(subprocess.check_output(["soxi", "-D", fn]))


def persist_recording(recfile, end_dt):
    recfile.seek(0, os.SEEK_SET)
    persist_fd, persist_fn = tempfile.mkstemp(".ogg", "rec_", PERSIST_DIR)
    os.fchmod(persist_fd, 0o644)
    os.close(persist_fd)
    persist_file = open(persist_fn, "w+b")
    shutil.copyfileobj(recfile, persist_file)
    persist_file.close()

    duration = recording_duration(persist_fn)
    start_dt = end_dt - datetime.timedelta(seconds=duration)

    filename = os.path.join(PERSIST_DIR, f"Recording_{start_dt:%Y%m%dT%H%M%S}-{end_dt:%H%M%S}.ogg")
    os.rename(persist_fn, filename)

    subprocess.run(["python3", os.path.join(os.path.dirname(__file__), "website.py")])


def main():
    signal.signal(signal.SIGINT, sigint)

    daemon.notify("READY=1")

    rec_environ = os.environ.copy()
    rec_environ["AUDIODRIVER"] = AUDIODRIVER
    rec_environ["AUDIODEV"] = AUDIODEV

    while (not quit):
        global busy
        busy = False

        with tempfile.TemporaryFile(suffix=".ogg", prefix="rec_") as outfile:
            try:
                rec_args = ["rec"] + REC_OPTIONS + ["-"]

                selector = selectors.DefaultSelector()

                # Start rec. It will not write output until it has actually started recording.
                rec = subprocess.Popen(rec_args,
                                       env=rec_environ,
                                       start_new_session=True,
                                       stdin=subprocess.DEVNULL,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.DEVNULL)

                # Wait for rec to produce output.
                print("entering select()", file=sys.stderr)
                selector.register(rec.stdout, selectors.EVENT_READ)
                try:
                    selector.select()
                    selector.close()
                except Interrupted:
                    print("interrupted while idle", file=sys.stderr)
                    return

                print("select() returned", file=sys.stderr)
                busy = True

                # Capture data until rec is done.
                data = None
                while (not data == b""):
                    data = rec.stdout.read(BUFFER_SIZE)
                    outfile.write(data)

                rec.wait()
                rec.stdout.close()
                outfile.flush()

            finally:
                if (rec.poll() is None):
                    print("killing rec", file=sys.stderr)
                    rec.send_signal(signal.SIGINT)

            persist_recording(outfile, datetime.datetime.now())


if (__name__ == "__main__"):
    main()
