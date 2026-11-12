#!/usr/bin/env python3
"""Build the Android debloat plan without touching the TV (offline, no network).

    py scripts/plan_android.py --list debloat.txt --enabled capture-e.txt \
        [--disabled capture-d.txt] [--wifi dumpsys-wifi.txt] [--keep package] \
        [--output batch.txt]

Inputs (captures made by hand from the TV, once):
    pm list packages -e --user 0      -> --enabled   (required)
    pm list packages -d --user 0      -> --disabled  (optional)
    dumpsys wifi                      -> --wifi      (optional: Wi-Fi owners and band)
The list is one package per line; '#' comments and empty lines are ignored.

Output per package: apply / rejected / not installed / already disabled, with the reason.
Exit 0 if the plan does not touch any core package; exit 1 if it does (the plan comes out
blocked and must not be applied); exit 2 if an input is missing or the file cannot be read.

With --output it writes only the packages in "apply" state, ready to hand to
cleanyourtv's tools/disable, which adds the guards that need to talk to the TV
(HOME, TV inputs, handlers) and the recovery record.

This runs nothing. After applying, wait >= 45 s before rebooting
(references/android.md). Never `pm uninstall`.
"""
import argparse
import re
import sys

# Android core and TV middleware: if one of these appears in the list, the whole plan is
# blocked. Copied verbatim from cleanyourtv (Gathin23/cleanyourtv, commit
# 6e8615eb0be0e843ceeebedae246d69f3e0a88d7, tools/disable.sh lines 68-69), because
# disabling any of them left TVs unable to boot (#884, #1578, #2557, #2803).
CORE_RE = ('^(android|android\\.ext\\.(services|shared)|com\\.android\\.sdksandbox|'
           'com\\.android\\.location\\.fused|com\\.android\\.systemui|com\\.android\\.shell|'
           'com\\.android\\.phone|com\\.android\\.settings|com\\.android\\.tv\\.settings|'
           'com\\.(google\\.)?android\\.(permissioncontroller|packageinstaller|ext\\.services|'
           'ext\\.shared|modulemetadata)|com\\.google\\.android\\.overlay\\.modules.*|'
           'com\\.android\\.providers\\..*|com\\.cltv\\.mal|'
           'com\\.mediatek\\.(tis|tv\\.service|tv\\.agent))$')
# Proven exception: no TV function uses these content providers.
CORE_OK = '^com\\.android\\.providers\\.(calendar|contacts|userdictionary|blockednumber)$'

# Factory menus and any brand's service. Copied from free-my-tv
# (simbasjungles/free-my-tv, app/src/io/freemytv/HomeMode.java, FACTORY pattern).
FACTORY_RE = r'^(.*\.)?(factory|factorymenu|facmenu|fac|hkcfac|testpq)(\..*)?$'
SETUPWRAITH = "com.google.android.tungsten.setupwraith"

APPLY = "apply"
REJECTED = "rejected"
NOT_INSTALLED = "not installed"
ALREADY_DISABLED = "already disabled"


