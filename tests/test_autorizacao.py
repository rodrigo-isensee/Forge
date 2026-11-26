"""ADR 0018, G1.1: formato, integridade e estado das autorizações gravadas (`bin/forge_autorizacao.py`, `bin/forge-check autorizacao ler`)."""
import argparse
import contextlib
import datetime
import errno
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_manutencao  # noqa: E402

BIN = Path(__file__).resolve().parent.parent / "bin"
fa = None  # carregado em setUpModule: na base, sem o módulo, cada teste cai por conta própria (R-QA)


def setUpModule():
    global fa
    spec = importlib.util.spec_from_file_location("forge_autorizacao", BIN / "forge_autorizacao.py")
    fa = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fa)


GRAVADOR = hashlib.sha256((BIN / "forge-check").read_bytes()).hexdigest()
CORPO = "pode aplicar o rótulo no PR 5\n\nnão é recorte"
UTC = datetime.timezone.utc


def concessao(corpo=CORPO, **troca):
    campos = {"Id": "A-1", "Ato": "rotulo-afrouxa-regra", "Alvos": "pr:5", "Validade": "ate:2026-11-18 08:00",
              "Validade-utc": "2026-11-18 11:00", "Fuso": "America/Sao_Paulo", "Origem-da-validade": "esta noite",
              "Estado-inicial": "ativa", "Motivo-da-pendencia": "nenhum", "Mensagem": "u-1",
              "Hora-da-fala": "2026-11-18T00:00:00Z", "Sessao": "s-1", "Pedido": "v047", "Sha256": fa.sha(CORPO), "Gravado-por": GRAVADOR,
              "Autoriza": fa.AUTORIZA, **troca}
    return evento(corpo, campos)


def evento(corpo, campos):
    return "".join(f"{k}: {v}\n" for k, v in campos.items() if v is not None) + "\n" + corpo


def confirmacao(hora="2026-11-18T00:05:00Z", corpo="confirmo A-1", **troca):
    return evento(corpo, {"Confirma": "A-1", "Mensagem": "u-2", "Hora-da-fala": hora, "Sessao": "s-1", "Sha256": fa.sha(corpo),
                          "Gravado-por": GRAVADOR, **troca})


def em(texto):
    return datetime.datetime.fromisoformat(texto).replace(tzinfo=UTC)


