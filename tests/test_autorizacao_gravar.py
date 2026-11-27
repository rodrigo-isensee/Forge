"""ADR 0018, G1.2: o `gravar` da autorização do dono (`bin/forge_autorizacao.py`, `forge-check autorizacao gravar`).

O corpo gravado é a mensagem inteira digitada pelo dono, lida da transcrição; ato, alvos, validade e pendência saem do texto
todo, e a concessão nasce `ativa` só quando o leitor (G1.1) também a lê `ativa`. PV-A2: a concessão solta de alvo `item:`
(sem marcador, fora da frase do ato, com ressalva ou com `Commit` fora do head com os pareceres) nunca nasce ativa."""
import argparse
import contextlib
import datetime
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
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_manutencao  # noqa: E402

BIN = Path(__file__).resolve().parent.parent / "bin"
GRAVADOR = hashlib.sha256((BIN / "forge-check").read_bytes()).hexdigest()
UTC = datetime.timezone.utc
SESSAO = "0b0c0d0e-0000-4000-8000-000000000001"
FALA = "2026-11-18T00:00:00.000Z"  # 17/11 21:00 em São Paulo
AGORA = datetime.datetime(2026, 11, 18, 0, 1, tzinfo=UTC)  # o gravar roda 1 min depois da fala
U1 = "11111111-1111-4111-8111-111111111111"
RAMO = "melhoria/pv-a2"
MARCAS = ("nao", "nunca", "ainda", "antes", "depois", "so", "se", "exceto", "menos", "sem")  # lista de teste do item 5
CASA_TROCADA = ("import pwd, runpy, sys, types; casa = sys.argv.pop(1); "
                "pwd.getpwuid = lambda uid: types.SimpleNamespace(pw_dir=casa); sys.argv = sys.argv[1:]; "
                "runpy.run_path(sys.argv[0], run_name='__main__')")  # o forge-check inteiro, com a casa do banco de senhas trocada
fa = None  # carregado em setUpModule: na base, sem o gravar, cada teste cai por conta própria (R-QA)


def setUpModule():
    global fa
    spec = importlib.util.spec_from_file_location("forge_autorizacao", BIN / "forge_autorizacao.py")
    fa = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fa)


def registro(texto, uuid=U1, **troca):
    return {"type": "user", "uuid": uuid, "sessionId": SESSAO, "timestamp": FALA, "origin": {"kind": "human"},
            "message": {"role": "user", "content": texto}, **troca}


def resumo_de_compactacao(texto, uuid=U1):
    """Forma real do resumo de compactação (texto do modelo): sem `origin`, com as duas marcas e `isSidechain` falso."""
    r = registro(texto, uuid=uuid, isCompactSummary=True, isVisibleInTranscriptOnly=True, isSidechain=False, promptId="p")
    del r["origin"]
    return r


def git(raiz, *args):
    env = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_", "PYTHON"))})
    env.update(GIT_CEILING_DIRECTORIES=str(Path(raiz).parent), GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    return subprocess.run(["git", "-C", str(raiz), "-c", "user.name=t", "-c", "user.email=t@t", *args], check=True,
                          capture_output=True, text=True, env=env, timeout=60).stdout.strip()


class Base(unittest.TestCase):
    def setUp(self):
        self.raiz = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.raiz)
        self.projetos = self.raiz / ".claude" / "projects"  # onde o Claude Code grava a transcrição (casa do dono = raiz)
        self.transcricao = self.projetos / "-raiz" / f"{SESSAO}.jsonl"
        self.transcricao.parent.mkdir(parents=True)
        ambiente = mock.patch.dict(os.environ, {"HOME": str(self.raiz / "outra"), "CLAUDE_CODE_SESSION_ID": SESSAO})
        ambiente.start()
        self.addCleanup(ambiente.stop)
        casa = mock.patch.object(fa, "casa_do_dono", lambda: self.raiz)  # A4: a casa vem do banco de senhas, nunca do HOME
        casa.start()
        self.addCleanup(casa.stop)

    def falar(self, *registros):
        self.transcricao.write_text("".join(json.dumps(r) + "\n" for r in registros), encoding="utf-8")

    def gravar(self, texto=None, ato="rotulo-afrouxa-regra", alvos="pr:5", uuid=U1, ramo="", pedido="v0478", agora=AGORA,
               pedidos=("v0478",)):
        if texto is not None:
            self.falar({"type": "assistant", "uuid": "x"}, registro(texto))
        a = argparse.Namespace(mensagem=uuid, transcricao=str(self.transcricao), ato=ato, alvos=alvos, ramo=ramo, pedido=pedido)
        ctx = {"gravador": GRAVADOR, "seguro": str, "pedido_existe": lambda p: p in pedidos}
        if pedidos is None:  # sem como conferir o pedido no registro (A6)
            del ctx["pedido_existe"]
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            rc = fa.cmd_gravar(self.raiz, a, ctx, agora)
        return rc, saida.getvalue()

    def forge_check(self, *args, uuid=U1, casa=None):
        """`forge-check autorizacao gravar` noutro processo, com o ambiente desta sessão (sem GIT_, FORGE_ e PYTHON herdados);
        `casa` troca só a pasta do usuário no banco de senhas (`pwd`), nunca o HOME (A4)."""
        env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_", "PYTHON"))}
        env["GIT_CEILING_DIRECTORIES"] = str(self.raiz.parent)
        cmd = [sys.executable, "-I", str(BIN / "forge-check")]
        if casa is not None:
            cmd = [sys.executable, "-I", "-c", CASA_TROCADA, str(casa), str(BIN / "forge-check")]
        return subprocess.run([*cmd, "--raiz", str(self.raiz), "autorizacao", "gravar", "--mensagem", uuid,
                               "--transcricao", str(self.transcricao), "--ato", "merge-main", "--alvos", "versao:0.47.3", *args],
                              capture_output=True, text=True, env=env, timeout=60)

    def lidas(self, agora="2026-11-18 00:01"):
        momento = datetime.datetime.strptime(agora, "%Y-%m-%d %H:%M").replace(tzinfo=UTC)
        return fa.concessoes(self.raiz, GRAVADOR, momento)[0]

    def gravada(self, texto, **kw):
        rc, saida = self.gravar(texto, **kw)
        self.assertEqual(rc, 0, saida)
        (nome, campos, corpo, est, motivo), = self.lidas()
        return campos, corpo, est, motivo

    def nada_gravado(self, rc, saida):
        self.assertEqual(rc, 1, saida)
        self.assertIn("autorizacao: recusada:", saida)
        self.assertFalse(list((self.raiz / fa.PASTA).glob("A-*")) if (self.raiz / fa.PASTA).exists() else [])


