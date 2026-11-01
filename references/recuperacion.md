# Recuperación — orden estricta, sin saltos

**Regla:** nunca saltar a factory reset. Seguir la escalera en orden; flashear queda fuera de esta skill. Todo lo que se cambia en Android con esta skill es **reversible con `pm enable`** porque nunca se usa `pm uninstall` (`Gathin23_cleanyourtv`, `docs/DOS-AND-DONTS.md` líneas 19-23).

## 0. Prevención (antes de tocar nada)

- Guardar la **lista aplicada** y el **registro** que hace el script antes de cambiar nada: en `~/.cleanyourtv/`, un archivo por tele y por lista, con el estado de cada paquete, **quién era dueño de Home** y las tres escalas de animación (`docs/restore.md` líneas 24-30).
- Si no hay registro, el restore habilita la lista entera y pone las escalas en `1.0` (líneas 59-60) — por eso el registro importa.
- Nunca deshabilitar el **único** launcher sin tener otro que responda a HOME (casos de bootloop verificados abajo).

## 1. La escalera de recuperación (en este orden)

Fuente: `Gathin23_cleanyourtv`, `docs/TROUBLESHOOTING.md` líneas 679-689 y `docs/faq.md` líneas 9-20.

1. **Esperar diez minutos** una vez (muchos "bootloops" son arranques lentos).
2. **Arranque en frío:** apagar del enchufe, esperar, encender. Repetir la medición.
3. **Mando del teléfono o ratón/teclado USB** para recuperar navegación si el mando no responde (casos documentados con mouse USB: `docs/devices/hisense-65d62qh.md`).
4. **Modo seguro:** mantener Power durante la animación de arranque (en muchas teles) — desactiva apps añadidas.
5. **Ajustes > Apps > mostrar apps del sistema > habilitar** el launcher/paquete en cuestión (o `pm enable <pkg>` si ADB responde).
6. **Recuperar la red:** si la Wi-Fi guardada era de setupwraith, reconectar no alcanza: olvidar la red y unirla de nuevo desde la tele, con control o teclado USB (`TROUBLESHOOTING.md` 633-643). Otra opción: un hotspot con el **mismo nombre y contraseña** de la red vieja. Después, reactivar la depuración si se apagó.
7. **Reintentar ADB** justo después de encender (`adb connect <ip>:5555` durante un par de minutos).
8. **`tools/restore.sh <lista>`** (o `restore.ps1` en Windows) con el registro: es el camino normal en cuanto ADB responde (`docs/restore.md` líneas 5-20).
9. **Borrar partición de caché** desde el menú de recuperación.
10. **Factory reset desde el menú de recuperación — ÚLTIMO RECURSO.** Avisar antes que cierra todas las sesiones.

## 2. Qué implica el factory reset (decirlo antes de hacerlo)

- "Everything these tools change lives in the user data the reset wipes, so **every disabled app comes back** and the new launcher is gone, **along with your own apps and accounts**." (`docs/faq.md` líneas 17-18.)
- Una tele que sigue en bucle **después** del reset apunta a hardware, no al debloat (`docs/faq.md` líneas 19-20).
- Antes del reset en Google TV: re-habilitar `setupwraith` si se deshabilitó (`docs/TROUBLESHOOTING.md` línea 603 y `docs/devices/fpd-cg50-c3.md`).

## 3. Casos reales de "bootloop" y su causa (no afirmar sin verificar)

| Caso | Causa real | Recuperación |
|---|---|---|
| KitKat COOP COTV-0001, 17 paquetes | se deshabilitó el **único** launcher sin reemplazo | re-habilitar ese launcher; la tele seguía respondiendo ADB (`TROUBLESHOOTING.md` 545-554) |
| Haier H50H5F, reinicios en bucle | causa **desconocida**; el reporte no la establece | `pm enable` de la lista aplicada si queda tiempo entre reinicios (528-544) |
| Stick Android con paquetes core | se tocó `com.android.providers.*`, overlays, etc. | `pm enable` + reinicio si ADB vive; si no, recovery (`515-527`) |
| JVC LT-43N7115, pantalla en el arranque | se deshabilitó el launcher de fábrica en CVTE | escalera completa de arriba (679-689) |
| ZTE B866F | deshabilitar **todos** los launchers dispara un factory reset en el siguiente arranque (`docs/devices/zte-b866f.md`) | evitar: nunca dejar la tele sin HOME |
| Google TV, Home abre una pantalla de recuperación | setupwraith responde HOME y lleva a `RecoveryActivity` (`tools/disable.sh` 192-196) | habilitar el launcher de fábrica y correr `restore` |

**Regla de honestidad:** si el usuario dice "se queda en el logo", **no** afirmar "lo rompiste con el debloat" sin comprobar: (a) qué paquete respondía a HOME antes y después (`cmd package resolve-activity ... category.HOME`), (b) si ADB sigue vivo, (c) qué lote se aplicó y cuándo. Pedir foto de la pantalla.

## 4. Si ADB se cerró

- Verificar con `tools/adb-closed.py` de cleanyourtv: **exit 0 solo si la tele rechaza la conexión**; timeout o sin respuesta = exit 2 (no es "cerrado"). (`Gathin23_cleanyourtv`, `tools/adb-closed.py` y su test.)
- Si la tele rechaza: reactivar *Depuración por Wi-Fi* desde Ajustes con el mando o el mouse; el puerto cambia, leerlo de la pantalla o `adb mdns services`.
- **Cerrar ADB al terminar** por defecto y avisar en texto plano: en firmware con `ro.adb.secure=0` (o sin definir), cualquier equipo de la LAN recibe shell (`docs/faq.md` líneas 27-29). "No leaving ADB open" es regla del proyecto (`DOS-AND-DONTS.md` línea 36).

## 5. Reglas que evitan llegar aquí

- Un solo comando por llamada; lotes chicos con verificación entre lote y lote.
- **≥45 s de espera antes de reiniciar** tras deshabilitar (los docs de cleanyourtv dicen ~15 s: `PROMPT.md` línea 116 y `TROUBLESHOOTING.md` línea 963; en `examples/tcl-40s5400a/debloat.txt` líneas 67-68, `adb reboot` "a few seconds" después del último lote **devolvió el lote entero**, y repetir con **60 s** de espera lo dejó todo deshabilitado; en `examples/xiaomi-mitv-aesp0/debloat.txt` línea 49 ni `sync` ni 15 s bastaron; en `examples/sony-bravia-bf1/debloat.txt` línea 15 recomiendan ~30 s; en una **TCL BeyondTV real** se perdió un lote al reiniciar enseguida: experiencia de un equipo). Usar 45 s como mínimo y más si la tele es lenta.
- Nunca `pm uninstall`; nunca `pm clear` sobre un launcher.
- No tocar `TV_INPUT_HARDWARE`, `TV_INPUT_BUTTON`, `CONNECT_INPUT`, paquetes core ni menús de fábrica (`DOS-AND-DONTS.md` línea 45).
- Antes de deshabilitar `setupwraith`: `dumpsys wifi | grep -o 'cname=[^ ]*'` — si es el dueño de la Wi-Fi guardada, primero olvidar y volver a unir la red (`TROUBLESHOOTING.md` 633-643).

## Fuentes

- `Gathin23_cleanyourtv` (MIT): `docs/restore.md`, `docs/faq.md`, `docs/TROUBLESHOOTING.md`, `docs/DOS-AND-DONTS.md`, `tools/adb-closed.py`.
- `paisanos-io_tv-makeover` (MIT): notas de tiempos de reinicio en sus `tvs/*/debloat.txt`.
