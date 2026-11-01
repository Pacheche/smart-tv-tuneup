# Rendimiento — qué se puede prometer y con qué evidencia

**Regla:** toda cifra se cita con su **contexto, modelo y unidad**. Un número medido en una tele no vale para otra. Si no hay medición antes/después en la tele del usuario, no se promete mejora.

## 1. Cifras verificadas (con su fuente y contexto)

| Cifra | Contexto exacto | Fuente |
|---|---|---|
| `katniss:interactor` al **30-33 % de un core en reposo**, incluso recién reiniciada; apagar la voz llevó el CPU en reposo de **~84 % a ~95 % libre** | Hitachi CDH-LE504KSMART20 (TCL BeyondTV), Android 11, RTD2851, **2 GB** | `paisanos-io_tv-makeover`, `tvs/hitachi-cdh-le504ksmart20/notes.md` líneas 3-4 |
| Memoria libre tras arranque: **~530-600 MB** con el Home de fábrica → **~640-690 MB** con el launcher cleanyourtv | misma tele, 2 GB | idem línea 5 |
| `voice_ap` + `katniss:interactor` **~45 % de un core todo el día**; el grupo 6 frena solo katniss (~22 %); `voice_ap` es un daemon nativo del firmware **y sigue sin root** | TCL BeyondTV RT2851 | `paisanos-io`, `tvs/tcl-beyondtv-rt2851/debloat.txt` líneas 26-27, 85 |
| **"Debloating alone did not make apps faster; the launcher, voice and animation changes did."** | resumen del repo | `paisanos-io_tv-makeover`, `README.md` línea 142 |
| Home: **96 MB vs 242 MB (−60 %)** | 98″ TCL Google TV, Android 14 | `simbasjungles_free-my-tv`, `README.md` línea 32 |
| Home p90 frame time **31 → 15 ms**, janky frames **2,41 % → 0,07 %**, Home ~96 MB | Sony BRAVIA (bf1) | `Gathin23_cleanyourtv`, `examples/sony-bravia-bf1/debloat.txt` línea 25 |
| Memoria disponible **~227-310 MB**, CPU total **~20 %**, la sonda más alta 3,2 % | LG 49UN7310PSC (webOS) | `frxnnk_webos-liquid-glass-launcher`, `docs/performance.md` línea 250 |
| **60,29 FPS** con `requestAnimationFrame` durante 3 s | mismo LG, app "Mi pantalla" | idem, `docs/home-takeover.md` línea 25 |
| Home aparcada **110 ms** vs arranque en frío **~2,6 s** | mismo LG | idem, `docs/performance.md` líneas 257-258 |
| Home del sistema: **5-9 ms de CPU y ~13-16 ms de GPU por frame** | DreamOS (Hisense) | `paisanos-io`, `README.md` línea 141 |
| Ruido de medición: dos corridas del mismo build en una TCL C755 variaron **0 ms** en respuesta de tecla, hasta **45 ms** en arranque en frío y **1 MB** en PSS | método de referencia | `Gathin23_cleanyourtv`, `docs/workflows/perf-ab.md` líneas 46-48 |

**Lectura honesta:** en estas teles el mayor ganador medido fue **apagar la voz** y **cambiar el launcher**; el debloat por sí solo no aceleró las apps.

## 2. Wi-Fi: comprobar la banda real antes de culpar a la tele

- **Muchas teles son solo 2.4 GHz aunque el SSID diga "5GHz"**: la frecuencia de `dumpsys wifi` es la que manda, no el nombre de la red. (`paisanos-io`, `skills/android-tv-debloat/SKILL.md` línea 47; `skills/android-tv-debloat/references/quirks.md` líneas 12-15.)
- El Hitachi de arriba: "Wi-Fi radio is 2.4 GHz only" y el router aislaba 2,4 y 5 GHz (`notes.md` línea 6).
- Algunos routers mantienen los SSID de 2,4 y 5 GHz separados: preguntar en qué red está la tele (`paisanos-io`, `README.md` línea 46).
- Un caso documentado: el código de país Wi-Fi cae a `CN` y esconde canales 5 GHz 100-144 (`Gathin23_cleanyourtv`, `examples/xiaomi-mitv-mteq0/debloat.txt` líneas 25-26).

**En la práctica:** antes de prometer "más rápido", leer la línea de Wi-Fi del snapshot y decirle al usuario en qué banda está.

## 3. Cómo medir antes y después (mínimo viable)

1. **Reposo de la tele** (sin apps abiertas): CPU y memoria libres (`dumpsys cpuinfo`, `dumpsys meminfo`).
2. **Arranque en frío** con cronómetro: apagar, encender, cronómetro hasta el Home usable.
3. **Tres acciones del usuario**: abrir YouTube, cambiar de app, volver al Home — cronómetro en cada una.
4. Registrar también **modelo, firmware, Android/Tizen/webOS y banda Wi-Fi**.

Comparar con el método de referencia de cleanyourtv (`docs/workflows/perf-ab.md`): si dos corridas del mismo build varían hasta 45 ms en arranque, una mejora menor que eso **no es mejora**.

## 4. Límites y excusas a rechazar

- **"Con el debloat todo va más rápido":** falso según la fuente (arriba). Decir qué sí cambia (voz, launcher, animaciones).
- **"Liberé X MB y ya no traba":** sin medición antes/después en esa tele, es anécdota.
- **"El chip es viejo, no se puede hacer nada":** falso; hay ganancias medidas en teles viejas, pero son de launcher/voz/animación, no magia.
- **`speed` → `speed-profile`:** en una TCL BeyondTV, cada actualización por Play Store devolvió la app a `speed-profile`. Sin root no se puede fijar: comprobar con `dumpsys package dexopt` y repetir `compile -m speed` si hace falta.

## Fuentes

- `paisanos-io_tv-makeover` (MIT): `README.md`, `tvs/hitachi-cdh-le504ksmart20/notes.md`, `tvs/tcl-beyondtv-rt2851/debloat.txt`, `tvs/sony-bravia-bf1` (vía cleanyourtv), `skills/android-tv-debloat/`.
- `Gathin23_cleanyourtv` (MIT): `docs/workflows/perf-ab.md`, `examples/sony-bravia-bf1/debloat.txt`, `examples/xiaomi-mitv-mteq0/debloat.txt`.
- `simbasjungles_free-my-tv` (MIT): `README.md`.
- `frxnnk_webos-liquid-glass-launcher` (MIT): `docs/performance.md`, `docs/home-takeover.md`.
