"""BP3-S3 (v0479, E39.3): o hook `agentes` guarda em cada reserva o caminho e o hash do brief (`briefs`) e, quando a sessão está
provadamente morta, move o registro para `interrompidos` em vez de apagá-lo. É só registro: nenhum teste aqui libera ou recusa
disparo a mais do que antes. Sai de `interrompidos` no relançamento do mesmo tipo com brief de mesmo caminho, na retomada por
`SendMessage` do mesmo id e no prazo (linha no `liberacoes.log`). O processo morto é um filho de verdade, já encerrado."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "hooks"))
import agentes  # noqa: E402

AID = "a0123456789abcdef"
OUTRO = "afedcba9876543210"
SESSAO = "0b6c1e2a-1111-4222-8333-944455556666"
MARCADOR = "MARCADOR-UNICO-DO-PROMPT-7f3a"
BRIEF = "Agente destino: forge:python-backend\nBranch: melhoria/x\nEtapa: codigo\n\n## Objetivo\nfazer\n"


def pid_morto():
    filho = subprocess.Popen([sys.executable, "-I", "-c", "pass"])
    filho.wait()
    return filho.pid


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-int-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        (self.tmp / ".forge" / "run").mkdir(parents=True)
        (self.tmp / "docs" / "briefs").mkdir(parents=True)
        self.brief = self.tmp / "docs" / "briefs" / "x-python-backend-1.md"
        self.brief.write_text(BRIEF, encoding="utf-8")
        self.hash = hashlib.sha256(BRIEF.encode()).hexdigest()
        self.arquivo = self.tmp / ".forge" / "run" / "agentes.json"
        self.agora = time.time()
        for patch in (mock.patch.dict(os.environ, {"HOME": str(self.tmp / "home"), "FORGE_NPROC": "8"}),
                      mock.patch.object(agentes, "medir", return_value=(0.0, 64.0, 64.0))):
            patch.start()
            self.addCleanup(patch.stop)

    def hook(self, **campos):
        h = agentes.Hook("agentes")
        h.entrada = {"hook_event_name": "PreToolUse", "session_id": SESSAO, "cwd": str(self.tmp), **campos}
        h.raiz = self.tmp
        h._run = self.tmp / ".forge" / "run"
        return h

    def briefs(self, nome="x-python-backend-1.md", sha=None):
        return [{"caminho": f"docs/briefs/{nome}", "sha256": sha or self.hash}]

    def registro(self, **campos):
        base = {"id": AID, "tipo": "forge:python-backend", "descricao": "S3", "desde": self.agora - 60, "branches": ["melhoria/x"],
                "escrita": ["melhoria/x"], "briefs": self.briefs(), "pid": pid_morto(), "pidns": agentes.namespace_de_pid(),
                "sessao": SESSAO}
        base.update(campos)
        return base

    def semear(self, agentes_=(), interrompidos=None):
        estado = {"agentes": list(agentes_)}
        if interrompidos is not None:
            estado["interrompidos"] = interrompidos
        self.arquivo.write_text(json.dumps(estado), encoding="utf-8")

    def gravado(self):
        return json.loads(self.arquivo.read_text(encoding="utf-8"))

    def evento(self, nome="SubagentStart", **campos):
        h = self.hook(hook_event_name=nome, **campos)
        agentes.atualizar_estado(h, nome, campos.get("tool_name"), [])
        return h

    def interrompido(self, **campos):
        base = {"id": AID, "tipo": "forge:python-backend", "descricao": "S3", "branches": ["melhoria/x"], "escrita": ["melhoria/x"],
                "briefs": self.briefs(), "sessao": SESSAO, "desde": self.agora - 90, "caiu_em": self.agora - 30}
        base.update(campos)
        return base


class Reserva(Base):
    def lancar(self, prompt=None):
        citado = "docs/briefs/x-python-backend-1.md"
        lidos = [(citado, str(self.brief), BRIEF.encode())]
        entrada = {"subagent_type": "forge:python-backend", "description": "S3 novo", "prompt": prompt or f"leia {citado} {MARCADOR}"}
        h = self.hook(tool_name="Agent", tool_input=entrada)
        agentes.atualizar_estado(h, "PreToolUse", "Agent", lidos)
        return h

    def test_a_reserva_guarda_o_caminho_e_o_hash_do_brief(self):
        self.lancar()
        reserva = self.gravado()["agentes"][0]
        self.assertEqual(reserva["briefs"], self.briefs())
        self.assertEqual(reserva["branches"], ["melhoria/x"])

    def test_nenhum_byte_do_prompt_entra_no_registro(self):
        self.lancar()
        self.assertNotIn(MARCADOR, self.arquivo.read_text(encoding="utf-8"))

    def test_so_o_caminho_seguro_de_docs_briefs_e_gravado(self):
        h = hashlib.sha256(b"x").hexdigest()
        for real in ("/tmp/fora.md", "/a/docs/briefs/../x.md", "/a/docs/briefs/x\n.md", "/a/docs/briefs/sub dir.md",
                     "/a/docs/briefs/" + "n" * 200 + ".md", "/a/docs/briefs/.md", "/a/docs/briefs/a..b.md"):
            with self.subTest(real=real):
                self.assertEqual(agentes.briefs_da_reserva([("c", real, b"x")]), [])
        self.assertEqual(agentes.briefs_da_reserva([("c", "/a/docs/briefs/ok-1.md", b"x"), ("c", "/b/docs/briefs/ok-1.md", b"x")]),
                         [{"caminho": "docs/briefs/ok-1.md", "sha256": h}])

    def test_sem_brief_selado_a_reserva_sai_com_a_lista_vazia(self):
        h = self.hook(tool_name="Agent", tool_input={"subagent_type": "Explore", "description": "ler", "prompt": "x"})
        agentes.atualizar_estado(h, "PreToolUse", "Agent", [])
        self.assertEqual(self.gravado()["agentes"][0]["briefs"], [])


class Interrupcao(Base):
    def test_sessao_morta_com_brief_vai_para_interrompidos(self):
        self.semear([self.registro()])
        self.evento()
        estado = self.gravado()
        self.assertEqual(estado["agentes"], [])
        (item,) = estado["interrompidos"]
        self.assertEqual((item["id"], item["tipo"], item["descricao"], item["branches"], item["escrita"], item["briefs"], item["sessao"]),
                         (AID, "forge:python-backend", "S3", ["melhoria/x"], ["melhoria/x"], self.briefs(), SESSAO))
        self.assertAlmostEqual(item["desde"], self.agora - 60, delta=1)
        self.assertGreaterEqual(item["caiu_em"], self.agora)
        self.assertNotIn("pid", item)

    def test_reserva_que_nunca_comecou_vai_com_id_nulo(self):
        self.semear([self.registro(id=None)])
        self.evento()
        self.assertIsNone(self.gravado()["interrompidos"][0]["id"])

    def test_sem_briefs_o_registro_sai_como_sempre(self):
        for briefs in ([], None, [{"caminho": "../x.md", "sha256": self.hash}], [{"caminho": "docs/briefs/a.md", "sha256": "xx"}]):
            with self.subTest(briefs=briefs):
                self.semear([self.registro(briefs=briefs)])
                self.evento()
                self.assertEqual(self.gravado().get("interrompidos"), [])

    def test_sessao_viva_outro_namespace_e_pid_ausente_ficam_nos_agentes(self):
        viva = self.registro(pid=os.getpid())
        outro_ns = self.registro(id=OUTRO, pidns="pid:[1]")
        sem_pid = self.registro(id="a1111111111111111")
        sem_pid.pop("pid")
        self.semear([viva, outro_ns, sem_pid])
        self.evento()
        estado = self.gravado()
        self.assertEqual({a["id"] for a in estado["agentes"]}, {AID, OUTRO, "a1111111111111111"})
        self.assertEqual(estado["interrompidos"], [])

    def test_registro_fora_do_prazo_nao_vira_interrompido(self):
        self.semear([self.registro(desde=self.agora - 3 * 3600)])
        self.evento()
        self.assertEqual(self.gravado()["interrompidos"], [])

    def test_o_interrompido_nao_ocupa_vaga_nem_aparece_nos_agentes(self):
        self.semear([self.registro()])
        self.evento()
        self.assertEqual(self.gravado()["agentes"], [])

    def test_teto_de_interrompidos(self):
        antigos = [self.interrompido(id=None, descricao=str(n), caiu_em=self.agora - 10) for n in range(agentes.INTERROMPIDOS_MAX)]
        self.semear([self.registro()], antigos)
        self.evento()
        lista = self.gravado()["interrompidos"]
        self.assertEqual(len(lista), agentes.INTERROMPIDOS_MAX)
        self.assertEqual(lista[-1]["id"], AID)
        self.assertEqual(lista[0]["descricao"], "1")

    def test_interrompidos_que_nao_e_lista_deixa_o_estado_ilegivel(self):
        self.arquivo.write_text(json.dumps({"agentes": [], "interrompidos": {}}), encoding="utf-8")
        with self.assertRaises(agentes.EstadoIlegivel):
            agentes.ler_estado(self.arquivo)

    def test_so_campos_de_forma_conhecida_passam_para_o_item(self):
        self.semear([self.registro(id="x\nforjado", tipo=None, descricao=None, sessao=5, pid_extra="nao passa")])
        self.evento()
        (item,) = self.gravado()["interrompidos"]
        self.assertEqual((item["id"], item["tipo"], item["descricao"], item["sessao"]), (None, "", "", None))
        self.assertNotIn("pid_extra", item)

    def test_briefs_que_nao_e_lista_vale_vazio(self):
        for valor in (None, "docs/briefs/a.md", {"caminho": "x"}):
            self.assertEqual(agentes.briefs_validos({"briefs": valor}), [], valor)

    def test_vigentes_tira_o_vencido_e_o_que_nao_e_registro(self):
        velho, bom = self.registro(desde=self.agora - 3 * 3600), self.registro(id=OUTRO, pid=os.getpid())
        lista = agentes.vigentes([velho, "texto", {"desde": "x"}, {"desde": True, "id": AID}, bom], self.agora, 2 * 3600)
        self.assertEqual([a["id"] for a in lista], [OUTRO])

    def test_item_sem_caiu_em_numerico_some(self):
        self.semear([], [self.interrompido(caiu_em="x"), "texto", self.interrompido()])
        self.evento()
        self.assertEqual(len(self.gravado()["interrompidos"]), 1)

    def test_caiu_em_nao_finito_deixa_o_estado_ilegivel(self):
        # segurança A1: 10**400 estoura a subtração; inf e nan nunca vencem nem ficam; todos recusam em vez de passar sem reserva
        for valor in (10**400, -(10**400), float("inf"), float("-inf"), float("nan")):
            with self.subTest(valor=str(valor)[:12]):
                estado = {"interrompidos": [self.interrompido(caiu_em=valor)]}
                with self.assertRaises(agentes.EstadoIlegivel):
                    agentes.interrompidos_vigentes(estado, self.agora, 2 * 3600)

    def test_caiu_em_finito_e_aceito_mesmo_enorme(self):
        for valor in (self.agora - 30, int(self.agora) - 30, 10**300):
            self.assertTrue(agentes.caiu_em_finito(valor), valor)
        for valor in ("x", None, [1], 10**400, float("nan")):
            self.assertFalse(agentes.caiu_em_finito(valor), valor)

    def test_disparo_com_caiu_em_enorme_e_recusado_sem_regravar_o_estado(self):
        semeado = json.dumps({"agentes": [], "interrompidos": [{**self.interrompido(), "caiu_em": 10**400}]})
        self.arquivo.write_text(semeado, encoding="utf-8")
        citado = "docs/briefs/x-python-backend-1.md"
        entrada = {"subagent_type": "forge:python-backend", "description": "novo", "prompt": f"leia {citado}"}
        h = self.hook(tool_name="Agent", hook_event_name="PreToolUse", tool_input=entrada)
        with self.assertRaises(SystemExit) as saida, mock.patch.object(sys, "stderr"), \
                mock.patch.object(h, "projeto", return_value=self.tmp), mock.patch.object(agentes, "ler_config"), \
                mock.patch.object(agentes, "e_clone_do_forge", return_value=False), \
                mock.patch.object(agentes, "conferir_brief", return_value=([(citado, str(self.tmp / citado), BRIEF.encode())], None)):
            agentes.principal(h)
        self.assertNotEqual(saida.exception.code, 0)
        self.assertEqual(self.arquivo.read_text(encoding="utf-8"), semeado)

    def test_lapide_e_autor_com_numero_nao_finito_deixam_o_estado_ilegivel(self):
        # E53.1 (A1): 10**400 estoura a subtração; inf e nan nunca vencem; cada função recusa em vez de passar sem reserva
        lapide = {"id": AID, "desde": self.agora - 30, "descricao": "d", "branches": []}
        autor = {"id": AID, "desde": self.agora - 30, "escrita": ["melhoria/x"]}
        for nome, funcao, item in (("lapides", agentes.lapides_vigentes, lapide), ("autores", agentes.autores_vigentes, autor)):
            for valor in (10**400, -(10**400), float("inf"), float("-inf"), float("nan")):
                with self.subTest(lista=nome, valor=str(valor)[:12]):
                    with self.assertRaises(agentes.EstadoIlegivel):
                        funcao({nome: [{**item, "desde": valor}]}, self.agora, 2 * 3600)

    def test_lapide_e_autor_finitos_seguem_o_prazo(self):
        lapide = {"id": AID, "desde": self.agora - 30}
        autor = {"id": AID, "desde": self.agora - 30, "escrita": []}
        velho = {"desde": self.agora - 3 * 3600}
        self.assertEqual(agentes.lapides_vigentes({"lapides": [lapide, {**lapide, **velho}, "x", {"desde": "x"}]}, self.agora, 2 * 3600), [lapide])
        self.assertEqual(agentes.autores_vigentes({"autores": [autor, {**autor, **velho}, "x", {"id": "?", "desde": float("inf")}]},
                                                  self.agora, 2 * 3600), [autor])

    def test_disparo_com_lapide_ou_autor_enorme_e_recusado_sem_regravar_o_estado(self):
        for nome, item in (("lapides", {"id": AID, "desde": 10**400}), ("autores", {"id": AID, "desde": 10**400, "escrita": []})):
            with self.subTest(lista=nome):
                semeado = json.dumps({"agentes": [], nome: [item]})
                self.arquivo.write_text(semeado, encoding="utf-8")
                citado = "docs/briefs/x-python-backend-1.md"
                entrada = {"subagent_type": "forge:python-backend", "description": "novo", "prompt": f"leia {citado}"}
                h = self.hook(tool_name="Agent", hook_event_name="PreToolUse", tool_input=entrada)
                with self.assertRaises(SystemExit) as saida, mock.patch.object(sys, "stderr"), \
                        mock.patch.object(h, "projeto", return_value=self.tmp), mock.patch.object(agentes, "ler_config"), \
                        mock.patch.object(agentes, "e_clone_do_forge", return_value=False), \
                        mock.patch.object(agentes, "conferir_brief", return_value=([(citado, str(self.tmp / citado), BRIEF.encode())], None)):
                    try:
                        agentes.principal(h)
                    except OverflowError:
                        self.fail("OverflowError escapou de principal: o disparo deveria ser recusado")
                self.assertNotEqual(saida.exception.code, 0)
                self.assertEqual(self.arquivo.read_text(encoding="utf-8"), semeado)


class Fechamento(Base):
    def lancar(self, tipo="forge:python-backend", nome="x-python-backend-1.md"):
        citado = f"docs/briefs/{nome}"
        entrada = {"subagent_type": tipo, "description": "relançado", "prompt": f"leia {citado}"}
        h = self.hook(tool_name="Agent", tool_input=entrada)
        agentes.atualizar_estado(h, "PreToolUse", "Agent", [(citado, str(self.tmp / citado), BRIEF.encode())])

    def log(self):
        arquivo = self.tmp / ".forge" / "run" / "liberacoes.log"
        return arquivo.read_text(encoding="utf-8") if arquivo.exists() else ""

    def test_relancamento_do_mesmo_tipo_e_caminho_fecha_mesmo_com_hash_novo(self):
        self.semear([], [self.interrompido(briefs=self.briefs(sha="0" * 64))])
        self.lancar()
        self.assertEqual(self.gravado()["interrompidos"], [])

    def test_outro_tipo_ou_outro_caminho_nao_fecha(self):
        self.semear([], [self.interrompido()])
        self.lancar(tipo="forge:qa-engineer")
        self.assertEqual(len(self.gravado()["interrompidos"]), 1)
        (self.tmp / "docs/briefs/y-python-backend-1.md").write_text(BRIEF, encoding="utf-8")
        self.semear([], [self.interrompido()])
        self.lancar(nome="y-python-backend-1.md")
        self.assertEqual(len(self.gravado()["interrompidos"]), 1)

    def test_lancamento_recusado_nao_fecha(self):
        self.semear([self.registro(pid=os.getpid(), descricao="relançado", id=OUTRO)], [self.interrompido()])
        with self.assertRaises(SystemExit), mock.patch.object(sys, "stderr"):
            self.lancar()
        self.assertEqual(len(self.gravado()["interrompidos"]), 1)

    def test_retomada_por_send_message_do_mesmo_id_fecha(self):
        self.semear([], [self.interrompido(), self.interrompido(id=OUTRO)])
        self.evento("PreToolUse", tool_name="SendMessage", tool_input={"to": AID, "message": "continue"})
        self.assertEqual([i["id"] for i in self.gravado()["interrompidos"]], [OUTRO])

    def test_send_message_sem_id_ou_para_outro_nao_fecha(self):
        self.semear([], [self.interrompido(id=None), self.interrompido()])
        for entrada in ({"to": None}, {"to": "a9999999999999999"}, ["x"]):
            with self.subTest(entrada=entrada):
                self.evento("PreToolUse", tool_name="SendMessage", tool_input=entrada)
                self.assertEqual(len(self.gravado()["interrompidos"]), 2)

    def test_prazo_vencido_fecha_e_deixa_linha_no_log(self):
        self.semear([], [self.interrompido(caiu_em=self.agora - 3 * 3600, descricao="SEGREDO-DESCRICAO"), self.interrompido(id=OUTRO)])
        self.evento()
        self.assertEqual([i["id"] for i in self.gravado()["interrompidos"]], [OUTRO])
        log = self.log()
        self.assertIn(f"id={AID} status=interrompido motivo=interrompido_vencido", log)
        self.assertNotIn("SEGREDO-DESCRICAO", log)

    def test_vencido_com_id_fora_da_forma_vira_traco_no_log(self):
        self.semear([], [self.interrompido(id="x\nR-TETO forjada", caiu_em=self.agora - 3 * 3600)])
        self.evento()
        log = self.log()
        self.assertEqual(len(log.splitlines()), 1)
        self.assertIn("id=- status=interrompido", log)


class FimDoAgente(Base):
    """RESERVA-NAO-CAI-NO-FIM: agentes do mesmo tipo disparados juntos trocavam o id na reserva (o `SubagentStart` casava pelo tipo e
    pela ordem); o `SubagentStop` de um soltava a branch do outro e prendia a própria até a expiração (~80 min). O disparo guarda o
    `tool_use_id`; o início e o fim casam com o `toolUseId` do meta do agente."""
    IDS = {"A": "a1111111111111111", "B": "a2222222222222222", "C": "a3333333333333333"}
    USOS = {"A": "toolu_AAAA", "B": "toolu_BBBB", "C": "toolu_CCCC"}

    def setUp(self):
        super().setUp()
        projetos = self.tmp / "home" / ".claude" / "projects" / "p"
        self.transcript = projetos / f"{SESSAO}.jsonl"
        (projetos / SESSAO / "subagents").mkdir(parents=True)
        self.transcript.write_text("", encoding="utf-8")

    def meta(self, quem):
        pasta = self.transcript.with_suffix("") / "subagents"
        (pasta / f"agent-{self.IDS[quem]}.meta.json").write_text(json.dumps({"toolUseId": self.USOS[quem]}), encoding="utf-8")

    def lancar(self, quem):
        entrada = {"subagent_type": "forge:tech-lead", "description": f"agente {quem}", "prompt": "sem brief"}
        h = self.hook(tool_name="Agent", tool_input=entrada, tool_use_id=self.USOS[quem])
        agentes.atualizar_estado(h, "PreToolUse", "Agent", [])
        estado = self.gravado()
        estado["agentes"][-1]["branches"] = estado["agentes"][-1]["escrita"] = [f"melhoria/{quem}"]
        self.arquivo.write_text(json.dumps(estado), encoding="utf-8")

    def evento(self, nome, quem):
        super().evento(nome, agent_id=self.IDS[quem], agent_type="forge:tech-lead", transcript_path=str(self.transcript))

    def presas(self):
        return sorted(b for a in self.gravado()["agentes"] for b in a.get("escrita", []))

    def test_o_fim_de_um_solta_a_branch_dele_e_nao_a_do_outro_vivo(self):
        for quem in "AB":
            self.lancar(quem)
            self.meta(quem)
        self.evento("SubagentStart", "B")  # B inicia primeiro: pelo tipo e pela ordem levaria a reserva de A
        self.evento("SubagentStart", "A")
        self.evento("SubagentStop", "A")
        self.assertEqual(self.presas(), ["melhoria/B"])
        self.evento("SubagentStop", "B")
        self.assertEqual(self.presas(), [])

    def test_agente_sem_reserva_propria_nao_leva_a_de_outro_disparo(self):
        for quem in "AB":
            self.lancar(quem)
        self.meta("C")
        self.evento("SubagentStart", "C")
        agentes_ = {a["descricao"]: a["id"] for a in self.gravado()["agentes"]}
        self.assertEqual(agentes_, {"agente A": None, "agente B": None, "": self.IDS["C"]})

    def test_sem_meta_no_inicio_o_fim_ainda_solta_a_reserva_do_proprio_agente(self):
        for quem in "AB":
            self.lancar(quem)
        self.evento("SubagentStart", "B")  # sem meta: casa pela ordem e troca os ids
        self.evento("SubagentStart", "A")
        for quem in "AB":
            self.meta(quem)
        self.evento("SubagentStop", "A")
        self.assertEqual(self.presas(), ["melhoria/B"])

    def test_sem_tool_use_id_vale_o_id_de_antes(self):
        self.semear([self.registro(id=AID, pid=os.getpid(), escrita=["melhoria/a"]), self.registro(id=OUTRO, pid=os.getpid(), escrita=["melhoria/b"])])
        self.evento("SubagentStop", "A")  # id que nenhum registro tem: nada cai
        self.assertEqual(self.presas(), ["melhoria/a", "melhoria/b"])
        super().evento("SubagentStop", agent_id=AID)
        self.assertEqual(self.presas(), ["melhoria/b"])

    def sem_tool_use_id(self, quem):
        """A reserva de antes da versão que grava o `tool_use_id`."""
        estado = self.gravado()
        for a in estado["agentes"]:
            if a["descricao"] == f"agente {quem}":
                a.pop("tool_use_id", None)
        self.arquivo.write_text(json.dumps(estado), encoding="utf-8")

    def donos(self):
        return {a["descricao"] or "(sem reserva)": a["id"] for a in self.gravado()["agentes"]}

    def test_tool_use_id_do_disparo_fora_da_forma_nao_entra_na_reserva(self):
        for valor in ("toolu_../x", "sem-forma", 123, ""):
            with self.subTest(valor=valor):
                self.arquivo.unlink(missing_ok=True)
                entrada = {"subagent_type": "forge:tech-lead", "description": "agente X", "prompt": "sem brief"}
                agentes.atualizar_estado(self.hook(tool_name="Agent", tool_input=entrada, tool_use_id=valor), "PreToolUse", "Agent", [])
                self.assertNotIn("tool_use_id", self.gravado()["agentes"][-1])

    def test_agent_id_fora_da_forma_nao_le_o_meta(self):
        for quem in "AB":
            self.lancar(quem)
        ruim = "zzzzzzzzzzzzzzzzz"
        pasta = self.transcript.with_suffix("") / "subagents"
        (pasta / f"agent-{ruim}.meta.json").write_text(json.dumps({"toolUseId": self.USOS["B"]}), encoding="utf-8")
        super().evento("SubagentStart", agent_id=ruim, agent_type="forge:tech-lead", transcript_path=str(self.transcript))
        self.assertEqual(self.donos(), {"agente A": ruim, "agente B": None})  # sem prova, a ordem de antes: a mais antiga

    def test_tool_use_id_do_meta_fora_da_forma_deixa_o_casamento_pela_ordem(self):
        for valor in ("sem-forma", 123, None):
            with self.subTest(valor=valor):
                self.arquivo.unlink(missing_ok=True)
                self.lancar("A")
                pasta = self.transcript.with_suffix("") / "subagents"
                (pasta / f"agent-{self.IDS['A']}.meta.json").write_text(json.dumps({"toolUseId": valor}), encoding="utf-8")
                self.evento("SubagentStart", "A")
                self.assertEqual(self.donos(), {"agente A": self.IDS["A"]})

    def test_reserva_antiga_sem_tool_use_id_casa_no_inicio(self):
        self.lancar("A")
        self.sem_tool_use_id("A")
        self.meta("A")
        self.evento("SubagentStart", "A")
        self.assertEqual(self.donos(), {"agente A": self.IDS["A"]})
        self.assertEqual(self.presas(), ["melhoria/A"])

    def test_reserva_do_proprio_disparo_vem_antes_da_antiga_sem_tool_use_id(self):
        self.lancar("B")  # a antiga, mais velha: grava o tool_use_id e depois o perde
        self.sem_tool_use_id("B")
        self.lancar("A")
        for quem in "AB":
            self.meta(quem)
        self.evento("SubagentStart", "A")
        self.evento("SubagentStart", "B")
        self.evento("SubagentStop", "A")
        self.assertEqual(self.presas(), ["melhoria/B"])  # o fim de A não solta a branch de B, ainda vivo
        self.evento("SubagentStop", "B")
        self.assertEqual(self.presas(), [])

    def test_fim_sem_agent_id_nao_solta_reserva_nenhuma(self):
        self.lancar("A")
        super().evento("SubagentStop", transcript_path=str(self.transcript))
        self.assertEqual(self.presas(), ["melhoria/A"])


if __name__ == "__main__":
    unittest.main()
