# LG webOS: what you can do without root

**Rule:** none of the reviewed sources documents a `pm disable` or a bloatware disable on webOS. The only thing verified without root is **installing the launcher as an app**, and that app **does not replace the LG Home**. Say it that way to the user; do not promise webOS debloat.

## 1. Entry without root: Developer Mode + Key Server

First of all, ask for the model and webOS version from the TV's information screen, with a photo if needed.

Flow verified in the `simbasjungles_free-my-tv` repo (`CLAUDE.md` lines 119-136, `webos/install.py`):

1. Ask for the **TV IP** (and the city, if API content is going to be used).
2. On the TV (the user does it): LG Content Store → **Developer Mode** → sign in with a free LG developer account (`webostv.developer.lge.com`) → **Dev Mode Status ON** (the TV reboots) → **Key Server ON**. It shows the IP and a **6-character passphrase** (length confirmed in the `danielthejoker18_FreeMyTvWebOS` repo, `scripts/install.py` line 86 and `README.md` line 289).
3. The installer downloads the encrypted private key from the TV's Key Server: `http://<IP>:9991/webos_rsa` (`danielthejoker18_FreeMyTvWebOS`, `scripts/install.py` lines 88-90). It goes over unencrypted HTTP: with Key Server on, anyone on the Wi-Fi who has the passphrase can download it, so turn it off when done (its `README.md` lines 88-89).
4. SSH on port **9922**, user **`prisoner`**. Developer Mode lasts **~40 days**; the app's **EXTEND** button renews it. **If it expires, the TV erases the developer apps** (`CLAUDE.md` line 135).
5. The passphrase is typed **in the user's terminal, not in the chat**; the unlocked key stays in `~/.ssh/freemytv_webos_<IP>` (`webos/install.py` docstring).

**Host fingerprint:** the first connection saves the fingerprint and the following ones require it. Use `danielthejoker18_FreeMyTvWebOS/scripts/install.py` (`accept-new` with its own `known_hosts`, line 135): it aborts if the fingerprint changes on that IP, but it trusts the first contact, so do it only on the home network. `simbasjungles_free-my-tv/webos/install.py` uses `StrictHostKeyChecking=no` and discards `known_hosts` (line 35): **do not run it without changing those options**. frxnnk uses `StrictHostKeyChecking=yes` with an already accepted fingerprint (`installer/transport.cjs`).

## 2. What you can do without root

| Action | Without root | With root |
|---|---|---|
| Install the launcher as an app (`python3 scripts/install.py <IP>` from FreeMyTvWebOS) | **yes** | yes |
| Make the launcher replace the LG Home | **no** | yes |
| Disable/uninstall bloatware | **no** | see `references/root-webos.md` |
| Service that relaunches the launcher (watchdog) | no | yes |
| SSH access on port 22 / service mode | no | yes |

Evidence: "It installs through LG's own Developer Mode, with nothing rooted or changed on the TV. LG's home screen stays where it is" (`simbasjungles_free-my-tv`, `README.md` line 108, and `docs/webos/full_description.html`). "Installing and optimizing requires verified root" (`frxnnk_webos-liquid-glass-launcher`, `docs/local-installer.md` line 11). Without root, frxnnk's app "opens by hand on every boot and the system Home takes over when you press Home" (its `docs/home-takeover.md`).

**Honest implication:** on webOS without root, the user gets a launcher that opens with a shortcut (a number key on the remote or the LG app list) but **Home still shows the factory Home**. Ask whether that works for them before continuing.

## 3. Verified practical details

- The first `install.py` must be run by **the user in their terminal** (it cannot answer the prompt from the agent chat) (`CLAUDE.md` line 127).
- `--uninstall` from the free-my-tv installer erases the app (`CLAUDE.md` line 136); the FreeMyTvWebOS one has no uninstall: it is removed from the LG app list.
- Third-party launchers query external services: FreeMyTvWebOS uses Open-Meteo, ipapi.co (sees your IP), TMDB and TVMaze. Warn before installing. Its "60 FPS" has no measurement in the repo: do not repeat it.
- When closing: turn Key Server off. Do not turn Developer Mode off if the launcher must remain: when it expires or is turned off, the TV erases those apps.
- On non-4K TVs, the build changes the resolution to 1280x720; on webOS 3 (2019 HD) a 1920x1080 app came out on a third of the screen (#402) (`CLAUDE.md` lines 130-133).
- webOS 3: `listLaunchPoints` denied → empty shelf; there is a separate flow with `python3 webos/apps.py` (`CLAUDE.md` line 137).
- A 2024 TV resets plain connections on port **3000** → use TLS on **3001** (#355/#357) (`CLAUDE.md` line 141).
- Verified watchdog: "a watchdog in a separate process returns to the factory Home after **three crashes in five minutes**, and a *boot check* keeps the choice after updates" (`simbasjungles_free-my-tv`, `README.md` line 315). **There is no "3 s" or "fallback to 45 s" figure in the sources: do not claim it.**

## 4. What NOT to do

- Do not say "you can disable bloatware on webOS without root": it is not documented.
- Do not copy `StrictHostKeyChecking=no`.
- Do not leave the passphrase or the private key in the repo or in the chat.
- Do not touch root in this skill: see `references/root-webos.md`.
- Do not promise the launcher replaces the Home without root: it is false.

## Sources

- `simbasjungles_free-my-tv`: `webos/install.py`, `CLAUDE.md`, `README.md`, `docs/webos/full_description.html` (MIT).
- `frxnnk_webos-liquid-glass-launcher`: `docs/local-installer.md`, `docs/home-takeover.md`, `installer/transport.cjs` (MIT).
- `danielthejoker18_FreeMyTvWebOS`: `scripts/install.py`, `README.md` (MIT).