class Ler(unittest.TestCase):
    def setUp(self):
        self.raiz = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.raiz)
        self.pasta = self.raiz / fa.PASTA
        self.pasta.mkdir(parents=True)

    def ler(self, agora="2026-11-18 10:59"):
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            rc = fa.cmd_ler(self.raiz, {"gravador": GRAVADOR, "seguro": str}, em(agora))
        return rc, saida.getvalue()

    def estados(self, agora, **eventos):
        shutil.rmtree(self.pasta)
        self.pasta.mkdir()
        for nome, texto in eventos.items():
            (self.pasta / nome.replace("_", "-")).write_text(texto, encoding="utf-8")
        return [est for _, _, _, est, _ in fa.concessoes(self.raiz, GRAVADOR, em(agora))[0]]

    def test_integra_mostra_a_mensagem_inteira_validade_no_fuso_e_em_utc(self):
        (self.pasta / "A-1").write_text(concessao(), encoding="utf-8")
        rc, saida = self.ler()
        self.assertEqual(rc, 0, saida)
        self.assertIn("A-1 · ativa · rotulo-afrouxa-regra · pr:5 · validade ate:2026-11-18 08:00 America/Sao_Paulo = "
                      "2026-11-18 11:00 UTC · pedido v047", saida)
        self.assertIn("1 ativa(s)", saida)
        self.assertIn("A-1 · vencida · ", self.ler("2026-11-18 11:00")[1])
        self.assertIn("> pode aplicar o rótulo no PR 5\n> \n> não é recorte\n", saida)

    def test_evento_adulterado_ou_fora_da_forma(self):
        casos = {"corpo": dict(corpo=CORPO + "!"), "gravador": dict(**{"Gravado-por": "0" * 64}),
                 "ato": dict(Ato="merge"), "alvos": dict(Alvos="pr:5 e pr:6"), "inicial": dict(**{"Estado-inicial": "x"}),
                 "autoriza": dict(Autoriza="tudo"), "ausente": dict(Sessao=None), "pedido": dict(Pedido="../v047")}
        for caso, troca in casos.items():
            with self.subTest(caso=caso):
                (self.pasta / "A-1").write_text(concessao(**troca), encoding="utf-8")
                rc, saida = self.ler()
                self.assertEqual(rc, 1, saida)
                self.assertIn("A-1 · adulterada (", saida)

    def test_evento_ilegivel_e_erro_e_nada_e_integro_por_ele(self):
        fora = self.raiz / "fora"
        fora.write_text(concessao(), encoding="utf-8")
        duplicado = concessao().replace("Id: A-1\n", f"Sha256: {'0' * 64}\nId: A-1\n")
        casos = {"link": lambda a: a.symlink_to(fora), "pasta": lambda a: a.mkdir(),
                 "utf8": lambda a: a.write_bytes(b"Id: \xff\n\nx"), "repetido": lambda a: a.write_text(duplicado),
                 "sem-linha-vazia": lambda a: a.write_text(concessao("", Sha256=fa.sha("")).rstrip("\n"))}
        for caso, criar in casos.items():
            with self.subTest(caso=caso):
                shutil.rmtree(self.pasta)
                self.pasta.mkdir()
                criar(self.pasta / "A-1")
                rc, saida = self.ler()
                self.assertEqual(rc, 1, saida)
                self.assertIn("autorizacao: erro: A-1: ", saida)
                self.assertNotIn("A-1 · ", saida)
                if caso == "link":  # o texto do erro do sistema, sem o "[Errno n]" nem o caminho
                    self.assertIn(f"autorizacao: erro: A-1: {os.strerror(errno.ELOOP)}\n", saida)

    def test_pasta_que_e_link_e_nome_fora_da_forma_sao_erro(self):
        outra = self.raiz / "outra"
        outra.mkdir()
        (outra / "A-1").write_text(concessao(), encoding="utf-8")
        self.pasta.rmdir()
        self.pasta.symlink_to(outra)
        rc, saida = self.ler()
        self.assertEqual((rc, "ativa ·" in saida, "não é pasta comum" in saida), (1, False, True), saida)
        self.pasta.unlink()
        self.pasta.mkdir()
        (self.pasta / "A-1.bak").write_text(concessao(), encoding="utf-8")
        self.assertEqual(self.ler(), (1, "autorizacao: erro: A-1.bak: nome fora da forma\n"
                                         "autorizacao: 0 adulterada(s), 1 erro(s) de leitura, 0 ativa(s); só leitura, "
                                         "nada barra\n"))

    def test_pasta_ausente_nada_e_so_concessao_e_listada(self):
        shutil.rmtree(self.pasta)
        self.assertEqual(self.ler()[0], 0)
        self.pasta.mkdir()
        for nome in ("U-A-1", "M-0a1b"):  # só presença: vazios, não são lidos
            (self.pasta / nome).write_text("", encoding="utf-8")
        (self.pasta / "C-A-1").write_text(concessao(Id="C-A-1"), encoding="utf-8")
        rc, saida = self.ler()
        self.assertEqual((rc, saida.count("autorizacao: ")), (0, 1), saida)

    def test_forge_check_autorizacao_ler_aceita_so_o_gravado_por_ele(self):
        (self.pasta / "A-1").write_text(concessao(), encoding="utf-8")
        (self.pasta / "A-2").write_text(concessao(**{"Id": "A-2", "Gravado-por": "f" * 64}), encoding="utf-8")
        env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_", "PYTHON"))}
        env["GIT_CEILING_DIRECTORIES"] = str(self.raiz.parent)
        r = subprocess.run([sys.executable, "-I", str(BIN / "forge-check"), "--raiz", str(self.raiz), "autorizacao", "ler"],
                           capture_output=True, text=True, env=env, timeout=60)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertRegex(r.stdout, "A-1 · (ativa|vencida) ")
        self.assertIn("A-2 · adulterada (Gravado-por não é o forge-check carregado)", r.stdout)


    def test_validade_em_utc_a6_e_teto_d1_fala_as_21h_locais_que_ja_e_o_dia_seguinte_em_utc(self):
        # fala 17/11 21:00 em São Paulo = 18/11 00:00 UTC; "esta noite" = 18/11 08:00 local = 11:00 UTC, não 19/11
        uso = {"Validade": "uso-unico", "Validade-utc": "uso-unico", "Origem-da-validade": "quando der"}
        casos = [({}, "2026-11-18 10:59", "ativa"), ({}, "2026-11-18 11:00", "vencida"),
                 ({"Validade-utc": "2026-11-18 08:00"}, "2026-11-18 07:00", "adulterada"),  # A6: local lido como UTC
                 ({"Fuso": "Nada/X"}, "2026-11-18 07:00", "adulterada"),
                 ({"Validade": "por:2026-11-18 08:00"}, "2026-11-18 07:00", "adulterada"),
                 ({"Hora-da-fala": "2026-11-18T00:00:00"}, "2026-11-18 07:00", "adulterada"),
                 ({"Origem-da-validade": "até amanhã", "Validade": "ate:2026-11-21 08:00", "Validade-utc": "2026-11-21 11:00"},
                  "2026-11-19 23:59", "ativa"),
                 ({"Origem-da-validade": "Até amanhã", "Validade": "ate:2026-11-21 08:00", "Validade-utc": "2026-11-21 11:00"},
                  "2026-11-20 00:00", "vencida"),
                 ({"Origem-da-validade": "até 30/11", "Validade": "ate:2026-11-30 08:00", "Validade-utc": "2026-11-30 11:00"},
                  "2026-11-24 23:59", "ativa"),
                 ({"Origem-da-validade": "até 30/11", "Validade": "ate:2026-11-30 08:00", "Validade-utc": "2026-11-30 11:00"},
                  "2026-11-25 00:00", "vencida"),
                 (uso, "2026-11-19 23:59", "ativa"), (uso, "2026-11-20 00:00", "vencida")]
        for troca, agora, esperado in casos:
            with self.subTest(troca=troca, agora=agora):
                self.assertEqual(self.estados(agora, A_1=concessao(**troca)), [esperado])

    def test_retirada_uso_fechamento_do_pedido_e_confirmacao(self):
        agora, pendente = "2026-11-18 07:00", concessao(**{"Estado-inicial": "pendente-confirmacao"})
        uso = concessao(**{"Validade": "uso-unico", "Validade-utc": "uso-unico", "Origem-da-validade": "quando der"})
        fim = concessao(**{"Origem-da-validade": "até o fim deste pedido"})
        casos = [(dict(R_1=evento("", {"Retira": "A-1"})), "retirada"), (dict(A_1=uso, U_A_1=""), "usada"),
                 (dict(A_1=uso, U_A_1_1=""), "ativa"), (dict(A_1=fim, F_v047=""), "vencida"), (dict(A_1=fim, F_v046=""), "ativa"),
                 (dict(F_v047=""), "ativa"), (dict(A_1=pendente), "pendente"), (dict(A_1=pendente, C_A_1=confirmacao()), "ativa"),
                 (dict(A_1=pendente, C_A_1=confirmacao("2026-11-18T00:00:00Z")), "pendente"),
                 (dict(A_1=pendente, C_A_1=confirmacao(Sha256="0" * 64)), "pendente"),
                 (dict(A_1=pendente, C_A_1=confirmacao(**{"Gravado-por": "f" * 64})), "pendente"),
                 (dict(A_1=pendente, C_A_1=confirmacao(Confirma="A-2")), "pendente"),
                 (dict(A_1=pendente, C_A_1=confirmacao("ontem")), "pendente"), (dict(lixo=""), "inativa")]
        for eventos, esperado in casos:
            with self.subTest(eventos=list(eventos), esperado=esperado):
                self.assertEqual(self.estados(agora, **{"A_1": concessao(), **eventos}), [esperado])


