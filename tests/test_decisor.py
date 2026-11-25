"""Orkastery 3 (0.44.2): decisão óbvia por regra fixa (`bin/forge_decisor.py`, pelo `forge-check decisoes registrar|reverter|conferir`),
placar no `forge-check metricas` e a linha `decidido:` conferida no .githooks/commit-msg."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_git_herdado, sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
FORGE_CHECK = str(RAIZ / "bin" / "forge-check")
FATOS_OK = {"irreversivel": "nao", "dinheiro": "nao", "escopo": "nao", "alternativas-piores": "sim", "reversivel": "sim", "erro-barato": "sim",
            "so-aperta": "sim", "seguranca": "docs/security/confirma.md"}  # D5: só aperta, com a confirmação escrita da segurança
TEXTO = {"pedido": "p1", "porta": "nome do arquivo de teste", "criterio": "R-PROVA", "fato": "a convenção test_<modulo> já vale",
         "porque": "segue a convenção", "como-mudar": "renomear o arquivo", "custo-reverter": "um commit"}
FRONTMATTER_OK = {"tipo": "revisao-seguranca", "contrato": "1", "pedido": "p1", "branch": "melhoria/x", "commit": "0" * 40,
                  "parecer": "aprovado", "revisor": "forge:security-engineer", "data": "2026-11-24"}
CONFIRMA = "docs/security/confirma.md"


def parecer_da_seguranca(corpo, **troca):
    """O parecer da segurança com frontmatter (`troca` muda ou, com None, tira um campo) e o `corpo` depois dele."""
    campos = {k: v for k, v in {**FRONTMATTER_OK, **troca}.items() if v is not None}
    return "---\n" + "".join(f"{k}: {v}\n" for k, v in campos.items()) + "---\n# Review de segurança\n\n" + corpo


def git(raiz, *args):
    """git na raiz temporária, sem o git de quem roda a suíte e sem config global (AR-4)."""
    env = sem_git_herdado(HOME=str(raiz), GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    return subprocess.run(["git", "-C", str(raiz), "-c", "user.name=t", "-c", "user.email=t@t", *args], capture_output=True,
                          text=True, env=env, timeout=30, check=True)


def commitar(raiz, arquivos):
    """Grava {caminho: texto} na raiz (repositório novo na primeira vez) e commita tudo: o parecer fica no HEAD."""
    if not (Path(raiz) / ".git").exists():
        git(raiz, "init", "-q")
    for nome, texto in arquivos.items():
        (Path(raiz) / nome).parent.mkdir(parents=True, exist_ok=True)
        (Path(raiz) / nome).write_text(texto, encoding="utf-8")
    git(raiz, "add", "-A")
    git(raiz, "commit", "-q", "--allow-empty", "-m", "parecer")


class ComRaiz(unittest.TestCase):
    """Raiz temporária em git com a confirmação da segurança válida no HEAD; o forge-check roda com -I e sem o git herdado."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-decisor-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        commitar(self.tmp, {CONFIRMA: parecer_da_seguranca("Só aperta: nome do arquivo de teste\n")})

    def rodar(self, *args):
        r = subprocess.run([sys.executable, "-I", FORGE_CHECK, "--raiz", str(self.tmp), *args], capture_output=True, text=True,
                           env=sem_git_herdado(HOME=str(self.tmp / "home")))
        return r.returncode, r.stdout

    def registrar(self, **troca):
        campos = {**TEXTO, **FATOS_OK, **troca}
        return self.rodar("decisoes", "registrar", *[x for k, v in campos.items() for x in (f"--{k}", v)])

    def registro(self):
        arq = self.tmp / "docs" / "kanban" / "decisoes-obvias.jsonl"
        return [json.loads(l) for l in arq.read_text(encoding="utf-8").splitlines()]


