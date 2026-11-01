#!/usr/bin/env python3
"""Clona cleanyourtv en un commit fijo y verifica que el HEAD coincida.

    py scripts/fetch_cleanyourtv.py [--dest RUTA]

Solo clona y deja el árbol en el commit fijo; no ejecuta nada del repo. Después de
clonar hace `git rev-parse HEAD` y lo compara con COMMIT: si no coincide, sale con
error (exit 1) y no se usa nada de esa copia.

El destino por defecto queda fuera de carpetas sincronizadas (Google Drive / OneDrive
rompen los archivos de .git). Si la ruta elegida cae dentro de una, se avisa y no se
clona: elegir otra con --dest.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

REPO = "https://github.com/Gathin23/cleanyourtv.git"
COMMIT = "6e8615eb0be0e843ceeebedae246d69f3e0a88d7"
DESTINO_POR_DEFECTO = Path.home() / ".cache" / "smart-tv-tuneup" / "cleanyourtv"
# Marcadores de carpetas sincronizadas (se comparan en minúsculas contra cada parte
# de la ruta). "Mi unidad" es Google Drive en español.
CARPETAS_SINCRONIZADAS = ("mi unidad", "onedrive", "google drive", "dropbox", "icloud")


def carpeta_sincronizada(ruta):
    """True si la ruta cae dentro de una carpeta sincronizada conocida."""
    partes = [p.lower() for p in Path(ruta).expanduser().resolve().parts]
    return any(marcador in parte for parte in partes for marcador in CARPETAS_SINCRONIZADAS)


def head_de(ruta):
    """HEAD del repo en `ruta`, o None si no hay repo o git falla."""
    if not (Path(ruta) / ".git").exists():
        return None
    try:
        out = subprocess.run(["git", "-C", str(ruta), "rev-parse", "HEAD"],
                             capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if out.returncode != 0:
        return None
    return out.stdout.strip()


def correr(cmd):
    """Ejecuta un comando git y devuelve (ok, texto)."""
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except (OSError, subprocess.TimeoutExpired) as e:
        return False, str(e)
    texto = (out.stdout + out.stderr).strip()
    return out.returncode == 0, texto


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Clona cleanyourtv en el commit fijo y verifica el HEAD.")
    parser.add_argument("--dest", help="dónde clonar (por defecto %s)" % DESTINO_POR_DEFECTO)
    args = parser.parse_args(argv)

    destino = Path(args.dest).expanduser() if args.dest else DESTINO_POR_DEFECTO

    if carpeta_sincronizada(destino):
        print("Esa ruta está dentro de una carpeta sincronizada (%s). La sincronización "
              "rompe los archivos de .git." % destino, file=sys.stderr)
        print("Elegir otra con --dest, por ejemplo: --dest %s"
              % (Path.home() / ".cache" / "smart-tv-tuneup" / "cleanyourtv"), file=sys.stderr)
        return 2

    if shutil.which("git") is None:
        print("no se encontró git en el PATH: instalarlo antes de clonar.", file=sys.stderr)
        return 2

    if destino.exists():
        head = head_de(destino)
        if head is None:
            print("%s existe pero no es un repo de git usable: borrarlo o elegir otro "
                  "--dest (no se toca nada sin que lo pidas)." % destino, file=sys.stderr)
            return 1
        if head == COMMIT:
            print("OK: %s ya está en el commit fijo %s." % (destino, COMMIT))
            print("No ejecutar nada de ese repo sin revisarlo; ver references/android.md.")
            return 0
        print("FALLO: el HEAD de %s es %s y se esperaba %s. No se usa esa copia."
              % (destino, head, COMMIT), file=sys.stderr)
        print("Borrar la carpeta o elegir otro --dest; no se modifica nada por tu cuenta.",
              file=sys.stderr)
        return 1

    print("Clonando %s en %s ..." % (REPO, destino))
    ok, texto = correr(["git", "clone", REPO, str(destino)])
    if not ok:
        print("falló el clone: %s" % texto, file=sys.stderr)
        return 1

    ok, texto = correr(["git", "-C", str(destino), "checkout", "--detach", COMMIT])
    if not ok:
        print("falló el checkout del commit fijo: %s" % texto, file=sys.stderr)
        return 1

    head = head_de(destino)
    if head != COMMIT:
        print("FALLO: el HEAD verificado es %s y se esperaba %s: no se usa esa copia."
              % (head, COMMIT), file=sys.stderr)
        return 1

    print("OK: HEAD verificado = %s" % head)
    print("Eso solo deja el código a mano: leerlo y revisarlo antes de correr cualquier "
          "cosa de adentro. No ejecutar scripts del repo por automatismo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
