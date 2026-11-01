---
name: smart-tv-tuneup
description: "Use when a smart TV is slow (tele lenta, TV lenta), shows bloatware or ads, or the user wants to debloat, clean up or speed up an Android TV or Google TV (TCL, Hisense), tune an LG webOS or Samsung Tizen set, choose or install a launcher without replacing the factory Home, work over ADB, SDB or webOS SSH, close ADB when finished, or recover a TV that stopped responding after changes; also use when the user asks whether debloating really makes a TV faster or why their TV lags."
metadata:
  version: "0.1.0"
---

# smart-tv-tuneup

Esta skill es un procedimiento para que ejecutes vos, el agente: no la resumas ni se la pases a la persona como guía. Ajuste de televisor inteligente sin root. En Android TV/Google TV se limpia y se puede cambiar el Home; en LG webOS y Samsung Tizen solo se instala un launcher como app, que **no** reemplaza el Home de fábrica. Los cambios de Android se revierten con un registro guardado antes de tocar nada.

## Cómo aplicarla

- Las rutas son relativas a la carpeta de este `SKILL.md`. Python: `py` en Windows, `python3` en el resto.
- Corré vos los scripts y comandos. Pedile a la persona solo lo que exige la tele: activar la depuración, aceptar avisos, tocar el control o pasar la IP.
- Leé `references/` a medida que la necesites: la de la plataforma detectada, `rendimiento.md` para medir y `recuperacion.md` ante cualquier falla.
- Pedí aprobación antes del primer cambio. Si una regla o un script te frena, parate y explicá por qué: no busques otro camino.
- Sin terminal o sin acceso a la red de la tele, indicale los pasos a la persona y no des nada por hecho sin que confirme el resultado.

## Fases (en este orden, sin saltar ninguna)

Si piden apurarse o no preguntar, las fases siguen igual: identificar, hacer solo las preguntas sobre apps que usa, respaldar y proponer un primer lote chico. Si el tiempo no alcanza, decirlo y dejar el resto para otra sesión.

1. **Identificar (solo lectura).** `scripts/detect_tv.py <ip>` solo abre y lee puertos; no escribe nada. Registrar modelo exacto, firmware, plataforma y fingerprint antes de cualquier cambio.
2. **Preguntar apps.** Antes de apagar nada, preguntar al dueño qué apps usa de verdad, streaming, asistente de voz, Chromecast, medios USB y actualizaciones (se mantienen por defecto).
3. **Respaldar y medir base.** Capturar estado (paquetes, Home y quién responde, dueños de Wi-Fi, ajustes) y métricas tras un reinicio: MemAvailable, CPU en reposo, banda Wi-Fi real (un SSID llamado "5GHz" no prueba nada: mirar la frecuencia en `dumpsys wifi`).
4. **Mostrar el plan sin tocar nada.** `scripts/plan_android.py` corre offline; para webOS/Tizen, el plan manual. El usuario aprueba antes de la primera orden.
5. **Aplicar en lotes chicos y verificar.** En Android, con `tools/disable` de cleanyourtv, que guarda el registro y se niega a lo peligroso. Si se cambia el Home, el launcher nuevo se instala y verifica antes del lote que incluya el de fábrica. Tras cada lote: relectura de paquetes, Home responde, apps principales abren, botones reales del control. Esperar **≥45 s** antes de reiniciar: cleanyourtv dice ~15 s, pero una TCL BeyondTV perdió un lote al reiniciar enseguida (experiencia de un equipo) y hay listas TCL que esperan 60 s.
6. **Medir otra vez** igual que la base y comparar.
7. **Cerrar.** ADB se cierra por defecto y solo se da por cerrado si `tools/adb-closed.py` de cleanyourtv dice que la tele rechaza la conexión: un timeout no cuenta. Si la persona pide dejarlo abierto, explicar el riesgo y hacerlo solo si lo acepta de forma explícita. webOS: apagar Key Server; Developer Mode sigue encendido si el launcher debe quedar, porque al vencer la tele borra esas apps. Tizen: `sdb disconnect`.
8. **Informe.** Qué cambió, métricas antes/después con su unidad y contexto, y cómo revertir cada cosa. Sin medición antes y después, no se afirma ninguna mejora.

