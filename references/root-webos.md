# webOS with root: guide

**This skill does not run or automate root.** This file is a guide: if the user asks for it, first read the TV's model and firmware and compare them with the profile below, explain requirements and risks, and point to the sources. Without root there is no Home of your own and no deleting LG apps; with root those features exist, but they are only declared for that profile. If the model does not match, say so: there is no declared support.

## 1. The only thing the frxnnk project declares as supported

Source: `frxnnk_webos-liquid-glass-launcher` repo, `docs/root-automation.md` (MIT).

- **Only accepted profile:** model **49UN7310PSC**, firmware **04.64.00**, webOS **5.6.2-21**, build `jhericurl-jimna`, board **K6LP_ATSC_BR**. "No downgrade, flashing or declared support for other models" (lines 8-10).
- The plan lasts **five minutes**, is consumed **once** and is checked again before applying it; the preparation steps do not root (lines 47-48). Requires **Python 3.8+**.
- It pins the SlopBro and HBC sources **by commit and SHA-256**, and the HBC IPK **0.7.3** by SHA-256 (line 22; IPK hash on line 131).
- **It does not download or run the upstream `autoroot.sh`** (line 28); it includes its **AGPL-3.0-or-later** `COPYING` because it is a derivative.
- If anything stays uncertain: keep it, record recovery and return a **partial result with a physical boot pending**: "it does not reboot the TV to manufacture that confirmation" (lines 39-45).
- Safety stops: `DEVMODE_TOKEN_INVALID` (token turned into a directory) and `SIGNED_BACKUP_REQUIRED` (missing a verifiable backup of the original script) (lines 60-61).
- Hash of the stock script observed on that unit: `18b6b7cce77d640fef78d9d247d6fc672b0850bd728dd2a3c44105a485abc846` (line 66). It only works for that unit.

## 2. Verified risks (why this skill does not do it)

From `frxnnk_webos-liquid-glass-launcher`, `docs/root-and-home.md`:

- **HBC 0.7.3 opens root Telnet without authentication by default**; the normal disable flag is not consulted in the failsafe branch (lines 123-126). On that install, `/var/luna/preferences/webosbrew_telnet_disabled` had to be created and port 23 verified closed.
- HBC uses Dropbear **without explicitly disabling passwords** (line 127).
- The elevation **changes LS2 configuration and permissions** and enables a service with broad root execution + a persistent activity (lines 129-131).
- **SlopBro** downloads HBC without checking the hash, changes the persistent Developer Mode state, can rename LG's startup script and **implements no transactional rollback** (lines 134-136). Its client disables WSS certificate verification and delivers the payload over HTTP (line 138).
- There is no complete unroot procedure for this hardware (line 142).
- The previous upstream autoroot **broke Developer Mode** on that TV (the stock script had to be recovered and the token recreated by hand) (`root-automation.md` lines 54-56).

## 3. If the user insists anyway (limit of this skill)

1. Put in writing that there is **a single declared profile** and that whoever asks assumes the risk.
2. Require the user's explicit confirmation **in writing** before any step.
3. Always keep: root SSH access, the authorized key, a **backup of the TV state** and the HBC IPK (`root-and-home.md` line 146).
4. Verify after a cold boot: port 23 closed and root access by key.
5. Warn that there is **no automatic rollback** and no complete unroot procedure.

**Outside the scope of this skill:** running the exploit, touching the firmware, flashing, downgrading or automating any of those steps.

## Sources

- `frxnnk_webos-liquid-glass-launcher` (MIT): `docs/root-automation.md`, `docs/root-and-home.md`, `docs/local-installer.md`, `README.md`.
- The webOS Homebrew Channel root guides are at `github.com/webosbrew`: point there; this skill does not reproduce or run them.