def read_text(path):
    """Read a capture: PowerShell 5.1 redirects `>` as UTF-16, everything else as UTF-8."""
    with open(path, "rb") as f:
        data = f.read()
    if data[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return data.decode("utf-16", errors="replace")
    return data.decode("utf-8-sig", errors="replace")


def read_list(path):
    """List of packages to disable: one per line, '#' comments."""
    packages = []
    for line in read_text(path).splitlines():
        text = line.split("#", 1)[0].strip()
        if not text:
            continue
        if text.startswith("package:"):
            text = text[len("package:"):]
        packages.append(text)
    return packages


def read_packages(path):
    """Output of `pm list packages [-e|-d] --user 0` -> set of names."""
    packages = set()
    for line in read_text(path).splitlines():
        text = line.strip()
        if text.startswith("package:"):
            text = text[len("package:"):]
        if text:
            packages.add(text)
    return packages


def read_wifi(path):
    """Best effort with `dumpsys wifi`: {'owners': set, 'ssid': str, 'frequency': int}."""
    data = {}
    text = read_text(path)
    data["owners"] = set(re.findall(r"cname=([\w.]+)", text))
    m = re.search(r"SSID:\s*([^,\n]+)", text)
    if m:
        data["ssid"] = m.group(1).strip()
    m = re.search(r"[Ff]requency:\s*(\d{4})", text)
    if m:
        data["frequency"] = int(m.group(1))
    return data


def band(frequency):
    """Band label from the frequency in MHz (best effort)."""
    if frequency is None:
        return "not detected"
    if frequency < 3000:
        return "2.4 GHz"
    if frequency < 5900:
        return "5 GHz"
    return "6 GHz"


def classify(name, enabled, disabled, keep, wifi_owners=None):
    """Return (state, reason) for a package in the list.

    wifi_owners: packages that own saved networks, or None if there is no capture.
    """
    if name in keep:
        return REJECTED, "keep: the user asked for it"
    if re.match(CORE_RE, name) and not re.match(CORE_OK, name):
        return REJECTED, "Android/TV core or middleware: do not touch"
    if re.match(FACTORY_RE, name):
        return REJECTED, "factory menu or service: do not touch"
    if wifi_owners is not None and name in wifi_owners:
        return REJECTED, "owner of a saved Wi-Fi network: disabling it erases the network"
    if not wifi_owners and name == SETUPWRAITH:
        return REJECTED, "with no readable owners in dumpsys wifi there is no way to know if it owns the Wi-Fi"
    if name in enabled:
        return APPLY, "enabled and not core"
    if disabled is not None:
        if name in disabled:
            return ALREADY_DISABLED, "it was already disabled"
        return NOT_INSTALLED, "it does not appear in -e or -d"
    return NOT_INSTALLED, "missing from -e (without a -d capture it cannot be told apart from 'already disabled')"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Offline Android debloat plan: classifies the list without touching the TV.")
    parser.add_argument("--list", required=True, help="file with the packages to disable")
    parser.add_argument("--enabled", required=True,
                        help="capture of: pm list packages -e --user 0")
    parser.add_argument("--disabled",
                        help="optional capture of: pm list packages -d --user 0")
    parser.add_argument("--wifi", help="optional capture of: dumpsys wifi")
    parser.add_argument("--keep", action="append", default=[], metavar="PACKAGE",
                        help="package kept even if it is in the list (repeatable)")
    parser.add_argument("--output", help="write only the packages in 'apply' state here")
    args = parser.parse_args(argv)

    try:
        listing = read_list(args.list)
        enabled = read_packages(args.enabled)
        disabled = read_packages(args.disabled) if args.disabled else None
        wifi = read_wifi(args.wifi) if args.wifi else None
    except OSError as e:
        print("could not read an input: %s" % e, file=sys.stderr)
        return 2

    if not listing:
        print("the list has no packages (comments only or empty): nothing to plan.",
              file=sys.stderr)
        return 2

    keep = set(args.keep)
    counts = {APPLY: 0, REJECTED: 0, NOT_INSTALLED: 0, ALREADY_DISABLED: 0}
    touches_core = []
    applicable = []
    wifi_owners = wifi["owners"] if wifi is not None else None
    print("Debloat plan (offline, without touching the TV). Nothing is executed with this.")
    print()
    for name in listing:
        state, reason = classify(name, enabled, disabled, keep, wifi_owners)
        counts[state] += 1
        if state == APPLY:
            applicable.append(name)
        if state == REJECTED and reason.startswith("Android/TV core"):
            touches_core.append(name)
        print("  %-16s %-28s %s" % (state, name, reason))

    print()
    print("Summary: %d apply, %d rejected, %d not installed, %d already disabled."
          % (counts[APPLY], counts[REJECTED], counts[NOT_INSTALLED], counts[ALREADY_DISABLED]))

    if wifi is not None:
        if "frequency" in wifi:
            print("Wi-Fi detected: %s at %d MHz (%s). Many TVs are 2.4 GHz only even "
                  "though the SSID says 5 GHz: the frequency decides, not the name "
                  "(references/performance.md)."
                  % (wifi.get("ssid", "unknown SSID"), wifi["frequency"],
                     band(wifi["frequency"])))
        else:
            print("Wi-Fi: the frequency could not be read from the capture; check it by hand "
                  "before blaming the TV.")

    if touches_core:
        print()
        print("PLAN BLOCKED: the list touches Android core or TV middleware "
              "packages:", ", ".join(touches_core))
        print("Take them out of the list (or comment them out) and run this again. Nothing "
              "was sent to the TV.")
        return 1

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8", newline="\n") as f:
                f.write("".join(p + "\n" for p in applicable))
        except OSError as e:
            print("could not write the output: %s" % e, file=sys.stderr)
            return 2

    print()
    print("If the plan is approved: apply in batches with cleanyourtv's tools/disable, "
          "verify after each batch and wait >= 45 s before rebooting "
          "(references/android.md).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
