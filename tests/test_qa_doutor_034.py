"""QA do AVISO-VERSAO-UMA-VEZ (versao-033): hook real, virada de dia por FORGE_HOJE, remoto git local e raiz descartável."""
import importlib.machinery
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_doutor as td  # noqa: E402

DIAS = ["2026-11-01", "2026-11-02", "2026-11-03", "2026-11-04"]


class AvisoUmaVezPontaAPonta(td.DoutorVersao):
    def stop_em(self, dia):
        entrada = json.dumps({"hook_event_name": "Stop", "session_id": "s1", "cwd": str(self.proj)})
        r = subprocess.run([sys.executable, str(td.HOOK)], input=entrada, env=dict(self.env, FORGE_HOJE=dia), cwd=self.proj,
                           capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def avisa(self, dia, versao):
        return f"Saiu a versão {versao}" in self.stop_em(dia)

    def test_tres_dias_seguidos_avisa_so_no_primeiro_e_o_atraso_segue_provado(self):  # CA: uma vez só; fronteira: dia 2 e dia 3
        nova = self.mais_nova()
        self.tag(f"v{nova}")
        self.assertEqual([self.avisa(d, nova) for d in DIAS[:3]], [True, False, False])
        c = self.cache()
        self.assertEqual((c["data"], c["defasado"], c["atual"], c["ultima"]), (DIAS[2], True, self.versao, nova))

    def test_versao_ainda_mais_nova_avisa_e_depois_cala(self):  # CA: versão mais nova volta a avisar, uma vez
        nova = self.mais_nova()
        self.tag(f"v{nova}")
        self.assertTrue(self.avisa(DIAS[0], nova))
        a, b, c = (int(n) for n in self.versao.split("."))
        outra = f"{a}.{b}.{c + 2}"
        self.tag(f"v{outra}")
        self.assertEqual([self.avisa(DIAS[1], outra), self.avisa(DIAS[2], outra)], [True, False])

    def test_sem_rede_no_dia_do_meio_nao_perde_o_silencio_nem_o_aviso_futuro(self):  # borda: consulta falha
        nova = self.mais_nova()
        self.tag(f"v{nova}")
        self.assertTrue(self.avisa(DIAS[0], nova))
        sumido = self.tmp / "publicado-fora.git"
        self.publicado.rename(sumido)
        self.assertNotIn("Saiu a versão", self.stop_em(DIAS[1]))  # falhou: sem aviso de versão e sem quebrar
        sumido.rename(self.publicado)
        arq = self.proj / ".forge/run/versao-nova"
        antigo = self.cache()
        self.assertIn("falhou_em", antigo)  # a falha preserva a marca de aviso e o par
        self.assertEqual((antigo["avisado"], antigo["ultima"]), (True, nova))
        antigo["falhou_em"] = 0  # passou a espera de nova tentativa (o relógio real não deixa esperar no teste)
        arq.write_text(json.dumps(antigo), encoding="utf-8")
        self.assertFalse(self.avisa(DIAS[2], nova))  # a mesma versão continua calada depois da falha
        a, b, c = (int(n) for n in self.versao.split("."))
        self.tag(f"v{a}.{b}.{c + 2}")
        self.assertTrue(self.avisa(DIAS[3], f"{a}.{b}.{c + 2}"))

    def test_cache_adulterado_nao_derruba_o_hook_nem_cala_o_aviso(self):  # borda: tipo errado em avisado, lixo no arquivo
        nova = self.mais_nova()
        self.tag(f"v{nova}")
        self.assertTrue(self.avisa(DIAS[0], nova))
        par = {"atual": self.versao, "ultima": nova, "defasado": True, "data": DIAS[0]}
        for dia, lixo in zip((DIAS[1], DIAS[1], DIAS[2], DIAS[3]),  # só `True` literal silencia; JSON inválido e lista não derrubam
                             (json.dumps({**par, "avisado": "true"}), json.dumps({**par, "avisado": 1}), "{não é json", "[1,2]")):
            (self.proj / ".forge/run/versao-nova").write_text(lixo, encoding="utf-8")
            self.assertTrue(self.avisa(dia, nova), lixo)

    def test_o_forge_check_le_o_atraso_do_cache_mesmo_calado(self):  # o cache continua provando para o forge-check
        nova = self.mais_nova()
        self.tag(f"v{nova}")
        self.assertEqual([self.avisa(d, nova) for d in DIAS[:2]], [True, False])
        self.assertEqual(self.cache()["avisado"], True)
        carregador = importlib.machinery.SourceFileLoader("forge_check_qa", str(td.RAIZ / "bin/forge-check"))
        fc = importlib.util.module_from_spec(importlib.util.spec_from_loader("forge_check_qa", carregador))
        carregador.exec_module(fc)
        fc.versao_da_propria_copia = lambda: self.versao
        self.assertEqual(fc.comparar_com_o_cache_do_projeto(self.proj)[0], "atrasada")


def load_tests(loader, tests, pattern):  # só os testes desta classe, não os herdados do DoutorVersao
    return unittest.TestSuite(AvisoUmaVezPontaAPonta(n) for n in AvisoUmaVezPontaAPonta.__dict__ if n.startswith("test_"))
