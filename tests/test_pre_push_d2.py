"""PORTAO-D2 (E173.2, estudo determinístico de 24/11): o D2 do `.githooks/pre-push`, provado pelo ajuste único.

Ajuste único (v0478 E174.9, decisão do dono de 24/11): o D2 vai por cima do patch do envio local, num patch só,
`patches/prepush-unico.patch`; este módulo prova o D2 nele e o `tests/test_prepush_unico.py` prova o envio local.

O `.githooks/pre-push` em vigor é arquivo do dono e não muda neste item: o teste copia o hook para $TMPDIR, aplica o patch na cópia e
roda o original e o remendado de verdade num repositório descartável, com um `gh` falso no PATH. Cada checagem nova barra no
remendado e passa no original: o índice do Forge (bin/, hooks/, scripts/ tocados), o teto H1 com o PR aberto sem `teto: excedido` e o
passo pr-texto da catraca (seções e T1). Sem PR, o teto só avisa; sem rede, tudo avisa e segue (o CI confere); o envio só de
parecer (docs/{reviews,qa,security,devops}/) só avisa, para o revisor enviar o parecer que reprova (E173.16). A neutralidade já
estava no hook (PARECER-NEUTRALIDADE-CEDO) e segue barrando no remendado. Nenhum teste local passa a rodar no envio (ENVIO-LEVE).
Depois que o dono aplicar o patch, o hook em vigor já tem o PORTAO-D2: o teste confere só ele e pula a comparação com o original.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
HOOK = RAIZ / ".githooks" / "pre-push"
PATCH = RAIZ / "patches" / "prepush-unico.patch"
AMBIENTE = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_", "GH_", "GITHUB_"))})
ZERO = "0" * 40
BRANCH = "melhoria/x"
TERMO = "pilhafalsa"  # stack inventada: o detector do núcleo lê a lista do config.json do repositório descartável
CONFIG = {"termos_proibidos_hash": [], "neutralidade_nucleo": {"termos": [rf"\b{TERMO}\b"], "pastas": ["agents/"]}}
# gh falso: só responde ao `gh pr view <BRANCH> --json ...` com o nome exato da branch (checklist 12: nada de prefixo).
GH_FALSO = """#!/bin/bash
[ "$1 $2" = "pr view" ] && [ "$3" = "$GH_FALSO_BRANCH" ] || { echo "gh falso: chamada inesperada: $*" >&2; exit 3; }
case "$GH_FALSO_MODO" in
  sem-pr) echo "no pull requests found for branch \\"$3\\"" >&2; exit 1 ;;
  sem-rede) echo "error connecting to api.github.com" >&2; exit 1 ;;
  *) cat "$GH_FALSO_JSON" ;;
