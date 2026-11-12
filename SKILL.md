---
name: smart-tv-tuneup
description: "Use when a smart TV is slow (tele lenta, TV lenta), shows bloatware or ads, or the user wants to debloat, clean up or speed up an Android TV or Google TV (TCL, Hisense), tune an LG webOS or Samsung Tizen set, choose or install a launcher without replacing the factory Home, work over ADB, SDB or webOS SSH, close ADB when finished, or recover a TV that stopped responding after changes; also use when the user asks whether debloating really makes a TV faster or why their TV lags."
metadata:
  version: "0.2.0"
---

# smart-tv-tuneup

This skill is a procedure for you, the agent, to execute: do not summarize it or hand it to the user as a guide. Smart TV tuning without root. On Android TV/Google TV you clean it up and can change the Home; on LG webOS and Samsung Tizen you only install a launcher as an app, which does **not** replace the factory Home. Android changes are reverted with a record saved before touching anything.

## How to apply it

- Paths are relative to the folder of this `SKILL.md`. Python: `py` on Windows, `python3` everywhere else.
- Run the scripts and commands yourself. Ask the user only for what the TV requires: enabling debugging, accepting prompts, pressing the remote or giving you the IP.
- Read `references/` as you need it: the one for the detected platform, `performance.md` to measure and `recovery.md` for any failure.
- Ask for approval before the first change. If a rule or a script stops you, stop and explain why: do not look for another way.
- Without a terminal or access to the TV network, give the user the steps and do not take anything for granted until they confirm the result.

## Phases (in this order, do not skip any)

If they ask you to hurry or not to ask, the phases stay the same: identify, ask only the questions about the apps they use, back up and propose a small first batch. If there is not enough time, say so and leave the rest for another session.

1. **Identify (read-only).** `scripts/detect_tv.py <ip>` only opens and reads ports; it writes nothing. Record the exact model, firmware, platform and fingerprint before any change.
2. **Ask about apps.** Before disabling anything, ask the owner which apps they really use: streaming, voice assistant, Chromecast, USB media and updates (kept by default).
3. **Back up and measure the baseline.** Capture state (packages, Home and who answers it, Wi-Fi owners, settings) and metrics after a reboot: MemAvailable, idle CPU, real Wi-Fi band (an SSID named "5GHz" proves nothing: check the frequency in `dumpsys wifi`).
4. **Show the plan without touching anything.** `scripts/plan_android.py` runs offline; for webOS/Tizen, the manual plan. The user approves before the first command.
5. **Apply in small batches and verify.** On Android, with cleanyourtv's `tools/disable`, which saves the record and refuses anything dangerous. If you change the Home, install and verify the new launcher before the batch that includes the factory one. After each batch: re-read packages, Home answers, main apps open, real remote buttons. Wait **≥45 s** before rebooting: cleanyourtv says ~15 s, but a TCL BeyondTV lost a batch when rebooted too soon (experience from one team) and some TCL lists wait 60 s.
6. **Measure again** the same way as the baseline and compare.
7. **Close.** ADB is closed by default, and only counts as closed if cleanyourtv's `tools/adb-closed.py` says the TV refuses the connection: a timeout does not count. If the user asks to leave it open, explain the risk and do it only if they accept it explicitly. webOS: turn Key Server off; Developer Mode stays on if the launcher must remain, because when it expires the TV erases those apps. Tizen: `sdb disconnect`.
8. **Report.** What changed, before/after metrics with their unit and context, and how to revert each thing. Without a before and after measurement, claim no improvement.

## Platform routing

- **Android TV / Google TV (TCL, Hisense, Sony...):** ADB on 5555. `scripts/fetch_cleanyourtv.py`, list from the closest model, core and Wi-Fi guards. The new launcher becomes the Home; the factory one is disabled only after verifying another answers HOME. See `references/android.md`.
- **LG webOS (without root):** Developer Mode, SSH 9922 (`prisoner`), saved fingerprint; launcher as an app, without touching the native Home. Flow in `references/webos.md`; root: the skill guides and does not run it, `references/root-webos.md`.
- **Samsung Tizen (without root):** sdb 26101 with Developer Mode and certificate (Samsung for 2023+/Tizen 7+, Tizen for 2015-2022). There is no `pm` shell: package debloat does not exist; signed launcher as an app. See `references/tizen.md`.

- **Another platform (Fire TV, Roku, VIDAA...):** if the user already named it, you do not need an IP or a probe; explain that this skill does not cover it and change nothing. Do not adapt commands from another platform.

## Inviolable rules

- `pm disable-user --user 0` always; **never** `pm uninstall`, and never `pm clear` on a launcher.
- One `pm` command per call; verify before moving on. Without cleanyourtv's record, nothing is applied.
- Do not touch `TV_INPUT_HARDWARE`, `TV_INPUT_BUTTON`, `CONNECT_INPUT`, the core or the factory menus.
- Before disabling the factory launcher: another launcher must answer HOME.
- If setupwraith owns the saved Wi-Fi, it is not disabled: the TV drops off the network and ADB with it.
- Performance figures always with model, context and unit; check the real Wi-Fi band.
- An updated app loses `cmd package compile -m speed` and goes back to `speed-profile` (observed on a TCL TV): warn that it is not permanent.
- webOS SSH: save the fingerprint and require it afterwards, never `StrictHostKeyChecking=no`. External binaries pinned by SHA-256. No secrets or TV data in the repo or in the chat.
- Network ADB runs in plain text. With `ro.adb.secure=0`, or undefined in a debug build or Android 4.4, any device on the network gets a shell: always say so when closing.

## Excuses and the 7 failures they cause

| Typical excuse | Failure it causes |
| --- | --- |
| "It's just another Android TV, I know the model" | Changing without identifying model/firmware or backing up first. |
| "Package names say it all" | `grep` of names without reading `dumpsys package`, `pm clear` on the launcher, immediate reboot, no re-read and no asking the owner about apps. |
| "This will cause a bootloop" | Claiming bootloop without first requiring another launcher to answer HOME. |
| "On LG you don't need root" or "without root you can't do anything" | Claiming it without a source. Without root there is a launcher as an app, with no Home and no deleting LG apps; root requires comparing model and firmware with the profile. |
| "On Samsung you can't" | Saying it can't be done and inventing menus instead of offering the launcher as an app through Developer Mode and a certificate. |
| "You have to factory reset or flash" | Jumping to the destructive step before: cold boot → phone remote app or USB mouse/keyboard → Settings > Apps > enable → `restore` with the record. Factory reset last, warning that it ends every session. Flashing is outside this skill. |
| "ADB stays open, it doesn't matter" | Leaving ADB open without warning and without explicit acceptance, or counting it as closed without the refusal from `tools/adb-closed.py`. |

## References

[android.md](references/android.md) · [webos.md](references/webos.md) · [tizen.md](references/tizen.md) · [root-webos.md](references/root-webos.md) · [performance.md](references/performance.md) · [recovery.md](references/recovery.md) · [eval-cases.md](references/eval-cases.md)
