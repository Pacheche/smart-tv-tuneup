# Android TV / Google TV: full flow

The whole Android part is without root and without `uninstall`. If a step cannot be done, stop and say so; do not skip it.

## 1. Identify (read-only)

- Model, brand, firmware and fingerprint: `getprop ro.product.model`, `ro.build.fingerprint`, `ro.board.platform`, `ro.build.version.release`.
- Ports: 5555 (network ADB). If it is closed: USB debugging is missing, or the TV only offers Wireless debugging (Google TV) → `adb pair` with the code from Developer > Wireless debugging, then `adb connect`, `adb tcpip 5555`.
- The first authorization without "Allow always" only holds for that connection: ask for "Allow always" on the TV and retry once (without it, the next call hangs ~120 s).
- If the TV does not respond after a reboot: on TCL Android TV port 5555 reopens ~25 s after boot, before `sys.boot_completed`; wait for `getprop sys.boot_completed` before measuring anything.
- Look for the profile of the closest model in the cleanyourtv examples (brand, model, chip such as rtd2851/mt9221/s905x4, Android, platform name such as BeyondTV/PatchWall) and read its header before deciding.

## 2. Ask about apps (before touching anything)

A list of questions with a recommendation, never "I turn off whatever sounds like junk": apps they really use (grouped), the four dock apps in order, voice assistant (recommend disabling if it eats CPU), Chromecast, USB player, screensaver, firmware updates (keep by default), optional private DNS (does not block YouTube ads).

## 3. Back up and measure the baseline

- Save: `getprop`, package lists, all settings, who answers HOME and its claimants, TV inputs, Wi-Fi owners (`dumpsys wifi`), and a summary (model, board, Android, GPU, memory, storage, Wi-Fi band/RSSI, top CPU).
- Baseline after a reboot, same as the final measurement: wait ~150 s after boot; compare MemAvailable, swap and idle CPU, not a snapshot in use. Capture with `adb shell cat /proc/meminfo` and `adb shell top -b -n 1`.
- Idle CPU: on Realtek/MediaTek the load average lies (kernel threads in D state); use `%idle` from `top`.
- Video with stutter: YouTube > Settings > "Stats for nerds" during playback (speed, buffer health, dropped frames) + real band from `dumpsys wifi`: many TVs are 2.4 GHz only even when the SSID says "5GHz" (the frequency in `dumpsys wifi` is the truth, not the SSID name).
- `/data` with less than ~10 % free: installs fail and the TV drags.

## 4. Plan without touching anything

Download the tools with `scripts/fetch_cleanyourtv.py`; the command prints the folder. Start from the closest list in `examples/<brand-model>/debloat.txt`, never from a `grep` of names.

`scripts/plan_android.py` runs offline on that list and the captures of `pm list packages -e --user 0`, `pm list packages -d --user 0` and `dumpsys wifi`, with a `--keep` for each app the user uses. `--output batch.txt` leaves only what is applicable. Rules it implements (source: cleanyourtv `tools/disable.sh` lines 68-69, commit `6e8615eb`; factory: free-my-tv `HomeMode.java`):

- `CORE_RE`: Android core and TV middleware (systemui, settings, phone, shell, permissioncontroller, packageinstaller, providers, com.cltv.mal, com.mediatek.*) → a list that touches this exits with 1 and is not applied.
- `CORE_OK`: proven exceptions: calendar/contacts/userdictionary/blockednumber providers.
- Factory menus: rejected. Owners of a saved Wi-Fi: rejected; without a `dumpsys wifi` capture, setupwraith too.

The plan cannot check what needs talking to the TV (HOME, `TV_INPUT_HARDWARE`, handlers): those guards run in `tools/disable`.

Never disable, whatever the name: the Live TV app and the input services (a disabled input driver leaves HDMI at "No Signal" until a full restore and cold boot), the sources/inputs menu, remote control and Bluetooth pairing, keyboard, Play Store and Play Services, Settings, and `com.google.android.tungsten.setupwraith` when `dumpsys wifi` shows it as the owner of the saved Wi-Fi (disabling it erases that network and drops the TV off the network, and ADB and the phone remote with it). Do not touch `TV_INPUT_HARDWARE`, `TV_INPUT_BUTTON` or `CONNECT_INPUT`.

## 5. Apply in batches and verify

If you are going to change the Home, do section 6 first. Without a verified new launcher, take the factory one out of the batch: disabling it always goes through `tools/disable`, never with a lone `pm`.

