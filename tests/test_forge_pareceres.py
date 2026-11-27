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
from ambiente_git import remoto_sem_manutencao, sem_manutencao  # noqa: E402

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
if "/issues/comments/" in alvo and alvo.rsplit("/", 1)[1] in estado.get("comentarios", {}):
    sai(estado["comentarios"][alvo.rsplit("/", 1)[1]])
if alvo.endswith("/issues/comments/501"):
    sai({"id": 501, "body": estado["comentario"], "html_url": estado.get("url_lida", url + "#issuecomment-501"),
         "user": {"login": estado["login"]}})
if "/statuses/" in alvo and "POST" in a:
    estado["statuses"].insert(0, corpo | {"creator": {"login": estado["login"]}}); sai(corpo)
if a[:2] == ["pr", "view"]:
    sai(estado["pr_view"])
if alvo.endswith("/statuses") and "--slurp" in a and "por_commit" in estado:
    sai(estado["por_commit"].get(alvo.split("/")[-2], [[]]))
if alvo.endswith("/statuses") and "--slurp" in a:
    sai(estado["paginas"] if "paginas" in estado else [estado["statuses"]])
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
    """Um clone do Forge em `~/.forge-contrib/wt/` com um commit, a pasta de controle da máquina (M4.1) e o `gh` falso no PATH; o
    ambiente herdado não chega ao `gh`. A conta aceita é a dona do `origin` (`dono`, M1.4)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(subprocess.run, ["rm", "-rf", str(self.tmp)])
        self.repo, self.bin = self.tmp / ".forge-contrib" / "wt" / "repo", self.tmp / "bin"
        self.controle = self.tmp / ".forge-contrib" / ".forge" / "run"
        self.repo.mkdir(parents=True), self.bin.mkdir(), self.controle.mkdir(parents=True)
        self.env = sem_manutencao({"PATH": "/usr/bin:/bin", "HOME": str(self.tmp), "GIT_CONFIG_NOSYSTEM": "1"})
        for args in (["init", "-q", "-b", "develop"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q",
                                                       "--allow-empty", "-m", "base"],
                     ["remote", "add", "origin", "https://github.com/dono/repo.git"]):  # M18.1: o remoto do PR
            subprocess.run(["git", *args], cwd=self.repo, env=self.env, check=True)
        self.sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.repo, env=self.env, capture_output=True, text=True).stdout.strip()
        gh = self.bin / "gh"
        gh.write_text(f"#!{sys.executable} -I\n{GH_FALSO}", encoding="utf-8")
        gh.chmod(0o755)
        self.estado({"prs": [{"number": 7, "headRefName": BRANCH, "headRefOid": self.sha, "isCrossRepository": False,
                              "url": "https://github.com/dono/repo/pull/7"}], "login": "dono", "statuses": []})
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
        self.estado(statuses=[{"context": "pareceres", "state": "success", "creator": {"login": "dono"}}], falha_em="--slurp")
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

    def test_c19_conta_da_sessao_fora_da_lista_recusa(self):
        """M1.4: `GH_TOKEN` de outra conta no ambiente; o `publicar` recusa antes de gravar qualquer coisa."""
        for login in ("outra", None, ""):
            with self.subTest(login):
                self.estado(login=login)
                with self.assertRaisesRegex(fp().Recusa, "M1.4"):
                    self.publicar()
                self.assertFalse([c for c in self.chamadas() if "POST" in c], "gravou")

    def test_conta_da_sessao_em_outra_caixa_publica(self):
        self.estado(login="Dono")
        self.assertEqual(self.publicar()[1], ("success", "todos os exigidos"))

    def test_m4_1_registra_cada_publicacao_na_pasta_de_controle(self):
        self.publicar()
        linhas = (self.controle / "pareceres-publicados.jsonl").read_text(encoding="utf-8").splitlines()
        sha256 = hashlib.sha256(parecer(self.sha).strip().encode()).hexdigest()
        self.assertEqual([json.loads(x) for x in linhas],
                         [{"sha": self.sha, "contexto": "parecer-review", "sha256": sha256, "comentario": 501}])

    def test_m4_1_sem_pasta_de_controle_nada_se_grava(self):
        subprocess.run(["rm", "-rf", str(self.controle)], check=True)
        with self.assertRaisesRegex(fp().Recusa, "M4.1"):
            self.publicar()
        self.assertFalse([c for c in self.chamadas() if "POST" in c], "gravou")

    def test_m4_1_registro_por_link_nao_grava_status(self):
        alvo = self.tmp / "fora.jsonl"
        (self.controle / "pareceres-publicados.jsonl").symlink_to(alvo)
        with self.assertRaisesRegex(fp().Recusa, "M4.1"):
            self.publicar()
        self.assertFalse(alvo.exists(), "seguiu o link")
        self.assertEqual(self.gravou_status(), [])

    def test_c17_gh_com_erro_ou_ausente(self):
        self.estado(falha=True)
        with self.assertRaisesRegex(fp().Recusa, "saiu com 1"):
            self.publicar()
        os.environ["PATH"] = "/nada"
        with self.assertRaisesRegex(fp().Recusa, "sem resposta legível"):
            self.publicar()


class RemotoDoPr(GhFalso):
    """M18.1 (T18, C23): o PR em que se publica é do repositório do `origin` da cópia e a branch é dele; `GH_REPO` apontado para
    outro repositório, remoto de outro projeto ou PR de fork recusam antes de qualquer gravação."""

    publicar = Publicar.publicar

    def origin(self, url):
        subprocess.run(["git", "remote", "set-url", "origin", url], cwd=self.repo, env=self.env, check=True)

    def recusa(self, trecho):
        with self.assertRaises(Exception) as erro:  # outra exceção (o `m.groups()` de None) é falha, não erro do teste
            self.publicar()
        self.assertIsInstance(erro.exception, fp().Recusa, repr(erro.exception))
        self.assertRegex(str(erro.exception), trecho)
        self.assertFalse([c for c in self.chamadas() if "POST" in c], "nada gravado")

    def test_c23_remoto_diferente_do_pr(self):
        """Sessão de projeto com `GH_REPO` no Forge: o `gh` acha o PR do Forge, o `origin` da cópia é o do projeto."""
        self.origin("https://github.com/outro/projeto.git")
        self.recusa(r"PR #7 \(https://github.com/dono/repo/pull/7\) não é do repositório do `origin` da cópia \(M18.1\)")

    def test_c23_pr_de_outro_repositorio_com_o_mesmo_dono(self):
        self.estado(prs=[self.estado()["prs"][0] | {"url": "https://github.com/dono/repo-2/pull/7"}])
        self.recusa("não é do repositório do `origin`")

    def test_c23_pr_de_fork_com_a_mesma_branch(self):
        for cruzado in ({"isCrossRepository": True}, {"isCrossRepository": None}, {}):
            with self.subTest(cruzado=cruzado):
                pr = {k: v for k, v in self.estado()["prs"][0].items() if k != "isCrossRepository"}
                self.estado(prs=[pr | cruzado])
                self.recusa("vem de outro repositório")

    def test_c23_sem_origin_ou_origin_fora_das_formas(self):
        subprocess.run(["git", "remote", "remove", "origin"], cwd=self.repo, env=self.env, check=True)
        self.recusa("o `origin` da cópia não é um repositório lido")
        subprocess.run(["git", "remote", "add", "origin", "x"], cwd=self.repo, env=self.env, check=True)
        for url in ("/workspaces/repo", "file:///tmp/x@github.com:dono/repo", "https://github.com/dono/repo/extra"):
            with self.subTest(url=url):
                self.origin(url)
                self.recusa("o `origin` da cópia não é um repositório lido")

    def test_formas_do_remoto_que_valem(self):
        for url in ("https://github.com/dono/repo", "https://github.com/Dono/Repo.git/", "git@github.com:dono/repo.git",
                    "ssh://git@github.com/dono/repo.git", "https://x-access-token:abc@github.com/dono/repo.git"):
            with self.subTest(url=url):
                self.origin(url)
                self.assertEqual(fp().repositorio_do_remoto(str(self.repo)), ("github.com", "dono", "repo"))
        self.origin("https://github.com/dono/repo.git")
        self.estado(prs=[self.estado()["prs"][0] | {"url": "https://github.com/DONO/Repo/pull/7"}])
        self.assertEqual(self.publicar()[1], ("success", "todos os exigidos"))


class Agregado(GhFalso):
    def status(self, contexto, estado="success", login="dono", descricao=None):
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

    def test_c19_agregado_pela_conta_da_base(self):
        """M1.4: o agregado conta só a dona do `origin`, mesmo com a sessão em outra conta; caixa diferente vale."""
        self.estado(login="outra")
        self.assertEqual(self.agregado(self.status("parecer-review", login="outra"), exigidos=("review",))[0], "pending")
        self.assertEqual(self.agregado(self.status("parecer-review", login="DONO"), exigidos=("review",))[0], "success")
        self.assertNotIn(["api", "user"], self.chamadas())

    def test_item_que_nao_e_objeto_fica_de_fora(self):
        self.assertEqual(self.agregado(5, "x", self.status("parecer-review"), exigidos=("review",)), ("success", "todos os exigidos"))

    def test_statuses_ilegiveis_recusam(self):
        self.estado(statuses={"x": 1})
        with self.assertRaises(fp().Recusa):
            fp().agregado(str(self.repo), self.sha, ["review"])


class Ler(GhFalso):
    """G2.2, a leitura (E29.1, F1 do estudo de atrito): o status vale só com o comentário íntegro do PR do head e das contas."""
    URL = "https://github.com/dono/repo/pull/7#issuecomment-{}"

    def publicado(self, id_=601, texto=None, state="success", login="dono", descricao=None, url=None, autor="dono",
                  html=None, veredito="aprovado", contexto="parecer-review", registro=None, sha=None):
        sha = sha or self.sha
        texto = parecer(sha, veredito) if texto is None else texto
        comentario = {"id": id_, "body": texto, "user": {"login": autor}, "html_url": html or self.URL.format(id_)}
        self.estado(comentarios=self.estado().get("comentarios", {}) | {str(id_): comentario})
        sha256 = hashlib.sha256(fp().normalizar(texto).encode()).hexdigest()
        if registro is not False:  # M4.1: o que o `publicar` grava na pasta de controle
            self.registrar(registro or self.controle, sha=sha, contexto=contexto, sha256=sha256, comentario=id_)
        return {"context": contexto, "state": state, "creator": {"login": login}, "target_url": url or self.URL.format(id_),
                "description": descricao or f"{veredito} · sha256 {sha256} · 0 bloqueantes · 0 recomendados"}

    def registrar(self, pasta, **linha):
        pasta.mkdir(parents=True, exist_ok=True)
        with open(pasta / "pareceres-publicados.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(linha) + "\n")

    def ler(self, *statuses):
        self.estado(statuses=list(statuses))
        return fp().ler(str(self.repo), BRANCH, self.sha, PEDIDO)

    def invalido(self, *statuses):
        veredito, motivo = self.ler(*statuses)["review"]
        self.assertIsNone(veredito, motivo)
        return motivo

    def test_aprovado_com_comentario_integro(self):
        self.assertEqual(self.ler(self.publicado()), {"review": ("aprovado", self.URL.format(601))})

    def test_reprovado_vale_como_reprovado(self):
        self.assertEqual(self.ler(self.publicado(state="failure", veredito="reprovado"))["review"][0], "reprovado")

    def test_c1_status_do_bot_ignorado(self):
        self.assertEqual(self.ler(self.publicado(login="github-actions[bot]")), {})

    def test_c19_conta_fora_da_lista_ignorada(self):
        """M1.4 (C19, `test_c19_login_fora_da_lista_da_base` do modelo): com o `GH_TOKEN` de outra conta no ambiente (`gh api user` = `outra`), o status dela segue fora: a conta aceita é
        a dona do `origin`, nunca a da sessão."""
        self.estado(login="outra")
        self.assertEqual(self.ler(self.publicado(login="outra", autor="outra")), {})
        self.assertNotIn(["api", "user"], self.chamadas(), "a leitura perguntou a conta da sessão")
        self.assertIn("M5.2", self.invalido(self.publicado(autor="outra")))  # comentário de fora da lista

    def test_conta_dona_em_outra_caixa_vale(self):
        """O GitHub não distingue caixa no login: `Dono` no `creator` é a dona do `origin` `dono`."""
        self.assertEqual(self.ler(self.publicado(login="Dono", autor="DONO"))["review"][0], "aprovado")

    def test_c5_status_sem_registro_de_publicar(self):
        """M4.1 (T4): status e comentário íntegros gravados pelo Bash, sem o `publicar`, não valem."""
        self.assertIn("M4.1", self.invalido(self.publicado(registro=False)))
        self.assertFalse([c for c in self.chamadas() if any("/issues/comments/" in x for x in c)], "leu o comentário")

    def test_c5_registro_de_outra_publicacao_nao_vale(self):
        status = self.publicado(registro=False)
        sha256 = status["description"].split(" ")[3]
        for linha in ({"sha": "b" * 40, "contexto": "parecer-review", "sha256": sha256, "comentario": 601},
                      {"sha": self.sha, "contexto": "parecer-qa", "sha256": sha256, "comentario": 601},
                      {"sha": self.sha, "contexto": "parecer-review", "sha256": "c" * 64, "comentario": 601},
                      {"sha": self.sha, "contexto": "parecer-review", "sha256": sha256, "comentario": 602}):
            with self.subTest(linha):
                self.registrar(self.controle, **linha)
                self.assertIn("M4.1", self.invalido(status))

    def test_c5_registro_so_no_run_do_clone_nao_vale(self):
        """O `.forge/run/` do clone não é a pasta de controle: o portão publica num clone e o `forge-fechar` lê noutro."""
        self.assertIn("M4.1", self.invalido(self.publicado(registro=self.repo / ".forge" / "run")))

    def test_c5_linha_ilegivel_do_registro_fica_de_fora(self):
        (self.controle / "pareceres-publicados.jsonl").write_text('x\n[1]\n{"sha": 1}\n{"sha": []}\n', encoding="utf-8")
        self.assertEqual(self.ler(self.publicado())["review"][0], "aprovado")

    def test_c5_pasta_de_controle_por_link_falha_fechada(self):
        status = self.publicado(registro=self.repo / ".forge" / "run")
        reais = {"run": self.controle, ".forge": self.controle.parent}
        for nome, pasta in reais.items():
            with self.subTest(nome):
                guardada = pasta.with_name(pasta.name + "-real")
                pasta.rename(guardada)
                pasta.symlink_to(self.repo / ".forge" / ("run" if nome == "run" else ""))
                with self.assertRaisesRegex(fp().Recusa, "M4.1"):
                    self.ler(status)
                pasta.unlink(), guardada.rename(pasta)
        with self.subTest("registro por link"):
            (self.controle / "pareceres-publicados.jsonl").symlink_to(self.repo / ".forge" / "run" / "pareceres-publicados.jsonl")
            with self.assertRaisesRegex(fp().Recusa, "M4.1"):
                self.ler(status)

    def test_c5_sem_pasta_de_controle_falha_fechada(self):
        status = self.publicado()
        subprocess.run(["rm", "-rf", str(self.controle)], check=True)
        with self.assertRaisesRegex(fp().Recusa, "M4.1"):
            self.ler(status)

    def test_c5_publicado_num_clone_lido_noutro(self):
        """O portão publica no clone dele; quem lê roda noutro clone da mesma máquina e acha o registro na pasta de controle."""
        url, _ = fp().publicar(str(self.repo), "review", "aprovado", parecer(self.sha), self.sha, BRANCH, 0, 0, ["review"])
        outro = self.repo.with_name("outro")
        subprocess.run(["git", "clone", "-q", str(self.repo), str(outro)], env=self.env, check=True)
        subprocess.run(["git", "remote", "set-url", "origin", "https://github.com/dono/repo.git"], cwd=outro, env=self.env, check=True)
        self.assertEqual(fp().ler(str(outro), BRANCH, self.sha, PEDIDO), {"review": ("aprovado", url)})
        self.assertFalse((self.repo / ".forge" / "run" / "pareceres-publicados.jsonl").exists(), "gravou no clone")

    def test_c2_bot_mais_novo_nao_esconde_failure_da_conta(self):
        lido = self.ler(self.publicado(602, login="github-actions[bot]"), self.publicado(601, state="failure", veredito="reprovado"))
        self.assertEqual(lido["review"][0], "reprovado")

    def test_mais_novo_da_conta_vale(self):
        lido = self.ler(self.publicado(602, state="failure", veredito="reprovado"), self.publicado(601))
        self.assertEqual(lido["review"][0], "reprovado")

    def test_c3_contexto_parecido(self):
        for contexto in ("Parecer-review", "parecer-review ", "parecer/review", "ci/parecer-review"):
            with self.subTest(contexto):
                self.assertEqual(self.ler(self.publicado(contexto=contexto)), {})

    def test_c6_comentario_editado(self):
        status = self.publicado()
        self.publicado(texto=parecer(self.sha) + "\nAdendo.\n")  # mesmo id, corpo novo
        self.assertIn("M5.1", self.invalido(status))

    def test_c6_comentario_apagado(self):
        status = self.publicado()
        self.estado(comentarios={})
        with self.assertRaises(fp().Recusa):
            self.ler(status)

    def test_c7_comentario_de_outra_conta(self):
        self.assertIn("M5.2", self.invalido(self.publicado(autor="outra")))

    def test_comentario_de_outro_pr_pelo_mesmo_id(self):
        self.assertIn("M6.1", self.invalido(self.publicado(html="https://github.com/dono/repo/pull/5#issuecomment-601")))

    def test_c8_target_url_fora_do_formato(self):
        for url in ("https://gist.github.com/dono/1", "https://github.com/dono/repo/pull/5#issuecomment-601",
                    "https://github.com/outro/repo/pull/7#issuecomment-601", "https://exemplo.com/dono/repo/pull/7#issuecomment-601",
                    "http://github.com/dono/repo/pull/7#issuecomment-601", self.URL.format(601) + "x"):
            with self.subTest(url):
                self.assertIn("M6.1", self.invalido(self.publicado(url=url)))
        self.assertFalse([c for c in self.chamadas() if any("/issues/comments/" in x for x in c)], "seguiu o target_url")

    def test_c9_descricao_fora_da_forma(self):
        for descricao in ("aprovado · sha256 abc · 0 bloqueantes · 0 recomendados", "ok", "aprovado · sha256 " + "a" * 64):
            with self.subTest(descricao):
                self.assertIn("M7.1", self.invalido(self.publicado(descricao=descricao)))
        inteira = self.publicado()["description"]
        self.assertIn("M7.1", self.invalido(self.publicado(descricao=inteira + " x")))  # casa inteira, não pelo começo

    def test_c10_commit_do_texto_diferente_do_sha(self):
        self.assertIn("M8.1", self.invalido(self.publicado(texto=parecer("b" * 40))))

    def test_c10_pedido_ou_tipo_do_texto_diferente(self):
        for texto in (parecer(self.sha, pedido="v8"), parecer(self.sha, tipo="qa")):
            with self.subTest(texto[:40]):
                self.assertIn("M8.1", self.invalido(self.publicado(texto=texto)))

    def test_c10_veredito_diferente_do_estado(self):
        self.assertIn("M8.1", self.invalido(self.publicado(state="failure")))  # descrição aprovado, estado failure
        self.assertIn("M8.1", self.invalido(self.publicado(texto=parecer(self.sha, "reprovado"))))  # texto reprovado

    def test_sem_frontmatter(self):
        self.assertIn("M8.1", self.invalido(self.publicado(texto="# Review\nsem cabeçalho\n")))

    def test_frontmatter_sem_a_linha_de_abertura(self):
        self.assertIn("M8.1", self.invalido(self.publicado(texto="x" + parecer(self.sha)[3:])))

    def test_c17_api_com_erro(self):
        status = self.publicado()
        self.estado(falha_em=f"repos/dono/repo/commits/{self.sha}/statuses")  # o PR lido, os statuses com erro
        with self.assertRaises(fp().Recusa):
            self.ler(status)

    def test_c17_pagina_2_lida(self):
        self.estado(paginas=[[self.publicado(602, login="outra")], [self.publicado(601)]])
        self.assertEqual(fp().ler(str(self.repo), BRANCH, self.sha, PEDIDO)["review"][0], "aprovado")

    def test_c17_paginas_ilegiveis(self):
        for paginas in ({"x": 1}, [{"context": "parecer-review"}]):
            with self.subTest(paginas):
                self.estado(paginas=paginas)
                with self.assertRaises(fp().Recusa):
                    fp().ler(str(self.repo), BRANCH, self.sha, PEDIDO)

    def test_status_sem_descricao_ou_sem_target_url(self):
        sem_descricao, sem_url = self.publicado(), self.publicado()
        del sem_descricao["description"], sem_url["target_url"]
        self.assertIn("M7.1", self.invalido(sem_descricao))
        self.assertIn("M6.1", self.invalido(sem_url))

    def test_linha_do_frontmatter_sem_chave_valor_fica_de_fora(self):
        texto = parecer(self.sha).replace("contrato: 1\n", "contrato: 1\nnota\n", 1)
        self.assertEqual(self.ler(self.publicado(texto=texto))["review"][0], "aprovado")

    def test_item_da_pagina_que_nao_e_objeto_fica_de_fora(self):
        self.estado(paginas=[[5, "x", self.publicado(601)]])
        self.assertEqual(fp().ler(str(self.repo), BRANCH, self.sha, PEDIDO)["review"][0], "aprovado")

    def test_contas_que_nao_sao_conjunto_recusadas(self):
        """M1.1 e M1.4: o chamador não passa mais a lista de contas (nem a alarga); ela é o conjunto fechado da dona do `origin`."""
        self.estado(statuses=[self.publicado(login="outra", autor="outra")])
        for contas in ({"outra"}, frozenset({"outra"}), ["outra"], "outra"):
            with self.subTest(contas), self.assertRaises(TypeError):
                fp().ler(str(self.repo), BRANCH, self.sha, PEDIDO, contas)
        self.assertEqual(fp().contas_aceitas(str(self.repo)), frozenset({"dono"}))

    def test_contas_com_login_vazio_recusadas(self):
        """Login vazio no status, no comentário ou na sessão nunca é a dona."""
        self.assertEqual(self.ler(self.publicado(login="")), {})
        self.assertIn("M5.2", self.invalido(self.publicado(autor="")))
        self.estado(login="")
        with self.assertRaisesRegex(fp().Recusa, "M1.4"):
            fp().publicar(str(self.repo), "review", "aprovado", parecer(self.sha), self.sha, BRANCH, 0, 0, ["review"])
        self.assertFalse([c for c in self.chamadas() if "POST" in c], "gravou")
        self.estado(statuses=[self.publicado(login="")])
        self.assertEqual(fp().agregado(str(self.repo), self.sha, ["review"])[0], "pending")

    def test_contas_frozenset_vale(self):
        self.assertIsInstance(fp().contas_aceitas(str(self.repo)), frozenset)
        self.assertEqual(self.ler(self.publicado())["review"][0], "aprovado")

    def test_status_e_comentario_sem_login_de_texto_ficam_fora(self):
        """Sonda S1 do review 2d3e3f3, refeita para a conta da base: login que não é texto nunca casa com a dona."""
        for login in (None, 5, ["dono"]):
            with self.subTest(login):
                self.assertEqual(self.ler(self.publicado(login=login)), {})
                self.assertIn("M5.2", self.invalido(self.publicado(autor=login)))
        sem_creator = self.publicado()
        del sem_creator["creator"]
        self.assertEqual(self.ler(sem_creator), {})

    def fora_do_contrato(self, status):
        with self.assertRaisesRegex(fp().Recusa, "fora do contrato"):
            self.ler(status)

    def test_resposta_fora_do_contrato_vira_recusa(self):
        """Sondas S3 a S5 da segurança 2d3e3f3: `creator` do status, `user` do comentário e PR sem `number`."""
        status = self.publicado()
        self.fora_do_contrato(status | {"creator": "conta"})
        self.estado(comentarios={"601": self.estado()["comentarios"]["601"] | {"user": "conta"}})
        self.fora_do_contrato(status)
        self.publicado()  # o comentário íntegro de volta
        self.estado(prs=[{k: v for k, v in self.estado()["prs"][0].items() if k != "number"}])
        self.fora_do_contrato(status)

    def test_sha_que_nao_e_head_do_pr(self):
        self.estado(prs=[self.estado()["prs"][0] | {"headRefOid": "c" * 40}])
        with self.assertRaises(fp().Recusa):
            self.ler(self.publicado())


class Vigentes(GhFalso):
    """C2a (F1 parte 2; ADR 0019 emendada, C0-1 e C0-2): por tipo, o status mais novo entre os commits do PR, com a origem
    ancestral do head; casos C13, C14 e C24 do modelo de ameaças e a falha fechada do registro (CONTROLE-RUN-GRAFIA)."""
    URL, publicado, registrar = Ler.URL, Ler.publicado, Ler.registrar

    def setUp(self):
        super().setUp()
        self.a = self.sha
        self.b, self.c = (self.commit(nome) for nome in ("b", "c"))  # b e c filhos de a: c fora da história do head b
        self.estado(prs=[self.estado()["prs"][0] | {"headRefOid": self.b}], pr_view={
            "number": 7, "headRefName": BRANCH, "url": "https://github.com/dono/repo/pull/7",
            "commits": [{"oid": self.a}, {"oid": self.b}]})

    def commit(self, nome):
        arvore = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=self.repo, env=self.env, capture_output=True,
                                text=True).stdout.strip()
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit-tree", arvore, "-p", self.a, "-m", nome],
                              cwd=self.repo, env=self.env, capture_output=True, text=True, check=True).stdout.strip()

    def em(self, sha, segundo, **kw):
        """O status publicado em `sha`, criado no segundo `segundo` (o id cresce junto)."""
        return sha, self.publicado(id_=600 + segundo, sha=sha, **kw) | {"created_at": f"2026-11-27T10:00:{segundo:02d}Z",
                                                                         "id": segundo}

    def vigentes(self, *publicados, pr=7):
        por_commit = {}
        for sha, s in sorted(publicados, key=lambda x: -x[1]["id"]):
            por_commit.setdefault(sha, [[]])[0].append(s)
        self.estado(por_commit=por_commit)
        return fp().vigentes(str(self.repo), pr, self.b, PEDIDO)

    def test_c14_aprovado_herdado_traz_a_origem(self):
        """A origem é o commit do status, não o head nem um intermediário: o domínio se mede dela (C2b)."""
        lido = self.vigentes(self.em(self.a, 1))
        self.assertEqual(lido, {"review": ("aprovado", self.URL.format(601), self.a)})

    def test_c13_failure_mais_novo_barra_success_antigo(self):
        lido = self.vigentes(self.em(self.a, 1), self.em(self.b, 2, state="failure", veredito="reprovado"))
        self.assertEqual(lido["review"][:1] + lido["review"][2:], ("reprovado", self.b))

    def test_mais_novo_pelo_tempo_nao_pelo_commit(self):
        lido = self.vigentes(self.em(self.b, 1, state="failure", veredito="reprovado"), self.em(self.a, 2))
        self.assertEqual(lido["review"][0], "aprovado")

    def test_c24_comentario_do_mais_novo_apagado_nao_recua(self):
        """T21: o `reprovado` mais novo tem o comentário apagado; a leitura não volta ao `aprovado` de antes."""
        antigo, novo = self.em(self.a, 1), self.em(self.b, 2, state="failure", veredito="reprovado")
        self.estado(comentarios={"601": self.estado()["comentarios"]["601"]})
        try:
            veredito = self.vigentes(antigo, novo)["review"][0]
        except fp().Recusa:
            veredito = None
        self.assertIsNone(veredito)

    def test_c24_comentario_do_mais_novo_editado_invalida_o_tipo(self):
        antigo, novo = self.em(self.a, 1), self.em(self.b, 2, state="failure", veredito="reprovado")
        self.publicado(id_=602, sha=self.b, texto=parecer(self.b) + "\nAdendo.\n", registro=False)
        self.assertIn("M5.1", self.vigentes(antigo, novo)["review"][1])

    def test_c13_origem_fora_da_historia_do_head(self):
        self.estado(pr_view=self.estado()["pr_view"] | {"commits": [{"oid": self.a}, {"oid": self.c}, {"oid": self.b}]})
        lido = self.vigentes(self.em(self.c, 1))
        self.assertEqual(lido["review"][1:], ("origem do status fora da história do head (C0-2)", self.c))

    def test_c0_2_origem_ausente_na_copia_falha_fechada(self):
        fora = "d" * 40
        self.estado(pr_view=self.estado()["pr_view"] | {"commits": [{"oid": fora}, {"oid": self.b}]})
        with self.assertRaisesRegex(fp().Recusa, "C0-2"):
            self.vigentes(self.em(fora, 1))

    def test_c0_2_commit_fora_do_pr_nao_conta(self):
        """Status de um commit que não é do PR (a `develop` trazida) não entra na leitura."""
        self.assertEqual(self.vigentes(self.em(self.c, 1)), {})

    def test_c13_status_forjado_nao_vale(self):
        self.assertEqual(self.vigentes(self.em(self.a, 1, login="github-actions[bot]", registro=False)), {})
        self.assertIn("M4.1", self.vigentes(self.em(self.a, 2, registro=False))["review"][1])

    def test_registro_sem_status_falha_fechada(self):
        """CONTROLE-RUN-GRAFIA: linha do registro de um commit do PR sem o status correspondente recusa a leitura."""
        status = self.em(self.a, 1)
        sha256 = status[1]["description"].split(" ")[3]
        self.registrar(self.controle, sha="e" * 40, contexto="parecer-qa", sha256=sha256, comentario=601)  # fora do PR
        self.registrar(self.controle, sha=self.b, contexto="outro", sha256=sha256, comentario=601)  # fora da lista
        self.assertEqual(self.vigentes(status)["review"][0], "aprovado")
        for linha in ({"contexto": "parecer-qa", "sha256": sha256, "comentario": 601},
                      {"contexto": "parecer-review", "sha256": "c" * 64, "comentario": 601},
                      {"contexto": "parecer-review", "sha256": sha256, "comentario": 602}):
            with self.subTest(linha):
                self.registrar(self.controle, sha=self.a, **linha)
                with self.assertRaisesRegex(fp().Recusa, "CONTROLE-RUN-GRAFIA"):
                    self.vigentes(status)
                (self.controle / "pareceres-publicados.jsonl").write_text("", encoding="utf-8")
                status = self.em(self.a, 1)

    def test_registro_com_status_de_outra_conta_falha_fechada(self):
        with self.assertRaisesRegex(fp().Recusa, "CONTROLE-RUN-GRAFIA"):
            self.vigentes(self.em(self.a, 1, login="outra"))

    def test_pr_de_outro_numero_ou_sem_o_head(self):
        original = self.estado()["pr_view"]
        for mudar in ({"number": 8}, {"url": "https://github.com/dono/repo/pull/8"}, {"commits": [{"oid": self.a}]},
                      {"commits": [{"oid": "HEAD"}, {"oid": self.b}]}):
            with self.subTest(mudar):
                self.estado(pr_view=original | mudar)
                with self.assertRaises(fp().Recusa):
                    self.vigentes(self.em(self.a, 1))

    def test_pr_nao_numerico_sai_recusa(self):
        """C2A-RECOMENDADOS A2: o número do PR fora da forma é Recusa, nunca ValueError solto."""
        for pr in ("abc", None, "7a"):
            with self.subTest(pr), self.assertRaisesRegex(fp().Recusa, "fora do contrato"):
                self.vigentes(self.em(self.a, 1), pr=pr)

    def test_status_sem_created_at_fora_do_contrato(self):
        sha, status = self.em(self.a, 1)
        with self.assertRaisesRegex(fp().Recusa, "fora do contrato"):
            self.vigentes((sha, status | {"created_at": None}))

    def test_statuses_ilegiveis_de_um_commit_recusam(self):
        for paginas in ({"x": 1}, [{"x": 1}]):
            with self.subTest(paginas):
                self.estado(por_commit={self.a: paginas})
                with self.assertRaisesRegex(fp().Recusa, "ilegíveis"):
                    fp().vigentes(str(self.repo), 7, self.b, PEDIDO)

    def test_todas_as_paginas_de_cada_commit(self):
        sha, status = self.em(self.a, 1)
        self.estado(por_commit={sha: [[], [status]]})
        self.assertEqual(fp().vigentes(str(self.repo), 7, self.b, PEDIDO)["review"][0], "aprovado")

    def test_item_que_nao_e_objeto_e_status_sem_descricao_ficam_de_fora(self):
        """Na mesma página do status válido: o item que não é objeto sai, e o de outro contexto sem descrição nem target_url não
        derruba a conferência do registro; ele mesmo não vale."""
        sha, status = self.em(self.a, 2)
        vazio = {"context": "parecer-qa", "state": "success", "creator": {"login": "dono"}, "created_at": "2026-11-27T10:00:03Z",
                 "id": 3}
        self.estado(por_commit={sha: [["x", vazio, status]]})
        lido = fp().vigentes(str(self.repo), 7, self.b, PEDIDO)
        self.assertEqual((lido["review"][0], lido["qa"][0]), ("aprovado", None))


class PastaDeControle(unittest.TestCase):
    """M4.1: uma pasta por máquina para todos os clones; no projeto, a da cópia que contém `.forge/wt/`."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(subprocess.run, ["rm", "-rf", str(self.tmp)])
        p = mock.patch.dict(os.environ, {"HOME": str(self.tmp / "casa")})
        p.start()
        self.addCleanup(p.stop)

    def pastas(self, *rels):
        for rel in rels:
            (self.tmp / rel).mkdir(parents=True, exist_ok=True)

    def test_clone_de_projeto_usa_a_copia_que_contem_wt(self):
        self.pastas("proj/.forge/run", "proj/.forge/wt/c/.forge/run")
        self.assertEqual(fp().pasta_de_controle(str(self.tmp / "proj/.forge/wt/c")), self.tmp / "proj/.forge/run")
        self.assertEqual(fp().pasta_de_controle(str(self.tmp / "proj")), self.tmp / "proj/.forge/run")

    def test_copia_principal_fora_de_forge_wt_usa_a_propria(self):
        """Só o par `.forge/wt` marca o clone de projeto: uma pasta `wt` ou `.forge` solta no caminho não muda a cópia."""
        for rel in ("a/wt/proj", "b/.forge/proj"):
            with self.subTest(rel):
                self.pastas(f"{rel}/.forge/run")
                self.assertEqual(fp().pasta_de_controle(str(self.tmp / rel)), self.tmp / rel / ".forge/run")

    def test_copia_principal_do_forge_usa_a_forge_contrib(self):
        self.pastas("casa/.forge-contrib/.forge/run", "forge/.claude-plugin", "forge/.forge/run")
        (self.tmp / "forge/.claude-plugin/plugin.json").write_text('{"name": "forge"}', encoding="utf-8")
        self.assertEqual(fp().pasta_de_controle(str(self.tmp / "forge")), self.tmp / "casa/.forge-contrib/.forge/run")
        (self.tmp / "forge/.forge/versao").write_text("0.1.0\n", encoding="utf-8")  # projeto com o manifesto não é o Forge
        self.assertEqual(fp().pasta_de_controle(str(self.tmp / "forge")), self.tmp / "forge/.forge/run")
        for ilegivel in ("{", "[]", '{"name": "outro"}'):
            with self.subTest(ilegivel):
                (self.tmp / "forge/.forge/versao").unlink(missing_ok=True)
                (self.tmp / "forge/.claude-plugin/plugin.json").write_text(ilegivel, encoding="utf-8")
                self.assertEqual(fp().pasta_de_controle(str(self.tmp / "forge")), self.tmp / "forge/.forge/run")


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
            registro = {"caminho": f".forge/pareceres/{pedido}/{tipo}.md", "sha256": hashlib.sha256(texto.strip().encode()).hexdigest(), "papel": papel}
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