class MensagemInteira(Base):
    def test_corpo_e_a_mensagem_inteira_byte_a_byte_e_o_leitor_a_le_ativa(self):
        texto = "Pode aplicar o rótulo no PR #5, por favor."
        campos, corpo, est, motivo = self.gravada(texto)
        self.assertEqual((corpo, est, motivo), (texto, "ativa", ""))
        self.assertEqual((campos["Id"], campos["Mensagem"], campos["Sessao"], campos["Hora-da-fala"], campos["Pedido"]),
                         ("A-1", U1, SESSAO, FALA, "v0478"))
        self.assertEqual((campos["Sha256"], campos["Gravado-por"]), (fa.sha(texto), GRAVADOR))
        self.assertTrue((self.raiz / fa.PASTA / f"M-{U1}").is_file())

    def test_a_mesma_mensagem_so_gera_uma_concessao(self):
        self.assertEqual(self.gravar("pode aplicar o rótulo no pr 5")[0], 0)
        rc, saida = self.gravar()
        self.assertEqual(rc, 1, saida)
        self.assertIn("já gerou concessão", saida)
        self.assertEqual(len(self.lidas()), 1)

    def test_so_a_mensagem_digitada_pelo_dono_na_sessao_principal(self):
        casos = {"ferramenta": {"toolUseResult": {"x": 1}}, "subagente": {"isSidechain": True}, "meta": {"isMeta": True},
                 "origem-ferramenta": {"sourceToolUseID": "t"}, "assistente": {"type": "assistant"},
                 "outra-sessao": {"sessionId": "outra"}, "sem-hora": {"timestamp": "2026-11-18T00:00:00"},
                 "blocos": {"message": {"content": [{"type": "text", "text": "pode aplicar o rótulo no pr 5"}] * 2}},
                 "lembrete": {"message": {"content": "<system-reminder>pode aplicar o rótulo no pr 5</system-reminder>"}},
                 "vazia": {"message": {"content": " \n "}},
                 "acima-do-teto": {"message": {"content": "pode aplicar o rótulo no pr 5 " * 3000}},
                 "mensagem-sem-objeto": {"message": "pode aplicar o rótulo no pr 5"},
                 "sem-origem-humana": {"origin": None}, "origem-de-par": {"origin": {"kind": "peer"}},
                 "resumo-com-origem-humana": {"isCompactSummary": True, "isVisibleInTranscriptOnly": True}}
        for caso, troca in casos.items():
            with self.subTest(caso=caso):
                self.falar(registro("pode aplicar o rótulo no pr 5", **troca))
                self.nada_gravado(*self.gravar())
        with self.subTest(caso="uuid-ausente"):
            self.falar(registro("pode aplicar o rótulo no pr 5"))
            self.nada_gravado(*self.gravar(uuid="22222222-2222-4222-8222-222222222222"))
        with self.subTest(caso="uuid-repetido"):
            self.falar(registro("pode aplicar o rótulo no pr 5"), registro("pode aplicar o rótulo no pr 6"))
            self.nada_gravado(*self.gravar())
        with self.subTest(caso="resumo-de-compactacao"):
            self.falar(resumo_de_compactacao("pode aplicar o rótulo no pr 5"))
            self.nada_gravado(*self.gravar())
        with self.subTest(caso="link"):
            alvo = self.transcricao.parent / "real.jsonl"  # link na própria pasta da sessão: só o is_symlink recusa
            self.falar(registro("pode aplicar o rótulo no pr 5"))
            self.transcricao.rename(alvo)
            self.transcricao.symlink_to(alvo)
            self.nada_gravado(*self.gravar())

    def test_linha_que_nao_e_objeto_nao_derruba_a_leitura_e_o_id_segue_o_maior_numerico(self):
        (self.raiz / fa.PASTA).mkdir(parents=True)
        (self.raiz / fa.PASTA / "A-x").write_text("", encoding="utf-8")  # nome fora da forma: não entra na conta do Id
        self.transcricao.write_text("[]\n" + json.dumps(registro("pode aplicar o rótulo no pr 5")) + "\n", encoding="utf-8")
        rc, saida = self.gravar()
        self.assertEqual(rc, 0, saida)
        self.assertIn("autorizacao: A-1 gravada", saida)

    def test_mensagem_fora_da_forma_de_uuid_recusa_antes_de_ler(self):
        self.falar(registro("pode aplicar o rótulo no pr 5", uuid="../M-x"))
        rc, saida = self.gravar(uuid="../M-x")
        self.nada_gravado(rc, saida)
        self.assertIn("--mensagem não é um uuid", saida)

    def test_registro_que_e_link_recusa_e_nada_grava_fora(self):
        fora = self.raiz / "fora"
        fora.mkdir()
        for link in (self.raiz / ".forge", self.raiz / fa.PASTA):
            with self.subTest(link=link.name):
                shutil.rmtree(self.raiz / ".forge", ignore_errors=True)
                (self.raiz / ".forge").unlink(missing_ok=True)
                link.parent.mkdir(exist_ok=True)
                link.symlink_to(fora, target_is_directory=True)
                rc, saida = self.gravar("pode aplicar o rótulo no pr 5")
                self.assertEqual(rc, 1, saida)
                self.assertIn("não é pasta comum", saida)
                self.assertEqual(list(fora.iterdir()), [])

    def test_um_bloco_de_texto_vale_como_a_mensagem(self):
        self.falar(registro(None, message={"content": [{"type": "text", "text": "pode aplicar o rótulo no pr 5"}]}))
        rc, saida = self.gravar()
        self.assertEqual(rc, 0, saida)
        self.assertEqual(self.lidas()[0][2], "pode aplicar o rótulo no pr 5")

    def test_nao_existe_opcao_de_texto_no_comando(self):
        env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_", "PYTHON"))}
        env["GIT_CEILING_DIRECTORIES"] = str(self.raiz.parent)
        for opcao in ("--palavras", "--texto", "--corpo"):
            with self.subTest(opcao=opcao):
                r = subprocess.run([sys.executable, "-I", str(BIN / "forge-check"), "--raiz", str(self.raiz), "autorizacao",
                                    "gravar", "--mensagem", U1, "--transcricao", str(self.transcricao), "--ato", "merge-main",
                                    "--alvos", "versao:0.47.3", "--pedido", "v0478", opcao, "pode mesclar a main 0.47.3"],
                                   capture_output=True, text=True, env=env, timeout=60)
                self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                self.assertFalse((self.raiz / fa.PASTA).exists())

    def test_forge_check_autorizacao_gravar_grava_o_que_o_ler_aceita(self):
        agora = datetime.datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        self.falar(registro("pode mesclar a main 0.47.3", timestamp=agora))
        r = self.forge_check("--pedido", "v0478", casa=self.raiz)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("autorizacao: A-1 gravada · ativa", r.stdout)
        self.assertEqual(self.lidas(datetime.datetime.now(UTC).strftime("%Y-%m-%d %H:%M"))[0][1]["Gravado-por"], GRAVADOR)