class Decisor(ComRaiz):
    def test_as_quatro_condicoes_de_pe_decide_e_imprime_a_linha_do_commit(self):
        rc, out = self.registrar()
        self.assertEqual(rc, 0, out)
        self.assertIn("decidido: nome do arquivo de teste — R-PROVA — a convenção test_<modulo> já vale", out)
        r = self.registro()[0]
        self.assertEqual((r["resultado"], r["o_que"], r["como_mudar"], r["custo_reverter"]),
                         ("decidida", "nome do arquivo de teste", "renomear o arquivo", "um commit"))

    def test_porta_fechada_vira_pergunta(self):
        for porta in ("irreversivel", "dinheiro", "escopo"):
            rc, out = self.registrar(**{porta: "sim"})
            self.assertEqual(rc, 1, out)
            self.assertIn(f"porta fechada: {porta}", out)
        self.assertEqual({r["resultado"] for r in self.registro()}, {"pergunta"})

    def test_condicao_que_falta_vira_pergunta(self):
        for k in ("alternativas-piores", "reversivel", "erro-barato"):
            rc, out = self.registrar(**{k: "nao"})
            self.assertEqual(rc, 1, (k, out))
        rc, out = self.registrar(criterio="porque sim")
        self.assertEqual(rc, 1, out)
        self.assertIn("critério escrito", out)

    def test_fato_ausente_nao_grava(self):
        rc, _ = self.registrar(reversivel="talvez")
        self.assertEqual(rc, 2)
        self.assertEqual(self.registrar(porque="")[0], 2, "sem o porquê não grava")
        self.assertFalse((self.tmp / "docs" / "kanban" / "decisoes-obvias.jsonl").exists())

    def test_o_decisor_nao_recebe_objetivo_nem_conversa(self):
        sys.path.insert(0, str(RAIZ / "bin"))
        try:
            import forge_decisor  # noqa: PLC0415
        finally:
            sys.path.pop(0)
        fatos = {"irreversivel": False, "dinheiro": False, "escopo": False, "criterio": "R-PROVA", "alternativas_piores": True,
                 "reversivel": True, "erro_barato": True, "so_aperta": True, "seguranca": True}
        self.assertEqual(forge_decisor.decidir(**fatos), ("decidida", None))
        for extra in ("objetivo", "conversa"):
            with self.assertRaises(TypeError):
                forge_decisor.decidir(**fatos, **{extra: "x"})
        rc, _ = self.rodar("decisoes", "registrar", "--objetivo", "x")
        self.assertEqual(rc, 2, "o CLI não tem --objetivo")

    def test_reverter_pede_id_e_porque(self):
        self.registrar()
        self.assertEqual(self.rodar("decisoes", "reverter", "--id", "D0001")[0], 2)
        self.assertEqual(self.rodar("decisoes", "reverter", "--porque", "x")[0], 2)

    def test_reverter_e_placar_no_metricas(self):
        self.registrar()
        self.registrar(dinheiro="sim")
        self.assertEqual(self.rodar("decisoes", "reverter", "--id", "D0001", "--porque", "quebrou o nome")[0], 0)
        self.assertEqual(self.rodar("decisoes", "reverter", "--id", "D0002", "--porque", "x")[0], 1, "pergunta não se reverte")
        rc, out = self.rodar("metricas", "--develop", "x", "--main", "y")
        self.assertIn("metricas: placar decididas=1 perguntas=1 revertidas=1", out)

    def test_conferir_recusa_linha_decidido_fora_da_forma(self):
        msg = self.tmp / "msg"
        for texto, rc in (("feat: x\n\ndecidido: nome — R-PROVA — o fato\n", 0), ("feat: x\n\ndecidido: escolhi o nome\n", 1),
                          ("feat: x\n\ndecidido: nome — porque quis — fato\n", 1), ("feat: sem linha\n", 0)):
            msg.write_text(texto, encoding="utf-8")
            self.assertEqual(self.rodar("decisoes", "conferir", "--mensagem", str(msg))[0], rc, texto)

    def test_commit_msg_do_githooks_recusa_o_commit(self):
        repo = self.tmp / "r"
        shutil.copytree(RAIZ / ".githooks", repo / ".githooks")
        (repo / "bin").mkdir()
        for nome in ("forge-check", "forge_decisor.py"):
            shutil.copy(RAIZ / "bin" / nome, repo / "bin" / nome)
        env = sem_manutencao(dict(os.environ, HOME=str(self.tmp / "home"), GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1"))
        g = lambda *a: subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", "-c",  # noqa: E731
                                       "core.hooksPath=.githooks", *a], capture_output=True, text=True, env=env)
        g("init", "-q")
        g("add", ".")
        self.assertNotEqual(g("commit", "-q", "-m", "x\n\ndecidido: sem forma").returncode, 0)
        self.assertEqual(g("commit", "-q", "-m", "x\n\ndecidido: nome — R-PROVA — fato").returncode, 0)


