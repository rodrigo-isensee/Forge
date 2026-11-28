"""H2-AUTOR-FICA-ATE-O-MERGE (v047, E2.10): o autor fica com o item até o merge. O `SubagentStop` de um agente de escrita grava
em `autores` o id dele e as branches que escrevia; o disparo de escrita numa delas, dentro de expiracao_horas, avisa (R-TETO,
código 0) que o autor pode ser retomado por `SendMessage`, sem recusar. Lápide (liberado como morto), autor ativo e prazo vencido
tiram o aviso.

Os casos de ponta a ponta são os fixtures `autor-*` de tests/hooks/agentes/ (o hook roda como o Claude Code o roda); aqui, os
ramos que o fixture não distingue: a retomada que herda as branches renova o prazo, o autor de várias branches perde só a
tomada, o id não texto fica fora do conjunto do aviso, e os dois avisos (D3 e H2) saem num JSON só.

HOOK-AGENTE-PEDIDO-GRANDE (v0481, E50.1, R-TETO): o hook `agentes` decide dentro dos 8 s com o pedido grande.

O aviso de brief vencido (D3) refaz o `corrigir_derivados` do `brief selar`; com centenas de linhas `conferida` no `## Histórico`,
o `desde_da_branch` do forge-check abria um `git` por pergunta (416 no v0481, 16 s) e o vigia recusava o disparo. O `GitEmLote` do
hook responde as mesmas perguntas com um `rev-list` por ponta e um `cat-file --batch-check` só. Aqui: a resposta é a mesma da
chamada de sempre em cada forma de pergunta, o número de processos não cresce com o pedido, e o disparo com o pedido grande sai
em tempo, com as recusas e o aviso de antes."""
import hashlib
import io
import json
import os
import subprocess
import sys
import time
import unittest
from unittest import mock
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import minimo  # noqa: E402
import test_hooks  # noqa: E402
import test_selo_e_entrega as selo  # noqa: E402  (só o módulo: as classes de teste dele não rodam de novo aqui)
from test_hooks import FIXTURES, HOOKS, Fixture  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

if str(HOOKS) not in sys.path:
    sys.path.insert(0, str(HOOKS))
import agentes  # noqa: E402

A, B = "a0123456789abcdef", "afedcba9876543210"


class PeloHook(unittest.TestCase):
    _pasta_temporaria = test_hooks.Hooks._pasta_temporaria
    executar_em_lote = test_hooks.Hooks.executar_em_lote
    executar_fixture = test_hooks.Hooks.executar_fixture
    depende_de_pid_ou_trava = staticmethod(test_hooks.Hooks.depende_de_pid_ou_trava)

    def test_fixtures_do_pedido(self):
        """Avisa com o autor retomável; libera calado com lápide, ativo, prazo vencido, outra branch, parecer e `autores` ilegível."""
        achados = sorted((FIXTURES / "agentes").glob("autor-*.json"))
        casos = [(f"agentes/{p.stem}", Fixture(p)) for p in minimo(achados, 20, "fixtures do autor retomável")]
        self.assertEqual(self.executar_em_lote(casos), len(casos), "todo caso é verificado")


