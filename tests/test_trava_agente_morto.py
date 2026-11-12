"""TRAVA-AGENTE-MORTO (v0457 E23.60; parecer de segurança da E23.46, C1 a C12): o hook `agentes` tira na hora o registro do
agente que a notificação terminal do Claude Code prova parado, e só com ela. Um teste de abuso por condição de C1 a C11."""
import io
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

AQUI = Path(__file__).resolve().parent
HOOKS = AQUI.parent / "hooks"
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(HOOKS))
from ambiente_git import sem_manutencao  # noqa: E402

import agentes  # noqa: E402
import pesado  # noqa: E402

SESSAO = "0b6c1e2a-1111-4222-8333-944455556666"
OUTRA = "0b6c1e2a-1111-4222-8333-000000000000"
AID = "a0123456789abcdef"
USO = "toolu_01AbCdEfGhIjKlMnOpQrStUv"
LANCADOR = ("import runpy, sys; sys.path.insert(0, sys.argv[1]); "
            "sys.argv = [sys.argv[2]]; runpy.run_path(sys.argv[0], run_name='__main__')")


def carimbo(segundos):
    return datetime.fromtimestamp(segundos, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def cabecalho(aid=AID, uso=USO, status="failed", saida=True):
    linhas = ["<task-notification>", f"<task-id>{aid}</task-id>", f"<tool-use-id>{uso}</tool-use-id>"]
    linhas += [f"<output-file>/tmp/x/tasks/{aid}.output</output-file>"] if saida else []
    return "\n".join(linhas + [f"<status>{status}</status>", '<summary>Agent "x" failed</summary>', "</task-notification>"])


def notificacao(quando, conteudo=None, **campos):
    entrada = {"parentUuid": "p", "isSidechain": False, "type": "user", "promptSource": "system", "origin": {"kind": "task-notification"},
               "timestamp": carimbo(quando), "sessionId": SESSAO, "message": {"role": "user", "content": conteudo or cabecalho()}}
    entrada.update(campos)
    return entrada


class Base(unittest.TestCase):
    """Home temporário com `~/.claude/projects/-p/<sessão>.jsonl` e o meta.json do agente; o hook com a pasta do estado própria."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-tam-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.home = self.tmp / "home"
        self.projeto = self.home / ".claude" / "projects" / "-p"
        self.projeto.mkdir(parents=True)
        self.transcript = self.projeto / f"{SESSAO}.jsonl"
        self.meta = self.projeto / SESSAO / "subagents" / f"agent-{AID}.meta.json"
        self.meta.parent.mkdir(parents=True)
        self.meta.write_text(json.dumps({"agentType": "forge:tech-lead", "toolUseId": USO}), encoding="utf-8")
        self.run = self.tmp / "run"
        self.run.mkdir()
        self.agora = time.time()
        patch = mock.patch.dict(os.environ, {"HOME": str(self.home)})
        patch.start()
        self.addCleanup(patch.stop)

    def escrever(self, *entradas, cru=b""):
        self.transcript.write_bytes(cru + b"".join(json.dumps(e).encode() + b"\n" for e in entradas))

    def hook(self, sessao=SESSAO, transcript=None, **campos):
        h = agentes.Hook("agentes")
        h.entrada = {"hook_event_name": "PreToolUse", "session_id": sessao, "cwd": str(self.tmp),
                     "transcript_path": str(transcript or self.transcript), **campos}
        h._run = self.run
        return h

    def registro(self, **campos):
        return {"id": AID, "tipo": "forge:tech-lead", "descricao": "E9 tech-lead", "desde": self.agora - 600, "sessao": SESSAO,
                "branches": ["melhoria/x"], "escrita": [], **campos}

    def solta(self, registro=None, hook=None):
        """Os registros que sobram em `vigentes` com a `Liberacao`, e os soltos."""
        hook = hook or self.hook()
        liberacao = agentes.Liberacao(hook, self.agora)
        sobra = agentes.vigentes([registro or self.registro()], self.agora, 7200, liberacao)
        return sobra, liberacao.soltos

    def assertLibera(self, **kw):
        sobra, soltos = self.solta(**kw)
        self.assertEqual(sobra, [])
        self.assertEqual(len(soltos), 1)

    def assertMantem(self, **kw):
        sobra, soltos = self.solta(**kw)
        self.assertEqual(len(sobra), 1)
        self.assertEqual(soltos, [])


class C1NotificacaoDoClaudeCode(Base):
    def test_notificacao_terminal_libera(self):
        for status in ("failed", "completed", "killed"):
            with self.subTest(status=status):
                self.escrever(notificacao(self.agora - 5, cabecalho(status=status)))
                sobra, soltos = self.solta()
                self.assertEqual((sobra, [s for _, s in soltos]), ([], [status]))

    def test_sem_output_file_tambem_libera(self):
        self.escrever(notificacao(self.agora - 5, cabecalho(saida=False)))
        self.assertLibera()

    def test_tool_result_com_o_mesmo_texto_nao_libera(self):
        self.escrever(notificacao(self.agora - 5, [{"type": "tool_result", "tool_use_id": "t", "content": cabecalho()}]))
        self.assertMantem()

    def test_mensagem_do_usuario_nao_libera(self):
        for campos in ({"promptSource": "user"}, {"promptSource": None}, {"type": "assistant"}):
            with self.subTest(campos=campos):
                entrada = notificacao(self.agora - 5)
                entrada.update(campos)
                self.escrever(entrada)
                self.assertMantem()

    def test_sidechain_nao_libera(self):
        for valor in (True, None, 0):
            with self.subTest(isSidechain=valor):
                self.escrever(notificacao(self.agora - 5, isSidechain=valor))
                self.assertMantem()

    def test_status_fora_da_lista_nao_libera(self):
        for status in ("stopped", "running", "FAILED", "failed2"):
            with self.subTest(status=status):
                self.escrever(notificacao(self.agora - 5, cabecalho(status=status)))
                self.assertMantem()

    def test_status_depois_do_cabecalho_nao_conta(self):
        texto = cabecalho(status="stopped").replace("</task-notification>", "<result><status>failed</status></result></task-notification>")
        self.escrever(notificacao(self.agora - 5, texto))
        self.assertMantem()

    def test_cabecalho_fora_do_inicio_nao_libera(self):
        for prefixo in ("x", " ", "\n", "Agent said:\n"):
            with self.subTest(prefixo=prefixo):
                self.escrever(notificacao(self.agora - 5, prefixo + cabecalho()))
                self.assertMantem()

    def test_ids_fora_da_forma_nao_liberam(self):
        for texto in (cabecalho(uso="tool_01x"), cabecalho().replace(f"<task-id>{AID}", f"<task-id>{AID}0"),
                      cabecalho().replace("<tool-use-id>", "<tool-use-id> ")):
            with self.subTest(texto=texto[:80]):
                self.escrever(notificacao(self.agora - 5, texto))
                self.assertMantem()

    def test_linha_fora_da_forma_e_pulada_sem_parar_a_leitura(self):
        lixo = b'["<task-notification>"]\n{"type": "user", "message": "<task-notification>"}\n{<task-notification>\n'
        self.escrever(notificacao(self.agora - 5), cru=lixo)
        self.assertLibera()

    def test_carimbo_fora_da_forma_nao_libera(self):
        for valor in ("2026-11-12 15:59:10", 1731000000, None, carimbo(self.agora)[:-1] + "+00:00"):
            with self.subTest(timestamp=valor):
                self.escrever(notificacao(self.agora - 5, timestamp=valor))
                self.assertMantem()


class C2ConfereJuntos(Base):
    def test_tool_use_id_diferente_do_meta_nao_libera(self):
        self.escrever(notificacao(self.agora - 5, cabecalho(uso="toolu_01Outro")))
        self.assertMantem()

    def test_task_id_de_outro_agente_nao_libera(self):
        self.escrever(notificacao(self.agora - 5, cabecalho(aid="a00000000000000ff")))
        self.assertMantem()

    def test_notificacao_anterior_ao_desde_nao_libera(self):
        self.escrever(notificacao(self.agora - 601))
        self.assertMantem()

    def test_meta_ausente_ou_sem_tool_use_id_nao_libera(self):
        self.escrever(notificacao(self.agora - 5))
        for conteudo in (None, "{}", "[1]", '{"toolUseId": 7}', "não é json"):
            with self.subTest(meta=conteudo):
                if conteudo is None:
                    self.meta.unlink()
                else:
                    self.meta.write_text(conteudo, encoding="utf-8")
                self.assertMantem()

    def test_uma_notificacao_divergente_mantem(self):
        self.escrever(notificacao(self.agora - 9, cabecalho(uso="toolu_01Outro")), notificacao(self.agora - 5))
        self.assertMantem()


class C3SoDaSessaoAtual(Base):
    def test_registro_de_outra_sessao_nao_sai(self):
        self.escrever(notificacao(self.agora - 5))
        self.assertMantem(registro=self.registro(sessao=OUTRA))
        self.assertMantem(registro={k: v for k, v in self.registro().items() if k != "sessao"})

    def test_sessao_ou_id_fora_da_forma_nao_saem(self):
        self.escrever(notificacao(self.agora - 5))
        self.assertMantem(hook=self.hook(sessao=SESSAO.upper()))
        self.assertMantem(registro=self.registro(id="a0123456789ABCDEF"))
        self.assertMantem(registro=self.registro(id="b0123456789abcdef"))

    def test_sessao_fora_da_forma_nao_sai_nem_com_transcript_e_meta_do_mesmo_nome(self):
        for sessao in ("x", SESSAO + "0", "../" + SESSAO):
            with self.subTest(sessao=sessao):
                transcript = self.projeto / f"{sessao}.jsonl"
                meta = self.projeto / sessao / "subagents" / f"agent-{AID}.meta.json"
                meta.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(self.meta, meta)
                transcript.write_text(json.dumps(notificacao(self.agora - 5)) + "\n", encoding="utf-8")
                self.assertMantem(hook=self.hook(sessao=sessao, transcript=transcript), registro=self.registro(sessao=sessao))

    def test_transcript_fora_de_projects_ou_de_outra_sessao_nao_vale(self):
        fora = self.tmp / "fora" / "-p" / f"{SESSAO}.jsonl"
        fora.parent.mkdir(parents=True)
        self.escrever(notificacao(self.agora - 5))
        shutil.copy(self.transcript, fora)
        shutil.copytree(self.meta.parent.parent, fora.with_suffix(""))  # o meta.json ao lado: só a pasta-base recusa
        outro = self.projeto / f"{OUTRA}.jsonl"
        shutil.copy(self.transcript, outro)
        for caminho in (fora, outro, self.projeto / ".." / "-p" / ".." / f"{SESSAO}.jsonl"):
            with self.subTest(caminho=str(caminho)):
                self.assertMantem(hook=self.hook(transcript=caminho))
        self.assertMantem(hook=self.hook(transcript=Path(f"-p/{SESSAO}.jsonl")))

    def test_link_para_fora_nao_vale(self):
        fora = self.tmp / "fora.jsonl"
        fora.write_text(json.dumps(notificacao(self.agora - 5)) + "\n", encoding="utf-8")
        self.transcript.symlink_to(fora)
        self.assertMantem()

    def test_meta_por_link_nao_vale(self):
        self.escrever(notificacao(self.agora - 5))
        verdadeiro = self.tmp / "meta.json"
        verdadeiro.write_text(json.dumps({"toolUseId": USO}), encoding="utf-8")
        self.meta.unlink()
        self.meta.symlink_to(verdadeiro)
        self.assertMantem()

    def test_pasta_do_meta_por_link_nao_vale(self):
        self.escrever(notificacao(self.agora - 5))
        fora = self.tmp / "fora-da-sessao"
        shutil.copytree(self.meta.parent.parent, fora)
        shutil.rmtree(self.meta.parent.parent)
        self.meta.parent.parent.symlink_to(fora)
        self.assertMantem()


class C4Orcamento(Base):
    def test_notificacao_alem_do_teto_de_bytes_fica(self):
        enchimento = (json.dumps({"type": "assistant", "x": "y" * 1000}) + "\n").encode() * 2200
        self.transcript.write_bytes(json.dumps(notificacao(self.agora - 5)).encode() + b"\n" + enchimento)
        self.assertMantem()

    def test_notificacao_no_fim_de_transcript_grande_libera(self):
        enchimento = (json.dumps({"type": "assistant", "x": "y" * 1000}) + "\n").encode() * 2200
        self.escrever(notificacao(self.agora - 5), cru=enchimento)
        self.assertLibera()

    def test_prazo_estourado_mantem(self):
        self.escrever(notificacao(self.agora - 5))
        with mock.patch.object(agentes, "PRAZO_DA_LEITURA_S", -1):
            self.assertMantem()

    def test_transcript_que_nao_e_arquivo_regular_mantem(self):
        os.mkfifo(self.transcript)
        self.assertMantem()

    def test_descritor_que_nao_e_arquivo_regular_mantem(self):
        self.escrever(notificacao(self.agora - 5))
        real = os.fstat

        def como_dispositivo(fd):
            lido = real(fd)
            return os.stat_result((stat.S_IFCHR | 0o600, *tuple(lido)[1:]))
        with mock.patch.object(agentes.os, "fstat", como_dispositivo):
            self.assertMantem()


class C9ParadaSemFilho(Base):
    def setUp(self):
        super().setUp()
        self.escrever(notificacao(self.agora - 5))

    def travar(self, pid, desde):
        (self.run / "pesado.json").write_text(json.dumps({"pid": pid, "inicio": pesado.inicio_de(pid), "agente": AID,
                                                          "desde": desde}), encoding="utf-8")

    def test_registro_de_escrita_com_pesado_ocupado_fica(self):
        self.travar(os.getpid(), self.agora - 5)
        self.assertMantem(registro=self.registro(escrita=["melhoria/x"]))

    def test_registro_de_escrita_com_pesado_malformado_fica(self):
        (self.run / "pesado.json").write_text("[]", encoding="utf-8")
        self.assertMantem(registro=self.registro(escrita=["melhoria/x"]))

    def test_registro_de_escrita_com_pesado_livre_ou_vencido_sai(self):
        self.assertLibera(registro=self.registro(escrita=["melhoria/x"]))
        self.travar(os.getpid(), self.agora - pesado.TRAVA_S - 1)
        self.assertLibera(registro=self.registro(escrita=["melhoria/x"]))

    def test_registro_so_de_leitura_nao_olha_o_pesado(self):
        self.travar(os.getpid(), self.agora - 5)
        self.assertLibera(registro=self.registro(escrita=[]))

    def test_notificacao_de_parada_da_sessao_anterior_nao_libera(self):
        self.escrever(notificacao(self.agora - 5, cabecalho(status="stopped")))
        self.assertMantem()


class C8Lapide(Base):
    def setUp(self):
        super().setUp()
        patch = mock.patch("sys.stderr", io.StringIO())  # a recusa escreve no stderr
        patch.start()
        self.addCleanup(patch.stop)

    def lapides(self):
        return [agentes.lapide(self.registro(), self.agora)]

    def retomar(self, agentes_vigentes, lapides, alvo=AID):
        return self.hook(tool_name="SendMessage", tool_input={"to": alvo, "message": "volte"}), agentes_vigentes, lapides

    def test_retomar_com_relancamento_na_mesma_descricao_recusa(self):
        relancado = self.registro(id="a00000000000000aa", branches=[])
        with self.assertRaises(SystemExit) as saida:
            agentes.recusar_retomada(*self.retomar([relancado], self.lapides()))
        self.assertEqual(saida.exception.code, 2)

    def test_retomar_com_relancamento_na_mesma_branch_recusa(self):
        relancado = self.registro(id="a00000000000000aa", descricao="outra", branches=["melhoria/z", "melhoria/x"])
        with self.assertRaises(SystemExit):
            agentes.recusar_retomada(*self.retomar([relancado], self.lapides()))

    def test_retomar_sem_relancamento_passa(self):
        outro = self.registro(id="a00000000000000aa", descricao="outra", branches=["melhoria/y"])
        self.assertIsNone(agentes.recusar_retomada(*self.retomar([outro], self.lapides())))
        self.assertIsNone(agentes.recusar_retomada(*self.retomar([self.registro(id="a00000000000000aa")], self.lapides(),
                                                                 alvo="a00000000000000bb")))

    def test_erro_na_conferencia_recusa(self):
        fundo = []
        for _ in range(100000):
            fundo = [fundo]
        hook = self.hook(tool_name="SendMessage", tool_input={"to": fundo})
        with self.assertRaises(SystemExit) as saida:
            agentes.recusar_retomada(hook, [], self.lapides())
        self.assertEqual(saida.exception.code, 2)

    def test_lapide_vence_com_o_prazo_do_registro(self):
        estado = {"lapides": [{"id": AID, "desde": self.agora - 7200}, {"id": AID, "desde": self.agora - 10}, "x"]}
        self.assertEqual([l["desde"] for l in agentes.lapides_vigentes(estado, self.agora, 7200)], [self.agora - 10])
        for lixo in (5, "ab", {"id": AID}):
            with self.subTest(lapides=lixo):
                self.assertEqual(agentes.lapides_vigentes({"lapides": lixo}, self.agora, 7200), [])

    def test_lapide_so_guarda_branches_de_texto(self):
        for branches, esperado in ((["melhoria/x", 1, None], ["melhoria/x"]), ("melhoria/x", []), (None, [])):
            with self.subTest(branches=branches):
                feita = agentes.lapide(self.registro(branches=branches), self.agora)
                self.assertEqual((feita["id"], feita["branches"], feita["descricao"]), (AID, esperado, "E9 tech-lead"))


class C10ProjectsProtegido(Base):
    def test_nenhum_papel_escreve_no_transcript_nem_no_meta(self):
        import conformidade
        politica = json.loads((HOOKS / "conformidade.json").read_text(encoding="utf-8"))
        entradas = [c for c in politica["caminhos"] if c["caminho"].startswith("~/.claude/projects/")]
        self.assertEqual([c["quem"] for c in entradas], [[], []])
        tipos = [t for lista in politica["papeis"].values() for t in lista] + [None, "general-purpose"]
        self.assertGreaterEqual(len(tipos), 10)
        for tipo in tipos:
            for alvo in (f"~/.claude/projects/-p/{SESSAO}.jsonl", f"~/.claude/projects/-p/{SESSAO}/subagents/agent-{AID}.meta.json",
                         f"~/.claude/projects/-p/{SESSAO}/subagents/agent-{AID}.jsonl"):
                with self.subTest(tipo=tipo, alvo=alvo):
                    recusa = conformidade.escrita_barrada(tipo, alvo, str(self.tmp), "melhoria/x")
                    self.assertIsNotNone(recusa)
                    self.assertIn("TRAVA-AGENTE-MORTO", " ".join(map(str, recusa)))

    def test_memoria_do_agente_segue_livre(self):
        """A pasta `memory/` do projeto em ~/.claude/projects/ não é prova de nada (fixture conformidade/home-claude-memoria-libera)."""
        import conformidade
        recusa = conformidade.escrita_barrada("forge:tech-lead", "~/.claude/projects/-p/memory/a.md", str(self.tmp), "melhoria/x")
        self.assertNotIn("TRAVA-AGENTE-MORTO", " ".join(map(str, recusa or ())))


class C11Log(Base):
    def test_liberacao_registra_id_e_status_sem_descricao(self):
        agentes.registrar_liberacao(self.hook(), AID, "failed")
        linha = (self.run / "liberacoes.log").read_text(encoding="ascii")
        self.assertRegex(linha, rf"^\d{{4}}-\d\d-\d\dT\d\d:\d\d:\d\d agentes R-TETO id={AID} status=failed motivo=notificacao\n$")

    def test_log_nao_segue_link_e_gira_no_limite(self):
        alvo = self.tmp / "alvo"
        alvo.write_text("", encoding="utf-8")
        (self.run / "liberacoes.log").symlink_to(alvo)
        agentes.registrar_liberacao(self.hook(), AID, "failed")
        self.assertEqual(alvo.read_text(encoding="utf-8"), "")
        (self.run / "liberacoes.log").unlink()
        (self.run / "liberacoes.log").write_bytes(b"x" * (agentes.LIMITE_LOG + 1))
        agentes.registrar_liberacao(self.hook(), AID, "killed")
        self.assertEqual((self.run / "liberacoes.log.1").stat().st_size, agentes.LIMITE_LOG + 1)
        self.assertIn("status=killed", (self.run / "liberacoes.log").read_text(encoding="ascii"))


def git(*args, cwd):
    env = sem_manutencao({"PATH": os.environ.get("PATH", ""), "HOME": str(cwd), "GIT_CONFIG_NOSYSTEM": "1",
                          "GIT_CONFIG_GLOBAL": os.devnull})
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env, timeout=60)


class PeloHook(Base):
    """C5, C6, C7, C8 e C11 pelo hook inteiro, num clone do Forge temporário (estado no diretório comum)."""

    def setUp(self):
        super().setUp()
        self.clone = self.tmp / "clone"
        (self.clone / ".claude-plugin").mkdir(parents=True)
        (self.clone / ".claude-plugin" / "plugin.json").write_text('{"name": "forge"}\n', encoding="utf-8")
        git("init", "-q", "-b", "develop", cwd=self.clone)
        git("-c", "user.email=t@example.com", "-c", "user.name=T", "commit", "-q", "--allow-empty", "-m", "base", cwd=self.clone)
        (self.clone / ".forge").write_text("", encoding="utf-8")
        self.estado = self.clone / ".git" / "forge" / "run" / "agentes.json"
        self.estado.parent.mkdir(parents=True)
        self.proc = self.tmp / "proc"
        self.proc.mkdir()
        (self.proc / "loadavg").write_text("0.1 0.1 0.1\n", encoding="utf-8")
        (self.proc / "meminfo").write_text("MemTotal: 16777216 kB\nMemAvailable: 8388608 kB\n", encoding="utf-8")

    def semear(self, *registros, lapides=None):
        self.estado.write_text(json.dumps({"agentes": list(registros), "lapides": lapides or []}), encoding="utf-8")

    def evento(self, extra=None, **campos):
        entrada = {"session_id": SESSAO, "cwd": str(self.clone), "transcript_path": str(self.transcript), **campos}
        env = sem_manutencao({"PATH": os.environ.get("PATH", ""), "HOME": str(self.home), "GIT_CONFIG_NOSYSTEM": "1",
                              "GIT_CONFIG_GLOBAL": os.devnull, "FORGE_PROC": str(self.proc), "FORGE_NPROC": "1", **(extra or {})})
        return subprocess.run([sys.executable, "-I", "-c", LANCADOR, str(HOOKS), str(HOOKS / "agentes.py")],
                              input=json.dumps(entrada), cwd=self.clone, env=env, capture_output=True, text=True, timeout=120)

    def lancar(self, tipo="Explore", descricao="E9 tech-lead", extra=None):
        return self.evento(extra, hook_event_name="PreToolUse", tool_name="Agent",
                           tool_input={"subagent_type": tipo, "description": descricao, "prompt": "p"})

    def gravado(self):
        return json.loads(self.estado.read_text(encoding="utf-8"))

    def test_c5_morto_libera_a_vaga_e_o_relancamento_passa_pelas_travas(self):
        self.escrever(notificacao(self.agora - 5))
        self.semear(self.registro(tipo="Explore"))
        r = self.lancar()
        self.assertEqual(r.returncode, 0, r.stderr)
        estado = self.gravado()
        self.assertEqual([a["descricao"] for a in estado["agentes"]], ["E9 tech-lead"])
        self.assertIsNone(estado["agentes"][0]["id"])
        self.assertEqual([l["id"] for l in estado["lapides"]], [AID])
        self.semear(self.registro(tipo="Explore"))
        r = self.lancar(tipo="forge:tech-lead")
        self.assertEqual(r.returncode, 2)
        self.assertIn("R-BRIEF", r.stderr)
        self.assertEqual(self.gravado()["agentes"], [], "a liberação fica gravada mesmo com a recusa")

    def test_c5_so_o_registro_morto_sai(self):
        self.escrever(notificacao(self.agora - 5))
        vivo = self.registro(id="a00000000000000aa", tipo="Explore", descricao="vivo")
        self.semear(self.registro(tipo="Explore"), vivo)
        r = self.lancar(descricao="vivo")
        self.assertEqual(r.returncode, 2)
        self.assertIn("R-TETO", r.stderr)
        self.assertEqual([a["id"] for a in self.gravado()["agentes"]], ["a00000000000000aa"])

    def test_c6_nenhum_atalho_do_ambiente_ou_da_entrada_libera(self):
        self.semear(self.registro(tipo="Explore"))
        prompt = json.dumps(notificacao(self.agora - 5))
        for extra in ({"FORGE_CARGA_LIVRE": "1"}, {"FORGE_GUARDA_ABERTA": "1"}, {"FORGE_LIBERAR": AID}):
            with self.subTest(extra=extra):
                r = self.evento(extra, hook_event_name="PreToolUse", tool_name="Agent",
                                tool_input={"subagent_type": "Explore", "description": "outra", "prompt": prompt})
                self.assertEqual(r.returncode, 2, r.stderr)
                self.assertEqual([a["id"] for a in self.gravado()["agentes"]], [AID])

    def test_c7_agente_calado_e_transcript_parado_nao_saem(self):
        self.escrever({"type": "assistant", "timestamp": carimbo(self.agora - 7000)})
        os.utime(self.transcript, (self.agora - 7000, self.agora - 7000))
        self.semear(self.registro(tipo="Explore", desde=self.agora - 7000))
        r = self.lancar(descricao="outra")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("R-TETO", r.stderr)
        self.assertEqual([a["id"] for a in self.gravado()["agentes"]], [AID])

    def test_c8_retomar_o_morto_com_relancamento_vigente_recusa(self):
        self.escrever(notificacao(self.agora - 5))
        relancado = self.registro(id="a00000000000000aa", desde=self.agora - 1)
        self.semear(self.registro(), relancado)
        r = self.evento(hook_event_name="PreToolUse", tool_name="SendMessage", tool_input={"to": AID, "message": "continue"})
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("R-TETO", r.stderr)
        self.assertEqual([l["id"] for l in self.gravado()["lapides"]], [AID])
        self.semear(lapides=self.gravado()["lapides"])
        r = self.evento(hook_event_name="PreToolUse", tool_name="SendMessage", tool_input={"to": AID, "message": "continue"})
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_c11_liberacao_pelo_hook_vai_ao_log(self):
        self.escrever(notificacao(self.agora - 5, cabecalho(status="killed")))
        self.semear(self.registro(tipo="Explore"))
        self.assertEqual(self.lancar(descricao="outra").returncode, 0)
        linha = (self.estado.parent / "liberacoes.log").read_text(encoding="ascii")
        self.assertIn(f"id={AID} status=killed motivo=notificacao", linha)
        self.assertNotIn("E9", linha)


if __name__ == "__main__":
    unittest.main()
