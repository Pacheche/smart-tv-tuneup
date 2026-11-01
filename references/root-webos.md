# webOS con root: guía

**Esta skill no ejecuta ni automatiza root.** Este archivo es una guía: si la persona lo pide, primero leer modelo y firmware de la tele y compararlos con el perfil de abajo, explicar requisitos y riesgos, y remitir a las fuentes. Sin root no hay Home propio ni borrado de apps de LG; con root esas funciones existen, pero solo están declaradas para ese perfil. Si el modelo no coincide, decirlo: no hay soporte declarado.

## 1. Lo único que el proyecto de frxnnk declara como soportado

Fuente: `frxnnk_webos-liquid-glass-launcher` repo, `docs/root-automation.md` (MIT).

- **Único perfil aceptado:** modelo **49UN7310PSC**, firmware **04.64.00**, webOS **5.6.2-21**, build `jhericurl-jimna`, board **K6LP_ATSC_BR**. "No hay downgrade, flasheo ni soporte declarado para otros modelos" (líneas 8-10).
- El plan dura **cinco minutos**, se consume **una sola vez** y se vuelve a comprobar antes de aplicarlo; los pasos de preparación no rootéan (líneas 47-48). Requiere **Python 3.8+**.
- Fija fuentes de SlopBro y HBC **por commit y SHA-256**, y el IPK de HBC **0.7.3** por SHA-256 (línea 22; hash del IPK en línea 131).
- **No descarga ni ejecuta el `autoroot.sh` upstream** (línea 28); incluye su `COPYING` de **AGPL-3.0-or-later** por ser una derivación.
- Si algo queda incierto: conserva, registra recuperación y devuelve resultado **parcial con arranque físico pendiente** — "no reinicia la TV para fabricar esa confirmación" (líneas 39-45).
- Paradas de seguridad: `DEVMODE_TOKEN_INVALID` (token convertido en directorio) y `SIGNED_BACKUP_REQUIRED` (falta backup verificable del script original) (líneas 60-61).
- Hash del script stock observado en esa unidad: `18b6b7cce77d640fef78d9d247d6fc672b0850bd728dd2a3c44105a485abc846` (línea 66) — **solo sirve para esa unidad**.

## 2. Riesgos verificados (por qué esta skill no lo hace)

De `frxnnk_webos-liquid-glass-launcher`, `docs/root-and-home.md`:

- **HBC 0.7.3 abre Telnet root sin autenticación por defecto**; el flag normal de desactivación no se consulta en la rama failsafe (líneas 123-126). En esa instalación hubo que crear `/var/luna/preferences/webosbrew_telnet_disabled` y verificar el puerto 23 cerrado.
- HBC usa Dropbear **sin deshabilitar explícitamente las contraseñas** (línea 127).
- La elevación **modifica configuración y permisos LS2** y habilita un servicio con ejecución root amplia + actividad persistente (líneas 129-131).
- **SlopBro** descarga HBC sin comprobar hash, cambia el estado persistente de Developer Mode, puede renombrar el script de inicio de LG y **no implementa rollback transaccional** (líneas 134-136). Su cliente desactiva la verificación del certificado WSS y entrega el payload por HTTP (línea 138).
- No hay un procedimiento completo de unroot para este hardware (línea 142).
- El autoroot upstream anterior **rompió Developer Mode** en esa TV (hubo que recuperar el script stock y recrear el token a mano) (`root-automation.md` líneas 54-56).

## 3. Si aun así el usuario insiste (límite de esta skill)

1. Dejar por escrito que hay **un solo perfil declarado** y que el riesgo lo asume quien lo pide.
2. Exigir confirmación explícita del usuario **por escrito** antes de cualquier paso.
3. Conservar siempre: acceso SSH root, clave autorizada, **backup del estado de la TV** y el IPK de HBC (`root-and-home.md` línea 146).
4. Verificar tras arranque en frío: puerto 23 cerrado y acceso root por clave.
5. Avisar de que **no hay rollback automático** ni un procedimiento completo de unroot.

**Fuera del alcance de esta skill:** ejecutar el exploit, tocar el firmware, flashear, hacer downgrade o automatizar cualquiera de esos pasos.

## Fuentes

- `frxnnk_webos-liquid-glass-launcher` (MIT): `docs/root-automation.md`, `docs/root-and-home.md`, `docs/local-installer.md`, `README.md`.
- Las guías de root de webOS Homebrew Channel están en `github.com/webosbrew` — remitir ahí; esta skill no las reproduce ni las ejecuta.