RAMO = "melhoria/pv-a2"
ITEM = "pode aplicar o rótulo afrouxa-regra no item PV-A2"
TIPOS = {"reviews": "review", "qa": "qa", "security": "revisao-seguranca"}  # os EXIGIDOS, pela pasta
MARCAS = ("nao", "nunca", "ainda", "antes", "depois", "so", "se", "exceto", "menos", "sem")  # lista de teste do item 5


def git(raiz, *args):
    env = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_", "PYTHON"))})
    env.update(GIT_CEILING_DIRECTORIES=str(Path(raiz).parent), GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    return subprocess.run(["git", "-C", str(raiz), "-c", "user.name=t", "-c", "user.email=t@t", *args], check=True,
                          capture_output=True, text=True, env=env, timeout=60).stdout.strip()


class ItemPresoAoCommit(unittest.TestCase):
    """Emenda PR-VERDE E1 (PV-A2): o alvo `item:` vale só para o `Commit` que é o head do `Ramo` com os pareceres aprovados."""

    def setUp(self):
        self.raiz = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.raiz)
        (self.raiz / fa.PASTA).mkdir(parents=True)
        git(self.raiz, "init", "-q", "-b", "develop")
        (self.raiz / ".git" / "info" / "exclude").write_text(".forge/\n", encoding="utf-8")  # o registro fica fora do git
        self.commitar("base.txt", "base")
        git(self.raiz, "switch", "-q", "-c", RAMO)
        self.revisado = self.commitar("codigo.txt", "item")
        for pasta in TIPOS:
            self.parecer(self.revisado, tipo=pasta)

    def commitar(self, nome, texto):
        (self.raiz / nome).parent.mkdir(parents=True, exist_ok=True)
        (self.raiz / nome).write_text(texto, encoding="utf-8")
        git(self.raiz, "add", "-A")
        git(self.raiz, "commit", "-q", "-m", nome)
        return git(self.raiz, "rev-parse", "HEAD")

    def parecer(self, commit, veredito="aprovado", tipo="reviews", ramo=RAMO):
        return self.commitar(f"docs/{tipo}/pv-a2.md", f"---\ntipo: {TIPOS.get(tipo, 'revisao-devops')}\npedido: v0\n"
                                                     f"branch: {ramo}\ncommit: {commit}\n"
                                                     f"escopo:\nparecer: {veredito}\n---\n# parecer\n")  # campo vazio

    def estado(self, corpo=ITEM, **troca):
        troca = {"Alvos": "item:PV-A2", "Commit": self.revisado, "Ramo": RAMO, "Sha256": fa.sha(corpo), **troca}
        (self.raiz / fa.PASTA / "A-1").write_text(concessao(corpo, **troca), encoding="utf-8")
        (_, _, _, est, motivo), = fa.concessoes(self.raiz, GRAVADOR, em("2026-11-18 07:00"))[0]
        return est, motivo

    def test_head_com_os_pareceres_aprovados_fica_ativa_e_o_parecer_pode_citar_o_sha_curto(self):
        self.assertEqual(self.estado(), ("ativa", ""))
        self.parecer(self.revisado[:7], tipo="qa")
        self.assertEqual(self.estado("pode aplicar o rótulo no itemPV-A2"), ("ativa", ""))

    def test_git_herdado_do_ambiente_nao_desvia_a_leitura(self):
        with unittest.mock.patch.dict(os.environ, {"GIT_DIR": str(self.raiz / "nada")}):
            self.assertEqual(self.estado(), ("ativa", ""))

    def test_alvo_sem_marcador_fora_da_frase_ou_com_ressalva_nao_nasce_ativa(self):
        casos = {"sem-marcador": "pode aplicar o rótulo no PV-A2", "outro-cartao": "pode aplicar o rótulo no item PV-A2X",
                 "cartao-maior": "pode aplicar o rótulo no item PV-A2.1",
                 "fora-da-frase": "o item PV-A2 está pronto. Pode aplicar o rótulo",
                 "frase-sem-ato": "pode mesclar o item PV-A2", "negacao": "não aplique o rótulo no item PV-A2",
                 "condicao": "pode aplicar o rótulo no item PV-A2 se o CI passar",
                 **{f"ressalva-{i}": f"{ITEM} {r}" for i, r in enumerate(("depois do CI verde", "antes da release",
                                                                          "sem a segurança", "só com o QA"))}}
        for caso, corpo in casos.items():
            with self.subTest(caso=caso):
                est, motivo = self.estado(corpo)
                self.assertEqual(est, "adulterada", motivo)
                ressalva = caso.startswith(("negacao", "condicao", "ressalva"))
                self.assertIn("ressalva" if ressalva else "sem item <CARTAO> na frase do ato", motivo)
                pendente = self.estado(corpo, **{"Estado-inicial": "pendente-confirmacao", "Motivo-da-pendencia": "x"})
                self.assertEqual(pendente, ("pendente", "x"))

    def test_vocabulario_fechado_sem_marca_aceita_data_e_hora_e_o_termo_do_ato_fora_do_nome_do_cartao(self):
        self.assertFalse(set(MARCAS) & fa.VOCABULARIO)
        self.assertEqual(self.estado(f"{ITEM} até 21/11 18:00, por favor"), ("ativa", ""))
        self.assertEqual(fa.fora_do_vocabulario("Pode aplicar, depois do CI 742"), ["742", "ci", "depois"])
        corpo = "pode mesclar o item ROTULO-1"  # o termo do ato só no nome do cartão não é ato
        self.assertEqual(self.estado(corpo, Alvos="item:ROTULO-1", Sha256=fa.sha(corpo)),
                         ("adulterada", "ativa sem item <CARTAO> na frase do ato"))

    def test_commit_abreviado_ausente_ramo_fora_da_forma_ou_ato_errado_e_adulterada(self):
        casos = {"abreviado": dict(Commit=self.revisado[:12], motivo="Commit não é sha de 40 caracteres"),
                 "maiusculo": dict(Commit=self.revisado.upper(), motivo="Commit não é sha de 40 caracteres"),
                 "sem-commit": dict(Commit=None, motivo="Commit não é sha de 40 caracteres"),
                 "opcao": dict(Ramo="-x", motivo="Ramo fora da forma"), "pontos": dict(Ramo="a..b", motivo="Ramo fora da forma"),
                 "sem-ramo": dict(Ramo=None, motivo="Ramo fora da forma"),
                 "ato": dict(Ato="merge-main", motivo="Ato do alvo item: não é rotulo-afrouxa-regra")}
        for caso, troca in casos.items():
            with self.subTest(caso=caso):
                motivo = troca.pop("motivo")
                self.assertEqual(self.estado(**troca), ("adulterada", motivo))

    def test_commit_que_nao_e_o_head_com_os_pareceres_aprovados_fica_inativa(self):
        git(self.raiz, "switch", "-q", "-c", "outra", "develop")
        de_outra = self.commitar("outra.txt", "x")
        git(self.raiz, "switch", "-q", RAMO)
        self.assertEqual(self.estado(Commit=de_outra), ("inativa", "Commit fora do Ramo"))
        self.assertEqual(self.estado(Ramo="outra", Commit=self.revisado), ("inativa", "Commit fora do Ramo"))
        self.assertEqual(self.estado(Ramo="nenhuma"), ("inativa", "Ramo sem ref no clone"))
        self.assertEqual(self.estado(Ramo="outra", Commit=de_outra), ("inativa", "Commit sem os pareceres aprovados nele"))
        antes = git(self.raiz, "rev-parse", "develop")
        self.assertEqual(self.estado(Commit=antes), ("inativa", "Commit não é o head: o Ramo muda depois dele"))
        casos = {"reprovado": dict(commit=self.revisado, veredito="reprovado", tipo="security"),
                 "outro-commit": dict(commit=antes, tipo="security"), "curto-demais": dict(commit=self.revisado[:6], tipo="qa"),
                 "sem-commit": dict(commit="", tipo="qa")}
        for caso, parecer in casos.items():
            with self.subTest(caso=caso):
                topo = git(self.raiz, "rev-parse", "HEAD")
                self.parecer(**parecer)
                self.assertEqual(self.estado(), ("inativa", "Commit sem os pareceres aprovados nele"))
                git(self.raiz, "reset", "-q", "--hard", topo)
        self.assertEqual(self.estado(), ("ativa", ""))
        self.commitar("codigo.txt", "mudou depois do parecer")
        self.assertEqual(self.estado(), ("inativa", "Commit não é o head: o Ramo muda depois dele"))

    def test_so_o_parecer_de_review_ou_codigo_renomeado_para_a_pasta_de_parecer_fica_inativa(self):
        git(self.raiz, "reset", "-q", "--hard", self.revisado)
        self.parecer(self.revisado)  # um aprovado só não basta: faltam QA e segurança (EXIGIDOS)
        self.assertEqual(self.estado(), ("inativa", "Commit sem os pareceres aprovados nele"))
        guarda = self.commitar("bin/guarda.py", f"---\ntipo: qa\nbranch: {RAMO}\ncommit: {self.revisado}\nparecer: aprovado\n---\n")
        for pasta in TIPOS:
            self.parecer(guarda, tipo=pasta)
        self.assertEqual(self.estado(Commit=guarda), ("ativa", ""))
        topo = self.commitar("bin/nota.md", f"---\nbranch: {RAMO}\n---\n")  # frontmatter do Ramo fora das pastas de parecer
        self.assertEqual(self.estado(Commit=guarda), ("inativa", "Commit não é o head: o Ramo muda depois dele"))
        git(self.raiz, "reset", "-q", "--hard", f"{topo}~1")
        git(self.raiz, "mv", "bin/guarda.py", "docs/qa/guarda.md")
        git(self.raiz, "commit", "-q", "-m", "mv")  # o código sai do Ramo com o nome de parecer
        self.assertEqual(self.estado(Commit=guarda), ("inativa", "Commit não é o head: o Ramo muda depois dele"))

    def test_ramo_sem_parecer_dele_fica_inativo_e_a_ref_do_origin_vale_antes_da_local(self):
        git(self.raiz, "reset", "-q", "--hard", self.revisado)
        self.parecer(self.revisado, ramo=f"{RAMO}-x")  # depois do Commit, parecer de outro ramo é mudança do Ramo
        self.assertEqual(self.estado(), ("inativa", "Commit não é o head: o Ramo muda depois dele"))
        outro = self.parecer(self.revisado, veredito="reprovado", tipo="devops", ramo=f"{RAMO}-x")  # o git grep acha pelo trecho
        for pasta in TIPOS:
            self.parecer(outro, tipo=pasta)
        self.assertEqual(self.estado(Commit=outro), ("ativa", ""))  # vale só o nome exato
        self.commitar("docs/qa/sem-frente.md", f"# parecer\nbranch: {RAMO}\ncommit: {outro}\nparecer: aprovado\n---\n")
        self.assertEqual(self.estado(Commit=outro), ("inativa", "Commit não é o head: o Ramo muda depois dele"))  # sem frontmatter
        git(self.raiz, "update-ref", f"refs/remotes/origin/{RAMO}", git(self.raiz, "rev-parse", "develop"))
        self.assertEqual(self.estado(), ("inativa", "Commit fora do Ramo"))

    def test_parecer_com_tipo_fora_da_sua_pasta_fica_inativa(self):
        git(self.raiz, "reset", "-q", "--hard", self.revisado)
        self.parecer(self.revisado)
        self.parecer(self.revisado, tipo="qa")
        falso = f"---\ntipo: revisao-seguranca\nbranch: {RAMO}\ncommit: {self.revisado}\nparecer: aprovado\n---\n"
        self.commitar("docs/qa/falso.md", falso)  # sonda S5 da segurança: o QA não supre o parecer de segurança
        self.assertEqual(self.estado(), ("inativa", "Parecer com tipo fora da sua pasta"))
        git(self.raiz, "rm", "-q", "docs/qa/falso.md")
        git(self.raiz, "commit", "-q", "-m", "rm")
        self.parecer(self.revisado, tipo="security")
        self.assertEqual(self.estado(), ("ativa", ""))
        self.commitar("docs/devops/sem-tipo.md", f"---\nbranch: {RAMO}\ncommit: {self.revisado}\nparecer: aprovado\n---\n")
        self.assertEqual(self.estado(), ("inativa", "Parecer com tipo fora da sua pasta"))  # tipo ausente não tem pasta