class PrPeloStatus(GhFalso):
    """C2b (F1 parte 2): o `forge-check pr` lê o parecer pelo status vigente (C2a) só com a lista fechada na develop do `origin`;
    sem ela, o caminho de arquivo de hoje, sem chamar o `gh`. O domínio do tipo se mede da origem do status ao head (M11.1, M12.1)."""
    URL, publicado, registrar, em, commit = Ler.URL, Ler.publicado, Ler.registrar, Vigentes.em, Vigentes.commit

    def setUp(self):
        super().setUp()
        self.a = self.sha
        self.b = self.commit("b")  # b: filho de a sem mudança
        (self.repo / "bin").mkdir()
        (self.repo / "bin" / "x.py").write_text("print(1)\n", encoding="utf-8")
        for args in (["add", "bin/x.py"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "código"]):
            subprocess.run(["git", *args], cwd=self.repo, env=self.env, check=True)
        self.d = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.repo, env=self.env, capture_output=True, text=True).stdout.strip()

    def pr(self, head, lista, *publicados, previo=False, branch=BRANCH, topo=None, chamar=None):
        """As linhas do review do `cmd_pr` (do `forge-check pr`, `pelo_status`) no `head` do PR #7 (commits a e head), com
        `lista_fechada` devolvendo `lista`; `chamar` troca a chamada."""
        por_commit = {}
        for sha, s in sorted(publicados, key=lambda x: -x[1]["id"]):
            por_commit.setdefault(sha, [[]])[0].append(s)
        self.estado(por_commit=por_commit, prs=[self.estado()["prs"][0] | {"headRefOid": topo or head}] if self.estado()["prs"] else [],
                    pr_view={"number": 7, "headRefName": BRANCH, "url": "https://github.com/dono/repo/pull/7",
                             "commits": [{"oid": self.a}, {"oid": topo or head}]})
        with mock.patch.object(fc().modulo_do_bin("forge_pareceres"), "lista_fechada", return_value=lista):
            with contextlib.redirect_stderr(io.StringIO()):  # o aviso do `--previo`
                saida = (chamar or (lambda: fc().cmd_pr(self.repo, PEDIDO, head, None, branch, previo=previo, pelo_status=True)))()
        return [x for x in saida if x.startswith("docs/reviews")]

    def test_sem_a_lista_nada_muda(self):
        """Dormente: o status aprovado não conta, o arquivo segue exigido e o `gh` nem é chamado."""
        self.assertEqual(self.pr(self.b, None, self.em(self.a, 1)), [f"docs/reviews: review: sem parecer para o pedido `{PEDIDO}` (R-REVIEW)"])
        self.assertEqual(self.chamadas(), [])

    def test_pr_da_lista_com_status_aprovado_e_dominio_intacto_passa(self):
        self.assertEqual(self.pr(self.b, frozenset({7}), self.em(self.a, 1)), [])

    def test_dominio_mexido_depois_da_origem_recusa(self):
        """M12.1: a origem a, não o head, é o ponto de partida: bin/x.py mudou em d depois do status de a."""
        linhas = self.pr(self.d, frozenset({7}), self.em(self.a, 1))
        self.assertEqual(len(linhas), 1, linhas)
        self.assertIn(f"status parecer-review de {self.a[:7]}", linhas[0])
        self.assertIn("commit: desatualizado: bin/x.py mudou depois do parecer", linhas[0])

    def test_sem_ref_le_o_head(self):
        """Sem `--ref`, o head é o HEAD da cópia (d, com bin/x.py depois do status de a)."""
        self.assertIn("commit: desatualizado: bin/x.py", self.pr(None, frozenset({7}), self.em(self.a, 1), topo=self.d)[0])

    def test_ref_que_nao_resolve_reprova(self):
        self.assertIn("leitura do status parecer-review recusada: o commit  não é o head",
                      self.pr("f" * 40, frozenset({7}), self.em(self.a, 1))[0])

    def test_reprovado_vigente_barra(self):
        linhas = self.pr(self.b, frozenset({7}), self.em(self.a, 1, state="failure", veredito="reprovado"))
        self.assertIn("parecer: o último parecer não é aprovado", linhas[0])

    def test_status_que_nao_vale_reprova(self):
        linhas = self.pr(self.b, frozenset(), self.em(self.a, 1, registro=False))
        self.assertIn(f"docs/reviews: review: status parecer-review de {self.a[:7]} não vale: status sem registro", linhas[0])

    def test_fora_da_lista_so_o_status(self):
        """M20.1: fora da lista, sem status o tipo falta (o arquivo não é lido); na lista, sem status, o caminho de arquivo."""
        self.assertIn("fora da lista fechada, o parecer em arquivo não vale (M20.1)", self.pr(self.b, frozenset({8}))[0])
        self.assertEqual(self.pr(self.b, frozenset({7})), [f"docs/reviews: review: sem parecer para o pedido `{PEDIDO}` (R-REVIEW)"])

    def test_sem_pr_aberto_fica_ausente(self):
        """Antes do PR (o pré-voo do envio), nenhum publicado: ausente, que o `--previo` só avisa."""
        self.estado(prs=[])
        self.assertEqual(self.pr(self.b, frozenset(), previo=True), [])
        self.assertIn("sem o status parecer-review", self.pr(self.b, frozenset())[0])

    def test_branch_de_integracao_segue_o_arquivo(self):
        """Na promoção (branch de integração) o status não entra: o caminho de arquivo de hoje."""
        self.assertEqual(self.pr(self.b, frozenset({7}), self.em(self.a, 1), branch="develop"),
                         [f"docs/reviews: review: sem parecer para o pedido `{PEDIDO}` (R-REVIEW)"])

    def test_hook_e_catraca_seguem_o_arquivo(self):
        """O `cmd_pr` sem `pelo_status` (o hook `parecer` e a catraca) não lê a lista nem o `gh` (CORPUS-CUSTO-CONTADOR)."""
        mod = fc().modulo_do_bin("forge_pareceres")
        with mock.patch.object(mod, "lista_fechada", side_effect=AssertionError("lida")):
            linhas = self.pr(self.b, frozenset({7}), self.em(self.a, 1),
                             chamar=lambda: fc().cmd_pr(self.repo, PEDIDO, self.b, None, BRANCH))
        self.assertEqual(linhas, [f"docs/reviews: review: sem parecer para o pedido `{PEDIDO}` (R-REVIEW)"])

    def test_forge_check_pr_le_o_status(self):
        """O `pr_da_cli` (o `forge-check pr` e o `forge-fechar`) liga o status, sem e com `--base`."""
        for base in (None, "develop"):
            with self.subTest(base=base):
                self.assertEqual(self.pr(self.b, frozenset({7}), self.em(self.a, 1), chamar=lambda: fc().pr_da_cli(
                    self.repo, PEDIDO, self.b, base, BRANCH, conferir=False)), [])

    def test_leitura_recusada_reprova(self):
        self.estado(falha=True)
        self.assertIn("leitura do status parecer-review recusada: gh pr list saiu com 1", self.pr(self.b, frozenset({7}))[0])


