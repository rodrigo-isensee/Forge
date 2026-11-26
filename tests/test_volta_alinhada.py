"""R-QA (ORDEM DO DONO 25/11 07:31; v0481 E14.44): a conferência da entrega (`forge-check entrega --pedido`) da 3ª volta em diante
recusa teste removido ou enfraquecido no diff da volta, com as medidas da catraca; a 2ª volta não tem a restrição. Sem rede."""
import hashlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_selo_e_entrega import Repositorio  # noqa: E402

DOIS_TESTES = "def test_a():\n    assert 1\n\n\ndef test_b():\n    assert 2\n"


class TerceiraVoltaNaConferencia(Repositorio):
    def setUp(self):
        super().setUp()
        self.git("switch", "-q", "develop")  # a base já traz o teste que a volta não pode enfraquecer
        self.gravar("tests/test_a.py", DOIS_TESTES)
        self.git("add", "tests/test_a.py")
        self.commit("teste da base")
        self.git("push", "-q", "origin", "develop")
        self.git("fetch", "-q", "origin")
        self.git("switch", "-q", "melhoria/x")
        self.git("merge", "-q", "--ff-only", "develop")
        self.base = self.git("rev-parse", "HEAD")

    def selar_volta(self, n):
        """O brief de código da branch com `## Entregar (volta n)`, selado pela linha do Histórico (a volta à mão não passa no `selar`)."""
        arq = self.brief(arquivos="bin/app, docs/notas/, tests/")
        texto = arq.read_text(encoding="utf-8")
        self.assertIn("## Entregar\n", texto)
        arq.write_text(texto.replace("## Entregar\n", f"## Entregar (volta {n})\n", 1), encoding="utf-8")
        sha = hashlib.sha256(arq.read_bytes()).hexdigest()
        pedido = self.proj / "docs/pedidos/exemplo.md"
        pedido.write_text(self.pedido() + f"- 2026-01-01 09:30: brief selado docs/briefs/{arq.name} {sha}\n", encoding="utf-8")

    def entregar_sem_um_teste(self):
        self.gravar("tests/test_a.py", "def test_a():\n    assert 1\n")
        return self.entregar("tests/test_a.py")

    def conferir(self):
        return self.rodar("entrega", "--pedido", "exemplo", "--branch", "melhoria/x", "--etapa", "codigo", "--sem-gravar")

    def test_terceira_volta_que_remove_teste_nao_cumpre(self):
        self.selar_volta(3)
        self.entregar_sem_um_teste()
        rc, saida = self.conferir()
        self.assertIn("volta: a volta 3 em diante só corrige o que o portão apontou, sem mudar lógica nem enfraquecer teste (R-QA): "
                      "R-CONFORMIDADE: testes `test_*` caíram de 2 para 1", saida)
        self.assertIn("resultado: não cumpriu", saida)
        self.assertEqual(rc, 1, saida)

    def test_segunda_volta_nao_tem_a_restricao(self):
        self.selar_volta(2)
        self.entregar_sem_um_teste()
        rc, saida = self.conferir()
        self.assertNotIn("(R-QA)", saida)

    def test_terceira_volta_sem_mexer_em_teste_cumpre_a_restricao(self):
        self.selar_volta(3)
        self.entregar()
        rc, saida = self.conferir()
        self.assertNotIn("(R-QA)", saida)


if __name__ == "__main__":
    unittest.main()
