"""G2.1 (pedido v0481, ADR 0019; modelo de ameaças docs/security/ameacas/g2-parecer-status.md): `forge-check parecer publicar`
confere o parecer local e o publica como comentário do PR e status do commit, com o agregado `pareceres`. Sem rede: o `gh` é um
falso no PATH que guarda o estado num JSON e registra cada chamada; nenhum status de verdade é gravado."""
import contextlib
import functools
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
BRANCH, PEDIDO = "melhoria/v9-publicar", "v9"

GH_FALSO = r'''
import json, os, sys
d = os.environ["GH_FALSO"]
estado = json.load(open(os.path.join(d, "estado.json")))
a = sys.argv[1:]
open(os.path.join(d, "chamadas.log"), "a").write(json.dumps(a) + "\n")
def sai(obj):
    json.dump(estado, open(os.path.join(d, "estado.json"), "w")); print(json.dumps(obj)); sys.exit(0)
if estado.get("falha") or estado.get("falha_em") in a:
    sys.exit(1)
if a[:2] == ["pr", "list"]:
    sai(estado["prs"])
if a == ["api", "user"]:
    sai({"login": estado["login"]})
corpo = json.loads(sys.stdin.read() or "{}") if "--input" in a else {}
alvo = a[-3] if "--input" in a else a[-1]
url = estado["prs"][0]["url"] if estado["prs"] else ""
if alvo.endswith("/comments") and "POST" in a:
    estado["comentario"] = corpo["body"] + estado.get("sujar", "")
    sai({"id": 501, "html_url": url + "#issuecomment-501"})
if alvo.endswith("/issues/comments/501"):
    sai({"id": 501, "body": estado["comentario"], "html_url": estado.get("url_lida", url + "#issuecomment-501")})
if "/statuses/" in alvo and "POST" in a:
    estado["statuses"].insert(0, corpo | {"creator": {"login": estado["login"]}}); sai(corpo)
if alvo.endswith("/statuses") and "--slurp" in a:
    sai([estado["statuses"]])
sys.exit(1)
'''


@functools.lru_cache(maxsize=None)
def fp():
    """bin/forge_pareceres.py carregado sob demanda: sem ele (a base), cada teste falha sozinho."""
    return SourceFileLoader("forge_pareceres_teste", str(RAIZ / "bin" / "forge_pareceres.py")).load_module()


@functools.lru_cache(maxsize=None)
def fc():
    return SourceFileLoader("forge_check_pareceres", str(RAIZ / "bin" / "forge-check")).load_module()


def parecer(commit, veredito="aprovado", tipo="review", achados="", pedido=PEDIDO):
    return (f"---\ntipo: {tipo}\ncontrato: 1\npedido: {pedido}\nbranch: {BRANCH}\ncommit: {commit}\nparecer: {veredito}\n"
            f"revisor: forge:tech-lead\ndata: 2026-11-24\n---\n# Review: {pedido}\n\n{achados}## Parecer\nSíntese.\n")


