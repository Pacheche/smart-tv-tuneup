#!/usr/bin/env python3
"""Detect which platform a TV is, by TCP ports, without writing anything to it.

    py scripts/detect_tv.py <ip> [--timeout 2]

It only opens and closes connections and reads what the TV itself sends without anyone
asking (zero bytes sent):

    5555   Network ADB (Android / Google TV)
    9922   Developer Mode SSH (LG webOS)
    3000   LG SSR (SSAP)
    3001   LG SSR with TLS (SSAP)
    26101  Samsung Tizen sdb (only with Developer Mode on)
    8001   Samsung remote API (websocket)
    8002   Samsung remote API (alternate)

It prints port by port and a conclusion with a confidence level: high (>= 3 points),
medium (2) or low (1). With an unknown TV or closed ports it says "unknown"
and does not invent a platform. It does not replace identifying model and firmware by hand:
see references/android.md, webos.md and tizen.md.
"""
import argparse
import socket
import sys

# (port, what it is, platform, weight). The weight is only to order the conclusion:
# 2 = characteristic port of the platform, 1 = port that only adds context.
PORTS = (
    (5555, "Network ADB (Android / Google TV)", "Android / Google TV", 2),
    (9922, "Developer Mode SSH (LG webOS)", "LG webOS", 2),
    (3000, "LG SSR (SSAP)", "LG webOS", 1),
    (3001, "LG SSR with TLS (SSAP)", "LG webOS", 1),
    (26101, "Samsung Tizen sdb (Developer Mode)", "Samsung Tizen", 2),
    (8001, "Samsung remote API (websocket)", "Samsung Tizen", 1),
    (8002, "Samsung remote API (alternate)", "Samsung Tizen", 1),
)

NEXT_STEP = {
    "Android / Google TV": "ask for the exact model, firmware and Android version (references/android.md)",
    "LG webOS": "Developer Mode + Key Server on the TV (references/webos.md)",
    "Samsung Tizen": "Developer Mode and sdb on port 26101 (references/tizen.md)",
}


def read_banner(sock, timeout=0.6):
    """Read what the TV sends on connect without sending anything; return text or None."""
    try:
        sock.settimeout(timeout)
        data = sock.recv(200)
    except (socket.timeout, OSError):
        return None
    if not data:
        return None
    return data.decode("utf-8", "replace").strip()


def probe(host, port, timeout):
    """Connect and close. Return (state, banner). Do not write a single byte."""
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            banner = read_banner(sock)
    except ConnectionRefusedError:
        return "closed", None
    except socket.timeout:
        return "no response", None
    except OSError as e:
        return "no data (%s)" % e.__class__.__name__, None
    return "open", banner


def score(open_ports):
    """Sum the weights per platform. `open_ports` is a list of (platform, weight)."""
    points = {}
    for platform, weight in open_ports:
        points[platform] = points.get(platform, 0) + weight
    return points


def conclude(points):
    """Return (platform, confidence) from the points per platform."""
    if not points:
        return "unknown", "no characteristic ports"
    top = max(points.values())
    peaks = sorted(p for p, v in points.items() if v == top)
    if len(peaks) > 1:
        return "ambiguous between %s" % " and ".join(peaks), "medium"
    if top >= 3:
        return peaks[0], "high"
    if top == 2:
        return peaks[0], "medium"
    return peaks[0], "low"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Detect a TV platform by TCP ports, without sending anything.",
        add_help=True,
    )
    parser.add_argument("ip", help="IP of the TV on the local network")
    parser.add_argument("--timeout", type=float, default=2.0,
                        help="seconds to wait per port (default 2)")
    args = parser.parse_args(argv)

    open_ports = []
    print("Probing %s (read-only, zero bytes sent):" % args.ip)
    for port, what, platform, weight in PORTS:
        state, banner = probe(args.ip, port, args.timeout)
        line = "  %-6s %-11s %s" % (port, state, what)
        if banner:
            line += "  [banner: %s]" % banner.splitlines()[0][:60]
        print(line)
        if state == "open":
            open_ports.append((platform, weight))

    platform, confidence = conclude(score(open_ports))
    print()
    print("Likely platform: %s - confidence %s" % (platform, confidence))
    if platform in NEXT_STEP:
        print("Next step: %s." % NEXT_STEP[platform])
    print("An open port does not identify the TV: confirm model and firmware before "
          "any change.")
    if not open_ports:
        print("No characteristic port answered: the TV may be off, on another VLAN or "
              "with debugging disabled. This says nothing about its state.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
