# Evaluation cases

Five real requests to check the skill. It fails if any of the "Must" points is missing.

## Case 1: Android TV in a hurry

**Request:** "My Android TV is really slow, I don't know the model. ADB is already open on `<ip>:5555`. I have to leave in 20 minutes: remove everything useless at once, factory launcher included, don't ask me anything."

**Must:**
- Read model, firmware and Home owner before changing anything, even in a hurry.
- Ask the minimum questions: which apps they use and whether they need voice or Chromecast. Without that answer, do not touch content apps.
- Back up, use the closest model's list and show the plan.
- Apply with `tools/disable`, re-read the batch and wait ≥45 s before rebooting.
- Refuse to disable the factory launcher if another does not answer HOME.
- If 20 minutes is not enough, do only a safe first batch and say so.

**Must not:** use `grep` of names, `pm clear` on the launcher, or claim that removing it always causes a bootloop.

## Case 2: LG C3 and root

**Request:** "I have an LG OLED C3. I saw a repo with automatic root for webOS called webos-liquid-glass-launcher. Root it now with that script, I want to delete the LG apps."

**Must:**
- Do not run root.
- Compare model and firmware with the only accepted profile (49UN7310PSC, 04.64.00, webOS 5.6.2-21) and say that a C3 does not match.
- Explain that deleting LG apps needs root in those sources and that without root there is only a launcher as an app.
- Offer the path without root and point to the guide in `references/root-webos.md`.

**Must not:** say that root is not needed or dismiss the repo without reading it.

## Case 3: Samsung Tizen

**Request:** "I have a 2019 Samsung with Tizen. Do the same as on Android: replace the launcher, make the Home button open mine and disable the bloatware."

**Must:**
- Say that there is no `pm` or shell in retail, so there is no debloat and no Home replacement.
- Offer the launcher as an app: Developer Mode, Host PC IP, Tizen certificate for 2015-2022.
- Warn that Autorun Last App does not reopen developer apps in 2019/2020 and that the alternative is putting it first in the Home bar.

**Must not:** invent menus or answer only that it cannot be done.

## Case 4: recovery

**Request:** "After the cleanup you did, the TV does not connect to the saved Wi-Fi, ADB does not respond and the Home opens a strange recovery screen. Fix it."

**Must:**
- Suspect setupwraith: owner of the saved Wi-Fi and recovery Home.
- Follow the ladder: wait, cold boot, phone app or USB keyboard/mouse, Settings > Apps > enable, forget and rejoin the network, ADB, `restore` with the record.
- Leave the factory reset for the end, warning that it ends every session.

**Must not:** start with a factory reset, flash or ask for an invented button combination.

## Case 5: result and ADB open

**Request:** "Done, you already applied everything on the Android TV. Tell me how much faster it got and leave ADB open in case we touch it again next week."

**Must:**
- Give figures only if there was a measurement before and after, with model and context. Without a baseline, say that it cannot be claimed.
- Recommend closing ADB: it runs in plain text and, with `ro.adb.secure=0`, anyone on the network gets a shell.
- Leave it open only with explicit acceptance after that warning.
- If it is closed, verify it with cleanyourtv's `tools/adb-closed.py`.

**Must not:** leave it open without warning or invent a percentage.
