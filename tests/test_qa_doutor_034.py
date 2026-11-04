"""QA do AVISO-VERSAO-UMA-VEZ (pedido versao-033): o hook `doutor.py` roda de verdade, com virada de dia real (FORGE_HOJE por chamada,
sem editar o cache), remoto git local e raiz descartável. Obrigação: a mesma versão nova avisa uma vez; versão mais nova volta a avisar;
o cache segue provando o atraso para o `forge-check`; cache adulterado não esconde aviso nem derruba o hook."""
import importlib.machinery
import importlib.util
import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_doutor as td  # noqa: E402

RAIZ = td.RAIZ
DIAS = ["2026-11-01", "2026-11-02", "2026-11-03", "2026-11-04"]


class AvisoUmaVezPontaAPonta(td.DoutorVersao):

    def stop_em(self, dia):
        entrada = {"hook_event_name": "Stop", "session_id": "s1", "cwd": str(self.proj)}
        env = dict(self.env, FORGE_HOJE=dia)
        r = subprocess.run([sys.executable, str(td.HOOK)], input=json.dumps(entrada), env=env, cwd=self.proj,
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
        arq = self.proj / ".forge/run/versao-nova"
        for lixo in ({"avisado": "true", "atual": self.versao, "ultima": nova, "defasado": True, "data": DIAS[0]},
                     {"avisado": 1, "atual": self.versao, "ultima": nova, "defasado": True, "data": DIAS[0]}):
            arq.write_text(json.dumps(lixo), encoding="utf-8")
            self.assertTrue(self.avisa(DIAS[1], nova), lixo)  # só `True` literal silencia
        arq.write_text("{não é json", encoding="utf-8")
        self.assertTrue(self.avisa(DIAS[2], nova))
        arq.write_text("[1,2]", encoding="utf-8")
        self.assertTrue(self.avisa(DIAS[3], nova))

    def test_o_forge_check_le_o_atraso_do_cache_mesmo_calado(self):  # o cache continua provando para o forge-check
        nova = self.mais_nova()
        self.tag(f"v{nova}")
        self.avisa(DIAS[0], nova)
        self.avisa(DIAS[1], nova)
        self.assertEqual(self.cache()["avisado"], True)
        carregador = importlib.machinery.SourceFileLoader("forge_check_qa", str(RAIZ / "bin/forge-check"))
        spec = importlib.util.spec_from_loader("forge_check_qa", carregador)
        fc = importlib.util.module_from_spec(spec)
        carregador.exec_module(fc)
        fc.versao_da_propria_copia = lambda: self.versao
        estado, _ = fc.comparar_com_o_cache_do_projeto(self.proj)
        self.assertEqual(estado, "atrasada")


def load_tests(loader, tests, pattern):  # só os testes desta classe, não os herdados do DoutorVersao
    suite = unittest.TestSuite()
    for nome in AvisoUmaVezPontaAPonta.__dict__:
        if nome.startswith("test_"):
            suite.addTest(AvisoUmaVezPontaAPonta(nome))
    return suite


if __name__ == "__main__":
    unittest.main()