class TranscricaoDaSessaoEmCurso(Base):
    """S4 da segurança: só a transcrição da sessão em curso, na pasta onde o Claude Code a grava, serve ao gravar."""

    def recusada(self, transcricao, sessao=SESSAO):
        transcricao.parent.mkdir(parents=True, exist_ok=True)
        transcricao.write_text(json.dumps(registro("pode aplicar o rótulo no pr 5", sessionId=sessao)) + "\n", encoding="utf-8")
        self.transcricao = transcricao
        rc, saida = self.gravar()
        self.nada_gravado(rc, saida)
        self.assertIn("não é o .jsonl comum da sessão em curso", saida)

    def test_transcricao_fora_da_pasta_do_claude_code_recusa(self):
        self.recusada(self.raiz / "tmp" / "sessao" / f"{SESSAO}.jsonl")  # a que um agente escreve em $TMPDIR

    def test_transcricao_de_outra_sessao_recusa(self):
        outra = "0b0c0d0e-0000-4000-8000-000000000002"
        self.recusada(self.projetos / "-raiz" / f"{outra}.jsonl", sessao=outra)

    def test_sem_sessao_em_curso_no_ambiente_recusa(self):
        del os.environ["CLAUDE_CODE_SESSION_ID"]
        self.recusada(self.transcricao)

    def test_pasta_do_projeto_que_e_link_para_fora_recusa(self):
        fora = self.raiz / "fora"
        fora.mkdir()
        (self.projetos / "-link").symlink_to(fora, target_is_directory=True)
        self.recusada(self.projetos / "-link" / f"{SESSAO}.jsonl")

    def test_home_e_sessao_do_chamador_nao_escolhem_a_transcricao(self):
        """S4 da segurança (f88a2a8e, A4): o agente escreve a transcrição numa pasta sua e aponta o HOME e a sessão para ela; a
        casa vem do banco de senhas e recusa. A mesma transcrição, com a casa do banco de senhas nela, grava (o controle)."""
        agora = datetime.datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        self.falar(registro("pode mesclar a main 0.47.3", timestamp=agora))
        os.environ["HOME"] = str(self.raiz)
        r = self.forge_check("--pedido", "v0478")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("não é o .jsonl comum da sessão em curso", r.stdout)
        self.assertFalse((self.raiz / fa.PASTA).exists())
        self.assertEqual(self.forge_check("--pedido", "v0478", casa=self.raiz).returncode, 0)


