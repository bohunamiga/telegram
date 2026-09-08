#!/usr/bin/env python3
"""Send a command to the MorphOS QEMU monitor (unix socket) and print the reply.
Usage: morphos-vm-mon.py "<monitor command>"
e.g.  morphos-vm-mon.py "screendump /tmp/m.ppm"
      morphos-vm-mon.py "sendkey ret"
      morphos-vm-mon.py "info status"
"""
import os, socket
import sys
import time

SOCK = os.environ.get("MORPHOS_MON", "/tmp/morphos-monitor.sock")


def _connect(s, path, tries=12):
    """QEMU's monitor chardev serves ONE client at a time: a connect that lands
    while the previous helper's socket is still being torn down is REFUSED.
    Retry briefly instead of failing the whole step."""
    for i in range(tries):
        try:
            s.connect(path); return
        except ConnectionRefusedError:
            if i == tries - 1: raise
            time.sleep(0.5)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "info status"
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(10)
    _connect(s, SOCK)
    time.sleep(0.3)
    try:
        s.recv(65536)  # QEMU monitor banner
    except Exception:
        pass
    s.sendall((cmd + "\n").encode())
    time.sleep(0.6)
    out = b""
    try:
        while True:
            chunk = s.recv(65536)
            if not chunk:
                break
            out += chunk
            if len(chunk) < 65536:
                break
    except Exception:
        pass
    sys.stdout.write(out.decode(errors="replace"))
    s.close()


if __name__ == "__main__":
    main()
