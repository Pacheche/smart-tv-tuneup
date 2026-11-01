# Android TV / Google TV: flujo completo

Toda la parte Android es sin root y sin `uninstall`. Si un paso no puede hacerse, se para y se avisa; no se salta.

## 1. Identificar (solo lectura)

- Modelo, marca, firmware y fingerprint: `getprop ro.product.model`, `ro.build.fingerprint`, `ro.board.platform`, `ro.build.version.release`.
- Puertos: 5555 (ADB de red). Si está cerrado: falta USB debugging, o la tele solo ofrece Wireless debugging (Google TV) → `adb pair` con el código de Desarrollador > Depuración inalámbrica, luego `adb connect`, `adb tcpip 5555`.
- La primera autorización sin "Permitir siempre" vale solo para esa conexión: pedir en la tele "Permitir siempre" y reintentar una vez (sin eso, la siguiente llamada se cuelga ~120 s).
- Si la tele no responde tras un reinicio: en TCL Android TV el 5555 vuelve a abrir ~25 s después del arranque, antes de `sys.boot_completed`; esperar a `getprop sys.boot_completed` antes de medir nada.
- Buscar el perfil del modelo más parecido en los ejemplos de cleanyourtv (marca, modelo, chip como rtd2851/mt9221/s905x4, Android, nombre de plataforma como BeyondTV/PatchWall) y leer su cabecera antes de decidir.

## 2. Preguntar apps (antes de tocar nada)

Lista de preguntas con recomendación, nunca "apago lo que suene a basura": apps que usa de verdad (agrupadas), los cuatro apps del dock en orden, asistente de voz (recomendar apagar si come CPU), Chromecast, reproductor USB, salvapantallas, actualizaciones de firmware (por defecto mantener), DNS privado opcional (no bloquea anuncios de YouTube).

## 3. Respaldar y medir base

- Guardar: `getprop`, listas de paquetes, todos los ajustes, quién responde HOME y sus reclamantes, entradas TV, dueños de Wi-Fi (`dumpsys wifi`), y un resumen (modelo, board, Android, GPU, memoria, almacenamiento, banda/RSSI de Wi-Fi, CPU top).
- Base tras un reinicio, igual que la medida final: esperar ~150 s tras el arranque; comparar MemAvailable, swap y CPU en reposo, no un pantallazo en uso. Capturar con `adb shell cat /proc/meminfo` y `adb shell top -b -n 1`.
- CPU en reposo: en Realtek/MediaTek el load average es mentira (hilos del kernel en estado D); usar `%idle` de `top`.
- Vídeo con tirones: YouTube > Ajustes > "Datos para expertos" durante la reproducción (velocidad, salud del búfer, cuadros perdidos) + banda real de `dumpsys wifi`: muchas teles son de solo 2,4 GHz aunque el SSID diga "5GHz" (la frecuencia de `dumpsys wifi` es la verdad, no el nombre del SSID).
- `/data` con menos de ~10 % libre: las instalaciones fallan y la tele se arrastra.

## 4. Plan sin tocar nada

Bajar las herramientas con `scripts/fetch_cleanyourtv.py`; el comando imprime la carpeta. Partir de la lista más parecida de `examples/<marca-modelo>/debloat.txt`, nunca de un `grep` de nombres.

`scripts/plan_android.py` corre offline sobre esa lista y las capturas de `pm list packages -e --user 0`, `pm list packages -d --user 0` y `dumpsys wifi`, con un `--keep` por cada app que la persona usa. `--salida lote.txt` deja solo lo aplicable. Reglas que implementa (origen: cleanyourtv `tools/disable.sh` líneas 68-69, commit `6e8615eb`; fábrica: free-my-tv `HomeMode.java`):

- `CORE_RE`: núcleo de Android y middleware TV (systemui, settings, phone, shell, permissioncontroller, packageinstaller, providers, com.cltv.mal, com.mediatek.*) → la lista que toque esto sale con exit 1 y no se aplica.
- `CORE_OK`: excepciones probadas: providers de calendar/contacts/userdictionary/blockednumber.
- Menús de fábrica: rechazados. Dueños de una Wi-Fi guardada: rechazados; sin captura de `dumpsys wifi`, setupwraith también.

El plan no puede comprobar lo que exige hablar con la tele (HOME, `TV_INPUT_HARDWARE`, handlers): esas guardas corren en `tools/disable`.

Nunca deshabilitar, pase lo que pase el nombre: la app de Live TV y los servicios de entradas (un driver de entrada deshabilitado deja HDMI en "No Signal" hasta restauración completa y arranque en frío), el menú de fuentes/entradas, control remoto y emparejamiento Bluetooth, teclado, Play Store y Play Services, Ajustes, y `com.google.android.tungsten.setupwraith` cuando `dumpsys wifi` la muestra como dueña de la Wi-Fi guardada (deshabilitarla borra esa red y tira la tele de la red, y con ella ADB y el mando del celular). No tocar `TV_INPUT_HARDWARE`, `TV_INPUT_BUTTON` ni `CONNECT_INPUT`.

## 5. Aplicar en lotes y verificar

Si se va a cambiar el Home, hacer antes la sección 6. Sin launcher nuevo verificado, sacar el de fábrica del lote: su deshabilitado va siempre por `tools/disable`, nunca con un `pm` suelto.

