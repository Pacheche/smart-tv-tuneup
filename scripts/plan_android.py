#!/usr/bin/env python3
"""Arma el plan de debloat de Android sin tocar la tele (offline, sin red).

    py scripts/plan_android.py --lista debloat.txt --habilitados captura-e.txt \
        [--deshabilitados captura-d.txt] [--wifi dumpsys-wifi.txt] [--keep paquete] \
        [--salida lote.txt]

Entradas (capturas hechas a mano desde la tele, una sola vez):
    pm list packages -e --user 0      -> --habilitados   (obligatorio)
    pm list packages -d --user 0      -> --deshabilitados (opcional)
    dumpsys wifi                      -> --wifi          (opcional: dueños de la Wi-Fi y banda)
La lista es un paquete por línea; '#' comenta y las líneas vacías se ignoran.

Salida por paquete: aplicar / rechazado / no instalado / ya apagado, con el motivo.
Exit 0 si el plan no toca nada del núcleo; exit 1 si toca (el plan sale bloqueado y no
hay que aplicarlo); exit 2 si falta una entrada o el archivo no se puede leer.

Con --salida escribe solo los paquetes en estado "aplicar", listos para pasarle a
tools/disable de cleanyourtv, que suma las guardas que necesitan hablar con la tele
(HOME, entradas de TV, handlers) y el registro de recuperación.

Esto NO ejecuta nada. Tras aplicar, esperar >= 45 s antes de reiniciar
(references/android.md). Nunca `pm uninstall`.
"""
import argparse
import re
import sys

# Núcleo de Android y middleware de TV: si uno de estos sale en la lista, el plan se
# bloquea entero. Copiado literal de cleanyourtv (Gathin23/cleanyourtv, commit
# 6e8615eb0be0e843ceeebedae246d69f3e0a88d7, tools/disable.sh líneas 68-69), porque
# deshabilitar cualquiera de ellos dejó teles sin arrancar (#884, #1578, #2557, #2803).
CORE_RE = ('^(android|android\\.ext\\.(services|shared)|com\\.android\\.sdksandbox|'
           'com\\.android\\.location\\.fused|com\\.android\\.systemui|com\\.android\\.shell|'
           'com\\.android\\.phone|com\\.android\\.settings|com\\.android\\.tv\\.settings|'
           'com\\.(google\\.)?android\\.(permissioncontroller|packageinstaller|ext\\.services|'
           'ext\\.shared|modulemetadata)|com\\.google\\.android\\.overlay\\.modules.*|'
           'com\\.android\\.providers\\..*|com\\.cltv\\.mal|'
           'com\\.mediatek\\.(tis|tv\\.service|tv\\.agent))$')
# Excepción probada: estos content providers no los usa ninguna función de la tele.
CORE_OK = '^com\\.android\\.providers\\.(calendar|contacts|userdictionary|blockednumber)$'

# Menús de fábrica y servicio de cualquier marca. Copiado de free-my-tv
# (simbasjungles/free-my-tv, app/src/io/freemytv/HomeMode.java, patrón FACTORY).
FACTORY_RE = r'^(.*\.)?(factory|factorymenu|facmenu|fac|hkcfac|testpq)(\..*)?$'
SETUPWRAITH = "com.google.android.tungsten.setupwraith"

APLICAR = "aplicar"
RECHAZADO = "rechazado"
NO_INSTALADO = "no instalado"
YA_APAGADO = "ya apagado"