class GhFalso(unittest.TestCase):
    """Um repositório git com um commit e o `gh` falso no PATH; o ambiente herdado não chega ao `gh`."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(subprocess.run, ["rm", "-rf", str(self.tmp)])
        self.repo, self.bin = self.tmp / "repo", self.tmp / "bin"
        self.repo.mkdir(), self.bin.mkdir()
        env = sem_manutencao({"PATH": "/usr/bin:/bin", "HOME": str(self.tmp), "GIT_CONFIG_NOSYSTEM": "1"})
        for args in (["init", "-q", "-b", "develop"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q",
                                                       "--allow-empty", "-m", "base"]):
            subprocess.run(["git", *args], cwd=self.repo, env=env, check=True)
        self.sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.repo, env=env, capture_output=True, text=True).stdout.strip()
        gh = self.bin / "gh"
        gh.write_text(f"#!{sys.executable} -I\n{GH_FALSO}", encoding="utf-8")
        gh.chmod(0o755)
        self.estado({"prs": [{"number": 7, "headRefName": BRANCH, "headRefOid": self.sha,
                              "url": "https://github.com/dono/repo/pull/7"}], "login": "conta", "statuses": []})
        ambiente = {"PATH": f"{self.bin}:/usr/bin:/bin", "GH_FALSO": str(self.tmp), "HOME": str(self.tmp)}
        p = mock.patch.dict(os.environ, ambiente, clear=True)
        p.start()
        self.addCleanup(p.stop)

    def estado(self, novo=None, **mudar):
        arq = self.tmp / "estado.json"
        atual = novo if novo is not None else json.loads(arq.read_text(encoding="utf-8")) | mudar
        arq.write_text(json.dumps(atual), encoding="utf-8")
        return atual

    def chamadas(self):
        log = self.tmp / "chamadas.log"
        return [json.loads(x) for x in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []

    def gravou_status(self):
        return [c for c in self.chamadas() if any("/statuses/" in x for x in c) and "POST" in c]


class Publicar(GhFalso):
    def publicar(self, texto=None, veredito="aprovado", exigidos=("review",), branch=BRANCH):
        return fp().publicar(str(self.repo), "review", veredito, texto or parecer(self.sha), self.sha, branch, 0, 0, list(exigidos))

    def test_publica_comentario_status_e_agregado(self):
        url, agregado = self.publicar()
        self.assertEqual(url, "https://github.com/dono/repo/pull/7#issuecomment-501")
        self.assertEqual(agregado, ("success", "todos os exigidos"))
        review, agreg = self.estado()["statuses"][1], self.estado()["statuses"][0]
        texto_sha = hashlib.sha256(parecer(self.sha).strip().encode()).hexdigest()
        self.assertEqual((review["context"], review["state"], review["target_url"]), ("parecer-review", "success", url))
        self.assertEqual(review["description"], f"aprovado · sha256 {texto_sha} · 0 bloqueantes · 0 recomendados")
        self.assertEqual((agreg["context"], agreg["state"]), ("pareceres", "success"))
        self.assertNotIn("target_url", agreg)  # o agregado não aponta para um comentário
        pendente = self.estado()["statuses"][2]  # QA A1 do #878: o agregado sai de `success` antes do status do papel
        self.assertEqual((pendente["context"], pendente["state"]), ("pareceres", "pending"))

    def test_falha_entre_o_papel_e_o_agregado_nao_deixa_success(self):
        """QA A1 do #878 (sonda S2): o `pareceres` velho em `success`, a API cai depois do status do papel `reprovado`."""
        self.estado(statuses=[{"context": "pareceres", "state": "success", "creator": {"login": "conta"}}], falha_em="user")
        with self.assertRaisesRegex(fp().Recusa, "já gravado: o comentário no PR #7, pareceres pending, parecer-review failure"):
            self.publicar(veredito="reprovado")
        agregados = [s for s in self.estado()["statuses"] if s["context"] == "pareceres"]
        self.assertEqual(agregados[0]["state"], "pending", "o mais novo do agregado nunca fica success velho")

    def test_falha_antes_do_status_diz_o_que_ficou(self):
        self.estado(falha_em=f"repos/{{owner}}/{{repo}}/issues/comments/501")
        with self.assertRaisesRegex(fp().Recusa, "já gravado: o comentário no PR #7$"):
            self.publicar()
        self.assertEqual(self.gravou_status(), [])

    def test_lista_de_prs_ilegivel(self):
        self.estado(prs=7)
        with self.assertRaisesRegex(fp().Recusa, "0 PR aberto"):
            self.publicar()

    def test_reprovado_grava_failure_e_agregado_pending(self):
        _, agregado = self.publicar(veredito="reprovado")
        self.assertEqual(agregado, ("pending", "faltam: parecer-review"))
        self.assertEqual(self.estado()["statuses"][1]["state"], "failure")

    def test_c20_corpo_devolvido_difere_do_local(self):
        self.estado(sujar="x")
        with self.assertRaisesRegex(fp().Recusa, "M5.3"):
            self.publicar()
        self.assertEqual(self.gravou_status(), [])

    def test_crlf_devolvido_vale(self):
        self.publicar(texto=parecer(self.sha).replace("\n", "\r\n"))
        self.assertEqual(len(self.gravou_status()), 3)

    def test_comentario_de_outro_pr(self):
        self.estado(url_lida="https://github.com/dono/repo/pull/8#issuecomment-501")
        with self.assertRaisesRegex(fp().Recusa, "não é do PR #7"):
            self.publicar()
        self.assertEqual(self.gravou_status(), [])

    def test_commit_que_nao_e_head_do_pr(self):
        self.estado(prs=[{"number": 7, "headRefName": BRANCH, "headRefOid": "f" * 40, "url": "u"}])
        with self.assertRaisesRegex(fp().Recusa, "não é o head"):
            self.publicar()
        self.assertFalse([c for c in self.chamadas() if "POST" in c])

    def test_branch_de_nome_parecido_nao_casa(self):
        for nome in (BRANCH + "-2", "x" + BRANCH, BRANCH.upper()):
            with self.subTest(nome=nome):
                self.estado(prs=[{"number": 7, "headRefName": nome, "headRefOid": self.sha, "url": "u"}])
                with self.assertRaisesRegex(fp().Recusa, "0 PR aberto"):
                    self.publicar()

    def test_dois_prs_da_branch(self):
        pr = {"number": 7, "headRefName": BRANCH, "headRefOid": self.sha, "url": "u"}
        self.estado(prs=[pr, pr | {"number": 8}])
        with self.assertRaisesRegex(fp().Recusa, "2 PR"):
            self.publicar()

    def test_c3_tipo_ou_veredito_fora_da_lista(self):
        for tipo, veredito in (("Review", "aprovado"), ("plano-tecnico", "aprovado"), ("review", "Aprovado")):
            with self.subTest(tipo=tipo, veredito=veredito), self.assertRaises(fp().Recusa):
                fp().publicar(str(self.repo), tipo, veredito, parecer(self.sha), self.sha, BRANCH, 0, 0, ["review"])
        with self.assertRaises(fp().Recusa):
            fp().publicar(str(self.repo), "review", "aprovado", parecer(self.sha), self.sha[:12], BRANCH, 0, 0, ["review"])
        self.assertEqual(self.chamadas(), [])

    def test_c17_gh_com_erro_ou_ausente(self):
        self.estado(falha=True)
        with self.assertRaisesRegex(fp().Recusa, "saiu com 1"):
            self.publicar()
        os.environ["PATH"] = "/nada"
        with self.assertRaisesRegex(fp().Recusa, "sem resposta legível"):
            self.publicar()