esac
"""
SECOES = "## Projeto de origem\nFábrica, estudo determinístico de 24/11.\n\n## Como medir\nMenos voltas de forma nas revisões do PR.\n"
# Índice falso no lugar do scripts/indice-forge.py (o real é do test_indice_forge): a saída do `--conferir` é o número gravado em
# `estado-do-indice`, fora do repositório (0 em dia, 1 fora de dia, outro = não conferiu), e cada chamada deixa a marca `indice-chamado`.
INDICE_FALSO = """import sys
from pathlib import Path
Path("../indice-chamado").write_text("sim")
rc = int(Path("../estado-do-indice").read_text().split()[0])
print(f"docs/indice-forge.md: estado {rc}")
sys.exit(rc if sys.argv[1:] == ["--conferir"] else 9)
"""
TESTE = "import unittest\nclass T(unittest.TestCase):\n    def test_a(self):\n        pass\n"


def aplicado(texto):
    return "PORTAO-D2" in texto


def codigo(linhas):
    """Módulo Python com docstring (o índice lê a primeira linha) e `linhas` linhas no total."""
    return '"""Ferramenta de teste."""\n' + "".join(f"x{i} = {i}\n" for i in range(linhas - 1))


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        raiz = Path(cls._tmp.name)
        orig, novo = raiz / "orig" / ".githooks", raiz / "novo" / ".githooks"
        for pasta in (orig, novo):
            pasta.mkdir(parents=True)
        cls.em_vigor_remendado = aplicado(HOOK.read_text(encoding="utf-8"))
        shutil.copy2(HOOK, novo / "pre-push")
        cls.originais = []
        if not cls.em_vigor_remendado:  # o dono ainda não aplicou: prova o original e o remendado
            shutil.copy2(HOOK, orig / "pre-push")
            r = subprocess.run(["git", "apply", str(PATCH)], cwd=raiz / "novo", env=AMBIENTE, capture_output=True, text=True)
            assert r.returncode == 0, r.stderr
            cls.originais = [orig / "pre-push"]
        cls.remendado = novo / "pre-push"
        falso = raiz / "falso"
        falso.mkdir()
        (falso / "gh").write_text(GH_FALSO)
        (falso / "gh").chmod(0o755)
        cls.path = f"{falso}{os.pathsep}{AMBIENTE.get('PATH', '')}"

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._dir.cleanup)
        base = Path(self._dir.name)
        self.repo = base / "repo"
        shutil.copytree(RAIZ / "bin", self.repo / "bin", ignore=shutil.ignore_patterns("__pycache__"))
        (self.repo / "scripts").mkdir()
        (self.repo / "scripts" / "indice-forge.py").write_text(INDICE_FALSO)
        self.estado_do_indice = base / "estado-do-indice"
        self.estado_do_indice.write_text("0\n")
        (self.repo / "tests").mkdir()
        for nome in ("catraca.py", "neutralidade.py"):
            shutil.copy(RAIZ / "tests" / nome, self.repo / "tests")
        (self.repo / "tests" / "config.json").write_text(json.dumps(CONFIG))
        (self.repo / ".gitignore").write_text("__pycache__/\n")
        self.pr_json = base / "pr.json"
        self.env = dict(AMBIENTE, PATH=self.path, HOME=str(base / "home"), XDG_RUNTIME_DIR=str(base),
                        GH_FALSO_BRANCH=BRANCH, GH_FALSO_JSON=str(self.pr_json), GH_FALSO_MODO="sem-pr")
        self.git("init", "-q", "-b", BRANCH)
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "t")
        self.commit("base")
        self.git("update-ref", "refs/remotes/origin/develop", "HEAD")

    def git(self, *args):
        r = subprocess.run(["git", *args], cwd=self.repo, env=AMBIENTE, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def commit(self, msg, indice=None, **arquivos):
        """`indice`: a saída que o índice falso dá depois deste commit (None mantém a de antes)."""
        if indice is not None:
            self.estado_do_indice.write_text(f"{indice}\n")
        for nome, texto in arquivos.items():
            alvo = self.repo / nome
            alvo.parent.mkdir(parents=True, exist_ok=True)
            alvo.write_text(texto)
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", msg)

    def pr(self, corpo, estado="OPEN"):
        self.env["GH_FALSO_MODO"] = "json"
        self.pr_json.write_text(json.dumps({"number": 7, "state": estado, "headRefOid": "a" * 40, "body": corpo}))

    def roda(self, hook, remoto=ZERO, ref=f"refs/heads/{BRANCH}", sha=None):
        """Envio de uma ref: `sha` local (HEAD por padrão) sobre o `remoto` (ZERO: a ref ainda não existe no remoto)."""
        sha = sha or self.git("rev-parse", "HEAD")
        r = subprocess.run([str(hook), "origin", "u"], cwd=self.repo, env=self.env, capture_output=True, text=True, timeout=120,
                           input=f"{ref} {sha} {ref} {remoto}\n")
        return r.returncode, r.stderr

    def compara(self, barra_com):
        """O remendado barra com o texto `barra_com`; o original (sem o patch) deixa passar."""
        codigo_, erro = self.roda(self.remendado)
        self.assertEqual(codigo_, 1, erro)
        self.assertIn(barra_com, erro)
        self.assertNotIn("envio leve", erro)
        for hook in self.originais:
            codigo_, erro = self.roda(hook)
            self.assertEqual(codigo_, 0, f"sem o patch o envio passava: {erro}")
            self.assertNotIn(barra_com, erro)

    def passa(self):
        codigo_, erro = self.roda(self.remendado)
        self.assertEqual(codigo_, 0, erro)
        self.assertIn("envio leve", erro, "o portão não pode trocar o envio leve por teste local")
        self.assertNotIn("rodando só os testes", erro)
        return erro


class PatchAplica(Base):
    def test_patch_so_toca_o_pre_push_e_mantem_o_modo(self):
        texto = PATCH.read_text(encoding="utf-8")
        self.assertEqual(re.findall(r"^diff --git (\S+) (\S+)$", texto, re.M), [("a/.githooks/pre-push", "b/.githooks/pre-push")])
        r = subprocess.run(["bash", "-n", str(self.remendado)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.access(self.remendado, os.X_OK))

    def test_patch_nao_acrescenta_teste_local_ao_envio(self):  # ENVIO-LEVE e G3: só checagem barata
        novas = [l for l in PATCH.read_text(encoding="utf-8").splitlines() if l.startswith("+") and not l.startswith("+++")]
        self.assertGreater(len(novas), 20)
        self.assertFalse([l for l in novas if re.search(r"unittest|forge-testes|suite-paralela", l)])


class Indice(Base):
    def chamado(self):
        marca = self.repo.parent / "indice-chamado"
        chamado = marca.exists()
        marca.unlink(missing_ok=True)
        return chamado

    def test_codigo_novo_sem_indice_barra_e_com_indice_passa(self):
        for pasta in ("bin", "hooks", "scripts"):
            with self.subTest(pasta):
                self.git("update-ref", "refs/remotes/origin/develop", "HEAD")  # cada pasta sozinha no delta (QA A1)
                self.commit("ferramenta nova", indice=1, **{f"{pasta}/nova_{pasta}.py": codigo(3), "tests/test_nova.py": TESTE})
                self.compara("docs/indice-forge.md fora de dia")
                self.assertIn("docs/indice-forge.md: estado 1", self.roda(self.remendado)[1])
                self.commit("indice", indice=0)
                self.chamado()
                self.passa()
                self.assertTrue(self.chamado(), "o envio que toca código confere o índice")

    def test_indice_que_nao_conferiu_avisa_e_segue(self):
        self.commit("ferramenta nova", indice=2, **{"bin/nova.py": codigo(3), "tests/test_nova.py": TESTE})
        self.assertIn("scripts/indice-forge.py --conferir não conferiu (saída 2)", self.passa())

    def test_envio_que_nao_toca_codigo_nao_confere_o_indice(self):
        self.commit("base com o índice velho", indice=1)  # a develop já veio assim; o envio só toca docs/
        self.git("update-ref", "refs/remotes/origin/develop", "HEAD")
        self.commit("so texto", **{"docs/a.md": "texto\n"})
        self.chamado()
        self.passa()
        self.assertFalse(self.chamado(), "envio sem bin/, hooks/ nem scripts/ não roda o índice")


class Teto(Base):
    def grande(self):
        self.commit("item grande", indice=0, **{"bin/grande.py": codigo(160), "tests/test_grande.py": TESTE})

    def test_sem_pr_aberto_o_teto_so_avisa(self):
        self.grande()
        erro = self.passa()
        self.assertIn("tamanho: 160 linhas de código, acima do teto de 150", erro)
        for hook in self.originais:
            self.assertNotIn("tamanho:", self.roda(hook)[1])

    def test_pr_aberto_sem_teto_excedido_barra_e_com_ele_passa(self):
        self.grande()
        self.pr(SECOES)
        self.compara("sem a linha `teto: excedido, 160 linhas, <motivo>` no corpo do PR #7")
        self.pr(SECOES + "\nteto: excedido, 160 linhas, cortar mais deixa a suíte vermelha\n")
        self.passa()

    def test_numero_menor_que_o_medido_nao_libera(self):
        self.grande()
        self.pr(SECOES + "\nteto: excedido, 150 linhas, número antigo\n")
        self.assertEqual(self.roda(self.remendado)[0], 1)

    def test_no_teto_nao_avisa(self):
        self.commit("no teto", indice=0, **{"bin/media.py": codigo(150), "tests/test_media.py": TESTE})
        self.pr(SECOES)
        self.assertNotIn("tamanho:", self.passa())


class TextoDoPr(Base):
    def test_pr_aberto_sem_como_medir_barra(self):
        self.commit("texto", **{"docs/a.md": "texto\n"})
        self.pr("## Projeto de origem\nFábrica, estudo determinístico de 24/11.\n")
        self.compara("PR sem a seção 'Como medir' preenchida")

    def test_codigo_sem_teste_nem_sem_teste_no_corpo_barra(self):  # T1, o mesmo passo pr-texto do CI
        self.commit("sem teste", indice=0, **{"bin/so_codigo.py": codigo(30)})
        self.pr(SECOES)
        self.compara("(T1)")
        self.pr(SECOES + "\n## Sem teste\n- bin/so_codigo.py: módulo de exemplo sem comportamento a provar aqui\n")
        self.passa()

    def test_pr_fechado_ou_mesclado_nao_e_conferido(self):
        self.commit("texto", **{"docs/a.md": "texto\n"})
        for estado in ("CLOSED", "MERGED"):
            with self.subTest(estado):
                self.pr("", estado=estado)
                self.passa()

    def test_sem_rede_avisa_e_segue(self):
        self.commit("texto", **{"docs/a.md": "texto\n"})
        self.env["GH_FALSO_MODO"] = "sem-rede"
        self.assertIn("não verificável (gh sem rede ou sem acesso)", self.passa())

    def test_gh_e_chamado_com_o_nome_exato_da_branch(self):
        self.commit("texto", **{"docs/a.md": "texto\n"})
        self.pr("")
        self.env["GH_FALSO_BRANCH"] = BRANCH + "-outra"  # o falso só responde ao nome exato: outro nome vira aviso, não reprova
        self.assertIn("não verificável", self.passa())


class Ponta(Base):
    """Só a ref de branch cuja ponta é o HEAD é conferida (QA A2 e A3): o teto e o corpo são os da branch do HEAD."""

    def item_defeituoso(self, nome_no_gh):
        self.commit("item grande", indice=0, **{"bin/grande.py": codigo(160), "tests/test_grande.py": TESTE})
        self.pr(SECOES)  # sem `teto: excedido`: conferido, barraria
        self.env["GH_FALSO_BRANCH"] = nome_no_gh

    def test_branch_cuja_ponta_nao_e_o_head_nao_e_conferida(self):
        anterior = self.git("rev-parse", "HEAD")
        self.item_defeituoso("outra")
        codigo_, erro = self.roda(self.remendado, ref="refs/heads/outra", sha=anterior)
        self.assertEqual(codigo_, 0, erro)
        self.assertNotIn("PR #7", erro)

    def test_ref_fora_de_refs_heads_nao_e_conferida(self):
        self.item_defeituoso("refs/tags/v1")
        codigo_, erro = self.roda(self.remendado, ref="refs/tags/v1")
        self.assertEqual(codigo_, 0, erro)
        self.assertNotIn("PR #7", erro)


class SoParecer(Base):
    """O envio só de parecer sobre o PR defeituoso só avisa (review A1, S1 e S2): o revisor envia o parecer que reprova."""

    AVISO = "envio só de parecer"

    def envia_parecer(self, *arquivos):
        anterior = self.git("rev-parse", "HEAD")
        self.commit("parecer", **{nome: "parecer\n" for nome in arquivos})
        return self.roda(self.remendado, remoto=anterior)

    def test_teto_estourado_so_avisa(self):  # S1
        self.commit("item grande", indice=0, **{"bin/grande.py": codigo(160), "tests/test_grande.py": TESTE})
        self.pr(SECOES)
        for pasta in ("reviews", "qa", "security", "devops"):
            with self.subTest(pasta):
                codigo_, erro = self.envia_parecer(f"docs/{pasta}/x.md")
                self.assertEqual(codigo_, 0, erro)
                self.assertIn("sem a linha `teto: excedido", erro)
                self.assertIn(self.AVISO, erro)

    def test_texto_do_pr_reprovado_so_avisa(self):  # S2
        self.commit("texto", **{"docs/a.md": "texto\n"})
        self.pr("## Projeto de origem\nFábrica.\n")
        codigo_, erro = self.envia_parecer("docs/reviews/x.md")
        self.assertEqual(codigo_, 0, erro)
        self.assertIn("reprovado pelo pr-texto", erro)
        self.assertIn(self.AVISO, erro)

    def test_indice_fora_de_dia_so_avisa(self):
        self.commit("ferramenta nova", indice=1, **{"bin/nova.py": codigo(3), "tests/test_nova.py": TESTE})
        codigo_, erro = self.envia_parecer("docs/qa/x.md")
        self.assertEqual(codigo_, 0, erro)
        self.assertIn("docs/indice-forge.md fora de dia", erro)
        self.assertIn(self.AVISO, erro)

    def test_delta_com_arquivo_fora_dos_pareceres_barra(self):
        self.commit("item grande", indice=0, **{"bin/grande.py": codigo(160), "tests/test_grande.py": TESTE})
        self.pr(SECOES)
        codigo_, erro = self.envia_parecer("docs/reviews/x.md", "docs/a.md")
        self.assertEqual(codigo_, 1, erro)
        self.assertNotIn(self.AVISO, erro)

    def test_ref_nova_ou_sha_remoto_desconhecido_barra(self):
        self.commit("item grande", indice=0, **{"bin/grande.py": codigo(160), "tests/test_grande.py": TESTE})
        self.pr(SECOES)
        self.commit("parecer", **{"docs/reviews/x.md": "parecer\n"})
        for remoto in (ZERO, "b" * 40):
            with self.subTest(remoto=remoto[:1]):
                codigo_, erro = self.roda(self.remendado, remoto=remoto)
                self.assertEqual(codigo_, 1, erro)
                self.assertNotIn(self.AVISO, erro)


class Neutralidade(Base):
    def test_stack_no_nucleo_segue_barrando_no_remendado(self):  # PARECER-NEUTRALIDADE-CEDO, que o patch não muda
        self.commit("stack", **{"agents/a.md": f"use {TERMO}\n"})
        for hook in [self.remendado, *self.originais]:
            codigo_, erro = self.roda(hook)
            self.assertEqual(codigo_, 1, erro)
            self.assertIn("stack no núcleo", erro)


if __name__ == "__main__":
    unittest.main()
