#!/usr/bin/env python3
"""Pruebas de los scripts de smart-tv-tuneup: sin red, sin git remoto y sin tele.

    py -I scripts/test_scripts.py

Todo lo que se prueba son funciones puras, archivos temporales y el cableado de la
salida (con `sondear` sustituido): ningún test abre un socket a una tele ni clona.
"""
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

# -I no mete el directorio del script en sys.path: hay que ponerlo a mano.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import detect_tv
import fetch_cleanyourtv
import plan_android


def escribir(ruta, texto):
    Path(ruta).write_text(texto, encoding="utf-8")
    return str(ruta)


class TestNucleo(unittest.TestCase):
    """CORE_RE / CORE_OK tienen que comportarse como en cleanyourtv."""

    def test_paquetes_nucleo_bloqueados(self):
        for paquete in ("com.android.systemui", "com.android.shell", "com.android.settings",
                        "com.android.phone", "com.google.android.permissioncontroller",
                        "com.android.packageinstaller", "com.cltv.mal", "com.mediatek.tis",
                        "com.android.location.fused", "android", "android.ext.services"):
            self.assertTrue(plan_android.re.match(plan_android.CORE_RE, paquete), paquete)
            self.assertFalse(plan_android.re.match(plan_android.CORE_OK, paquete), paquete)

    def test_excepcion_providers_permitidos(self):
        for paquete in ("com.android.providers.calendar", "com.android.providers.contacts",
                        "com.android.providers.userdictionary",
                        "com.android.providers.blockednumber"):
            self.assertTrue(plan_android.re.match(plan_android.CORE_RE, paquete), paquete)
            self.assertTrue(plan_android.re.match(plan_android.CORE_OK, paquete), paquete)

    def test_bloat_normal_no_es_nucleo(self):
        for paquete in ("com.google.android.tvlauncher", "com.netflix.ninja",
                        "com.example.bloat", "com.tcl.tvinput"):
            self.assertFalse(plan_android.re.match(plan_android.CORE_RE, paquete), paquete)