class VoltaDosPortoes(Base):
    """E90.10: recomendados da segurança f88a2a8e (A3, A5, A6) e A2 do review 44b4a481."""

    def test_fala_no_futuro_escrita_na_pasta_nao_fica_ativa_no_ler(self):
        """A3: o `ler` confere a `Hora-da-fala` contra agora, como o `gravar`; no próprio instante da fala ela vale."""
        self.gravada("pode aplicar o rótulo no pr 5")
        (_, _, _, est, motivo), = self.lidas("2026-11-17 23:59")
        self.assertEqual((est, motivo), ("adulterada", "Hora-da-fala no futuro"))
        self.assertEqual(self.lidas("2026-11-18 00:00")[0][3:], ("ativa", ""))

    def test_emoji_ou_negacao_em_outra_escrita_nasce_pendente(self):
        """A5 (S5, S6): o que não é letra latina, dígito ou pontuação comum conta como fora do vocabulário."""
        for i, texto in enumerate(("pode aplicar o rótulo no pr 5 \U0001F6AB\U0001F6AB", "pode aplicar o rótulo no pr 5 нет")):
            with self.subTest(texto=texto):
                uuid = f"{i:08d}-6666-4000-8000-000000000000"
                self.falar(registro(texto, uuid=uuid))
                self.assertEqual(self.gravar(uuid=uuid)[0], 0)
                campos, _, est, motivo = self.lidas()[-1][1:]
                self.assertEqual((campos["Estado-inicial"], est), ("pendente-confirmacao", "pendente"))
                self.assertIn("fora do vocabulário", motivo)

    def test_ponto_final_logo_depois_do_alvo_deixa_pendente(self):
        """E90.14 (decisão 3a do dono): "pr 5." e "0.47.3." seguem pendentes, como na base; "pr 5.1" não é o pr 5."""
        for i, (texto, ato, alvos, esperado) in enumerate((
                ("pode aplicar o rótulo no PR 5.", "rotulo-afrouxa-regra", "pr:5", "pendente"),
                ("pode mesclar a main 0.47.3.", "merge-main", "versao:0.47.3", "pendente"),
                ("pode aplicar o rótulo no pr 5.1", "rotulo-afrouxa-regra", "pr:5", "pendente"))):
            with self.subTest(texto=texto):
                uuid = f"{i:08d}-7777-4000-8000-000000000000"
                self.falar(registro(texto, uuid=uuid))
                self.assertEqual(self.gravar(ato=ato, alvos=alvos, uuid=uuid)[0], 0)
                self.assertEqual(self.lidas()[-1][3], esperado)

    def test_fim_deste_pedido_so_com_o_pedido_aberto(self):
        """A6 (S7): pedido fora do registro, com o `F-<Pedido>` gravado ou sem como conferir nasce pendente; o aberto, ativa."""
        texto = "pode aplicar o rótulo no pr 5 até o fim deste pedido"
        casos = (("nunca-fecha", ("v0478",), False, "pendente-confirmacao"), ("v0478", None, False, "pendente-confirmacao"),
                 ("v0478", ("v0478",), True, "pendente-confirmacao"), ("v0478", ("v0478",), False, "ativa"))
        for i, (pedido, pedidos, fechado, esperado) in enumerate(casos):
            with self.subTest(pedido=pedido, pedidos=pedidos, fechado=fechado):
                shutil.rmtree(self.raiz / fa.PASTA, ignore_errors=True)
                if fechado:
                    (self.raiz / fa.PASTA).mkdir(parents=True)
                    (self.raiz / fa.PASTA / f"F-{pedido}").write_text("")
                uuid = f"{i:08d}-8888-4000-8000-000000000000"
                self.falar(registro(texto, uuid=uuid))
                rc, saida = self.gravar(uuid=uuid, pedido=pedido, pedidos=pedidos)
                self.assertEqual(rc, 0, saida)
                campos = self.lidas()[-1][1]
                self.assertEqual(campos["Estado-inicial"], esperado)
                if esperado != "ativa":
                    self.assertEqual(campos["Motivo-da-pendencia"], "pedido inexistente ou fechado")  # sem o "nenhum" antes

    def test_forge_check_confere_o_pedido_no_registro(self):
        """A6 de ponta a ponta: o `forge-check` acha `docs/pedidos/<id>.md` da raiz; o pedido sem arquivo nasce pendente."""
        (self.raiz / "docs" / "pedidos").mkdir(parents=True)
        (self.raiz / "docs" / "pedidos" / "v0478.md").write_text("# Pedido v0478\n", encoding="utf-8")
        agora = datetime.datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        for i, (pedido, esperado) in enumerate((("v0478", "ativa"), ("nunca-fecha", "pendente-confirmacao"))):
            with self.subTest(pedido=pedido):
                uuid = f"{i:08d}-9999-4000-8000-000000000000"
                self.falar(registro("pode mesclar a main 0.47.3 até o fim deste pedido", uuid=uuid, timestamp=agora))
                r = self.forge_check("--pedido", pedido, uuid=uuid, casa=self.raiz)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertIn(f"gravada · {esperado}", r.stdout)


