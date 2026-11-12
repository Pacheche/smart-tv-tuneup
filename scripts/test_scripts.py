#!/usr/bin/env python3
"""Tests for the smart-tv-tuneup scripts: no network, no git remote and no TV.

    py -I scripts/test_scripts.py

Everything tested is pure functions, temporary files and the output wiring (with
`probe` replaced): no test opens a socket to a TV or clones anything.
"""
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

# -I does not put the script directory on sys.path: add it by hand.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import detect_tv
import fetch_cleanyourtv
import plan_android


def write_file(path, text):
    Path(path).write_text(text, encoding="utf-8")
    return str(path)


class TestCore(unittest.TestCase):
    """CORE_RE / CORE_OK have to behave as in cleanyourtv."""

    def test_core_packages_blocked(self):
        for package in ("com.android.systemui", "com.android.shell", "com.android.settings",
                        "com.android.phone", "com.google.android.permissioncontroller",
                        "com.android.packageinstaller", "com.cltv.mal", "com.mediatek.tis",
                        "com.android.location.fused", "android", "android.ext.services"):
            self.assertTrue(plan_android.re.match(plan_android.CORE_RE, package), package)
            self.assertFalse(plan_android.re.match(plan_android.CORE_OK, package), package)

    def test_allowed_providers_exception(self):
        for package in ("com.android.providers.calendar", "com.android.providers.contacts",
                        "com.android.providers.userdictionary",
                        "com.android.providers.blockednumber"):
            self.assertTrue(plan_android.re.match(plan_android.CORE_RE, package), package)
            self.assertTrue(plan_android.re.match(plan_android.CORE_OK, package), package)

    def test_normal_bloat_is_not_core(self):
        for package in ("com.google.android.tvlauncher", "com.netflix.ninja",
                        "com.example.bloat", "com.tcl.tvinput"):
            self.assertFalse(plan_android.re.match(plan_android.CORE_RE, package), package)


