# LG webOS — qué se puede hacer sin root

**Regla:** ninguna de las fuentes revisadas documenta un `pm disable` ni un deshabilitado de bloatware en webOS. Lo único verificado sin root es **instalar el launcher como app**, y esa app **no reemplaza el Home de LG**. Decirlo así al usuario; no prometer debloat webOS.

## 1. Entrada sin root: Developer Mode + Key Server

Antes de nada, pedir modelo y versión de webOS desde la pantalla de información de la tele, con una foto si hace falta.

Flujo verificado en `simbasjungles_free-my-tv` repo (`CLAUDE.md` líneas 119-136, `webos/install.py`):

1. Pedir la **IP de la tele** (y la ciudad, si se va a usar contenido con API).
2. En la tele (lo hace el usuario): LG Content Store → **Developer Mode** → entrar con cuenta LG developer gratis (`webostv.developer.lge.com`) → **Dev Mode Status ON** (la tele se reinicia) → **Key Server ON**. Muestra IP y una **passphrase de 6 caracteres** (longitud confirmada en `danielthejoker18_FreeMyTvWebOS` repo, `scripts/install.py` línea 86 y `README.md` línea 289).
3. El instalador baja la clave privada cifrada del Key Server de la tele: `http://<IP>:9991/webos_rsa` (`danielthejoker18_FreeMyTvWebOS`, `scripts/install.py` líneas 88-90). Va por HTTP sin cifrar: con Key Server encendido, cualquiera en la Wi-Fi que tenga la passphrase puede bajarla, así que se apaga al terminar (su `README.md` líneas 88-89).
4. SSH al puerto **9922**, usuario **`prisoner`**. Developer Mode dura **~40 días**; el botón **EXTEND** de la app lo renueva. **Si vence, la tele borra las apps de desarrollador** (`CLAUDE.md` línea 135).
5. La passphrase se teclea **en la terminal del usuario, no en el chat**; la clave desbloqueada queda en `~/.ssh/freemytv_webos_<IP>` (`webos/install.py` docstring).

**Huella del host:** la primera conexión guarda la huella y las siguientes la exigen. Usar `danielthejoker18_FreeMyTvWebOS/scripts/install.py` (`accept-new` con `known_hosts` propio, línea 135): aborta si la huella cambia en esa IP, pero confía en el primer contacto, así que se hace solo en la red de casa. `simbasjungles_free-my-tv/webos/install.py` usa `StrictHostKeyChecking=no` y descarta `known_hosts` (línea 35): **no correrlo sin cambiar esas opciones**. frxnnk usa `StrictHostKeyChecking=yes` con huella ya aceptada (`installer/transport.cjs`).

## 2. Qué se puede hacer sin root

| Acción | Sin root | Con root |
|---|---|---|
| Instalar el launcher como app (`python3 scripts/install.py <IP>` de FreeMyTvWebOS) | **sí** | sí |
| Que el launcher reemplace al Home de LG | **no** | sí |
| Deshabilitar/desinstalar bloatware | **no documentado** | no cubierto en esta skill |
| Servicio que relanza el launcher (watchdog) | no | sí |
| Acceso SSH en puerto 22 / service mode | no | sí |

Evidencia: "It installs through LG's own Developer Mode, with nothing rooted or changed on the TV. LG's home screen stays where it is" (`simbasjungles_free-my-tv`, `README.md` línea 108, y `docs/webos/full_description.html`). "Instalar y optimizar requiere root comprobado" (`frxnnk_webos-liquid-glass-launcher`, `docs/local-installer.md` línea 11). Sin root, la app de frxnnk "se abre a mano en cada arranque y el Home del sistema toma el control al pulsar Inicio" (su `docs/home-takeover.md`).

**Implicación honesta:** en webOS sin root, el usuario obtiene un launcher que abre con un atajo (tecla numérica en el mando o la lista de apps de LG) pero **Inicio sigue mostrando el Home de fábrica**. Preguntar si eso le sirve antes de seguir.

## 3. Detalles prácticos verificados

- El primer `install.py` debe correrlo **el usuario en su terminal** (no puede responder al prompt desde el chat del agente) (`CLAUDE.md` línea 127).
- `--uninstall` del instalador de free-my-tv borra la app (`CLAUDE.md` línea 136); el de FreeMyTvWebOS no trae desinstalación: se quita desde la lista de apps de LG.
- Los launchers de terceros consultan servicios externos: FreeMyTvWebOS usa Open-Meteo, ipapi.co (ve tu IP), TMDB y TVMaze. Avisarlo antes de instalar. Su "60 FPS" no tiene medición en el repo: no repetirlo.
- Al cerrar: apagar Key Server. No apagar Developer Mode si el launcher debe quedar: al vencer o apagarse, la tele borra esas apps.
- En TVs no 4K, el build cambia la resolución a 1280x720; en webOS 3 (2019 HD) una app 1920x1080 salía en un tercio de la pantalla (#402) (`CLAUDE.md` líneas 130-133).
- webOS 3: `listLaunchPoints` denegado → estante vacío; hay flujo aparte con `python3 webos/apps.py` (`CLAUDE.md` línea 137).
- Una TV 2024 resetea conexiones planas en el puerto **3000** → usar TLS en **3001** (#355/#357) (`CLAUDE.md` línea 141).
- Watchdog verificado: "un watchdog en proceso aparte vuelve al Home de fábrica tras **tres caídas en cinco minutos**, y un *boot check* conserva la elección tras actualizaciones" (`simbasjungles_free-my-tv`, `README.md` línea 315). **No hay cifra de "3 s" ni de "fallback a 45 s" en las fuentes: no afirmarla.**

## 4. Qué NO hacer

- No decir "se puede deshabilitar bloatware en webOS sin root": no está documentado.
- No copiar `StrictHostKeyChecking=no`.
- No dejar la passphrase ni la clave privada en el repo ni en el chat.
- No tocar root en esta skill: ver `references/root-webos.md`.
- No prometer que el launcher reemplaza el Home sin root: es falso.

## Fuentes

- `simbasjungles_free-my-tv`: `webos/install.py`, `CLAUDE.md`, `README.md`, `docs/webos/full_description.html` (MIT).
- `frxnnk_webos-liquid-glass-launcher`: `docs/local-installer.md`, `docs/home-takeover.md`, `installer/transport.cjs` (MIT).
- `danielthejoker18_FreeMyTvWebOS`: `scripts/install.py`, `README.md` (MIT).