class Autores(unittest.TestCase):
    def test_retomada_sem_escrita_herda_as_branches_e_renova_o_prazo(self):
        antigo = [{"id": A, "desde": 100.0, "escrita": ["melhoria/a"]}]
        self.assertEqual(agentes.guardar_autores(antigo, [{"id": A, "desde": 900.0}], 1000.0),
                         [{"id": A, "desde": 1000.0, "escrita": ["melhoria/a"]}])

    def test_id_fora_da_forma_nao_vira_autor(self):
        self.assertEqual(agentes.guardar_autores([], [{"id": "a1", "escrita": ["melhoria/a"]}], 1000.0), [])

    def test_novo_autor_tira_so_o_anterior_da_mesma_branch(self):
        autores = [{"id": B, "desde": 1.0, "escrita": ["melhoria/a"]}, {"id": B, "desde": 1.0, "escrita": ["melhoria/b"]}]
        novos = agentes.guardar_autores(autores, [{"id": A, "escrita": ["melhoria/a"]}], 2.0)
        self.assertEqual([(a["id"], a["escrita"]) for a in novos], [(B, ["melhoria/b"]), (A, ["melhoria/a"])])

    def test_autor_de_duas_branches_perde_so_a_tomada(self):
        autores = [{"id": B, "desde": 1.0, "escrita": ["melhoria/a", "melhoria/b"]}]
        novos = agentes.guardar_autores(autores, [{"id": A, "escrita": ["melhoria/a"]}], 2.0)
        self.assertEqual(novos, [{"id": B, "desde": 1.0, "escrita": ["melhoria/b"]}, {"id": A, "desde": 2.0, "escrita": ["melhoria/a"]}])

    def test_teto_proprio_de_autores(self):
        parados = [{"id": f"a{n:016x}", "escrita": [f"melhoria/{n}"]} for n in range(agentes.AUTORES_MAX + 1)]
        novos = agentes.guardar_autores([], parados, 1.0)
        self.assertEqual(len(novos), agentes.AUTORES_MAX)
        self.assertEqual(novos[-1]["escrita"], [f"melhoria/{agentes.AUTORES_MAX}"])

    def test_id_nao_texto_fica_fora_do_conjunto(self):
        autores = [{"id": A, "desde": 1.0, "escrita": ["melhoria/a"]}]
        self.assertEqual(agentes.autores_retomaveis(autores, [{"id": {"x": 1}}], [{"id": ["x"]}], {"melhoria/a"}),
                         [f"melhoria/a: {A}"])

    def test_retomada_com_entrada_fora_da_forma_nao_reserva(self):
        class Falso:
            campo = staticmethod(lambda nome: ["x"] if nome == "tool_input" else None)
        reservas = []
        agentes.reservar_retomada(Falso(), reservas, [{"id": A, "desde": 1.0, "escrita": ["melhoria/a"]}], 2.0)
        self.assertEqual(reservas, [])

    def test_prazo_unico_por_registro(self):
        """H2-RESERVA-DA-RETOMADA-PRAZO: a reserva sem início e a da retomada valem o prazo curto; o agente iniciado, o longo."""
        longo = 3600.0
        self.assertEqual(agentes.prazo_do_registro({"tipo": "Explore"}, longo), agentes.RESERVA_S)
        self.assertEqual(agentes.prazo_do_registro({"id": A, "tipo": agentes.RETOMADA}, longo), agentes.RESERVA_S)
        self.assertEqual(agentes.prazo_do_registro({"id": A, "tipo": "Explore"}, longo), longo)
        self.assertEqual(agentes.prazo_do_registro({"id": A, "tipo": agentes.RETOMADA}, 60.0), 60.0)

    def test_hora_da_recusa_da_retomada_usa_o_prazo_curto(self):
        """A hora anunciada na recusa é a da expiração real da reserva da retomada (RESERVA_S), não a de expiracao_horas."""
        class Falso:
            expira_s = staticmethod(lambda: 36000.0)
            run = staticmethod(lambda: Path("/x"))
        desde = 1_000_000.0
        reserva = {"id": A, "tipo": agentes.RETOMADA, "desde": desde, "escrita": ["melhoria/a"]}
        erro = io.StringIO()
        with redirect_stderr(erro), self.assertRaises(SystemExit):
            agentes.recusar_branch_ocupada(Falso(), [reserva], ["melhoria/a"])
        curta = agentes.time.strftime("%H:%M", agentes.time.localtime(desde + agentes.RESERVA_S))
        longa = agentes.time.strftime("%H:%M", agentes.time.localtime(desde + 36000.0))
        self.assertIn(f"expiração às {curta}", erro.getvalue())
        self.assertNotEqual(curta, longa)

    def test_inicio_sem_autor_nao_reserva_branch(self):
        """O SubagentStart de id fora de `autores` não ganha branch de escrita (só o retomado tardio a recupera)."""
        class Falso:
            campo = staticmethod(lambda nome: {"agent_id": A, "agent_type": "Explore"}.get(nome))
        registros = []
        with mock.patch.object(agentes, "da_sessao", return_value={}), mock.patch.object(agentes, "uso_do_agente", return_value=None):
            agentes.iniciar(Falso(), registros, [{"id": B, "desde": 1.0, "escrita": ["melhoria/a"]}], 2.0)
        self.assertEqual(registros, [{"id": A, "tipo": "Explore", "descricao": "", "desde": 2.0}])

    def test_lapide_e_ativo_tiram_o_autor_do_aviso(self):
        autores = [{"id": A, "desde": 1.0, "escrita": ["melhoria/a"]}]
        self.assertEqual(agentes.autores_retomaveis(autores, [], [], {"melhoria/a"}), [f"melhoria/a: {A}"])
        self.assertEqual(agentes.autores_retomaveis(autores, [], [{"id": A}], {"melhoria/a"}), [])
        self.assertEqual(agentes.autores_retomaveis(autores, [{"id": A}], [], {"melhoria/a"}), [])
        self.assertIsNone(agentes.aviso_de_autor([]))

    def test_dois_avisos_saem_num_json_so(self):
        saida, erro = io.StringIO(), io.StringIO()
        with redirect_stdout(saida), redirect_stderr(erro):
            agentes.avisar(["R-BRIEF: aviso: um", None, "R-TETO: aviso: dois"])
        self.assertEqual(json.loads(saida.getvalue()), {"systemMessage": "R-BRIEF: aviso: um R-TETO: aviso: dois"})
        self.assertEqual(erro.getvalue().splitlines(), ["R-BRIEF: aviso: um", "R-TETO: aviso: dois"])
        saida = io.StringIO()
        with redirect_stdout(saida):
            agentes.avisar([None, None])
        self.assertEqual(saida.getvalue(), "")