class TestPlanAndroid(unittest.TestCase):
    def test_rejects_factory(self):
        state, reason = plan_android.classify("com.tcl.factory.view", {"com.tcl.factory.view"},
                                              None, set(), set())
        self.assertEqual(state, plan_android.REJECTED)
        self.assertIn("factory", reason)

    def test_rejects_wifi_owner(self):
        state, reason = plan_android.classify("com.foo", {"com.foo"}, None, set(), {"com.foo"})
        self.assertEqual(state, plan_android.REJECTED)
        self.assertIn("Wi-Fi", reason)

    def test_setupwraith_without_capture_is_rejected(self):
        state, _ = plan_android.classify(plan_android.SETUPWRAITH, {plan_android.SETUPWRAITH},
                                         None, set(), None)
        self.assertEqual(state, plan_android.REJECTED)

    def test_setupwraith_without_readable_owners_is_rejected(self):
        state, _ = plan_android.classify(plan_android.SETUPWRAITH, {plan_android.SETUPWRAITH},
                                         None, set(), set())
        self.assertEqual(state, plan_android.REJECTED)

    def test_reads_powershell_utf16_capture(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "e.txt"
            path.write_bytes("package:com.bloat\r\n".encode("utf-16"))
            self.assertEqual(plan_android.read_packages(str(path)), {"com.bloat"})

    def test_output_only_applicable(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            (base / "list.txt").write_text("com.bloat\ncom.tcl.factory.view\n", encoding="utf-8")
            (base / "e.txt").write_text("package:com.bloat\npackage:com.tcl.factory.view\n",
                                        encoding="utf-8")
            output = base / "batch.txt"
            with contextlib.redirect_stdout(io.StringIO()):
                code = plan_android.main(["--list", str(base / "list.txt"), "--enabled",
                                          str(base / "e.txt"), "--output", str(output)])
            self.assertEqual(code, 0)
            self.assertEqual(output.read_text(encoding="utf-8"), "com.bloat\n")

    STATES = {"apply": plan_android.APPLY, "rejected": plan_android.REJECTED,
              "not installed": plan_android.NOT_INSTALLED, "already disabled": plan_android.ALREADY_DISABLED}

    def run_plan(self, listing, enabled, disabled=None, keep=()):
        with tempfile.TemporaryDirectory() as tmp:
            args = ["--list", write_file(Path(tmp) / "list.txt", listing),
                    "--enabled", write_file(Path(tmp) / "e.txt", enabled)]
            if disabled is not None:
                args += ["--disabled", write_file(Path(tmp) / "d.txt", disabled)]
            for package in keep:
                args += ["--keep", package]
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = plan_android.main(args)
            return code, output.getvalue()

    def test_states_per_package(self):
        code, output = self.run_plan(
            "com.foo.bloat\ncom.foo.old\ncom.foo.gone\ncom.android.systemui\n",
            "package:com.foo.bloat\npackage:com.android.systemui\n",
            "package:com.foo.old\n")
        self.assertEqual(code, 1)
        self.assertIn("apply", output)
        self.assertIn("com.foo.bloat", output)
        self.assertIn("already disabled", output)
        self.assertIn("not installed", output)
        self.assertIn("rejected", output)
        self.assertIn("PLAN BLOCKED", output)

    def test_clean_plan_exits_zero(self):
        code, output = self.run_plan(
            "com.foo.bloat\n# commented\n\n", "package:com.foo.bloat\n", "")
        self.assertEqual(code, 0)
        self.assertNotIn("PLAN BLOCKED", output)

    def test_keep_blocks_without_being_core(self):
        code, output = self.run_plan("com.foo.gusto\n", "package:com.foo.gusto\n",
                                     keep=["com.foo.gusto"])
        self.assertEqual(code, 0)
        self.assertIn("keep", output)
        self.assertNotIn("apply com.foo.gusto", output.replace("  ", " "))

    def test_empty_list_is_error(self):
        code, _ = self.run_plan("# comments only\n", "package:com.foo\n")
        self.assertEqual(code, 2)

    def test_classify_direct(self):
        self.assertEqual(plan_android.classify("com.foo", {"com.foo"}, None, set())[0],
                         plan_android.APPLY)
        self.assertEqual(plan_android.classify("com.foo", set(), {"com.foo"}, set())[0],
                         plan_android.ALREADY_DISABLED)
        self.assertEqual(plan_android.classify("com.foo", set(), None, set())[0],
                         plan_android.NOT_INSTALLED)
        self.assertEqual(
            plan_android.classify("com.android.shell", {"com.android.shell"}, None,
                                  set())[0],
            plan_android.REJECTED)

    def test_band(self):
        self.assertEqual(plan_android.band(2437), "2.4 GHz")
        self.assertEqual(plan_android.band(5180), "5 GHz")
        self.assertEqual(plan_android.band(6135), "6 GHz")
        self.assertEqual(plan_android.band(None), "not detected")


class TestDetectTv(unittest.TestCase):
    def test_one_characteristic_port_is_medium(self):
        points = detect_tv.score([("Android / Google TV", 2)])
        self.assertEqual(detect_tv.conclude(points), ("Android / Google TV", "medium"))

    def test_two_ports_same_platform_is_high(self):
        points = detect_tv.score([("LG webOS", 2), ("LG webOS", 1)])
        platform, confidence = detect_tv.conclude(points)
        self.assertEqual(platform, "LG webOS")
        self.assertEqual(confidence, "high")

    def test_one_port_is_low(self):
        points = detect_tv.score([("Samsung Tizen", 1)])
        self.assertEqual(detect_tv.conclude(points), ("Samsung Tizen", "low"))

    def test_no_ports_is_unknown(self):
        self.assertEqual(detect_tv.conclude(detect_tv.score([])),
                         ("unknown", "no characteristic ports"))

    def test_tie_is_ambiguous(self):
        points = detect_tv.score([("Android / Google TV", 2), ("LG webOS", 2)])
        platform, confidence = detect_tv.conclude(points)
        self.assertIn("ambiguous", platform)
        self.assertEqual(confidence, "medium")

    def test_main_without_network_prints_conclusion(self):
        responses = {5555: ("open", None), 9922: ("closed", None),
                     3000: ("closed", None), 3001: ("closed", None),
                     26101: ("closed", None), 8001: ("closed", None),
                     8002: ("closed", None)}
        output = io.StringIO()
        with mock.patch.object(detect_tv, "probe",
                               side_effect=lambda h, p, t: responses[p]):
            with contextlib.redirect_stdout(output):
                code = detect_tv.main(["192.0.2.1", "--timeout", "0.1"])
        self.assertEqual(code, 0)
        self.assertIn("Android / Google TV", output.getvalue())
        self.assertIn("confidence medium", output.getvalue())


class TestFetchCleanyourtv(unittest.TestCase):
    def test_commit_is_forty_hex(self):
        self.assertEqual(len(fetch_cleanyourtv.COMMIT), 40)
        self.assertRegex(fetch_cleanyourtv.COMMIT, r"^[0-9a-f]{40}$")

    def test_synced_folder(self):
        self.assertTrue(fetch_cleanyourtv.is_synced_folder(
            "C:/Users/x/Mi unidad/cleanyourtv"))
        self.assertTrue(fetch_cleanyourtv.is_synced_folder(
            "/home/u/OneDrive/backups"))
        self.assertFalse(fetch_cleanyourtv.is_synced_folder(
            "C:/Users/x/.cache/smart-tv-tuneup/cleanyourtv"))

    def test_head_without_repo_is_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(fetch_cleanyourtv.head_of(tmp))

    def test_default_dest_outside_synced(self):
        self.assertFalse(fetch_cleanyourtv.is_synced_folder(
            fetch_cleanyourtv.DEFAULT_DEST))


if __name__ == "__main__":
    unittest.main(verbosity=2)
