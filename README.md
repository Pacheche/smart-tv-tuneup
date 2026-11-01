# smart-tv-tuneup

An agent skill to speed up a slow smart TV the safe way: identify first, plan before touching anything, disable bloatware with `pm disable-user` (never uninstall), verify after every batch, and always leave a written way to revert.

> **Estado: v0.1.0, experimental.** Los scripts tienen pruebas offline y el método se evaluó con casos simulados, pero esta versión todavía no se ejecutó de punta a punta en una tele real.

## Instalación

Clonar (o copiar) esta carpeta dentro de la carpeta de skills del agente, por ejemplo en Claude Code:

```bash
git clone https://github.com/Pacheche/smart-tv-tuneup.git ~/.claude/skills/smart-tv-tuneup
```

Y listo: el agente la activa solo cuando el pedido trata de una tele lenta, bloatware, launcher o depuración ADB/webOS/Tizen. Sus scripts usan Python 3 sin dependencias; para aplicar en Android, la skill baja cleanyourtv en un commit fijo:

```bash
py scripts/detect_tv.py <ip de la tele>
py scripts/fetch_cleanyourtv.py
py scripts/plan_android.py --lista <cleanyourtv>/examples/<modelo>/debloat.txt --habilitados captura-e.txt --wifi dumpsys-wifi.txt --salida lote.txt
py -I scripts/test_scripts.py
```

`captura-e.txt` sale de `adb shell pm list packages -e --user 0`, y `dumpsys-wifi.txt`, de `adb shell dumpsys wifi`.

## Qué hace

- Identifica la tele **sin escribir nada** (sondeo TCP de solo lectura) y pide modelo, firmware y versión antes de cualquier cambio.
- Pregunta qué apps usa la persona y **respalda el estado base** (paquetes, quién responde a HOME, escalas, métricas).
- Muestra el plan **sin tocar nada**; recién después aplica en lotes chicos, un comando por llamada, verificando tras cada lote.
- Aplica `pm disable-user --user 0` **nunca** `pm uninstall`, y espera ≥ 45 s antes de reiniciar.
- Mide antes y después con modelo, contexto y unidad, cierra ADB al terminar y entrega el informe con **cómo revertir cada cosa**.

## Qué NO hace

- No hace root ni ejecuta nada de root (en webOS queda como referencia no ejecutada).
- No reemplaza el Home en LG ni Samsung: allí el launcher se instala como app. En Android sí puede cambiarlo.
- No deshabilita ni desinstala bloatware en webOS ni en Tizen sin root.
- No flashea ni hace downgrade, y el factory reset es el último escalón, con aviso previo.

## Soporte

| Plataforma | Qué esta skill sabe hacer |
|---|---|
| Android TV / Google TV (sin root) | Identificar, respaldar, planear y aplicar debloat por ADB con cleanyourtv, cambiar el Home, verificar y revertir |
| LG webOS (sin root) | Instalar launcher como app por Developer Mode; el Home de fábrica se queda |
| webOS con root | Solo referencia leída, nunca ejecutada |
| Samsung Tizen (sin root) | Instalar launcher como app por Developer Mode/sdb; sin shell ni `pm` en retail |
| Orsay (Samsung viejo) | No aplica |

## Advertencia de riesgo

Deshabilitar paquetes puede dejar una tele sin arrancar. Esta skill existe justo para reducir ese riesgo (identificar, respaldar, plan, lotes chicos, ≥ 45 s antes de reiniciar, nunca tocar el núcleo), pero el riesgo es real y lo asume quien la usa. Solo usarla en teles propias o con autorización de sus dueños. Ver `references/recuperacion.md` antes de empezar.

## Créditos

- La lista de paquetes del núcleo de Android (`CORE_RE` / `CORE_OK`) y el método de deshabilitar sin desinstalar vienen de [cleanyourtv](https://github.com/Gathin23/cleanyourtv) (MIT, commit fijo `6e8615eb0be0e843ceeebedae246d69f3e0a88d7`): se copian literales y con el origen anotado. Ver `THIRD_PARTY.md`.
- El patrón de menús de fábrica viene de [free-my-tv](https://github.com/simbasjungles/free-my-tv) (MIT), con el origen anotado.
- La idea de no inventar métricas que la tele no expone viene de [pranavsarathi/android-tv-makeover](https://github.com/pranavsarathi/android-tv-makeover): se toma solo la idea; no se copia código.
- El método de medición y los límites por plataforma se apoyan en [paisanos-io/tv-makeover](https://github.com/paisanos-io/tv-makeover), [simbasjungles/free-my-tv](https://github.com/simbasjungles/free-my-tv), [frxnnk/webos-liquid-glass-launcher](https://github.com/frxnnk/webos-liquid-glass-launcher) y [danielthejoker18/FreeMyTvWebOS](https://github.com/danielthejoker18/FreeMyTvWebOS) (todos MIT). Cada dato de los `references/` lleva su archivo y línea.

Licencia: MIT, © 2026 Francisco Rivarola.