FIXA = {"Validade": "fixa", "Validade-utc": "fixa", "Origem-da-validade": "sem prazo", "Alvos": "fixo"}
UNICO = {"Validade": "uso-unico", "Validade-utc": "uso-unico"}


class AtosFixos(unittest.TestCase):
    """Emenda AUTORIZACOES-FIXAS da ADR 0018 (F1 e F3): `corte-diario` e `so-aperta-com-seguranca` só com alvo `fixo` e validade
    `fixa`, sem o teto da D1; os atos de antes não aceitam nenhum dos dois."""
    setUp = Ler.setUp
    estados = Ler.estados

    def corte(self, agora="2026-11-18 07:00"):
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            rc = fa.cmd_corte(self.raiz, {"gravador": GRAVADOR, "seguro": str}, em(agora))
        return rc, saida.getvalue()

    def test_fixa_nao_vence_e_para_so_pela_retirada(self):
        for ato in fa.FIXOS:
            with self.subTest(ato=ato):
                fixa = concessao(**FIXA, Ato=ato)
                self.assertEqual(self.estados("2036-11-18 07:00", A_1=fixa), ["ativa"])
                self.assertEqual(self.estados("2036-11-18 07:00", A_1=fixa, R_1=evento("", {"Retira": "A-1"})), ["retirada"])

    def test_alvo_fixo_e_validade_fixa_so_nos_atos_fixos_e_eles_so_com_eles(self):
        casos = [({**FIXA, "Ato": "rotulo-afrouxa-regra"}, "validade fixa"), ({**FIXA, "Ato": "merge-main"}, "validade fixa"),
                 ({"Alvos": "fixo"}, "alvo fixo"), ({"Validade": "fixa", "Validade-utc": "fixa"}, "validade fixa"),
                 ({**FIXA, "Ato": "corte-diario", **UNICO}, "validade fixa"),
                 ({**FIXA, "Ato": "corte-diario", "Validade-utc": "2026-11-18 11:00"}, "validade fixa"),
                 ({**FIXA, "Ato": "corte-diario", "Validade": "ate:2026-11-18 08:00"}, "validade fixa"),
                 ({**FIXA, "Ato": "so-aperta-com-seguranca", "Alvos": "pr:5"}, "alvo fixo")]
        for troca, motivo in casos:
            with self.subTest(troca=troca):
                self.assertEqual(self.estados("2026-11-18 07:00", A_1=concessao(**troca)), ["adulterada"])
                self.assertIn(motivo, fa.concessoes(self.raiz, GRAVADOR, em("2026-11-18 07:00"))[0][0][4])

    def test_corte_diz_a_corte_diario_ativa_mais_nova_e_sem_ela_rc_1(self):
        linha = "autorizacao: A-{} sha256 " + fa.sha(CORPO) + " · corte-diario · fixo\n"
        nenhuma = (1, "autorizacao: nenhuma corte-diario ativa\n")
        (self.pasta / "A-1").write_text(concessao(**FIXA, Ato="corte-diario"), encoding="utf-8")
        (self.pasta / "A-2").write_text(concessao(**FIXA, Ato="corte-diario", Id="A-2"), encoding="utf-8")
        self.assertEqual(self.corte(), (0, linha.format(2)))
        (self.pasta / "R-1").write_text(evento("", {"Retira": "A-2"}), encoding="utf-8")
        self.assertEqual(self.corte(), (0, linha.format(1)))
        (self.pasta / "lixo").write_text("", encoding="utf-8")  # evento ilegível: nenhuma fica ativa
        self.assertEqual(self.corte(), nenhuma)
        for eventos in ({"A_1": concessao(**FIXA, Ato="so-aperta-com-seguranca")},
                        {"A_1": concessao(**FIXA, Ato="corte-diario", Sha256="0" * 64)},
                        {"A_1": concessao(**FIXA, Ato="corte-diario", **{"Estado-inicial": "pendente-confirmacao"})}):
            with self.subTest(eventos=eventos):
                self.estados("2026-11-18 07:00", **eventos)
                self.assertEqual(self.corte(), nenhuma)

    def test_forge_check_autorizacao_corte(self):  # ler --ato corte-diario, sem mudar o forge-check (R-CONFORMIDADE)
        (self.pasta / "A-1").write_text(concessao(**FIXA, Ato="corte-diario"), encoding="utf-8")
        env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_", "PYTHON"))}
        env["GIT_CEILING_DIRECTORIES"] = str(self.raiz.parent)
        r = subprocess.run([sys.executable, "-I", str(BIN / "forge-check"), "--raiz", str(self.raiz), "autorizacao", "ler", "--ato", "corte-diario"],
                           capture_output=True, text=True, env=env, timeout=60)
        self.assertEqual((r.returncode, r.stdout), (0, f"autorizacao: A-1 sha256 {fa.sha(CORPO)} · corte-diario · fixo\n"), r.stderr)


