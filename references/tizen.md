# Samsung Tizen: qué se puede hacer sin root

**Regla:** en Tizen retail **no hay ADB, no hay shell y no hay `pm disable-user`**. No se puede deshabilitar ni desinstalar bloatware de fábrica. Lo único es instalar apps (si el firmware lo permite) o usar el launcher como app. `sdb` en un firmware retail **solo admite archivos** (`filesync_support:push`), no comandos. (`Gathin23_cleanyourtv` repo, `docs/devices/samsung-tizen.md` líneas 43 y 106, y `tests/test_samsung_tizen_note.py`; `simbasjungles_free-my-tv` repo, `CLAUDE.md` línea 190.)

## 1. Entrada: Developer Mode + SDB

Flujo verificado en `simbasjungles_free-my-tv` repo (`CLAUDE.md` líneas 155-169, `README.md` línea 141):

1. Pedir la **IP de la tele** y la ciudad (si se usa contenido con API).
2. En la tele (lo hace el usuario): *Apps* → teclear **`1 2 3 4 5`** con el mando → **Developer mode ON** → *Host PC IP* = IP de esta computadora → **reiniciar la tele**.
3. Desde la PC: `sdb connect <IP>:26101`.
4. Firmar e instalar: `tizen` (Tizen Studio CLI, o el plugin `tizen-sdk-skills` de Samsung) + `python3 tizen/install.py <IP>` de free-my-tv (habla SDB directo). La app es de terceros y consulta servicios externos: avisarlo antes. Ojo: `tizen` corre en Java y los binarios de Samsung son Intel; en Apple Silicon sin Rosetta no funcionan.
5. **Certificado, una sola vez:** 2023+ (Tizen 7+) exige certificado **Samsung** con la cuenta Samsung del dueño y su **DUID**; 2015-2022 usan certificado **Tizen** (`tizen certificate`, luego `tizen security-profiles add`). Las actualizaciones necesitan **el mismo certificado**: con otro, la tele se niega (hay que desinstalar primero). **Certificados, contraseñas y DUID nunca al chat.** (`CLAUDE.md` líneas 167-169, 188-203.)

Ruta sin herramientas: **TizenBrew Installer** (`github.com/reisxd/TizenBrewInstaller`) instala el release escribiendo `simbasjungles/free-my-tv`; en 2023+ firma con la cuenta Samsung. **TizenBrew necesita 2017+**; en 2015/2016 hay que compilar a mano. (`CLAUDE.md` líneas 146, 149-152; `README.md` línea 141.)

## 2. Puertos y respuestas (verificado)

| Puerto | Estado | Qué es |
|---|---|---|
| 8001 | abierto | HTTP API remota (`GET /api/v2/` da modelo y estado) |
| 8002 | abierto | HTTPS de lo mismo (certificado self-signed) |
| 26101 | cerrado con Dev Mode off (responde rechazando), abierto con Dev Mode on | SDB |
| 5555 | cerrado | ADB no existe en Tizen retail |

Fuente: `Gathin23_cleanyourtv`, `docs/devices/samsung-tizen.md` (evidencia en un **UN50AU8000FXZA**, reporte #441; el test del repo bloquea que 5555/26101 aparezcan abiertos sin Dev Mode).

## 3. Límites de firmware (no prometer nada más)

| Escenario | Resultado | Fuente |
|---|---|---|
| 2015 UE48JU6100 (Tizen 2.3) | funciona, reportado (#317) | `simbasjungles`, `README.md` 141 |
| 2016 UE49K5670 (Full HD) | **rechaza instalaciones de desarrollador**: `failed[118]` incluso con el `tizen install` de Samsung (#349) | idem |
| 2016 UE49KU6640 / UN49KU6400 | `failed[118]` = copia de una instalación fallida previa → `--uninstall` y reinstalar con certificado Tizen | idem; `CLAUDE.md` 182-184 |
| Orsay (Samsung previas a Tizen) | **no corren el launcher** (alternativa: streamer Google TV por HDMI) | `README.md` 141 |
| 2015/2016 | no corren TizenBrew | idem |
| 2017/2018 (Tizen 3/4) | *TV Settings* en el cajón **congela la tele** (#257); el botón Settings del mando funciona | idem |
| **Autorun Last App** | probado en **2017**; **2019 y 2020 no lo reabren** (#356). En 2019/2020: poner el launcher primero en la barra Home | `CLAUDE.md` 196-199; `README.md` 146 |

## 4. Qué se puede hacer de verdad

1. **Identificar**: modelo, año, versión Tizen (Ajustes > Soporte). Sin esto no se califica nada.
2. **Instalar el launcher como app** (si el firmware lo permite). Si da `failed[118]`: `--uninstall` y reintentar con el certificado que corresponda; si sigue, informar y parar.
3. **Autorun Last App** solo en modelos donde esté probado (2017); avisar que en 2019/2020 no funciona.
4. **No** deshabilitar, **no** desinstalar bloatware, **no** flashear, **no** inventar menús de debloat.
5. **Un reporte vale para un equipo y un firmware:** no presentarlo como algo que aplica a toda la plataforma.

## 5. Excusas a rechazar

- "En Samsung se puede deshabilitar bloatware": falso en retail (sin shell).
- "Hay un menú de debloat en Ajustes": pedir foto de la pantalla real antes de afirmar.
- "Flashear Tizen arregla la lentitud": flashear queda fuera de esta skill.

## Fuentes

- `Gathin23_cleanyourtv`: `docs/devices/samsung-tizen.md`, `tests/test_samsung_tizen_note.py`, `docs/restore.md` (MIT).
- `simbasjungles_free-my-tv`: `README.md`, `CLAUDE.md`, `tizen/install.py`, `tizen/config.xml`, `web/tv.js` (MIT).
