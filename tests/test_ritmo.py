"""RITMO (0.45.7, E3): `ritmo` no .forge/config.json, lido pelo hook `agentes` e gravado pelo `forge ritmo`."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "hooks"))
sys.path.insert(0, str(RAIZ / "tests"))
import agentes  # noqa: E402
from ambiente_git import sem_manutencao  # noqa: E402


def sem_excecao(funcao, *args, **kwargs):
    """O resultado, ou o texto da exceção: o hook nunca pode cair por causa do ritmo, e a falha vira asserção."""
    try:
        return funcao(*args, **kwargs)
    except Exception as erro:  # noqa: BLE001 - o teste compara o texto com o esperado
        return f"exceção: {erro!r}"


def pasta_temporaria(caso):
    pasta = Path(tempfile.mkdtemp(prefix="ritmo-"))
    caso.addCleanup(shutil.rmtree, pasta, True)
    return pasta


class RitmoNoHook(unittest.TestCase):
    def proc(self):
        pasta = pasta_temporaria(self)
        (pasta / "loadavg").write_text("0.1\n", encoding="utf-8")
        (pasta / "meminfo").write_text("MemTotal: 16777216 kB\nMemAvailable: 8388608 kB\n", encoding="utf-8")
        return pasta

    def projeto(self, texto):
        raiz = pasta_temporaria(self)
        (raiz / ".forge").mkdir()
        if texto is not None:
            (raiz / ".forge/config.json").write_text(texto, encoding="utf-8")
        return raiz

    def test_economico_limita_a_um_qualquer_teto(self):
        proc = self.proc()
        with mock.patch.dict(os.environ, {"FORGE_NPROC": "8"}):
            for config in ({}, {"teto_agentes": 4}, {"teto_maximo": 5}):
                with self.subTest(config=config):
                    teto, motivo = agentes.calcular_teto(config, proc, ritmo="econômico")
                    self.assertEqual(teto, 1)
                    self.assertIn("ritmo econômico", motivo)

    def test_equilibrado_e_acelerado_ficam_no_teto_de_sempre(self):
        proc = self.proc()
        with mock.patch.dict(os.environ, {"FORGE_NPROC": "8"}):
            for ritmo in ("equilibrado", "acelerado"):
                with self.subTest(ritmo=ritmo):
                    self.assertEqual(sem_excecao(agentes.calcular_teto, {}, proc, ritmo=ritmo), (8, "adaptativo: load 0.1 de 8 núcleos, 8.0 GB disponíveis"))
                    self.assertEqual(sem_excecao(agentes.calcular_teto, {"teto_maximo": 5}, proc, ritmo=ritmo), (5, mock.ANY))

    def test_le_o_ritmo_do_config_sem_caixa_nem_acento(self):
        for texto, esperado in (('{"ritmo": "econômico"}', "econômico"), ('{"ritmo": " Economico "}', "econômico"),
                                ('{"ritmo": "acelerado"}', "acelerado")):
            with self.subTest(texto=texto):
                self.assertEqual(agentes.ritmo_do_projeto(self.projeto(texto)), esperado)

    def test_ausente_invalido_ou_ilegivel_vale_o_padrao(self):
        for texto in (None, "{}", '{"ritmo": "turbo"}', '{"ritmo": 1}', '{"ritmo": null}', "[]", '"econômico"', "{ruim"):
            with self.subTest(texto=texto):
                self.assertEqual(sem_excecao(agentes.ritmo_do_projeto, self.projeto(texto)), "equilibrado")
        self.assertEqual(sem_excecao(agentes.ritmo_do_projeto, None), "equilibrado")


class ComandoRitmo(unittest.TestCase):
    def setUp(self):
        self.raiz = pasta_temporaria(self)
        self.env = sem_manutencao({"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(self.raiz), "LANG": "C.UTF-8",
                                   "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
        subprocess.run(["git", "init", "-q", str(self.raiz)], env=self.env, check=True)
        (self.raiz / ".forge").mkdir()
        self.config = self.raiz / ".forge/config.json"

    def forge(self, *args, cwd=None):
        return subprocess.run([sys.executable, "-I", str(RAIZ / "bin/forge-ritmo"), *args], cwd=cwd or self.raiz,
                              env=self.env, capture_output=True, text=True, timeout=30)

    def test_grava_o_valor_canonico_e_guarda_as_outras_chaves(self):
        self.config.write_text('{"pesados": ["make test"]}\n', encoding="utf-8")
        r = self.forge("economico")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(self.config.read_text(encoding="utf-8")), {"pesados": ["make test"], "ritmo": "econômico"})
        self.assertIn("Ritmo de agora: econômico", self.forge().stdout)

    def test_sem_valor_mostra_o_padrao_e_as_tres_opcoes(self):
        r = self.forge()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("equilibrado (padrão)", r.stdout)
        for nome in ("econômico", "equilibrado", "acelerado", "uma por vez"):
            self.assertIn(nome, r.stdout)
        self.assertFalse(self.config.exists())

    def test_valor_desconhecido_sai_2_sem_gravar(self):
        self.config.write_text('{"ritmo": "acelerado"}', encoding="utf-8")
        r = self.forge("turbo")
        self.assertEqual(r.returncode, 2)
        self.assertIn("valor desconhecido", r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertEqual(self.config.read_text(encoding="utf-8"), '{"ritmo": "acelerado"}')
        self.assertEqual(self.forge("acelerado", "x").returncode, 2)

    def test_config_ilegivel_ou_nao_objeto_sai_1_sem_gravar(self):
        for texto in ("{ruim", "[]"):
            with self.subTest(texto=texto):
                self.config.write_text(texto, encoding="utf-8")
                r = self.forge("acelerado")
                self.assertEqual(r.returncode, 1)
                self.assertIn("nada gravado", r.stderr)
                self.assertNotIn("Traceback", r.stderr)
                self.assertEqual(self.config.read_text(encoding="utf-8"), texto)

    def test_fora_de_projeto_do_forge_sai_1(self):
        shutil.rmtree(self.raiz / ".forge")
        fora = pasta_temporaria(self)
        for preparo, cwd in ((None, None), ("arquivo", None), (None, fora)):
            with self.subTest(preparo=preparo, cwd=cwd):
                if preparo:  # `.forge` como arquivo, como no clone do Forge
                    (self.raiz / ".forge").write_text("arquivo\n", encoding="utf-8")
                r = self.forge("acelerado", cwd=cwd)
                self.assertEqual(r.returncode, 1)
                self.assertIn("projeto do Forge", r.stderr)
                self.assertNotIn("Traceback", r.stderr)

    def test_ritmo_gravado_que_nao_e_texto_mostra_o_padrao(self):
        self.config.write_text('{"ritmo": 1}', encoding="utf-8")
        r = self.forge()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("equilibrado (padrão)", r.stdout)

    def test_ajuda_sai_0_e_mostra_o_uso(self):
        r = self.forge("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("forge ritmo <valor>", r.stdout)


if __name__ == "__main__":
    unittest.main()