class EscopoPeloTextoTodo(Base):
    def test_sem_termo_de_ato_ou_com_ato_diferente_recusa_e_nada_grava(self):
        self.nada_gravado(*self.gravar("pode aplicar no pr 5"))
        self.nada_gravado(*self.gravar("pode mesclar a main 0.47.3"))

    def test_recorte_ou_ressalva_nasce_pendente_com_o_motivo(self):
        casos = {"negacao": ("não mescle a main 0.47.3 ainda", "merge-main", "versao:0.47.3", "fora do vocabulário"),
                 "condicao": ("pode mesclar a main 0.47.3 só se o CI passar", "merge-main", "versao:0.47.3", "fora do vocabulário"),
                 "dois-atos": ("pode aplicar o rótulo no pr 5 e mesclar a main", "rotulo-afrouxa-regra", "pr:5", "mais de um ato"),
                 "alvo-declarado-a-mais": ("pode aplicar o rótulo no pr 5", "rotulo-afrouxa-regra", "pr:5, pr:6", "alvos do texto"),
                 "alvo-generico": ("pode aplicar o rótulo neste plano", "rotulo-afrouxa-regra", "pr:5", "alvos do texto"),
                 "numero-solto": ("pode aplicar o rótulo no 5", "rotulo-afrouxa-regra", "pr:5", "alvos do texto"),
                 "fora-da-frase": ("o pr 5 está pronto. pode aplicar o rótulo", "rotulo-afrouxa-regra", "pr:5", "fora da frase"),
                 "validade-em-conflito": ("pode aplicar o rótulo no pr 5 hoje até sexta", "rotulo-afrouxa-regra", "pr:5",
                                          "mais de um termo de validade"),
                 "amanha-sem-ate": ("pode aplicar o rótulo no pr 5 amanhã", "rotulo-afrouxa-regra", "pr:5", "fora do mapa")}
        for i, (caso, (texto, ato, alvos, motivo)) in enumerate(casos.items()):
            with self.subTest(caso=caso):
                uuid = f"{i:08d}-0000-4000-8000-000000000000"
                self.falar(registro(texto, uuid=uuid))
                rc, saida = self.gravar(ato=ato, alvos=alvos, uuid=uuid)
                self.assertEqual(rc, 0, saida)
                campos, _, est, lido = self.lidas()[-1][1:]
                self.assertEqual((campos["Estado-inicial"], est), ("pendente-confirmacao", "pendente"))
                self.assertIn(motivo, lido)

    def test_toda_marca_de_negacao_ou_condicao_manda_a_pendencia(self):
        self.assertFalse(set(MARCAS) & fa.VOCABULARIO)
        for i, marca in enumerate(MARCAS):
            with self.subTest(marca=marca):
                uuid = f"{i:08d}-1111-4000-8000-000000000000"
                self.falar(registro(f"pode aplicar o rótulo no pr 5 {marca}", uuid=uuid))
                self.assertEqual(self.gravar(uuid=uuid)[0], 0)
                self.assertEqual(self.lidas()[-1][3], "pendente")

    def test_alvos_pr_e_versao_com_marcador(self):
        for i, (texto, ato, alvos) in enumerate((("pode aplicar o rótulo no pr #5, pull 6", "rotulo-afrouxa-regra", "pr:5, pr:6"),
                                                  ("pode mesclar a main 0.47.3", "merge-main", "versao:0.47.3"))):
            with self.subTest(texto=texto):
                uuid = f"{i:08d}-2222-4000-8000-000000000000"
                self.falar(registro(texto, uuid=uuid))
                self.assertEqual(self.gravar(ato=ato, alvos=alvos, uuid=uuid)[0], 0)
                self.assertEqual(self.lidas()[-1][3:], ("ativa", ""))


