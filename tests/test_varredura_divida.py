"""VARREDURA-SEMANAL-DIVIDA (v0478 E95.1): `scripts/varredura-divida.py` só lê e lista a dívida, uma linha por achado.

Classe do defeito: achado que some (branch mesclada ou parada, módulo lento, trecho de mutante fora do lugar, regra sem
teste, cópias pesando no disco), achado falso (branch fixa, branch nova, módulo por teste, regra citada, cópias de
projeto) e a varredura gravando no repositório. Fixtures em pasta temporária; o script roda com `python3 -I` e sem o
git herdado (AR-4).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_git_herdado  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / "scripts" / "varredura-divida.py"
DIA = 86400


def ambiente(**extra):
    return sem_git_herdado(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_AUTHOR_NAME="t",
                           GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t", **extra)


def git(pasta, *args, dias=0):
    data = f"@{int(time.time()) - dias * DIA} +0000"
    r = subprocess.run(["git", "-C", str(pasta), *args], capture_output=True, text=True, check=True, timeout=60,
                       env=ambiente(GIT_AUTHOR_DATE=data, GIT_COMMITTER_DATE=data))
    return r.stdout.strip()


def commit(pasta, pai, dias):
    arvore = git(pasta, "write-tree")
    return git(pasta, "commit-tree", arvore, *(["-p", pai] if pai else []), "-m", f"c{dias}", dias=dias)


def gravar(raiz, caminho, texto):
    alvo = raiz / caminho
    alvo.parent.mkdir(parents=True, exist_ok=True)
    alvo.write_text(texto, encoding="utf-8")


def rodar(*args, script=SCRIPT):
    """Sem as PYTHON* herdadas (o forge-mutante liga PYTHONDONTWRITEBYTECODE ou PYTHONPYCACHEPREFIX): quem evita o
    cache no filho é o script."""
    env = {k: v for k, v in ambiente().items() if not k.startswith("PYTHON")}
    return subprocess.run([sys.executable, "-I", str(script), *args], capture_output=True, text=True, timeout=120,
                          env=env, cwd=tempfile.gettempdir())


def mutante(ident, de, arquivo="codigo.py"):
    return {"id": ident, "guarda": "g", "arquivo": arquivo, "de": de, "para": "troca", "testes": ["tests.test_x.C.test_y"]}


def fotografia(pasta):
    return {p.relative_to(pasta).as_posix(): p.read_bytes() for p in sorted(pasta.rglob("*")) if p.is_file()}


class Varredura(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.raiz, self.wt = self.tmp / "repo", self.tmp / "wt"
        self.raiz.mkdir()
        gravar(self.raiz, "tests/pesos-d4.json", json.dumps({"test_a": 5, "test_b": 50, "test_c": 20, "test_b.K.t": 900}))
        gravar(self.raiz, "codigo.py", "if x > 1:\n    dobro\n    dobro\n")
        gravar(self.raiz, "tests/mutantes/ok.json", json.dumps({"pedido": "ok", "executor": "unittest", "mutantes": [
            mutante("M1", "if x > 1:"), mutante("M2", "sumiu"), mutante("M3", "dobro"),
            mutante("M4", "if x > 1:", "nao-existe.py")]}))
        gravar(self.raiz, "docs/regras/R-COBERTA.md", "x")
        gravar(self.raiz, "docs/regras/R-SOLTA.md", "x")
        gravar(self.raiz, "tests/test_x.py", "# R-COBERTA e R-SOLTA2\n")
        gravar(self.raiz, ".claude-plugin/plugin.json", json.dumps({"name": "forge"}))
        gravar(self.wt, "um/grande.bin", "0" * (3 * 1024 * 1024))
        (self.wt / "dois").mkdir()
        gravar(self.wt, "solta.txt", "não é cópia")
        git(self.raiz, "init", "-q")
        git(self.raiz, "add", "-A")
        antiga = commit(self.raiz, None, 100)
        git(self.raiz, "update-ref", "HEAD", antiga)
        refs = {"main": antiga, "develop": commit(self.raiz, antiga, 0), "melhoria/mesclada": antiga,
                "melhoria/parada": commit(self.raiz, antiga, 60), "melhoria/nova": commit(self.raiz, antiga, 5)}
        for nome, sha in refs.items():
            git(self.raiz, "update-ref", f"refs/remotes/origin/{nome}", sha)

    def tearDown(self):
        self._tmp.cleanup()

    def varrer(self, *extra):
        r = rodar("--raiz", str(self.raiz), "--copias", str(self.wt), "--lentos", "2", "--mb", "2", *extra)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.splitlines()

    def test_lista_cada_achado_em_ordem_estavel(self):
        self.assertEqual(self.varrer(), [
            "branch-mesclada · melhoria/mesclada · contida na origin/develop · cartão: apagar a branch remota melhoria/mesclada",
            "branch-parada · melhoria/parada · 60 dias sem commit · cartão: retomar ou fechar a branch melhoria/parada",
            "teste-lento · test_b · 50.0 s · cartão: acelerar test_b (50.0 s por rodada)",
            "teste-lento · test_c · 20.0 s · cartão: acelerar test_c (20.0 s por rodada)",
            "mutante-velho · tests/mutantes/ok.json M2 · o trecho aparece 0 vezes em codigo.py (precisa de uma) · cartão: atualizar o trecho do M2 em tests/mutantes/ok.json",
            "mutante-velho · tests/mutantes/ok.json M3 · o trecho aparece 2 vezes em codigo.py (precisa de uma) · cartão: atualizar o trecho do M3 em tests/mutantes/ok.json",
            "mutante-velho · tests/mutantes/ok.json M4 · o trecho aparece 0 vezes em nao-existe.py (precisa de uma) · cartão: atualizar o trecho do M4 em tests/mutantes/ok.json",
            "regra-sem-teste · R-SOLTA · nenhum teste em tests/ cita o ID · cartão: teste que cubra R-SOLTA",
            f"copias · {self.wt} · 2 cópias, 3 MB · cartão: limpar as cópias sem branch aberta (git worktree remove)",
            "varredura: 9 achado(s)"])

    def test_so_le(self):
        antes = (fotografia(self.tmp), git(self.raiz, "for-each-ref"), git(self.raiz, "status", "--porcelain"))
        self.varrer()
        self.assertEqual((fotografia(self.tmp), git(self.raiz, "for-each-ref"), git(self.raiz, "status", "--porcelain")), antes)

    def test_filho_nao_grava_cache_de_bytecode_no_forge(self):
        """O forge-mutante filho roda sem gravar bin/__pycache__/ na cópia do Forge (git status vazio, nenhuma pasta nova)."""
        forge = self.tmp / "forge"
        shutil.copytree(RAIZ / "bin", forge / "bin", ignore=shutil.ignore_patterns("__pycache__"))
        (forge / "scripts").mkdir()
        shutil.copy2(SCRIPT, forge / "scripts")
        git(forge, "init", "-q")
        git(forge, "add", "-A")
        git(forge, "commit", "-q", "-m", "c")
        r = rodar("--raiz", str(self.raiz), "--copias", str(self.wt), "--lentos", "2", "--mb", "2",
                  script=forge / "scripts" / "varredura-divida.py")
        self.assertEqual((r.returncode, r.stdout.splitlines()), (0, self.varrer()), r.stderr)
        self.assertEqual((git(forge, "status", "--porcelain", "--ignored"), sorted(forge.rglob("__pycache__"))), ("", []))

    def test_sem_develop_a_base_e_a_main(self):
        nova_main = git(self.raiz, "rev-parse", "origin/develop")
        git(self.raiz, "update-ref", "-d", "refs/remotes/origin/develop")
        git(self.raiz, "update-ref", "refs/remotes/origin/main", nova_main)
        branches = [linha for linha in self.varrer() if linha.startswith("branch-")]
        self.assertEqual([linha.split(" · ")[:3] for linha in branches],
                         [["branch-mesclada", "melhoria/mesclada", "contida na origin/main"],
                          ["branch-parada", "melhoria/parada", "60 dias sem commit"]])

    def test_base_dada_nao_se_lista(self):
        branches = [linha.split(" · ")[:3] for linha in self.varrer("--base", "origin/melhoria/nova") if linha.startswith("branch-")]
        self.assertEqual(branches, [["branch-mesclada", "melhoria/mesclada", "contida na origin/melhoria/nova"],
                                    ["branch-parada", "melhoria/parada", "60 dias sem commit"]])

    def test_spec_no_lugar_nao_gera_achado(self):
        gravar(self.raiz, "tests/mutantes/ok.json", json.dumps({"pedido": "ok", "executor": "unittest",
                                                                "mutantes": [mutante("M1", "if x > 1:")]}))
        git(self.raiz, "add", "-A")
        git(self.raiz, "update-ref", "HEAD", commit(self.raiz, git(self.raiz, "rev-parse", "HEAD"), 0))
        self.assertFalse([linha for linha in self.varrer() if linha.startswith("mutante-velho")])

    def test_spec_recusada_vira_um_achado_e_sem_spec_nenhum(self):
        gravar(self.raiz, "tests/mutantes/ruim.json", "{")
        git(self.raiz, "add", "-A")
        git(self.raiz, "update-ref", "HEAD", commit(self.raiz, git(self.raiz, "rev-parse", "HEAD"), 0))
        velhos = [linha for linha in self.varrer() if linha.startswith("mutante-velho")]
        self.assertEqual(len(velhos), 1, velhos)
        self.assertRegex(velhos[0], r"^mutante-velho · tests/mutantes · forge-mutante: .+ · cartão: corrigir a spec que o forge-mutante recusa$")
        for spec in (self.raiz / "tests" / "mutantes").glob("*.json"):
            spec.unlink()
        self.assertFalse([linha for linha in self.varrer() if linha.startswith("mutante-velho")])

    def test_pesos_ilegiveis_nao_geram_achado(self):
        gravar(self.raiz, "tests/pesos-d4.json", "[1, 2]")
        self.assertFalse([linha for linha in self.varrer() if linha.startswith("teste-lento")])

    def test_copias_abaixo_do_limite_ou_fora_do_forge_nao_se_listam(self):
        self.assertFalse([linha for linha in self.varrer("--mb", "3") if linha.startswith("copias")])
        self.assertEqual(self.varrer("--copias", str(self.tmp / "nada"), "--mb", "0")[-1], "varredura: 8 achado(s)")
        gravar(self.raiz, ".forge/versao", "0.0.0")
        self.assertFalse([linha for linha in self.varrer("--mb", "0") if linha.startswith("copias")])
        (self.raiz / ".forge" / "versao").unlink()
        gravar(self.raiz, ".claude-plugin/plugin.json", json.dumps({"name": "outro"}))
        self.assertFalse([linha for linha in self.varrer("--mb", "0") if linha.startswith("copias")])

    def test_subpasta_varre_o_repositorio_inteiro(self):
        self.assertEqual(rodar("--raiz", str(self.raiz / "docs"), "--copias", str(self.wt), "--lentos", "2", "--mb", "2").stdout,
                         "\n".join(self.varrer()) + "\n")

    def test_pasta_fora_do_git_varre_o_que_tem(self):
        sem_git = Path(self._tmp.name) / "solto"
        gravar(sem_git, "docs/regras/R-SOLTA.md", "x")
        r = rodar("--raiz", str(sem_git), "--copias", str(self.wt), "--mb", "-1")
        self.assertEqual((r.returncode, r.stdout.splitlines()), (0, [
            "regra-sem-teste · R-SOLTA · nenhum teste em tests/ cita o ID · cartão: teste que cubra R-SOLTA",
            "varredura: 1 achado(s)"]), r.stderr)

    def test_raiz_que_nao_existe_e_erro_de_uso(self):
        r = rodar("--raiz", str(self.tmp / "nada"))
        self.assertEqual((r.returncode, r.stdout), (2, ""))
        self.assertIn("não é pasta", r.stderr)


class ProjetoDoForgeInit(unittest.TestCase):
    def test_projeto_novo_roda_sem_achado(self):
        with tempfile.TemporaryDirectory() as tmp:
            projeto = Path(tmp) / "proj"
            projeto.mkdir()
            git(projeto, "init", "-q")
            subprocess.run(["bash", str(RAIZ / "bin" / "forge-init"), "--nome", "Demo", str(projeto)], check=True,
                           capture_output=True, text=True, timeout=120, env=ambiente())
            r = rodar("--raiz", str(projeto), "--copias", tmp, "--mb", "-1")
            self.assertEqual((r.returncode, r.stdout.splitlines()), (0, ["varredura: 0 achado(s)"]), r.stderr)


if __name__ == "__main__":
    unittest.main()