## Ruteo por plataforma

- **Android TV / Google TV (TCL, Hisense, Sony...):** ADB por 5555. `scripts/fetch_cleanyourtv.py`, lista del modelo más parecido, guardas de core y de Wi-Fi. El launcher nuevo pasa a ser el Home; el de fábrica se deshabilita solo tras verificar que otro responde a HOME. Ver `references/android.md`.
- **LG webOS (sin root):** Developer Mode, SSH 9922 (`prisoner`), huella guardada; launcher como app, sin tocar el Home nativo. Flujo en `references/webos.md`; root: la skill guía y no lo ejecuta, `references/root-webos.md`.
- **Samsung Tizen (sin root):** sdb 26101 con Developer Mode y certificado (Samsung para 2023+/Tizen 7+, Tizen para 2015-2022). No hay shell `pm`: no existe debloat de paquetes; launcher como app firmada. Ver `references/tizen.md`.

- **Otra plataforma (Fire TV, Roku, VIDAA...):** si la persona ya la nombró, no hace falta IP ni sonda; explicá que esta skill no la cubre y no cambies nada. No adaptes comandos de otra plataforma.

## Reglas inviolables

- `pm disable-user --user 0` siempre; **nunca** `pm uninstall`, y nunca `pm clear` sobre un launcher.
- Un comando `pm` por llamada; verificar antes de seguir. Sin el registro de cleanyourtv no se aplica nada.
- No tocar `TV_INPUT_HARDWARE`, `TV_INPUT_BUTTON`, `CONNECT_INPUT`, el core ni los menús de fábrica.
- Antes de deshabilitar el launcher de fábrica: otro launcher debe responder a HOME.
- Si setupwraith es dueña de la Wi-Fi guardada, no se deshabilita: la tele se cae de la red y ADB con ella.
- Cifras de rendimiento siempre con modelo, contexto y unidad; comprobar la banda Wi-Fi real.
- Una app actualizada pierde `cmd package compile -m speed` y vuelve a `speed-profile` (observado en una tele TCL): avisar que no es permanente.
- SSH webOS: guardar la huella y exigirla después, nunca `StrictHostKeyChecking=no`. Binarios externos fijados por SHA-256. Sin secretos ni datos de la tele en el repo ni en el chat.
- ADB de red va en texto plano. Con `ro.adb.secure=0`, o sin definir en build debug o Android 4.4, cualquier aparato de la red obtiene shell: decirlo siempre al cerrar.

## Excusas y los 7 fallos que impiden

| Excusa típica | Fallo que provoca |
| --- | --- |
| "Es una TV Android más, ya conozco el modelo" | Cambiar sin identificar modelo/firmware ni respaldar antes. |
| "Los nombres de los paquetes dicen todo" | `grep` de nombres sin leer `dumpsys package`, `pm clear` sobre el launcher, reinicio inmediato, sin relectura y sin preguntar apps al dueño. |
| "Esto va a hacer bootloop" | Afirmar bootloop sin exigir primero que otro launcher responda a HOME. |
| "En LG no hace falta root" o "sin root no se puede nada" | Afirmarlo sin fuente. Sin root hay launcher como app, sin Home ni borrado de apps de LG; el root exige comparar modelo y firmware con el perfil. |
| "En Samsung no se puede" | Decir que no se puede e inventar menús en vez de ofrecer el launcher como app por Developer Mode y certificado. |
| "Hay que hacer factory reset o flashear" | Saltar a lo destructivo antes de: arranque en frío → app de control remoto del celular o ratón/teclado USB → Ajustes > Apps > habilitar → `restore` con registro. Factory reset al final, avisando que cierra todas las sesiones. Flashear queda fuera de esta skill. |
| "ADB queda abierto, no importa" | Dejar ADB abierto sin avisar y sin aceptación explícita, o darlo por cerrado sin el rechazo de `tools/adb-closed.py`. |

## Referencias

[android.md](references/android.md) · [webos.md](references/webos.md) · [tizen.md](references/tizen.md) · [root-webos.md](references/root-webos.md) · [rendimiento.md](references/rendimiento.md) · [recuperacion.md](references/recuperacion.md) · [casos-de-evaluacion.md](references/casos-de-evaluacion.md)
