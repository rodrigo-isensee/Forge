"""RECIBO-CONTADOR-PELO-HOOK, item 4 (v0481 E20.11): o hook `ordens_teto` recusa gravar as ordens em vigor acima do teto do
hook `ordens` (15 linhas, 2000 caracteres) no Write, no Edit e no MultiEdit. Roda o hook de verdade (subprocesso com ambiente
limpo e Python com `-s -E`, a forma do hooks.json; o `-I` tiraria a pasta do script, de onde vem o `_comum`) num projeto
temporário com `.forge/versao` e git próprio; cada guarda tem o caso do ramo que recusa e o do que passa."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
HOOK = RAIZ / "hooks" / "ordens_teto.py"
ORDENS = ".forge/ordens/ordens-em-vigor.md"


def ordens(n):
    return "".join(f"ordem {i}\n" for i in range(1, n + 1))


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-ordens-teto-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.projeto = self.tmp / "projeto"
        (self.projeto / ".forge" / "ordens").mkdir(parents=True)
        (self.projeto / ".forge" / "versao").write_text("0.1.0\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q", str(self.projeto)], env=self.ambiente(), check=True, capture_output=True,
                       timeout=60)
        self.arquivo = self.projeto / ORDENS

    def ambiente(self):
        return {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(self.tmp), "LANG": "C.UTF-8",
                "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull}

    def rodar(self, ferramenta, entrada, evento="PreToolUse"):
        dados = {"hook_event_name": evento, "session_id": "s1", "tool_name": ferramenta, "tool_input": entrada,
                 "cwd": str(self.projeto)}
        return subprocess.run([sys.executable, "-s", "-E", str(HOOK)], input=json.dumps(dados), cwd=self.projeto,
                              env=self.ambiente(), capture_output=True, text=True, timeout=60)

    def write(self, conteudo, caminho=None):
        return self.rodar("Write", {"file_path": str(caminho or self.arquivo), "content": conteudo})

    def edit(self, velho, novo, **extra):
        return self.rodar("Edit", {"file_path": str(self.arquivo), "old_string": velho, "new_string": novo, **extra})

    def recusa(self, r, trecho):
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn(trecho, r.stderr)

    def passa(self, r):
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""))
        self.assertFalse((self.projeto / ".forge" / "run" / "erros.log").exists(), "nenhum erro interno")


class Write(Base):
    def test_16_linhas_recusa_com_as_contagens_e_15_passa(self):
        self.recusa(self.write(ordens(16)), "R-CONFORMIDADE: ordens-em-vigor.md ficaria com 16 linhas e "
                                            f"{len(ordens(16)) - 1} caracteres, acima do teto de 15 linhas e 2000")
        self.passa(self.write(ordens(15)))

    def test_2001_caracteres_recusa_e_2000_passa(self):
        self.recusa(self.write("x" * 2001), "1 linhas e 2001 caracteres")
        self.passa(self.write("x" * 2000))

    def test_outro_arquivo_passa(self):
        self.passa(self.write(ordens(20), self.projeto / "docs" / "notas.md"))

    def test_caminho_relativo_a_pasta_corrente_e_contado(self):
        self.recusa(self.rodar("Write", {"file_path": ORDENS, "content": ordens(16)}), "16 linhas")

    def test_sem_caminho_ou_conteudo_fora_da_forma_passa(self):
        self.passa(self.rodar("Write", {"content": ordens(16)}))
        self.passa(self.rodar("Write", {"file_path": 5, "content": ordens(16)}))
        self.passa(self.rodar("Write", {"file_path": str(self.arquivo), "content": ["x"] * 16}))

    def test_outro_evento_ou_outra_ferramenta_passa(self):
        self.passa(self.rodar("Write", {"file_path": str(self.arquivo), "content": ordens(16)}, evento="PostToolUse"))
        self.passa(self.rodar("NotebookEdit", {"file_path": str(self.arquivo), "content": ordens(16)}))

    def test_fora_de_projeto_do_forge_passa(self):
        (self.projeto / ".forge" / "versao").unlink()
        self.passa(self.write(ordens(16)))


class Edit(Base):
    def test_troca_que_passa_do_teto_recusa_e_a_que_cabe_passa(self):
        self.arquivo.write_text("ordem 1\n", encoding="utf-8")
        self.recusa(self.edit("ordem 1", "x" * 2045), "1 linhas e 2045 caracteres")
        self.passa(self.edit("ordem 1", "x" * 1999))

    def test_trecho_ausente_ou_vazio_ou_arquivo_ausente_passa(self):
        self.arquivo.write_text("ordem 1\n", encoding="utf-8")
        self.passa(self.edit("não existe", "x" * 2045))
        self.passa(self.edit("", "x" * 2045))
        self.passa(self.edit("ordem 1", ["x"] * 2045))
        self.arquivo.write_text(ordens(16), encoding="utf-8")  # já acima do teto (gravado pelo Bash): a troca falha sozinha
        self.passa(self.edit("não existe", "x"))
        self.arquivo.unlink()
        self.passa(self.edit("ordem 1", "x" * 2045))

    def test_replace_all_troca_todas_e_sem_ele_so_a_primeira(self):
        self.arquivo.write_text("a\n" * 8, encoding="utf-8")
        self.passa(self.edit("a", "x" * 300))
        self.recusa(self.edit("a", "x" * 300, replace_all=True), "8 linhas e 2407 caracteres")


class MultiEdit(Base):
    def multi(self, edicoes):
        return self.rodar("MultiEdit", {"file_path": str(self.arquivo), "edits": edicoes})

    def test_as_trocas_somadas_contam(self):
        self.arquivo.write_text(ordens(14), encoding="utf-8")
        self.recusa(self.multi([{"old_string": "ordem 14\n", "new_string": "ordem 14\nordem 15\n"},
                                {"old_string": "ordem 15\n", "new_string": "ordem 15\nordem 16\n"}]), "16 linhas")
        self.passa(self.multi([{"old_string": "ordem 14\n", "new_string": "ordem 14\nordem 15\n"}]))

    def test_troca_que_falha_ou_fora_da_forma_passa(self):
        self.arquivo.write_text(ordens(14), encoding="utf-8")
        mais = {"old_string": "ordem 14\n", "new_string": "ordem 14\nordem 15\nordem 16\n"}
        self.passa(self.multi([mais, {"old_string": "não existe", "new_string": "x"}]))
        self.passa(self.multi([{"old_string": "não existe", "new_string": "x"}, mais]))
        self.passa(self.multi([mais, "não é troca"]))
        self.passa(self.multi(mais))


if __name__ == "__main__":
    unittest.main()