class Agregado(GhFalso):
    def status(self, contexto, estado="success", login="conta", descricao=None):
        return {"context": contexto, "state": estado, "creator": {"login": login},
                "description": descricao or f"aprovado · sha256 {'a' * 64} · 0 bloqueantes · 0 recomendados"}

    def agregado(self, *statuses, exigidos=("review", "qa")):
        self.estado(statuses=list(statuses))
        return fp().agregado(str(self.repo), self.sha, list(exigidos))

    def test_todos_os_exigidos_success(self):
        self.assertEqual(self.agregado(self.status("parecer-review"), self.status("parecer-qa"))[0], "success")

    def test_agregado_pending_com_exigido_invalido(self):
        casos = {"ausente": [self.status("parecer-review")],
                 "c1 do bot": [self.status("parecer-review"), self.status("parecer-qa", login="github-actions[bot]")],
                 "c2 bot mais novo esconde failure": [self.status("parecer-review"), self.status("parecer-qa", login="outra"),
                                                      self.status("parecer-qa", "failure")],
                 "failure mais novo": [self.status("parecer-review"), self.status("parecer-qa", "failure"), self.status("parecer-qa")],
                 "c3 contexto parecido": [self.status("parecer-review"), self.status("Parecer-qa"), self.status("parecer-qa ")],
                 "descricao fora do publicar": [self.status("parecer-review"), self.status("parecer-qa", descricao="ok")],
                 "sha256 curto": [self.status("parecer-review"), self.status("parecer-qa", descricao="aprovado · sha256 abc · ")]}
        for nome, statuses in casos.items():
            with self.subTest(nome):
                self.assertEqual(self.agregado(*statuses), ("pending", "faltam: parecer-qa"))

    def test_item_que_nao_e_objeto_fica_de_fora(self):
        self.assertEqual(self.agregado(5, "x", self.status("parecer-review"), exigidos=("review",)), ("success", "todos os exigidos"))

    def test_statuses_ilegiveis_recusam(self):
        self.estado(statuses={"x": 1})
        with self.assertRaises(fp().Recusa):
            fp().agregado(str(self.repo), self.sha, ["review"])


