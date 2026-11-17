"""H2-AUTOR-FICA-ATE-O-MERGE (v047, E2.10): o autor fica com o item até o merge. O `SubagentStop` de um agente de escrita grava
em `autores` o id dele e as branches que escrevia; o disparo de escrita numa delas, dentro de expiracao_horas, avisa (R-TETO,
código 0) que o autor pode ser retomado por `SendMessage`, sem recusar. Lápide (liberado como morto), autor ativo e prazo vencido
tiram o aviso.

Os casos de ponta a ponta são os fixtures `autor-*` de tests/hooks/agentes/ (o hook roda como o Claude Code o roda); aqui, os
ramos que o fixture não distingue: a retomada que herda as branches renova o prazo, o autor de várias branches perde só a
tomada, o id não texto fica fora do conjunto do aviso, e os dois avisos (D3 e H2) saem num JSON só."""
import io
import json
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import minimo  # noqa: E402
import test_hooks  # noqa: E402
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


if __name__ == "__main__":
    unittest.main()