PROMPT = "Leia docs/briefs/exemplo-node-backend-1.md e execute."
FALSAS = 300  # linhas `conferida` de commits que não existem (outras branches do pedido, já mescladas por squash)
PROPRIAS = 12  # commits da branch, cada um com a sua linha `conferida`


class Processos(subprocess.Popen):
    """Conta os processos abertos (o `subprocess.run` do forge-check e o `Popen` do lote passam por aqui)."""
    abertos = 0

    def __init__(self, *args, **kwargs):
        Processos.abertos += 1
        super().__init__(*args, **kwargs)


class PedidoGrande(selo.Repositorio):
    def setUp(self):
        super().setUp()
        (self.proj / ".forge").mkdir()
        (self.proj / ".forge" / "versao").write_text("0.0.0\n", encoding="utf-8")
        self.proc = self.tmp / "proc"
        self.proc.mkdir()
        (self.proc / "loadavg").write_text("0.1 0.1 0.1\n", encoding="utf-8")
        (self.proc / "meminfo").write_text(f"MemTotal: {16 * 1024 * 1024} kB\nMemAvailable: {8 * 1024 * 1024} kB\n", encoding="utf-8")
        self.arq = self.brief()
        self.assertEqual(self.selar()[0], 0)
        proprias = []
        for n in range(PROPRIAS):
            self.gravar("bin/app", f"x\n{n}\n")
            self.git("add", "bin/app")
            proprias.append(self.commit(f"feat: passo {n}"))
        self.git("-c", "user.email=a@b", "-c", "user.name=a", "tag", "-a", "-m", "anotada", "anotada", proprias[3])
        self.tag = self.git("rev-parse", "anotada")
        self.arvore = self.git("rev-parse", "HEAD^{tree}")
        self.proprias, self.head = proprias, proprias[-1]
        falsas = [hashlib.sha1(str(n).encode()).hexdigest() for n in range(FALSAS)]
        linhas = [f"- 2026-01-03 10:00: entrega conferida {sha}\n" for sha in falsas[:FALSAS // 2] + proprias + falsas[FALSAS // 2:]]
        self.gravar("docs/pedidos/exemplo.md", self.pedido() + "".join(linhas))
        self.fc = selo.fc
        self.dados = self.arq.read_bytes()
        ambiente = mock.patch.dict(os.environ, {"HOME": str(self.home)})  # o git em processo sem a config global de quem roda (AR-4)
        ambiente.start()
        self.addCleanup(ambiente.stop)

    def lancar(self, prompt=PROMPT, tipo="forge:node-backend"):
        (self.proj / ".forge" / "run" / "agentes.json").unlink(missing_ok=True)
        entrada = {"hook_event_name": "PreToolUse", "tool_name": "Agent", "session_id": "s", "cwd": str(self.proj),
                   "tool_input": {"subagent_type": tipo, "description": f"d{time.monotonic_ns()}", "prompt": prompt}}
        env = dict(self.env, FORGE_PROC=str(self.proc), FORGE_NPROC="8")
        inicio = time.monotonic()
        r = subprocess.run([sys.executable, "-I", "-c", selo.LANCADOR, str(selo.HOOKS), str(selo.HOOKS / "agentes.py")],
                           input=json.dumps(entrada), cwd=self.proj, env=env, capture_output=True, text=True, timeout=120)
        return r, time.monotonic() - inicio

    def vencido(self, lote):
        with mock.patch("subprocess.Popen", Processos), mock.patch.object(agentes, "forge_check", lambda: self.fc):
            Processos.abertos = 0
            if lote:
                hook = mock.Mock(raiz=self.proj)
                linhas = [l.split(": ", 1)[1] for l in agentes.avisos_de_brief_vencido(hook, [("b", str(self.arq), self.dados)])]
                hook.registrar_erro.assert_not_called()
            else:
                linhas = self.fc.brief_vencido(self.proj, str(self.arq), self.dados)
            return linhas, Processos.abertos

    def test_mesma_resposta_em_toda_forma_de_pergunta(self):
        """Ancestral, não ancestral, tag anotada, árvore, ausente, ref por nome, faixa `a..b` e quebra de linha: como a chamada de sempre."""
        refs = [self.base, *self.proprias[::4], self.head, self.tag, self.arvore, "0" * 40, "develop", "melhoria/x",
                f"{self.base}..{self.head}", "HEAD\nHEAD"]
        e_ancestral, sha_do_commit = self.fc.e_ancestral, self.fc.sha_do_commit
        with agentes.GitEmLote(self.fc) as lote:
            for ref in refs:
                self.assertEqual(lote.sha_do_commit(self.proj, ref), sha_do_commit(self.proj, ref), ref)
                for ponta in (self.head, self.base, self.tag, self.proprias[3], "develop", f"{self.base}..{self.head}", "0" * 40):
                    self.assertEqual(lote.e_ancestral(self.proj, ref, ponta), e_ancestral(self.proj, ref, ponta), (ref, ponta))
            self.assertEqual(self.fc.e_ancestral, lote.e_ancestral)
        self.assertIs(self.fc.e_ancestral, e_ancestral)  # a saída devolve as originais
        self.assertIs(self.fc.sha_do_commit, sha_do_commit)
        self.assertTrue(e_ancestral(self.proj, self.tag, self.head))  # o caso que só a volta à chamada de sempre acerta

    def test_o_lote_ignora_o_git_do_ambiente(self):
        """Como o `git` do forge-check, o `cat-file` do lote sai sem as variáveis GIT_* herdadas (aqui, um GIT_DIR que não existe)."""
        with mock.patch.dict(os.environ, {"GIT_DIR": str(self.tmp / "nada")}), agentes.GitEmLote(self.fc) as lote:
            self.assertEqual(lote.sha_do_commit(self.proj, self.head), self.head)

    def test_o_aviso_e_o_mesmo_com_processos_que_nao_crescem_com_o_pedido(self):
        self.rodar("anotar", "--pedido", "exemplo", "--tipo", "decisao", "--confere", "mede", "--literal", "outra regra geral")
        self.dados = self.arq.read_bytes()
        sem_lote, antes = self.vencido(lote=False)
        com_lote, depois = self.vencido(lote=True)
        self.assertEqual(com_lote, sem_lote)
        self.assertTrue(any("hash das decisões" in l for l in com_lote), com_lote)
        self.assertGreater(antes, FALSAS, "sem o lote, um processo por linha do pedido")
        self.assertLessEqual(depois, 20, f"com o lote, {depois} processos para {FALSAS + PROPRIAS} linhas")

    def test_disparo_com_o_pedido_grande_sai_no_prazo_e_as_recusas_seguem(self):
        r, segundos = self.lancar()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("R-TETO", r.stderr)
        self.assertLess(segundos, agentes.PRAZO_DO_HOOK_S)
        r, _ = self.lancar(tipo="forge:tech-lead")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("o brief é para `node-backend`", r.stderr)
        self.rodar("anotar", "--pedido", "exemplo", "--tipo", "decisao", "--confere", "mede", "--literal", "outra regra geral")
        r, segundos = self.lancar()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("R-BRIEF: aviso: brief vencido", r.stderr)
        self.assertLess(segundos, agentes.PRAZO_DO_HOOK_S)
        self.arq.write_text(self.arq.read_text(encoding="utf-8") + "editado depois\n", encoding="utf-8")
        r, _ = self.lancar()
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("mudou depois do selo", r.stderr)



if __name__ == "__main__":
    unittest.main()