class TestPlanAndroid(unittest.TestCase):
    def test_rechaza_fabrica(self):
        estado, motivo = plan_android.clasificar("com.tcl.factory.view", {"com.tcl.factory.view"},
                                                 None, set(), set())
        self.assertEqual(estado, plan_android.RECHAZADO)
        self.assertIn("fábrica", motivo)

    def test_rechaza_dueno_de_wifi(self):
        estado, motivo = plan_android.clasificar("com.foo", {"com.foo"}, None, set(), {"com.foo"})
        self.assertEqual(estado, plan_android.RECHAZADO)
        self.assertIn("Wi-Fi", motivo)

    def test_setupwraith_sin_captura_se_rechaza(self):
        estado, _ = plan_android.clasificar(plan_android.SETUPWRAITH, {plan_android.SETUPWRAITH},
                                            None, set(), None)
        self.assertEqual(estado, plan_android.RECHAZADO)

    def test_setupwraith_sin_duenos_legibles_se_rechaza(self):
        estado, _ = plan_android.clasificar(plan_android.SETUPWRAITH, {plan_android.SETUPWRAITH},
                                            None, set(), set())
        self.assertEqual(estado, plan_android.RECHAZADO)

    def test_lee_captura_utf16_de_powershell(self):
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "e.txt"
            ruta.write_bytes("package:com.bloat\r\n".encode("utf-16"))
            self.assertEqual(plan_android.leer_paquetes(str(ruta)), {"com.bloat"})

    def test_salida_solo_aplicables(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            (base / "lista.txt").write_text("com.bloat\ncom.tcl.factory.view\n", encoding="utf-8")
            (base / "e.txt").write_text("package:com.bloat\npackage:com.tcl.factory.view\n",
                                        encoding="utf-8")
            salida = base / "lote.txt"
            with contextlib.redirect_stdout(io.StringIO()):
                codigo = plan_android.main(["--lista", str(base / "lista.txt"), "--habilitados",
                                            str(base / "e.txt"), "--salida", str(salida)])
            self.assertEqual(codigo, 0)
            self.assertEqual(salida.read_text(encoding="utf-8"), "com.bloat\n")

    ESTADOS = {"aplicar": plan_android.APLICAR, "rechazado": plan_android.RECHAZADO,
               "no instalado": plan_android.NO_INSTALADO, "ya apagado": plan_android.YA_APAGADO}

    def correr(self, lista, habilitados, deshabilitados=None, keep=()):
        with tempfile.TemporaryDirectory() as tmp:
            args = ["--lista", escribir(Path(tmp) / "lista.txt", lista),
                    "--habilitados", escribir(Path(tmp) / "e.txt", habilitados)]
            if deshabilitados is not None:
                args += ["--deshabilitados", escribir(Path(tmp) / "d.txt", deshabilitados)]
            for paquete in keep:
                args += ["--keep", paquete]
            salida = io.StringIO()
            with contextlib.redirect_stdout(salida):
                codigo = plan_android.main(args)
            return codigo, salida.getvalue()

    def test_estados_por_paquete(self):
        codigo, salida = self.correr(
            "com.foo.bloat\ncom.foo.old\ncom.foo.gone\ncom.android.systemui\n",
            "package:com.foo.bloat\npackage:com.android.systemui\n",
            "package:com.foo.old\n")
        self.assertEqual(codigo, 1)
        self.assertIn("aplicar", salida)
        self.assertIn("com.foo.bloat", salida)
        self.assertIn("ya apagado", salida)
        self.assertIn("no instalado", salida)
        self.assertIn("rechazado", salida)
        self.assertIn("PLAN BLOQUEADO", salida)

    def test_plan_limpio_sale_cero(self):
        codigo, salida = self.correr(
            "com.foo.bloat\n# comentada\n\n", "package:com.foo.bloat\n", "")
        self.assertEqual(codigo, 0)
        self.assertNotIn("PLAN BLOQUEADO", salida)

    def test_keep_bloquea_sin_ser_core(self):
        codigo, salida = self.correr("com.foo.gusto\n", "package:com.foo.gusto\n",
                                     keep=["com.foo.gusto"])
        self.assertEqual(codigo, 0)
        self.assertIn("keep", salida)
        self.assertNotIn("aplicar com.foo.gusto", salida.replace("  ", " "))

    def test_lista_vacia_es_error(self):
        codigo, _ = self.correr("# solo comentarios\n", "package:com.foo\n")
        self.assertEqual(codigo, 2)

    def test_clasificar_directo(self):
        self.assertEqual(plan_android.clasificar("com.foo", {"com.foo"}, None, set())[0],
                         plan_android.APLICAR)
        self.assertEqual(plan_android.clasificar("com.foo", set(), {"com.foo"}, set())[0],
                         plan_android.YA_APAGADO)
        self.assertEqual(plan_android.clasificar("com.foo", set(), None, set())[0],
                         plan_android.NO_INSTALADO)
        self.assertEqual(
            plan_android.clasificar("com.android.shell", {"com.android.shell"}, None,
                                    set())[0],
            plan_android.RECHAZADO)

    def test_banda(self):
        self.assertEqual(plan_android.banda(2437), "2.4 GHz")
        self.assertEqual(plan_android.banda(5180), "5 GHz")
        self.assertEqual(plan_android.banda(6135), "6 GHz")
        self.assertEqual(plan_android.banda(None), "no detectada")


class TestDetectTv(unittest.TestCase):
    def test_un_puerto_caracteristico_es_media(self):
        puntos = detect_tv.puntuar([("Android / Google TV", 2)])
        self.assertEqual(detect_tv.concluir(puntos), ("Android / Google TV", "media"))

    def test_dos_puertos_de_la_misma_plataforma_son_alta(self):
        puntos = detect_tv.puntuar([("LG webOS", 2), ("LG webOS", 1)])
        plataforma, certeza = detect_tv.concluir(puntos)
        self.assertEqual(plataforma, "LG webOS")
        self.assertEqual(certeza, "alta")

    def test_un_puerto_solo_es_baja(self):
        puntos = detect_tv.puntuar([("Samsung Tizen", 1)])
        self.assertEqual(detect_tv.concluir(puntos), ("Samsung Tizen", "baja"))

    def test_sin_puertos_es_desconocida(self):
        self.assertEqual(detect_tv.concluir(detect_tv.puntuar([])),
                         ("desconocida", "sin puertos característicos"))

    def test_empate_es_ambigua(self):
        puntos = detect_tv.puntuar([("Android / Google TV", 2), ("LG webOS", 2)])
        plataforma, certeza = detect_tv.concluir(puntos)
        self.assertIn("ambigua", plataforma)
        self.assertEqual(certeza, "media")

    def test_main_sin_red_imprime_conclusion(self):
        respuestas = {5555: ("abierto", None), 9922: ("cerrado", None),
                      3000: ("cerrado", None), 3001: ("cerrado", None),
                      26101: ("cerrado", None), 8001: ("cerrado", None),
                      8002: ("cerrado", None)}
        salida = io.StringIO()
        with mock.patch.object(detect_tv, "sondear",
                               side_effect=lambda h, p, t: respuestas[p]):
            with contextlib.redirect_stdout(salida):
                codigo = detect_tv.main(["192.0.2.1", "--timeout", "0.1"])
        self.assertEqual(codigo, 0)
        self.assertIn("Android / Google TV", salida.getvalue())
        self.assertIn("certeza media", salida.getvalue())


class TestFetchCleanyourtv(unittest.TestCase):
    def test_commit_de_cuarenta_hex(self):
        self.assertEqual(len(fetch_cleanyourtv.COMMIT), 40)
        self.assertRegex(fetch_cleanyourtv.COMMIT, r"^[0-9a-f]{40}$")

    def test_carpeta_sincronizada(self):
        self.assertTrue(fetch_cleanyourtv.carpeta_sincronizada(
            "C:/Users/x/Mi unidad/cleanyourtv"))
        self.assertTrue(fetch_cleanyourtv.carpeta_sincronizada(
            "/home/u/OneDrive/backups"))
        self.assertFalse(fetch_cleanyourtv.carpeta_sincronizada(
            "C:/Users/x/.cache/smart-tv-tuneup/cleanyourtv"))

    def test_head_sin_repo_da_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(fetch_cleanyourtv.head_de(tmp))

    def test_destino_por_defecto_fuera_de_sincronizadas(self):
        self.assertFalse(fetch_cleanyourtv.carpeta_sincronizada(
            fetch_cleanyourtv.DESTINO_POR_DEFECTO))


if __name__ == "__main__":
    unittest.main(verbosity=2)