- Apply each batch with cleanyourtv from its folder: `TV_HOST=<ip> tools/disable.sh <batch.txt>` or `tools/disable.ps1` on Windows, with its venv ready. Before the first command it saves each package's state, the Home owner and the animation scales in `~/.cleanyourtv/`; on a core it exits without sending anything. Without a record you do not continue.
- If a lone `pm` is needed: one command per call, always `pm disable-user --user 0 <pkg>`; **never** `pm uninstall`, and never `pm clear` on the launcher or on anything critical (it erases its data).
- After each batch, re-read with `pm list packages -e --user 0`: a command without an error does not prove the package ended up off.
- Re-running the whole list is fine: the record keeps the first state.
- After each batch: press Home, take a screenshot, open the main streaming apps (Netflix/HDMI usually show a black screen in a screenshot: check `mResumedActivity`), and for voice/remote batches ask the user to press the real buttons.
- Leave packages with an installer for the end (TCL `com.tcl.guard`, `appmarket2`).
- **Wait before rebooting: ≥45 s after the last `pm disable-user`.** cleanyourtv's docs recommend ~15 s (`PROMPT.md`, `docs/TROUBLESHOOTING.md`) and some lists wait 10-30 s, but there are cases where that was not enough: on a real TCL BeyondTV, rebooting right after a batch lost it completely (experience from one team); on a TCL 40S5400A an `adb reboot` "a few seconds" after the batch brought the whole batch back enabled and it only stayed stable with 60 s (`examples/tcl-40s5400a/debloat.txt` lines 67-68); on a Xiaomi (aesp0) `sync` + 15 s was not enough (the last eight packages came back) and ~40 s was (`examples/xiaomi-mitv-aesp0/debloat.txt` lines 49-50); and a Sony BRAVIA asks for ~90 s (`examples/sony-bravia-4k-ur3/debloat.txt` line 37). That is why this skill always requires ≥45 s, and verifying after boot with `pm list packages -e --user 0`.
- Several firmwares re-enable packages on every boot (e.g. TCL `com.tcl.overseasappshow`, `com.tcl.usercenter`): re-read the list after the reboot and note it in the header.

## 6. Change the Home (optional)

- On Android the Home is replaced. cleanyourtv's `launcher/build-and-install.sh` builds, installs, changes the Home and reverts if it does not end up on the new one. Requires JDK 17 and the Android SDK; build outside synced folders (on a real TV Gradle hung inside Google Drive).
- Only disable the factory launcher (`com.google.android.tvlauncher` or another) **after verifying that something else answers HOME**: `cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME` and `cmd package query-activities --brief -a android.intent.action.MAIN -c android.intent.category.HOME`. If the answer is `android` (chooser), if setupwraith is still active and answers HOME ahead of it, or if there is no other launcher installed: **do not disable the factory one**. Setup apps and the setup wizard also "answer HOME" but are not launchers.
- Claiming "bootloop" requires this: if the new launcher does not answer HOME and the factory one is disabled, the TV ends up in the chooser or blank; that is not a bootloop and it is fixed by enabling the factory one again.

## 7. Speed (optional, with honest expectations)

- Animation scales to 0.5 (`settings put global window_animation_scale 0.5`, same for `transition_animation_scale`, `animator_duration_scale`); `restore` resets them.
- Compile the dock apps to full: `cmd package compile -m speed -f <pkg>`, one per call; verify with `dumpsys package dexopt` (`status=speed`) instead of retrying. **Note:** a Play Store update returns the app to `speed-profile` (observed on a TCL BeyondTV): without root it cannot be pinned, you have to repeat it.
- Extreme mode only on very weak TVs (1 GB or less, Android 7-9) and with the owner's agreement: scales to 0, apps without background (`appops RUN_ANY_IN_BACKGROUND ignore` + bucket `rare`; never music, casting, launcher, keyboard or input services) and `pm trim-caches`.

## 8. Close ADB

- Closing is the default. Turn off on the TV: USB debugging, network debugging and wireless debugging.
- If the user asks to leave it open, explain that network ADB runs in plain text and do it only if they accept it explicitly. Better alternative: close it and note how to reopen it.
- Check from the cleanyourtv folder with `py -I tools/adb-closed.py <ip>`: **only exit 0 counts as closed** (the TV refused the connection). Timeout or nothing answering = exit 2 = could not check (the TV may be off, asleep or on another network); do not claim "closed".
- If the TV has `ro.adb.secure=0` (or does not define it in a debug build or Android 4.4), warn in plain text: port 5555 gives a shell to any device on the network without asking permission.

## 9. Revert

`TV_HOST=<ip> tools/restore.sh <the same list>` (or `restore.ps1`): replays the record, including the Home and the animation scales. Without a record it enables the whole list and sets the scales to 1.0: warn about it.

## Source references

- CORE guards, Home, setupwraith and closing: Gathin23/cleanyourtv (`tools/disable.sh`, `tools/adb-closed.py`, `docs/TROUBLESHOOTING.md`), commit `6e8615eb`.
- Flow, metrics and questions: paisanos-io/tv-makeover (`skills/android-tv-debloat/SKILL.md`, `references/quirks.md`).
- `pm disable-user` reversible and launcher watchdog: simbasjungles/free-my-tv (`app/src/io/freemytv/HomeMode.java`).