- Aplicar cada lote con cleanyourtv desde su carpeta: `TV_HOST=<ip> tools/disable.sh <lote.txt>` o `tools/disable.ps1` en Windows, con su venv preparado. Antes del primer comando guarda en `~/.cleanyourtv/` el estado de cada paquete, el dueño de Home y las escalas de animación; ante un core sale sin mandar nada. Sin registro no se sigue.
- Si hace falta un `pm` suelto: un comando por llamada, siempre `pm disable-user --user 0 <pkg>`; **nunca** `pm uninstall`, y nunca `pm clear` sobre el launcher ni sobre nada crítico (borra sus datos).
- Tras cada lote, releer con `pm list packages -e --user 0`: un comando sin error no prueba que el paquete quedó apagado.
- Re-correr la lista completa está bien: el registro conserva el primer estado.
- Tras cada lote: pulsar Home, captura de pantalla, abrir las apps streaming principales (Netflix/HDMI suelen dar pantalla negra en captura: comprobar `mResumedActivity`), y para lotes de voz/mando pedir al usuario que pulse los botones reales.
- Dejar para el final los paquetes con instalador (TCL `com.tcl.guard`, `appmarket2`).
- **Espera antes de reiniciar: ≥45 s tras el último `pm disable-user`.** Los docs de cleanyourtv recomiendan ~15 s (`PROMPT.md`, `docs/TROUBLESHOOTING.md`) y algunas listas esperan 10-30 s, pero hay casos donde no bastó: en una TCL BeyondTV real, reiniciar enseguida tras un lote hizo perderlo completo (experiencia de un equipo); en una TCL 40S5400A un `adb reboot` "a few seconds" después del lote devolvió el lote entero habilitado y solo quedó estable con 60 s (`examples/tcl-40s5400a/debloat.txt` líneas 67-68); en un Xiaomi (aesp0) `sync` + 15 s no bastaron —volvieron los últimos ocho paquetes— y ~40 s sí (`examples/xiaomi-mitv-aesp0/debloat.txt` líneas 49-50); y una Sony BRAVIA pide ~90 s (`examples/sony-bravia-4k-ur3/debloat.txt` línea 37). Por eso este skill exige ≥45 s siempre, y verificar tras el arranque con `pm list packages -e --user 0`.
- Varios firmwares reactivan paquetes en cada arranque (p. ej. TCL `com.tcl.overseasappshow`, `com.tcl.usercenter`): re-leer la lista tras el reinicio y anotarlo en la cabecera.

## 6. Cambiar el Home (opcional)

- En Android sí se reemplaza el Home. `launcher/build-and-install.sh` de cleanyourtv compila, instala, cambia el Home y revierte si no queda en el nuevo. Requiere JDK 17 y Android SDK; compilar fuera de carpetas sincronizadas (en una tele real Gradle se colgó dentro de Google Drive).
- Solo deshabilitar el launcher de fábrica (`com.google.android.tvlauncher` u otro) **después de verificar que otra cosa responde a HOME**: `cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME` y `cmd package query-activities --brief -a android.intent.action.MAIN -c android.intent.category.HOME`. Si la respuesta es `android` (chooser), si setupwraith sigue activa y responde HOME por delante, o si no hay otro launcher instalado: **no se deshabilita el de fábrica**. Las apps de configuración y el asistente de instalación también "responden HOME" pero no son launchers.
- Afirmar "bootloop" exige esto: si el nuevo launcher no responde a HOME y el de fábrica está deshabilitado, la tele queda en chooser o en blanco; eso no es bootloop y se arregla habilitando el de fábrica de nuevo.

## 7. Velocidad (opcional, con expectativas honestas)

- Escalas de animación a 0.5 (`settings put global window_animation_scale 0.5`, ídem `transition_animation_scale`, `animator_duration_scale`); `restore` las restablece.
- Compilar las apps del dock a full: `cmd package compile -m speed -f <pkg>`, una por llamada; verificar con `dumpsys package dexopt` (`status=speed`) en vez de reintentar. **Nota:** una actualización por Play Store devuelve la app a `speed-profile` (observado en una TCL BeyondTV): sin root no se puede fijar, hay que repetirlo.
- Modo extreme solo en teles muy débiles (1 GB o menos, Android 7-9) y con el dueño de acuerdo: escalas a 0, apps sin segundo plano (`appops RUN_ANY_IN_BACKGROUND ignore` + bucket `rare`; nunca música, casting, launcher, teclado ni servicios de entrada) y `pm trim-caches`.

## 8. Cerrar ADB

- Cerrar es lo predeterminado. Apagar en la tele: USB debugging, depuración de red y depuración inalámbrica.
- Si la persona pide dejarlo abierto, explicar que ADB de red va en texto plano y hacerlo solo si lo acepta de forma explícita. Mejor alternativa: cerrarlo y anotar cómo reabrirlo.
- Comprobar desde la carpeta de cleanyourtv con `py -I tools/adb-closed.py <ip>`: **solo exit 0 cuenta como cerrado** (la tele rechazó la conexión). Timeout o nada responde = exit 2 = no se pudo comprobar (la tele puede estar apagada, dormida o en otra red); no se afirma "cerrado".
- Si la tele tiene `ro.adb.secure=0` (o no lo define en build debug o Android 4.4), avisar con texto plano: el puerto 5555 da shell a cualquier aparato de la red sin pedir permiso.

## 9. Revertir

`TV_HOST=<ip> tools/restore.sh <la misma lista>` (o `restore.ps1`): reproduce el registro, incluido el Home y las escalas de animación. Sin registro habilita toda la lista y pone las escalas en 1.0: avisarlo.

## Referencias de origen

- Guardas CORE, Home, setupwraith y cierre: Gathin23/cleanyourtv (`tools/disable.sh`, `tools/adb-closed.py`, `docs/TROUBLESHOOTING.md`), commit `6e8615eb`.
- Flujo, métricas y preguntas: paisanos-io/tv-makeover (`skills/android-tv-debloat/SKILL.md`, `references/quirks.md`).
- `pm disable-user` reversible y watchdog de launcher: simbasjungles/free-my-tv (`app/src/io/freemytv/HomeMode.java`).