class Validade(Base):
    """Item 6 e D1, fala às 00:00 UTC de 18/11. Esta etapa não lê o fuso do dono: o prazo local (data, dia da semana, "esta
    noite") nasce pendente com uso único (A2 da segurança); o tempo absoluto (48 h e o fim do pedido) segue valendo."""

    def validade(self, texto):
        campos, _, est, _ = self.gravada(f"pode aplicar o rótulo no pr 5 {texto}".strip())
        return campos["Validade"], campos["Validade-utc"], campos["Origem-da-validade"], campos["Fuso"], est

    def test_mapa_fechado_do_termo(self):
        dois_dias, sete_dias, uso = ("ate:2026-11-20 00:00", "2026-11-20 00:00"), ("ate:2026-11-25 00:00", "2026-11-25 00:00"), \
            ("uso-unico", "uso-unico")
        ativa, pendente = ("UTC", "ativa"), ("UTC", "pendente")
        casos = {"": (*dois_dias, "sem termo", *ativa), "hoje": (*dois_dias, "hoje", *ativa), "hj": (*dois_dias, "hj", *ativa),
                 "até amanhã": (*dois_dias, "ate amanha", *ativa),
                 "até o fim deste pedido": (*sete_dias, "ate o fim deste pedido", *ativa),
                 "esta noite": (*uso, "esta noite", *pendente), "até sexta-feira": (*uso, "ate sexta", *pendente),
                 "até a sexta": (*uso, "ate sexta", *pendente), "até 19/11 12:00": (*uso, "ate 19/11 12:00", *pendente),
                 "até 30/11": (*uso, "ate 30/11", *pendente)}
        for texto, esperado in casos.items():
            with self.subTest(texto=texto):
                shutil.rmtree(self.raiz / fa.PASTA, ignore_errors=True)
                self.assertEqual(self.validade(texto), esperado)

    def test_prazo_local_ja_passado_nao_nasce_ativa(self):
        """S2 da segurança: "até 16/11" dito em 18/11 nasce pendente, com o motivo, e o leitor não a vê ativa."""
        campos, _, est, motivo = self.gravada("pode aplicar o rótulo no pr 5 até 16/11")
        self.assertEqual((campos["Estado-inicial"], est), ("pendente-confirmacao", "pendente"))
        self.assertIn("prazo local sem fuso nesta etapa", motivo)

    def test_hora_da_fala_no_futuro_ou_mais_velha_que_48_h_recusa(self):
        """S3 da segurança: carimbo de 2030, 1 s no futuro ou de 48 h e 1 min atrás recusa; 48 h exatas ainda valem."""
        for i, (agora, aceita) in enumerate(((datetime.datetime(2030, 1, 1, tzinfo=UTC) - datetime.timedelta(days=1), None),
                                             (AGORA - datetime.timedelta(minutes=1, seconds=1), False),
                                             (AGORA + datetime.timedelta(hours=48, minutes=-1), True),
                                             (AGORA + datetime.timedelta(hours=48), False))):
            with self.subTest(agora=agora):
                shutil.rmtree(self.raiz / fa.PASTA, ignore_errors=True)
                fala = "2030-01-01T00:00:00.000Z" if aceita is None else FALA
                self.falar(registro("pode aplicar o rótulo no pr 5", uuid=f"{i:08d}-5555-4000-8000-000000000000", timestamp=fala))
                rc, saida = self.gravar(uuid=f"{i:08d}-5555-4000-8000-000000000000", agora=agora)
                if aceita:
                    self.assertEqual(rc, 0, saida)
                else:
                    self.nada_gravado(rc, saida)
                    self.assertIn("Hora-da-fala no futuro ou fora da sessão", saida)

    def test_conflito_nasce_pendente_e_vale_o_fim_mais_cedo(self):
        for texto, fim in {"hoje até o fim deste pedido": "2026-11-20 00:00", "hoje esta noite": "uso-unico",
                           "amanhã": "uso-unico"}.items():  # termo fora do mapa: uso único
            with self.subTest(texto=texto):
                shutil.rmtree(self.raiz / fa.PASTA, ignore_errors=True)
                validade = self.validade(texto)
                self.assertEqual((validade[1], validade[4]), (fim, "pendente"))