class ListaFechada(unittest.TestCase):
    """C2b (M20.1, M10.1): a lista fechada sai da develop do `origin` pelo commit do `git ls-remote`, nunca do head nem de um ref
    local recuado ou forjado; sem rede, do ref local; fora da forma ou só no ref local com a develop remota fora da cópia: Recusa."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(subprocess.run, ["rm", "-rf", str(self.tmp)])
        self.remoto, self.repo = self.tmp / "remoto.git", self.tmp / "repo"
        self.env = sem_manutencao({"PATH": "/usr/bin:/bin", "HOME": str(self.tmp), "GIT_CONFIG_NOSYSTEM": "1"})
        p = mock.patch.dict(os.environ, {"PATH": "/usr/bin:/bin", "HOME": str(self.tmp)}, clear=True)
        p.start()
        self.addCleanup(p.stop)
        self.git(self.tmp, "init", "-q", "--bare", "-b", "develop", str(self.remoto))
        remoto_sem_manutencao(self.remoto)
        self.git(self.tmp, "init", "-q", "-b", "develop", str(self.repo))
        self.git(self.repo, "remote", "add", "origin", str(self.remoto))
        self.vazio = self.commitar(None)

    def git(self, cwd, *args):
        return subprocess.run(["git", *args], cwd=cwd, env=self.env, check=True, capture_output=True, text=True).stdout.strip()

    def commitar(self, lista, enviar=True):
        arq = self.repo / fp().LISTA_FECHADA
        if lista is None:
            arq.unlink(missing_ok=True)
        else:
            arq.parent.mkdir(exist_ok=True)
            arq.write_text(lista, encoding="utf-8")
        self.git(self.repo, "add", "-A")
        self.git(self.repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "x")
        if enviar:
            self.git(self.repo, "push", "-q", "origin", "develop")
            self.git(self.repo, "fetch", "-q", "origin")
        return self.git(self.repo, "rev-parse", "HEAD")

    def lista(self):
        return fp().lista_fechada(str(self.repo))

    def test_sem_o_arquivo_dormente(self):
        self.assertIsNone(self.lista())

    def test_lista_da_develop_remota(self):
        self.commitar("[7, 12]")
        self.assertEqual(self.lista(), frozenset({7, 12}))

    def test_lista_so_no_head_nao_vale(self):
        self.git(self.repo, "switch", "-q", "-c", "melhoria/x")
        self.commitar("[7]", enviar=False)
        self.assertIsNone(self.lista())

    def test_ref_local_forjado_perde_para_o_remoto(self):
        com = self.commitar("[7]")
        self.commitar(None)
        self.git(self.repo, "update-ref", "refs/remotes/origin/develop", com)
        self.assertIsNone(self.lista())

    def test_develop_remota_fora_da_copia_com_lista_local_recusa(self):
        self.commitar("[7]")
        outro = self.tmp / "outro"
        self.git(self.tmp, "clone", "-q", str(self.remoto), str(outro))
        self.git(outro, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "y")
        self.git(outro, "push", "-q", "origin", "develop")  # a develop remota anda; a cópia não a tem
        with self.assertRaisesRegex(fp().Recusa, "git fetch origin develop"):
            self.lista()

    def test_so_a_linha_exata_da_develop(self):
        """O padrão do `ls-remote` casa o fim do nome: `a/refs/heads/develop` com a lista não vale pela develop."""
        com = self.commitar("[7]", enviar=False)
        self.git(self.repo, "push", "-q", "origin", f"{com}:refs/heads/a/refs/heads/develop")
        self.git(self.repo, "reset", "-q", "--hard", self.vazio)
        self.assertIsNone(self.lista())

    def test_sem_rede_vale_o_ref_local(self):
        self.commitar("[7]")
        self.git(self.repo, "remote", "set-url", "origin", str(self.tmp / "nao-existe.git"))
        self.assertEqual(self.lista(), frozenset({7}))

    def test_git_herdado_nao_desvia_a_leitura(self):
        """`GIT_DIR` no ambiente não troca a cópia lida: a lista de outra cópia não vale nesta."""
        self.commitar("[7]")
        limpo = self.tmp / "limpo"
        self.git(self.tmp, "init", "-q", "-b", "develop", str(limpo))
        with mock.patch.dict(os.environ, {"GIT_DIR": str(self.repo / ".git")}):
            self.assertIsNone(fp().lista_fechada(str(limpo)))

    def test_fora_da_forma_recusa(self):
        for texto in ('{"prs": [7]}', '[7, "8"]', "[true]", "[7,", ""):
            with self.subTest(texto):
                self.commitar(texto)
                with self.assertRaisesRegex(fp().Recusa, "fora da forma"):
                    self.lista()


if __name__ == "__main__":
    unittest.main()
