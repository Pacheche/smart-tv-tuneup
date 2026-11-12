# Recovery: strict order, no skipping

**Rule:** never jump to a factory reset. Follow the ladder in order; flashing is outside this skill. Everything changed on Android with this skill is **reversible with `pm enable`** because `pm uninstall` is never used (`Gathin23_cleanyourtv`, `docs/DOS-AND-DONTS.md` lines 19-23).

## 0. Prevention (before touching anything)

- Save the **applied list** and the **record** the script makes before changing anything: in `~/.cleanyourtv/`, one file per TV and per list, with each package's state, **who owned Home** and the three animation scales (`docs/restore.md` lines 24-30).
- Without a record, restore enables the whole list and sets the scales to `1.0` (lines 59-60). That is why the record matters.
- Never disable the **only** launcher without having another that answers HOME (verified bootloop cases below).

## 1. The recovery ladder (in this order)

Source: `Gathin23_cleanyourtv`, `docs/TROUBLESHOOTING.md` lines 679-689 and `docs/faq.md` lines 9-20.

1. **Wait ten minutes** once (many "bootloops" are slow boots).
2. **Cold boot:** unplug, wait, plug back in. Repeat the measurement.
3. **Phone remote or USB mouse/keyboard** to recover navigation if the remote does not respond (documented cases with a USB mouse: `docs/devices/hisense-65d62qh.md`).
4. **Safe mode:** hold Power during the boot animation (on many TVs); it disables the added apps.
5. **Settings > Apps > show system apps > enable** the launcher/package in question (or `pm enable <pkg>` if ADB responds).
6. **Recover the network:** if the saved Wi-Fi belonged to setupwraith, reconnecting is not enough: forget the network and join it again from the TV, with the remote or a USB keyboard (`TROUBLESHOOTING.md` 633-643). Another option: a hotspot with the **same name and password** as the old network. Then turn debugging back on if it was off.
7. **Retry ADB** right after powering on (`adb connect <ip>:5555` for a couple of minutes).
8. **`tools/restore.sh <list>`** (or `restore.ps1` on Windows) with the record: it is the normal path as soon as ADB responds (`docs/restore.md` lines 5-20).
9. **Wipe the cache partition** from the recovery menu.
10. **Factory reset from the recovery menu, as a last resort.** Warn first that it ends every session.

## 2. What the factory reset means (say it before doing it)

- "Everything these tools change lives in the user data the reset wipes, so **every disabled app comes back** and the new launcher is gone, **along with your own apps and accounts**." (`docs/faq.md` lines 17-18.)
- A TV that still loops **after** the reset points to hardware, not to the debloat (`docs/faq.md` lines 19-20).
- Before the reset on Google TV: re-enable `setupwraith` if it was disabled (`docs/TROUBLESHOOTING.md` line 603 and `docs/devices/fpd-cg50-c3.md`).

## 3. Real "bootloop" cases and their cause (do not claim without verifying)

| Case | Real cause | Recovery |
|---|---|---|
| KitKat COOP COTV-0001, 17 packages | the **only** launcher was disabled with no replacement | re-enable that launcher; the TV still answered ADB (`TROUBLESHOOTING.md` 545-554) |
| Haier H50H5F, reboot loop | **unknown** cause; the report does not establish it | `pm enable` of the applied list if there is time between reboots (528-544) |
| Android stick with core packages | `com.android.providers.*`, overlays, etc. were touched | `pm enable` + reboot if ADB lives; if not, recovery (`515-527`) |
| JVC LT-43N7115, screen at boot | the factory launcher was disabled on CVTE | the full ladder above (679-689) |
| ZTE B866F | disabling **all** launchers triggers a factory reset on the next boot (`docs/devices/zte-b866f.md`) | avoid it: never leave the TV without HOME |
| Google TV, Home opens a recovery screen | setupwraith answers HOME and leads to `RecoveryActivity` (`tools/disable.sh` 192-196) | enable the factory launcher and run `restore` |

**Honesty rule:** if the user says "it is stuck on the logo", **do not** claim "you broke it with the debloat" without checking: (a) which package answered HOME before and after (`cmd package resolve-activity ... category.HOME`), (b) whether ADB is still alive, (c) which batch was applied and when. Ask for a photo of the screen.

## 4. If ADB got closed

- Verify with cleanyourtv's `tools/adb-closed.py`: **exit 0 only if the TV refuses the connection**; timeout or no response = exit 2 (that is not "closed"). (`Gathin23_cleanyourtv`, `tools/adb-closed.py` and its test.)
- If the TV refuses: turn *Wireless debugging* back on from Settings with the remote or the mouse; the port changes, read it from the screen or `adb mdns services`.
- **Close ADB when finished** by default and warn in plain text: on firmware with `ro.adb.secure=0` (or undefined), any machine on the LAN gets a shell (`docs/faq.md` lines 27-29). "No leaving ADB open" is a project rule (`DOS-AND-DONTS.md` line 36).

## 5. Rules that keep you out of here

- One command per call; small batches with verification between batch and batch.
- **≥45 s wait before rebooting** after disabling (cleanyourtv's docs say ~15 s: `PROMPT.md` line 116 and `TROUBLESHOOTING.md` line 963; in `examples/tcl-40s5400a/debloat.txt` lines 67-68, an `adb reboot` "a few seconds" after the last batch **brought the whole batch back**, and repeating with a **60 s** wait left it all disabled; in `examples/xiaomi-mitv-aesp0/debloat.txt` line 49 neither `sync` nor 15 s was enough; in `examples/sony-bravia-bf1/debloat.txt` line 15 they recommend ~30 s; on a **real TCL BeyondTV** a batch was lost by rebooting too soon: experience from one team). Use 45 s as the minimum and more if the TV is slow.
- Never `pm uninstall`; never `pm clear` on a launcher.
- Do not touch `TV_INPUT_HARDWARE`, `TV_INPUT_BUTTON`, `CONNECT_INPUT`, core packages or factory menus (`DOS-AND-DONTS.md` line 45).
- Before disabling `setupwraith`: `dumpsys wifi | grep -o 'cname=[^ ]*'`. If it owns the saved Wi-Fi, first forget and rejoin the network (`TROUBLESHOOTING.md` 633-643).

## Sources

- `Gathin23_cleanyourtv` (MIT): `docs/restore.md`, `docs/faq.md`, `docs/TROUBLESHOOTING.md`, `docs/DOS-AND-DONTS.md`, `tools/adb-closed.py`.
- `paisanos-io_tv-makeover` (MIT): reboot timing notes in its `tvs/*/debloat.txt`.