def leer_texto(ruta):
    """Lee una captura: PowerShell 5.1 redirige `>` en UTF-16, el resto en UTF-8."""
    with open(ruta, "rb") as f:
        datos = f.read()
    if datos[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return datos.decode("utf-16", errors="replace")
    return datos.decode("utf-8-sig", errors="replace")


def leer_lista(ruta):
    """Lista de paquetes a deshabilitar: una por línea, '#' comenta."""
    paquetes = []
    for linea in leer_texto(ruta).splitlines():
        texto = linea.split("#", 1)[0].strip()
        if not texto:
            continue
        if texto.startswith("package:"):
            texto = texto[len("package:"):]
        paquetes.append(texto)
    return paquetes


def leer_paquetes(ruta):
    """Salida de `pm list packages [-e|-d] --user 0` -> conjunto de nombres."""
    paquetes = set()
    for linea in leer_texto(ruta).splitlines():
        texto = linea.strip()
        if texto.startswith("package:"):
            texto = texto[len("package:"):]
        if texto:
            paquetes.add(texto)
    return paquetes


def leer_wifi(ruta):
    """Mejor esfuerzo con `dumpsys wifi`: {'duenos': set, 'ssid': str, 'frecuencia': int}."""
    datos = {}
    texto = leer_texto(ruta)
    datos["duenos"] = set(re.findall(r"cname=([\w.]+)", texto))
    m = re.search(r"SSID:\s*([^,\n]+)", texto)
    if m:
        datos["ssid"] = m.group(1).strip()
    m = re.search(r"[Ff]requency:\s*(\d{4})", texto)
    if m:
        datos["frecuencia"] = int(m.group(1))
    return datos


def banda(frecuencia):
    """Etiqueta de banda a partir de la frecuencia en MHz (mejor esfuerzo)."""
    if frecuencia is None:
        return "no detectada"
    if frecuencia < 3000:
        return "2.4 GHz"
    if frecuencia < 5900:
        return "5 GHz"
    return "6 GHz"


def clasificar(nombre, habilitados, deshabilitados, keep, duenos_wifi=None):
    """Devuelve (estado, motivo) para un paquete de la lista.

    duenos_wifi: paquetes dueños de redes guardadas, o None si no hay captura.
    """
    if nombre in keep:
        return RECHAZADO, "keep: lo pidió el usuario"
    if re.match(CORE_RE, nombre) and not re.match(CORE_OK, nombre):
        return RECHAZADO, "núcleo de Android/TV middleware: no se toca"
    if re.match(FACTORY_RE, nombre):
        return RECHAZADO, "menú de fábrica o servicio: no se toca"
    if duenos_wifi is not None and nombre in duenos_wifi:
        return RECHAZADO, "dueño de una Wi-Fi guardada: apagarlo borra la red"
    if not duenos_wifi and nombre == SETUPWRAITH:
        return RECHAZADO, "sin dueños legibles en dumpsys wifi no se sabe si es dueño de la Wi-Fi"
    if nombre in habilitados:
        return APLICAR, "habilitado y no es núcleo"
    if deshabilitados is not None:
        if nombre in deshabilitados:
            return YA_APAGADO, "ya estaba deshabilitado"
        return NO_INSTALADO, "no aparece en -e ni -d"
    return NO_INSTALADO, "ausente en -e (sin captura -d no se distingue de 'ya apagado')"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Plan de debloat Android offline: clasifica la lista sin tocar la tele.")
    parser.add_argument("--lista", required=True, help="archivo con los paquetes a deshabilitar")
    parser.add_argument("--habilitados", required=True,
                        help="captura de: pm list packages -e --user 0")
    parser.add_argument("--deshabilitados",
                        help="captura opcional de: pm list packages -d --user 0")
    parser.add_argument("--wifi", help="captura opcional de: dumpsys wifi")
    parser.add_argument("--keep", action="append", default=[], metavar="PAQUETE",
                        help="paquete que se conserva aunque esté en la lista (se repite)")
    parser.add_argument("--salida", help="escribe aquí solo los paquetes en estado 'aplicar'")
    args = parser.parse_args(argv)

    try:
        lista = leer_lista(args.lista)
        habilitados = leer_paquetes(args.habilitados)
        deshabilitados = leer_paquetes(args.deshabilitados) if args.deshabilitados else None
        wifi = leer_wifi(args.wifi) if args.wifi else None
    except OSError as e:
        print("no se pudo leer una entrada: %s" % e, file=sys.stderr)
        return 2

    if not lista:
        print("la lista no tiene paquetes (solo comentarios o vacía): nada que planear.",
              file=sys.stderr)
        return 2

    keep = set(args.keep)
    conteo = {APLICAR: 0, RECHAZADO: 0, NO_INSTALADO: 0, YA_APAGADO: 0}
    toca_core = []
    aplicables = []
    duenos_wifi = wifi["duenos"] if wifi is not None else None
    print("Plan de debloat (offline, sin tocar la tele). Nada se ejecuta con esto.")
    print()
    for nombre in lista:
        estado, motivo = clasificar(nombre, habilitados, deshabilitados, keep, duenos_wifi)
        conteo[estado] += 1
        if estado == APLICAR:
            aplicables.append(nombre)
        if estado == RECHAZADO and motivo.startswith("núcleo"):
            toca_core.append(nombre)
        print("  %-16s %-28s %s" % (estado, nombre, motivo))

    print()
    print("Resumen: %d aplicar, %d rechazado, %d no instalado, %d ya apagado."
          % (conteo[APLICAR], conteo[RECHAZADO], conteo[NO_INSTALADO], conteo[YA_APAGADO]))

    if wifi is not None:
        if "frecuencia" in wifi:
            print("Wi-Fi detectado: %s a %d MHz (%s). Muchas teles son solo 2.4 GHz aunque "
                  "el SSID diga 5 GHz: manda la frecuencia, no el nombre (references/rendimiento.md)."
                  % (wifi.get("ssid", "SSID desconocido"), wifi["frecuencia"],
                     banda(wifi["frecuencia"])))
        else:
            print("Wi-Fi: no se pudo leer la frecuencia en la captura; revisarla a mano antes "
                  "de culpar a la tele.")

    if toca_core:
        print()
        print("PLAN BLOQUEADO: la lista toca paquetes del núcleo de Android o del middleware "
              "de la tele:", ", ".join(toca_core))
        print("Sácalos de la lista (o coméntalos) y vuelve a correr esto. En la tele no se "
              "envió nada.")
        return 1

    if args.salida:
        try:
            with open(args.salida, "w", encoding="utf-8", newline="\n") as f:
                f.write("".join(p + "\n" for p in aplicables))
        except OSError as e:
            print("no se pudo escribir la salida: %s" % e, file=sys.stderr)
            return 2

    print()
    print("Si el plan se aprueba: aplicar por lotes con tools/disable de cleanyourtv, "
          "verificar tras cada lote y esperar >= 45 s antes de reiniciar "
          "(references/android.md).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