class ConcessaoSolta(Base):
    """Oráculo `concessao-solta` (PV-A2): o alvo `item:` só nasce ativo preso ao head do Ramo com os pareceres aprovados."""
    ITEM = "pode aplicar o rótulo afrouxa-regra no item PV-A2"

    def setUp(self):
        super().setUp()
        git(self.raiz, "init", "-q", "-b", "develop")
        (self.raiz / ".git" / "info" / "exclude").write_text(".forge/\n.claude/\n", encoding="utf-8")
        self.commitar("base.txt", "base")
        git(self.raiz, "switch", "-q", "-c", RAMO)
        self.revisado = self.commitar("codigo.txt", "item")
        for pasta, tipo in {"reviews": "review", "qa": "qa", "security": "revisao-seguranca"}.items():
            self.commitar(f"docs/{pasta}/pv-a2.md", f"---\ntipo: {tipo}\nbranch: {RAMO}\ncommit: {self.revisado[:8]}\n"
                                                     "parecer: aprovado\n---\n")

    def commitar(self, nome, texto):
        (self.raiz / nome).parent.mkdir(parents=True, exist_ok=True)
        (self.raiz / nome).write_text(texto, encoding="utf-8")
        git(self.raiz, "add", "-A")
        git(self.raiz, "commit", "-q", "-m", nome)
        return git(self.raiz, "rev-parse", "HEAD")

    def item(self, texto=ITEM, uuid=U1):
        self.falar(registro(texto, uuid=uuid))
        return self.gravar(alvos="item:PV-A2", ramo=RAMO, uuid=uuid)

    def test_head_com_os_pareceres_grava_o_commit_inteiro_e_nasce_ativa(self):
        self.assertEqual(self.item()[0], 0)
        (_, campos, _, est, motivo), = self.lidas()
        self.assertEqual((campos["Commit"], campos["Ramo"], est, motivo), (self.revisado, RAMO, "ativa", ""))

    def test_sem_marcador_fora_da_frase_ou_com_ressalva_nunca_nasce_ativa(self):
        casos = ("pode aplicar o rótulo no PV-A2", "o item PV-A2 está pronto. Pode aplicar o rótulo",
                 "pode aplicar o rótulo no item PV-A2 se o CI passar", "não aplique o rótulo no item PV-A2",
                 "pode aplicar o rótulo no item PV-A2X")
        for i, texto in enumerate(casos):
            with self.subTest(texto=texto):
                uuid = f"{i:08d}-3333-4000-8000-000000000000"
                rc, saida = self.item(texto, uuid)
                self.assertEqual(rc, 0, saida)
                self.assertEqual(self.lidas()[-1][3], "pendente")

    def test_commit_fora_do_head_com_os_pareceres_recusa_e_nada_grava(self):
        self.commitar("codigo.txt", "mudou depois dos pareceres")
        rc, saida = self.item()
        self.nada_gravado(rc, saida)
        self.assertIn("Commit não é o head", saida)

    def test_commit_do_parecer_que_nao_e_sha_ou_nao_existe_nao_vira_ref(self):
        for i, commit in enumerate(("HEAD", "deadbeef0")):
            with self.subTest(commit=commit):
                self.commitar("docs/reviews/pv-a2.md", f"---\ntipo: review\nbranch: {RAMO}\ncommit: {commit}\nparecer: aprovado\n---\n")
                rc, saida = self.item(uuid=f"{i:08d}-4444-4000-8000-000000000000")
                self.nada_gravado(rc, saida)
                self.assertIn("Commit não é sha de 40 caracteres", saida)

    def test_ramo_sem_pareceres_ou_sem_ramo_recusa(self):
        self.nada_gravado(*self.gravar(self.ITEM, alvos="item:PV-A2", ramo="melhoria/outro"))
        self.nada_gravado(*self.gravar(alvos="item:PV-A2", ramo=""))
        self.nada_gravado(*self.gravar(alvos="item:PV-A2", ramo="-c"))


