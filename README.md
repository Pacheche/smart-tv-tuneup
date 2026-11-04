# smart-tv-tuneup

Skill para agentes de IA que optimiza smart TVs con Android TV, Google TV, LG webOS o Samsung Tizen.

Instalala y decile a tu agente "optimizá mi tele": la skill le indica cómo identificarla, limpiarla, medir el resultado y dejarla lista para revertir. El agente ejecuta el trabajo y te pide solo lo que hay que hacer en la tele.

## Instalación

```bash
npx skills add Pacheche/smart-tv-tuneup -g -y
```

O clonala en la carpeta de skills de tu agente:

| Agente | Carpeta |
|---|---|
| Claude Code | `~/.claude/skills/smart-tv-tuneup` |
| Codex | `~/.codex/skills/smart-tv-tuneup` |
| Copilot CLI, Gemini CLI | `~/.agents/skills/smart-tv-tuneup` |

```bash
git clone https://github.com/Pacheche/smart-tv-tuneup.git ~/.claude/skills/smart-tv-tuneup
```

Si tu agente no carga skills, abrí esta carpeta y pedile que siga `SKILL.md`; `AGENTS.md` ya lo dirige ahí.

## Uso

Pedile al agente, por ejemplo: "Mi tele está lenta, optimizala. La IP es 192.168.1.50". El agente necesita terminal, Python 3, git y estar en la misma red que la tele.

Comandos que usa la skill:

```bash
py scripts/detect_tv.py <ip de la tele>
py scripts/fetch_cleanyourtv.py
py scripts/plan_android.py --lista <cleanyourtv>/examples/<modelo>/debloat.txt --habilitados captura-e.txt --wifi dumpsys-wifi.txt --salida lote.txt
py -I scripts/test_scripts.py
```

`captura-e.txt` sale de `adb shell pm list packages -e --user 0`, y `dumpsys-wifi.txt`, de `adb shell dumpsys wifi`.

## Qué hace

- Identifica la tele sin escribir nada (sondeo TCP de solo lectura) y pide modelo, firmware y versión antes de cualquier cambio.
- Pregunta qué apps usa la persona y respalda el estado base (paquetes, quién responde a HOME, escalas, métricas).
- Muestra el plan sin tocar nada; recién después aplica en lotes chicos, un comando por llamada, verificando tras cada lote.
- Aplica `pm disable-user --user 0`, **nunca** `pm uninstall`, y espera ≥ 45 s antes de reiniciar.
- Mide antes y después con modelo, contexto y unidad, cierra ADB al terminar y entrega el informe con cómo revertir cada cosa.

## Qué NO hace

- No hace root: en webOS incluye una guía con requisitos y riesgos.
- No reemplaza el Home en LG ni Samsung: allí el launcher se instala como app. En Android sí puede cambiarlo.
- No deshabilita ni desinstala bloatware en webOS ni en Tizen sin root.
- No flashea ni hace downgrade, y el factory reset es el último escalón, con aviso previo.

## Soporte

| Plataforma | Qué esta skill sabe hacer |
|---|---|
| Android TV / Google TV (sin root) | Identificar, respaldar, planear y aplicar debloat por ADB con cleanyourtv, cambiar el Home, verificar y revertir |
| LG webOS (sin root) | Instalar launcher como app por Developer Mode; el Home de fábrica se queda |
| webOS con root | Guía de requisitos y riesgos |
| Samsung Tizen (sin root) | Instalar launcher como app por Developer Mode/sdb; sin shell ni `pm` en retail |
| Orsay (Samsung viejo) | No aplica |

## Advertencia de riesgo

Deshabilitar paquetes puede dejar una tele sin arrancar. Esta skill existe justo para reducir ese riesgo (identificar, respaldar, plan, lotes chicos, ≥ 45 s antes de reiniciar, nunca tocar el núcleo), pero el riesgo es real y lo asume quien la usa. Solo usarla en teles propias o con autorización de sus dueños. Ver `references/recuperacion.md` antes de empezar.

## Créditos

- `CORE_RE` y `CORE_OK` de `scripts/plan_android.py` vienen de [cleanyourtv](https://github.com/Gathin23/cleanyourtv) (MIT), que la skill también usa para aplicar los cambios en Android.
- `FACTORY_RE` de `scripts/plan_android.py` viene de [free-my-tv](https://github.com/simbasjungles/free-my-tv) (MIT).

Licencia: MIT, © 2026 Francisco Rivarola.