class ConfirmacaoDaSeguranca(ComRaiz):
    """A1 a A3 da segurança e A1 do review no #863: as sondas S1 a S9 (segurança) e S1 e S2 (review) viram casos. A confirmação
    só vale lida pelo git, com o frontmatter da segurança aprovado do mesmo pedido e a linha `Só aperta: <porta>`."""
    PORTA = TEXTO["porta"]

    def pergunta(self, rotulo, **troca):
        rc, out = self.registrar(**troca)
        self.assertEqual(rc, 1, (rotulo, out))
        self.assertIn("condição não atendida: seguranca", out, rotulo)

    def commitado_vira_pergunta(self, casos):
        for rotulo, texto in casos:
            with self.subTest(rotulo):
                commitar(self.tmp, {CONFIRMA: texto})
                self.pergunta(rotulo)

    def test_confirmacao_valida_decide_com_a_porta_de_espacos_normalizados(self):
        rc, out = self.registrar(porta="nome  do arquivo   de teste")
        self.assertEqual(rc, 0, out)
        self.assertIn("decidido: nome do arquivo de teste — R-PROVA", out)

    def test_arquivo_fora_do_git_vira_pergunta(self):  # S1 da segurança
        (self.tmp / "docs" / "security" / "f.md").write_text(parecer_da_seguranca(f"Só aperta: {self.PORTA}\n"), encoding="utf-8")
        self.pergunta("S1", seguranca="docs/security/f.md")

    def test_arquivo_mudado_na_arvore_ou_no_indice_vira_pergunta(self):
        arq = self.tmp / CONFIRMA
        arq.write_text(arq.read_text(encoding="utf-8") + "linha nova\n", encoding="utf-8")
        self.pergunta("árvore")
        git(self.tmp, "add", CONFIRMA)
        self.pergunta("índice")

    def test_frontmatter_que_nao_e_da_seguranca_aprovada_do_pedido_vira_pergunta(self):  # S2 e S8 da segurança
        corpo = f"Só aperta: {self.PORTA}\n"
        self.commitado_vira_pergunta([
            ("S1 sem frontmatter", f"qualquer coisa\n{corpo}"),
            ("S2 reprovado", parecer_da_seguranca("Só aperta? Não: afrouxa.\n" + corpo, parecer="reprovado")),
            ("S8 tipo review", parecer_da_seguranca(corpo, tipo="review")),
            ("S8 outro pedido", parecer_da_seguranca(corpo, pedido="outro")),
            ("sem pedido", parecer_da_seguranca(corpo, pedido=None)),
            ("outro revisor", parecer_da_seguranca(corpo, revisor="forge:tech-lead")),
            ("linha antes do frontmatter", "intro\n" + parecer_da_seguranca(corpo)),
            ("sem a abertura", parecer_da_seguranca(corpo).replace("---\n", "nota: sem abertura\n", 1)),
            ("chave repetida", parecer_da_seguranca(corpo).replace("parecer: aprovado\n", "parecer: reprovado\nparecer: aprovado\n")),
            ("sem fechamento", parecer_da_seguranca(corpo).replace("---\n# Review", "# Review")),
        ])

    def test_frase_solta_pergunta_ou_negacao_vira_pergunta(self):  # S3 a S6 da segurança, S2 do review
        self.commitado_vira_pergunta([(texto, parecer_da_seguranca(texto)) for texto in (
            "## Só aperta?\nNão. Aceita mais.\n", "A mudança não é só aperta: afrouxa.\n", "não\nsó aperta\n", "não  só aperta\n",
            "Não, só aperta?\n", f"não Só aperta: {self.PORTA}\n", f"  Só aperta: {self.PORTA}\n", f"Só aperta? {self.PORTA}\n",
            f"só aperta: {self.PORTA}\n", "Só aperta: outra porta\n", f"Só aperta: {self.PORTA} e mais\n")])

    def test_parecer_de_outro_item_ja_na_develop_vira_pergunta(self):  # S9 da segurança, S1 do review
        for nome in ("release-0.47.15.md", "heredoc-donos.md"):
            original = RAIZ / "docs" / "security" / nome
            self.assertTrue(original.is_file(), original)
            with self.subTest(nome):
                commitar(self.tmp, {CONFIRMA: original.read_text(encoding="utf-8")})
                self.pergunta(nome)

    def test_link_simbolico_no_git_vira_pergunta(self):
        os.symlink("confirma.md", self.tmp / "docs" / "security" / "link.md")
        commitar(self.tmp, {})
        self.pergunta("link", seguranca="docs/security/link.md")

    def test_parecer_executavel_no_git_vira_pergunta(self):
        (self.tmp / CONFIRMA).chmod(0o755)
        git(self.tmp, "-c", "core.fileMode=true", "add", CONFIRMA)
        git(self.tmp, "commit", "-q", "-m", "modo")
        self.assertIn("100755", git(self.tmp, "ls-tree", "HEAD", "--", CONFIRMA).stdout)
        self.pergunta("100755")

    def test_parecer_acima_do_teto_vira_pergunta(self):
        commitar(self.tmp, {CONFIRMA: parecer_da_seguranca(f"Só aperta: {self.PORTA}\n" + "x" * (1 << 20))})
        self.pergunta("teto")

    def test_raiz_que_nao_e_a_do_repositorio_vira_pergunta(self):
        de_fora = Path(tempfile.mkdtemp(prefix="forge-decisor-fora-")).resolve()
        self.addCleanup(shutil.rmtree, de_fora, ignore_errors=True)
        commitar(de_fora, {"sub/" + CONFIRMA: parecer_da_seguranca(f"Só aperta: {self.PORTA}\n")})
        self.tmp = de_fora / "sub"
        self.pergunta("subpasta de outro repositório")

    def test_git_dir_de_outro_repositorio_no_ambiente_vira_pergunta(self):  # A3 do QA no #863
        """O parecer está só na árvore da raiz; outro repositório tem o mesmo texto no HEAD. Um `GIT_DIR` herdado apontando
        para ele não pode fazer o git ler o HEAD de lá e confirmar um parecer que não está no git da raiz."""
        texto = parecer_da_seguranca(f"Só aperta: {self.PORTA}\n")
        (self.tmp / "docs" / "security" / "f.md").write_text(texto, encoding="utf-8")
        outro = Path(tempfile.mkdtemp(prefix="forge-decisor-outro-")).resolve()
        self.addCleanup(shutil.rmtree, outro, ignore_errors=True)
        commitar(outro, {"docs/security/f.md": texto})
        campos = {**TEXTO, **FATOS_OK, "seguranca": "docs/security/f.md"}
        r = subprocess.run([sys.executable, "-I", FORGE_CHECK, "--raiz", str(self.tmp), "decisoes", "registrar",
                            *[x for k, v in campos.items() for x in (f"--{k}", v)]], capture_output=True, text=True,
                           env=sem_git_herdado(HOME=str(self.tmp / "home"), GIT_DIR=str(outro / ".git")))
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("condição não atendida: seguranca", r.stdout)

    def test_git_ausente_vira_pergunta(self):
        sys.path.insert(0, str(RAIZ / "bin"))
        try:
            import forge_decisor  # noqa: PLC0415
        finally:
            sys.path.pop(0)
        vazio = self.tmp / "sem-git"
        vazio.mkdir()
        with unittest.mock.patch.dict(os.environ, {"PATH": str(vazio)}):
            self.assertFalse(forge_decisor.confirmacao_escrita(self.tmp, CONFIRMA, "p1", self.PORTA))
        self.assertTrue(forge_decisor.confirmacao_escrita(self.tmp, CONFIRMA, "p1", self.PORTA))


if __name__ == "__main__":
    unittest.main()
