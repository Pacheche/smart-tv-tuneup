# Performance: what you can promise and with what evidence

**Rule:** every figure is cited with its **context, model and unit**. A number measured on one TV does not hold for another. If there is no before/after measurement on the user's TV, promise no improvement.

## 1. Verified figures (with their source and context)

| Figure | Exact context | Source |
|---|---|---|
| `katniss:interactor` at **30-33 % of one core at idle**, even right after a reboot; disabling voice took idle CPU from **~84 % to ~95 % free** | Hitachi CDH-LE504KSMART20 (TCL BeyondTV), Android 11, RTD2851, **2 GB** | `paisanos-io_tv-makeover`, `tvs/hitachi-cdh-le504ksmart20/notes.md` lines 3-4 |
| Free memory after boot: **~530-600 MB** with the factory Home → **~640-690 MB** with the cleanyourtv launcher | same TV, 2 GB | ibid line 5 |
| `voice_ap` + `katniss:interactor` **~45 % of one core all day**; group 6 stops katniss alone (~22 %); `voice_ap` is a native firmware daemon **and still has no root** | TCL BeyondTV RT2851 | `paisanos-io`, `tvs/tcl-beyondtv-rt2851/debloat.txt` lines 26-27, 85 |
| **"Debloating alone did not make apps faster; the launcher, voice and animation changes did."** | repo summary | `paisanos-io_tv-makeover`, `README.md` line 142 |
| Home: **96 MB vs 242 MB (−60 %)** | 98″ TCL Google TV, Android 14 | `simbasjungles_free-my-tv`, `README.md` line 32 |
| Home p90 frame time **31 → 15 ms**, janky frames **2.41 % → 0.07 %**, Home ~96 MB | Sony BRAVIA (bf1) | `Gathin23_cleanyourtv`, `examples/sony-bravia-bf1/debloat.txt` line 25 |
| Available memory **~227-310 MB**, total CPU **~20 %**, highest probe 3.2 % | LG 49UN7310PSC (webOS) | `frxnnk_webos-liquid-glass-launcher`, `docs/performance.md` line 250 |
| **60.29 FPS** with `requestAnimationFrame` for 3 s | same LG, "Mi pantalla" app | ibid, `docs/home-takeover.md` line 25 |
| Home parked **110 ms** vs cold start **~2.6 s** | same LG | ibid, `docs/performance.md` lines 257-258 |
| System Home: **5-9 ms of CPU and ~13-16 ms of GPU per frame** | DreamOS (Hisense) | `paisanos-io`, `README.md` line 141 |
| Measurement noise: two runs of the same build on a TCL C755 varied **0 ms** in key response, up to **45 ms** in cold start and **1 MB** in PSS | reference method | `Gathin23_cleanyourtv`, `docs/workflows/perf-ab.md` lines 46-48 |

**Honest reading:** on these TVs the biggest measured winner was **disabling voice** and **changing the launcher**; debloat alone did not speed up the apps.

## 2. Wi-Fi: check the real band before blaming the TV

- **Many TVs are 2.4 GHz only even when the SSID says "5GHz"**: the frequency in `dumpsys wifi` is what counts, not the network name. (`paisanos-io`, `skills/android-tv-debloat/SKILL.md` line 47; `skills/android-tv-debloat/references/quirks.md` lines 12-15.)
- The Hitachi above: "Wi-Fi radio is 2.4 GHz only" and the router isolated 2.4 and 5 GHz (`notes.md` line 6).
- Some routers keep the 2.4 and 5 GHz SSIDs separate: ask which network the TV is on (`paisanos-io`, `README.md` line 46).
- A documented case: the Wi-Fi country code falls back to `CN` and hides 5 GHz channels 100-144 (`Gathin23_cleanyourtv`, `examples/xiaomi-mitv-mteq0/debloat.txt` lines 25-26).

**In practice:** before promising "faster", read the Wi-Fi line of the snapshot and tell the user which band it is on.

## 3. How to measure before and after (minimum viable)

1. **TV at idle** (no apps open): free CPU and memory (`dumpsys cpuinfo`, `dumpsys meminfo`).
2. **Cold start** with a stopwatch: power off, power on, stopwatch until the Home is usable.
3. **Three user actions**: open YouTube, switch apps, go back to the Home, with a stopwatch on each.
4. Also record **model, firmware, Android/Tizen/webOS and Wi-Fi band**.

Compare with cleanyourtv's reference method (`docs/workflows/perf-ab.md`): if two runs of the same build vary by up to 45 ms on boot, an improvement smaller than that **is not an improvement**.

## 4. Limits and excuses to reject

- **"With debloat everything goes faster":** false per the source (above). Say what does change (voice, launcher, animations).
- **"I freed X MB and it no longer stutters":** without a before/after measurement on that TV, it is an anecdote.
- **"The chip is old, nothing can be done":** false; there are measured gains on old TVs, but they come from launcher/voice/animation, not magic.
- **`speed` → `speed-profile`:** on a TCL BeyondTV, every Play Store update returned the app to `speed-profile`. Without root it cannot be pinned: check with `dumpsys package dexopt` and repeat `compile -m speed` if needed.

## Sources

- `paisanos-io_tv-makeover` (MIT): `README.md`, `tvs/hitachi-cdh-le504ksmart20/notes.md`, `tvs/tcl-beyondtv-rt2851/debloat.txt`, `tvs/sony-bravia-bf1` (via cleanyourtv), `skills/android-tv-debloat/`.
- `Gathin23_cleanyourtv` (MIT): `docs/workflows/perf-ab.md`, `examples/sony-bravia-bf1/debloat.txt`, `examples/xiaomi-mitv-mteq0/debloat.txt`.
- `simbasjungles_free-my-tv` (MIT): `README.md`.
- `frxnnk_webos-liquid-glass-launcher` (MIT): `docs/performance.md`, `docs/home-takeover.md`.