def no_repositorio(raiz, origem):
    """`raiz` vira repositório git com o `origin` dado (sem config do sistema nem global; o teto do git na pasta-mãe)."""
    env = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_", "PYTHON"))})
    env.update(GIT_CEILING_DIRECTORIES=str(Path(raiz).parent), GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    for args in (("init", "-q"), ("remote", "add", "origin", origem)):
        subprocess.run(["git", "-C", str(raiz), *args], check=True, capture_output=True, env=env, timeout=60)


FORGE = json.loads((BIN.parent / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["repository"]


class RotuloPeloTime(unittest.TestCase):
    """Emenda ROTULO-PELO-TIME da ADR 0018: o ato `rotulo-pelo-time` é sem prazo, como os fixos, e só fica ativo no repositório do
    próprio Forge: `origin` igual ao `repository` do plugin.json e raiz que não é projeto. Nos outros projetos nada muda."""
    setUp = Ler.setUp
    estados = Ler.estados
    TIME = {**FIXA, "Ato": "rotulo-pelo-time"}

    def motivo(self):
        return fa.concessoes(self.raiz, GRAVADOR, em("2036-11-18 07:00"))[0][0][3:]

    def test_ativo_so_com_o_origin_do_forge_e_sem_vencer(self):
        self.assertEqual(self.estados("2036-11-18 07:00", A_1=concessao(**self.TIME)), ["inativa"])  # sem git: sem origin
        no_repositorio(self.raiz, FORGE.upper() + ".git")  # o GitHub não diferencia maiúsculas; `.git` final vale
        self.assertEqual(self.motivo(), ("ativa", ""))
        self.assertEqual(self.estados("2036-11-18 07:00", A_1=concessao(**self.TIME), R_1=evento("", {"Retira": "A-1"})), ["retirada"])

    def test_outro_origin_ou_projeto_deixa_inativo(self):
        self.estados("2036-11-18 07:00", A_1=concessao(**self.TIME))
        no_repositorio(self.raiz, FORGE + "-site")
        self.assertEqual(self.motivo(), ("inativa", "só vale no repositório do Forge: o origin é outro"))
        shutil.rmtree(self.raiz / ".git")
        no_repositorio(self.raiz, FORGE)
        (self.raiz / ".forge" / "versao").write_text("0.47.18\n", encoding="utf-8")  # projeto com o origin do Forge
        self.assertEqual(self.motivo(), ("inativa", "só vale no repositório do Forge: a raiz é projeto ou o plugin não diz o repositório"))
        self.assertEqual(self.estados("2036-11-18 07:00", A_1=concessao(**FIXA, Ato="corte-diario")), ["ativa"])  # os outros fixos não mudam

    def test_plugin_sem_repositorio_nao_faz_o_forge(self):
        self.estados("2036-11-18 07:00", A_1=concessao(**self.TIME))
        no_repositorio(self.raiz, FORGE)
        plugin = self.raiz / "plugin"
        (plugin / ".claude-plugin").mkdir(parents=True)
        for manifesto in ('{"name": "forge"}', "[]", "{"):
            with self.subTest(manifesto=manifesto), unittest.mock.patch.object(fa, "__file__", str(plugin / "bin" / "x.py")):
                (plugin / ".claude-plugin" / "plugin.json").write_text(manifesto, encoding="utf-8")
                self.assertEqual(self.motivo(), ("inativa", "só vale no repositório do Forge: a raiz é projeto ou o plugin não diz o repositório"))

    def test_so_com_alvo_fixo_e_validade_fixa(self):
        no_repositorio(self.raiz, FORGE)
        for troca in ({"Alvos": "pr:5"}, UNICO, {"Validade-utc": "2026-11-18 11:00"}):
            with self.subTest(troca=troca):
                self.assertEqual(self.estados("2026-11-18 07:00", A_1=concessao(**{**self.TIME, **troca})), ["adulterada"])

    def test_ler_ato_diz_a_ativa_e_sem_ela_rc_1(self):
        (self.pasta / "A-1").write_text(concessao(**self.TIME), encoding="utf-8")
        a = argparse.Namespace(acao="ler", ato="rotulo-pelo-time")
        for origem, esperado in ((FORGE + "-site", (1, "autorizacao: nenhuma rotulo-pelo-time ativa\n")),
                                 (FORGE, (0, f"autorizacao: A-1 sha256 {fa.sha(CORPO)} · rotulo-pelo-time · fixo\n"))):
            with self.subTest(origem=origem):
                shutil.rmtree(self.raiz / ".git", ignore_errors=True)
                no_repositorio(self.raiz, origem)
                saida = io.StringIO()
                with contextlib.redirect_stdout(saida):
                    rc = fa.executar(a, self.raiz, {"gravador": GRAVADOR, "seguro": str})
                self.assertEqual((rc, saida.getvalue()), esperado)


if __name__ == "__main__":
    unittest.main()