class Descricao(unittest.TestCase):
    def test_c9_sha256_inteiro_e_teto_de_140(self):
        d = fp().descricao("riscos-aceitos", "texto", 99, 99)
        self.assertEqual(len(d.split("sha256 ")[1].split(" ")[0]), 64)
        self.assertLessEqual(len(d), 140)
        with self.assertRaisesRegex(fp().Recusa, "acima de 140"):
            fp().descricao("reprovado", "texto", 10 ** 20, 10 ** 20)


class Comando(GhFalso):
    """`forge-check parecer publicar`: a conferência do arquivo local antes de qualquer chamada ao `gh`."""

    def grava(self, texto, papel="tech-lead", tipo="review", pedido=PEDIDO, autoria=True):
        arq = self.repo / ".forge" / "pareceres" / pedido / f"{tipo}.md"
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(texto, encoding="utf-8")
        run = self.repo / ".forge" / "run"
        run.mkdir(parents=True, exist_ok=True)
        if autoria:
            registro = {"caminho": "x", "sha256": hashlib.sha256(texto.strip().encode()).hexdigest(), "papel": papel}
            with open(run / "autoria.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(registro) + "\n")
        return arq

    def roda(self, arq):
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida), contextlib.redirect_stderr(io.StringIO()):
            rc = fc().cmd_parecer_publicar(self.repo, str(arq))
        return rc, saida.getvalue()

    def recusa(self, arq, trecho):
        rc, saida = self.roda(arq)
        self.assertEqual(rc, 1, saida)
        self.assertIn(trecho, saida)
        self.assertEqual(self.chamadas(), [], "recusado antes de chamar o gh")

    def test_publica_pelo_comando(self):
        rc, saida = self.roda(self.grava(parecer(self.sha)))
        self.assertEqual(rc, 0, saida)
        self.assertIn(f"parecer publicado: parecer-review aprovado {self.sha[:7]} https://github.com/dono/repo/pull/7#issuecomment-501", saida)
        self.assertIn("agregado pareceres", saida)

    def test_contagem_de_achados_na_descricao(self):
        achados = "## Achados\n- A1 (recomendado) bin/x:1 · um\n- A2 (recomendado) bin/x:2 · dois\n\n"
        rc, saida = self.roda(self.grava(parecer(self.sha, achados=achados)))
        self.assertEqual(rc, 0, saida)
        self.assertTrue(self.estado()["statuses"][1]["description"].endswith(" · 0 bloqueantes · 2 recomendados"))

    def test_cli_recusa_sem_arquivo(self):
        r = subprocess.run([sys.executable, "-I", str(RAIZ / "bin" / "forge-check"), "parecer", "publicar", "docs/x.md"],
                           cwd=self.repo, env=dict(os.environ), capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("parecer publicar: recusado; nada gravado", r.stdout)
        self.assertEqual(self.chamadas(), [])

    def test_c11_sem_autoria_jsonl_recusa(self):
        self.recusa(self.grava(parecer(self.sha), autoria=False), "autoria: sem registro")

    def test_c11_papel_autor_publica(self):
        self.recusa(self.grava(parecer(self.sha), papel="dev"), "papel `tech-lead`")

    def test_texto_mudado_depois_da_autoria(self):
        arq = self.grava(parecer(self.sha))
        arq.write_text(parecer(self.sha, achados="Outra síntese.\n\n"), encoding="utf-8")
        self.recusa(arq, "autoria: sem registro")

    def test_caminho_fora_de_forge_pareceres(self):
        arq = self.repo / "docs" / "reviews" / f"{PEDIDO}.md"
        arq.parent.mkdir(parents=True)
        arq.write_text(parecer(self.sha), encoding="utf-8")
        self.recusa(arq, "use .forge/pareceres/")

    def test_pedido_ou_tipo_diferente_do_caminho(self):
        self.recusa(self.grava(parecer(self.sha, pedido="v8")), "iguais ao caminho")
        self.recusa(self.grava(parecer(self.sha, tipo="qa"), tipo="review"), "iguais ao caminho")
        self.recusa(self.grava(parecer(self.sha, tipo="plano-tecnico"), tipo="plano-tecnico"), "iguais ao caminho")

    def test_arquivo_ausente(self):
        self.recusa(self.repo / ".forge" / "pareceres" / PEDIDO / "review.md", "use .forge/pareceres/")

    def test_sem_frontmatter(self):
        self.recusa(self.grava("# Review sem frontmatter\n"), "use .forge/pareceres/")

    def test_contrato_quebrado(self):
        self.recusa(self.grava(parecer(self.sha, achados="## Achados\n- solto sem formato\n\n")), "achados:")

    def test_reprovado_sem_bloqueante(self):
        achados = f"## Achados\n- A1 (recomendado) bin/x:1 · texto\n\n"
        self.recusa(self.grava(parecer(self.sha, veredito="reprovado", achados=achados)), "sem achado bloqueante")

    def test_commit_que_nao_existe(self):
        self.recusa(self.grava(parecer("e" * 40)), "não é commit desta cópia")

    def test_c15_riscos_aceitos_sem_aceite(self):
        texto = parecer(self.sha, veredito="riscos-aceitos", tipo="revisao-seguranca")
        self.recusa(self.grava(texto, papel="seguranca", tipo="revisao-seguranca"), "riscos-aceitos")

    def test_c15_aceite_de_outro_commit(self):
        """M14.1 (segurança A2 do #878): o aceite do dono no commit do parecer, com `commit:` de outro commit, não vale."""
        aceite = self.repo / "docs" / "security" / "aceites" / f"{PEDIDO}.md"
        aceite.parent.mkdir(parents=True)
        aceite.write_text(f"---\npedido: {PEDIDO}\naceite: sim\ncommit: {self.sha}\n---\n", encoding="utf-8")
        env = sem_manutencao({"PATH": "/usr/bin:/bin", "HOME": str(self.tmp), "GIT_CONFIG_NOSYSTEM": "1"})
        for args in (["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "aceite"]):
            subprocess.run(["git", *args], cwd=self.repo, env=env, check=True)
        novo = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.repo, env=env, capture_output=True, text=True).stdout.strip()
        texto = parecer(novo, veredito="riscos-aceitos", tipo="revisao-seguranca")
        self.recusa(self.grava(texto, papel="seguranca", tipo="revisao-seguranca"), "sem o aceite do dono")


class Politica(unittest.TestCase):
    def test_caminho_por_papel_em_forge_pareceres(self):
        sys.path.insert(0, str(RAIZ / "hooks"))
        self.addCleanup(sys.path.remove, str(RAIZ / "hooks"))
        hook = SourceFileLoader("conformidade_pareceres", str(RAIZ / "hooks" / "conformidade.py")).load_module()
        caminhos = json.loads((RAIZ / "hooks" / "conformidade.json").read_text(encoding="utf-8"))["caminhos"]
        for tipo, papel in fc().PAPEL_DO_PARECER.items():
            with self.subTest(tipo=tipo):
                regras = [e for e in caminhos if hook.casa(f".forge/pareceres/{PEDIDO}/{tipo}.md", e["caminho"])]
                self.assertEqual([e["quem"] for e in regras], [[papel]])
        self.assertFalse([e for e in caminhos if hook.casa(f".forge/pareceres/{PEDIDO}/outro.md", e["caminho"])])

    def test_nenhum_workflow_usa_secrets(self):
        """M1.3: um PAT da conta dos agentes num workflow faria o `creator` do status passar pela lista positiva."""
        workflows = sorted((RAIZ / ".github" / "workflows").glob("*.yml"))
        self.assertGreaterEqual(len(workflows), 3)
        for arq in workflows:
            texto = arq.read_text(encoding="utf-8").replace("secrets.GITHUB_TOKEN", "")
            self.assertNotIn("secrets", texto, arq.name)


if __name__ == "__main__":
    unittest.main()
