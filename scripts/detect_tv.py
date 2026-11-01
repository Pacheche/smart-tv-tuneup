#!/usr/bin/env python3
"""Detecta de qué plataforma es una tele por puertos TCP, sin escribir nada en ella.

    py scripts/detect_tv.py <ip> [--timeout 2]

Solo abre y cierra conexiones y lee lo que la propia tele manda sin que nadie le pida
nada (cero bytes enviados):

    5555   ADB de red (Android / Google TV)
    9922   SSH de Developer Mode (LG webOS)
    3000   SSR de LG (SSAP)
    3001   SSR de LG con TLS (SSAP)
    26101  sdb de Samsung Tizen (solo con Developer Mode activo)
    8001   API remota Samsung (websocket)
    8002   API remota Samsung (alternativa)

Imprime puerto por puerto y una conclusión con nivel de certeza: alta (>= 3 puntos),
media (2) o baja (1). Con la tele desconocida o los puertos cerrados dice "desconocida"
y no inventa plataforma. No reemplaza identificar modelo y firmware a mano:
ver references/android.md, webos.md y tizen.md.
"""
import argparse
import socket
import sys

# (puerto, qué es, plataforma, peso). El peso es solo para ordenar la conclusión:
# 2 = puerto característico de la plataforma, 1 = puerto que solo suma contexto.
PUERTOS = (
    (5555, "ADB de red (Android / Google TV)", "Android / Google TV", 2),
    (9922, "SSH de Developer Mode (LG webOS)", "LG webOS", 2),
    (3000, "SSR de LG (SSAP)", "LG webOS", 1),
    (3001, "SSR de LG con TLS (SSAP)", "LG webOS", 1),
    (26101, "sdb de Samsung Tizen (Developer Mode)", "Samsung Tizen", 2),
    (8001, "API remota Samsung (websocket)", "Samsung Tizen", 1),
    (8002, "API remota Samsung (alternativa)", "Samsung Tizen", 1),
)

SIGUIENTE = {
    "Android / Google TV": "pedir modelo exacto, firmware y versión de Android (references/android.md)",
    "LG webOS": "Developer Mode + Key Server en la tele (references/webos.md)",
    "Samsung Tizen": "Developer Mode y sdb en el puerto 26101 (references/tizen.md)",
}


def leer_banner(sock, timeout=0.6):
    """Lee sin enviar nada lo que la tele manda al conectar; devuelve texto o None."""
    try:
        sock.settimeout(timeout)
        dato = sock.recv(200)
    except (socket.timeout, OSError):
        return None
    if not dato:
        return None
    return dato.decode("utf-8", "replace").strip()


def sondear(host, puerto, timeout):
    """Conecta y cierra. Devuelve (estado, banner). No escribe un solo byte."""
    try:
        with socket.create_connection((host, puerto), timeout=timeout) as sock:
            banner = leer_banner(sock)
    except ConnectionRefusedError:
        return "cerrado", None
    except socket.timeout:
        return "sin respuesta", None
    except OSError as e:
        return "sin datos (%s)" % e.__class__.__name__, None
    return "abierto", banner


def puntuar(abiertos):
    """Suma los pesos por plataforma. `abiertos` es una lista de (plataforma, peso)."""
    puntos = {}
    for plataforma, peso in abiertos:
        puntos[plataforma] = puntos.get(plataforma, 0) + peso
    return puntos


def concluir(puntos):
    """Devuelve (plataforma, certeza) a partir de los puntos por plataforma."""
    if not puntos:
        return "desconocida", "sin puertos característicos"
    mayor = max(puntos.values())
    cimas = sorted(p for p, v in puntos.items() if v == mayor)
    if len(cimas) > 1:
        return "ambigua entre %s" % " y ".join(cimas), "media"
    if mayor >= 3:
        return cimas[0], "alta"
    if mayor == 2:
        return cimas[0], "media"
    return cimas[0], "baja"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Detecta la plataforma de una tele por puertos TCP, sin enviar nada.",
        add_help=True,
    )
    parser.add_argument("ip", help="IP de la tele en la red local")
    parser.add_argument("--timeout", type=float, default=2.0,
                        help="segundos de espera por puerto (por defecto 2)")
    args = parser.parse_args(argv)

    abiertos = []
    print("Sondeando %s (solo lectura, cero bytes enviados):" % args.ip)
    for puerto, que_es, plataforma, peso in PUERTOS:
        estado, banner = sondear(args.ip, puerto, args.timeout)
        linea = "  %-6s %-11s %s" % (puerto, estado, que_es)
        if banner:
            linea += "  [banner: %s]" % banner.splitlines()[0][:60]
        print(linea)
        if estado == "abierto":
            abiertos.append((plataforma, peso))

    plataforma, certeza = concluir(puntuar(abiertos))
    print()
    print("Plataforma probable: %s — certeza %s" % (plataforma, certeza))
    if plataforma in SIGUIENTE:
        print("Siguiente paso: %s." % SIGUIENTE[plataforma])
    print("Un puerto abierto no identifica la tele: confirmar modelo y firmware antes de "
          "cualquier cambio.")
    if not abiertos:
        print("Ningún puerto característico respondió: la tele puede estar apagada, "
              "en otro VLAN o sin depuración activada. Esto no dice nada sobre su estado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
