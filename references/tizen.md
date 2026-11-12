# Samsung Tizen: what you can do without root

**Rule:** in retail Tizen **there is no ADB, no shell and no `pm disable-user`**. You cannot disable or uninstall factory bloatware. The only thing is installing apps (if the firmware allows it) or using the launcher as an app. `sdb` on retail firmware **only accepts files** (`filesync_support:push`), not commands. (`Gathin23_cleanyourtv` repo, `docs/devices/samsung-tizen.md` lines 43 and 106, and `tests/test_samsung_tizen_note.py`; `simbasjungles_free-my-tv` repo, `CLAUDE.md` line 190.)

## 1. Entry: Developer Mode + SDB

Flow verified in the `simbasjungles_free-my-tv` repo (`CLAUDE.md` lines 155-169, `README.md` line 141):

1. Ask for the **TV IP** and the city (if API content is used).
2. On the TV (the user does it): *Apps* → type **`1 2 3 4 5`** with the remote → **Developer mode ON** → *Host PC IP* = this computer's IP → **reboot the TV**.
3. From the PC: `sdb connect <IP>:26101`.
4. Sign and install: `tizen` (Tizen Studio CLI, or Samsung's `tizen-sdk-skills` plugin) + `python3 tizen/install.py <IP>` from free-my-tv (talks SDB directly). The app is third-party and queries external services: warn about it before. Note: `tizen` runs on Java and Samsung's binaries are Intel; on Apple Silicon without Rosetta they do not work.
5. **Certificate, once:** 2023+ (Tizen 7+) requires a **Samsung** certificate with the owner's Samsung account and its **DUID**; 2015-2022 use a **Tizen** certificate (`tizen certificate`, then `tizen security-profiles add`). Updates need **the same certificate**: with another one, the TV refuses (you have to uninstall first). **Certificates, passwords and DUIDs never in the chat.** (`CLAUDE.md` lines 167-169, 188-203.)

Path without tools: **TizenBrew Installer** (`github.com/reisxd/TizenBrewInstaller`) installs the release by writing `simbasjungles/free-my-tv`; on 2023+ it signs with the Samsung account. **TizenBrew needs 2017+**; on 2015/2016 you have to build by hand. (`CLAUDE.md` lines 146, 149-152; `README.md` line 141.)

## 2. Ports and responses (verified)

| Port | State | What it is |
|---|---|---|
| 8001 | open | remote HTTP API (`GET /api/v2/` gives model and state) |
| 8002 | open | HTTPS of the same (self-signed certificate) |
| 26101 | closed with Dev Mode off (answers by refusing), open with Dev Mode on | SDB |
| 5555 | closed | ADB does not exist in retail Tizen |

Source: `Gathin23_cleanyourtv`, `docs/devices/samsung-tizen.md` (evidence on a **UN50AU8000FXZA**, report #441; the repo test blocks 5555/26101 from appearing open without Dev Mode).

## 3. Firmware limits (promise nothing more)

| Scenario | Result | Source |
|---|---|---|
| 2015 UE48JU6100 (Tizen 2.3) | works, reported (#317) | `simbasjungles`, `README.md` 141 |
| 2016 UE49K5670 (Full HD) | **refuses developer installs**: `failed[118]` even with Samsung's `tizen install` (#349) | ibid |
| 2016 UE49KU6640 / UN49KU6400 | `failed[118]` = copy of a previous failed install → `--uninstall` and reinstall with a Tizen certificate | ibid; `CLAUDE.md` 182-184 |
| Orsay (Samsung before Tizen) | **do not run the launcher** (alternative: Google TV streamer over HDMI) | `README.md` 141 |
| 2015/2016 | do not run TizenBrew | ibid |
| 2017/2018 (Tizen 3/4) | *TV Settings* in the drawer **freezes the TV** (#257); the remote's Settings button works | ibid |
| **Autorun Last App** | tested on **2017**; **2019 and 2020 do not reopen it** (#356). On 2019/2020: put the launcher first in the Home bar | `CLAUDE.md` 196-199; `README.md` 146 |

## 4. What you can really do

1. **Identify**: model, year, Tizen version (Settings > Support). Without this nothing is qualified.
2. **Install the launcher as an app** (if the firmware allows it). If it gives `failed[118]`: `--uninstall` and retry with the matching certificate; if it persists, report and stop.
3. **Autorun Last App** only on models where it is tested (2017); warn that it does not work on 2019/2020.
4. **Do not** disable, **do not** uninstall bloatware, **do not** flash, **do not** invent debloat menus.
5. **One report holds for one unit and one firmware:** do not present it as something that applies to the whole platform.

## 5. Excuses to reject

- "On Samsung you can disable bloatware": false in retail (no shell).
- "There is a debloat menu in Settings": ask for a photo of the real screen before claiming it.
- "Flashing Tizen fixes the slowness": flashing is outside this skill.

## Sources

- `Gathin23_cleanyourtv`: `docs/devices/samsung-tizen.md`, `tests/test_samsung_tizen_note.py`, `docs/restore.md` (MIT).
- `simbasjungles_free-my-tv`: `README.md`, `CLAUDE.md`, `tizen/install.py`, `tizen/config.xml`, `web/tv.js` (MIT).