class AtosFixos(Base):
    """Emenda AUTORIZACOES-FIXAS da ADR 0018 (F1 e F2): o texto limpo grava `fixa` e `ativa`; alvo marcado, termo de validade,
    ressalva ou outro ato no texto nascem pendentes; o vocabulário novo vale só para os atos fixos."""

    def lida(self, i, texto, ato, alvos="fixo"):
        uuid = f"{i:08d}-5555-4000-8000-000000000000"
        self.falar(registro(texto, uuid=uuid))
        rc, saida = self.gravar(ato=ato, alvos=alvos, uuid=uuid)
        self.assertEqual(rc, 0, saida)
        return self.lidas("2036-11-18 00:01")[-1]

    def test_texto_limpo_grava_fixa_e_ativa_sem_vencer(self):
        for i, (texto, ato) in enumerate((("Autorizo o corte diário fixo.", "corte-diario"),
                                          ("autorizo aperta com segurança por escrito, fixo", "so-aperta-com-seguranca"))):
            with self.subTest(ato=ato):
                _, campos, corpo, est, motivo = self.lida(i, texto, ato)
                self.assertEqual((corpo, est, motivo, campos["Ato"], campos["Alvos"]), (texto, "ativa", "", ato, "fixo"))
                self.assertEqual((campos["Validade"], campos["Validade-utc"], campos["Origem-da-validade"]), ("fixa", "fixa", "sem prazo"))

    def test_alvo_validade_ressalva_ou_outro_ato_nascem_pendentes(self):
        casos = (("autorizo o corte diario ate amanha", "termo de validade em ato fixo"),
                 ("autorizo o corte diario da versao 0.47.3", "alvos do texto"), ("autorizo o corte diario as 06:00", "fora do mapa"),
                 ("autorizo o corte diario e o rotulo", "mais de um ato"), *((f"autorizo o corte diario {m}", "fora do vocabul")
                                                                            for m in MARCAS))
        for i, (texto, motivo) in enumerate(casos):
            with self.subTest(texto=texto):
                _, campos, _, est, lido = self.lida(i, texto, "corte-diario")
                self.assertEqual((campos["Estado-inicial"], est, campos["Validade"]), ("pendente-confirmacao", "pendente", "fixa"))
                self.assertIn(motivo, lido)

    def test_vocabulario_novo_so_nos_atos_fixos_e_sem_marca(self):
        self.assertFalse(set(MARCAS) & fa.VOCABULARIO_FIXO)
        _, campos, _, _, _ = self.lida(0, "pode mesclar a main 0.47.3 todo dia", "merge-main", "versao:0.47.3")
        self.assertEqual((campos["Estado-inicial"], campos["Validade"]), ("pendente-confirmacao", "ate:2026-11-20 00:00"))
        self.assertEqual(campos["Motivo-da-pendencia"], "palavra fora do vocabulário: dia, todo")
        _, campos, _, _, _ = self.lida(1, "pode mesclar a main 0.47.3 e o corte", "merge-main", "versao:0.47.3")
        self.assertIn("mais de um ato", campos["Motivo-da-pendencia"])

    def test_alvo_que_nao_e_fixo_no_ato_fixo_ou_fixo_no_ato_de_antes_recusa(self):
        self.nada_gravado(*self.gravar("autorizo o corte diario no pr 5", ato="corte-diario", alvos="pr:5"))
        self.nada_gravado(*self.gravar("pode aplicar o rotulo", alvos="fixo", uuid="22222222-2222-4222-8222-222222222222"))
        self.nada_gravado(*self.gravar("autorizo o corte diario", ato="merge-main", alvos="fixo", uuid="33333333-3333-4333-8333-333333333333"))

    def test_rotulo_pelo_time_grava_fixa_e_so_ativa_no_repositorio_do_forge(self):  # Emenda ROTULO-PELO-TIME
        texto = "autorizo o time ate a homologacao, fixo"
        _, campos, corpo, est, motivo = self.lida(0, texto, "rotulo-pelo-time")
        self.assertEqual((corpo, campos["Estado-inicial"], campos["Validade"], campos["Alvos"]), (texto, "ativa", "fixa", "fixo"))
        self.assertEqual((est, motivo), ("inativa", "só vale no repositório do Forge: o origin é outro"))
        git(self.raiz, "init", "-q")
        git(self.raiz, "remote", "add", "origin", json.loads((BIN.parent / ".claude-plugin" / "plugin.json").read_text())["repository"])
        self.assertEqual(self.lidas("2036-11-18 00:01")[-1][3:], ("ativa", ""))
        _, campos, _, _, _ = self.lida(1, "autorizo o rotulo pelo time ate a homologacao, fixo", "rotulo-pelo-time")
        self.assertIn("mais de um ato", campos["Motivo-da-pendencia"])  # o termo `rotulo` é do ato com prazo


if __name__ == "__main__":
    unittest.main()
