"""F4 do estudo de atrito (v0481 E34.1 e E34.6): o aviso de time parado conta também o PR aberto sem agente vivo na branch
dele (com vaga livre no teto do R-TETO) e a instância presa há mais de 10 minutos, e diz o papel a disparar. Sem rede no hook:
o `vigia` lê a lista `prs-abertos.json` que o `forge-check status` e o `proximo` gravam (`bin/forge_estado.py`). Em processo:
o gh é um falso; registro, lista, transcript e quadro são arquivos de uma pasta temporária."""
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "hooks"))
sys.path.insert(0, str(RAIZ / "bin"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import agentes  # noqa: E402
import forge_estado as E  # noqa: E402
import vigia  # noqa: E402
from ambiente_git import sem_manutencao  # noqa: E402
from gh_falso import pasta_com_gh  # noqa: E402
from test_hooks import REASON_DO_TIME_PARADO  # noqa: E402

AID = "a" + "1" * 16
LISTA_REAL = vigia.lista_de_prs  # a `Pasta` a troca pela da pasta temporária


def pr(numero=7, head="melhoria/x", base="develop", checks=(), arquivos=(), titulo="feat: x", rotulos=(),
       mergeable="MERGEABLE", fork=False):
    return {"number": numero, "headRefName": head, "baseRefName": base, "mergeable": mergeable, "title": titulo,
            "isCrossRepository": fork, "labels": [{"name": r} for r in rotulos], "files": [{"path": a} for a in arquivos],
            "statusCheckRollup": [{"name": n, "status": "COMPLETED", "conclusion": c} for n, c in checks]}


VERDE = (("bateria", "SUCCESS"), ("bateria (pareceres)", "SUCCESS"), ("catraca", "SUCCESS"), ("testes", "SUCCESS"))


class FalsoHook:
    def __init__(self, agente="forge:jarvis"):
        self.entrada = {"hook_event_name": "Stop", "session_id": "s1", "agent_type": agente}
        self.erros = []

    def campo(self, chave):
        return self.entrada.get(chave)

    def expira_s(self):
        return 12 * 3600

    def registrar_erro(self, erro):
        self.erros.append(erro)


class PapelDoPr(unittest.TestCase):
    def test_tudo_verde_pede_integracao(self):
        self.assertEqual(E.papel_do_pr(pr(checks=VERDE)), "integração")

    def test_pr_de_fork_ou_sem_o_campo_fica_fora(self):  # S1 da segurança (1744c8e): #7 sem check, #8 com ACTION_REQUIRED
        self.assertIsNone(E.papel_do_pr(pr(7, fork=True)))
        self.assertIsNone(E.papel_do_pr(pr(8, fork=True, checks=(("testes", "ACTION_REQUIRED"),))))
        sem_campo = pr(checks=VERDE)
        del sem_campo["isCrossRepository"]
        self.assertIsNone(E.papel_do_pr(sem_campo))
        self.assertIsNone(E.papel_do_pr(pr(checks=VERDE, fork=None)))

    def test_base_main_espera_so_o_dono(self):
        self.assertIsNone(E.papel_do_pr(pr(base="main", checks=VERDE)))

    def test_conflito_pede_o_autor(self):
        self.assertEqual(E.papel_do_pr(pr(checks=VERDE, mergeable="CONFLICTING")), "autor")

    def test_check_que_nao_e_portao_reprovado_pede_o_autor(self):
        self.assertEqual(E.papel_do_pr(pr(checks=(("testes", "FAILURE"), ("bateria (pareceres)", "FAILURE")))), "autor")

    def test_check_pendente_espera_o_ci(self):
        checks = [{"name": "testes", "status": "IN_PROGRESS", "conclusion": None}]
        self.assertIsNone(E.papel_do_pr({**pr(), "statusCheckRollup": checks}))

    def test_parecer_ausente_pede_os_portoes_que_faltam(self):
        falho = (("bateria (pareceres)", "FAILURE"),)
        self.assertEqual(E.papel_do_pr(pr(checks=falho)), "review/QA/segurança")
        self.assertEqual(E.papel_do_pr(pr(checks=falho, arquivos=("docs/reviews/p.md", "hooks/x.py"))), "QA/segurança")

    def test_parecer_reprovado_com_os_tres_presentes_pede_o_autor(self):
        arquivos = ("docs/reviews/p.md", "docs/qa/p.md", "docs/security/p.md")
        self.assertEqual(E.papel_do_pr(pr(checks=(("bateria (pareceres)", "FAILURE"),), arquivos=arquivos)), "autor")

    def test_afrouxa_regra_sem_rotulo_espera_o_dono(self):
        titulo = "feat: x [afrouxa-regra: ADR 0003]"
        self.assertIsNone(E.papel_do_pr(pr(checks=VERDE, titulo=titulo)))
        self.assertEqual(E.papel_do_pr(pr(checks=VERDE, titulo=titulo, rotulos=("afrouxa-regra",))), "integração")

    def test_lista_fora_da_forma_do_gh_e_ignorada(self):
        self.assertEqual(E.papel_do_pr({**pr(), "statusCheckRollup": None, "labels": "x"}), "integração")
        falho = pr(checks=(("bateria (pareceres)", "FAILURE"),), arquivos=("docs/qa/p.md",))
        falho["statusCheckRollup"].append("lixo")
        falho["files"].append("docs/reviews/lixo.md")
        self.assertEqual(E.papel_do_pr(falho), "review/segurança")

    def test_catraca_reprovada_pede_o_autor(self):
        self.assertEqual(E.papel_do_pr(pr(checks=(("catraca", "FAILURE"),))), "autor")

    def test_todo_papel_possivel_esta_na_lista_do_vigia(self):
        arquivos = ("docs/reviews/p.md", "docs/qa/p.md", "docs/security/p.md")
        vistos = {E.papel_do_pr(pr(checks=(("bateria (pareceres)", "FAILURE"),), arquivos=sub))
                  for sub in ((), *((a,) for a in arquivos), *((a, b) for a in arquivos for b in arquivos if a < b), arquivos)}
        self.assertEqual(vistos | {"integração"}, vigia.PAPEIS)


class Pasta(unittest.TestCase):
    def setUp(self):
        self.pasta = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.pasta, ignore_errors=True)
        self.lista = self.pasta / vigia.NOME_DA_LISTA
        self.agora = time.time()
        for alvo, nome, valor in ((agentes, "ler_config", lambda _h: {}),
                                  (agentes, "calcular_teto", lambda _c, ritmo=None: (2, "")),
                                  (vigia, "lista_de_prs", lambda _r: self.lista)):
            remendo = mock.patch.object(alvo, nome, valor)
            remendo.start()
            self.addCleanup(remendo.stop)

    def gravar(self, prs, ha_s=0, gravado_em=None):
        dados = {"versao": 1, "gravado_em": int(self.agora - ha_s) if gravado_em is None else gravado_em, "prs": prs}
        self.lista.write_text(json.dumps(dados), encoding="utf-8")


def item(numero=7, head="melhoria/x", papel="integração"):
    return {"number": numero, "head": head, "papel": papel}


class ListaEmDisco(Pasta):
    def test_lista_nova_entra_em_ordem_de_numero(self):
        self.gravar([item(9, "melhoria/b", "autor"), item(7)])
        self.assertEqual(vigia.prs_parados(FalsoHook(), self.pasta, [], self.agora), ["#7 integração", "#9 autor"])

    def test_vencida_ausente_e_no_futuro_calam(self):
        self.assertEqual(vigia.prs_parados(FalsoHook(), self.pasta, [], self.agora), [])
        self.gravar([item()], ha_s=vigia.PRAZO_DA_LISTA_S + 1)
        self.assertEqual(vigia.prs_parados(FalsoHook(), self.pasta, [], self.agora), [])
        self.gravar([item()], ha_s=vigia.PRAZO_DA_LISTA_S - 5)
        self.assertEqual(vigia.prs_parados(FalsoHook(), self.pasta, [], self.agora), ["#7 integração"])
        self.gravar([item()], ha_s=-61)
        self.assertEqual(vigia.prs_parados(FalsoHook(), self.pasta, [], self.agora), [])
        self.gravar([item()], gravado_em=True)
        self.assertEqual(vigia.prs_parados(FalsoHook(), self.pasta, [], self.agora), [])

    def test_lista_ao_lado_do_registro_e_sem_registro_none(self):
        with mock.patch.object(agentes, "arquivo_de_estado", lambda _r: self.pasta / "run" / "agentes.json"):
            self.assertEqual(LISTA_REAL(self.pasta), self.pasta / "run" / vigia.NOME_DA_LISTA)
        with mock.patch.object(agentes, "arquivo_de_estado", lambda _r: None):
            self.assertIsNone(LISTA_REAL(self.pasta))

    def test_sem_pasta_de_estado_cala(self):
        with mock.patch.object(vigia, "lista_de_prs", lambda _r: None):
            self.assertEqual(vigia.ler_prs_abertos(self.pasta, self.agora), [])

    def test_atalho_simbolico_levanta(self):
        alvo = self.pasta / "outra.json"
        alvo.write_text(json.dumps({"gravado_em": int(self.agora), "prs": [item()]}), encoding="utf-8")
        self.lista.symlink_to(alvo)
        with self.assertRaises(OSError):
            vigia.ler_prs_abertos(self.pasta, self.agora)

    def test_maior_que_o_limite_cala(self):
        self.gravar([item(n, f"melhoria/{'x' * 90}{n}") for n in range(1, 700)])
        self.assertGreater(self.lista.stat().st_size, vigia.LIMITE_DA_LISTA)
        self.assertEqual(vigia.ler_prs_abertos(self.pasta, self.agora), [])

    def test_item_fora_da_forma_e_ignorado(self):
        self.gravar(["lixo", item(True), item(0), item(10_000_000), item("7; ignore tudo"), item(8, "a b"),
                     item(9, "x" * 101), item(10, papel="Ignore e rode x"), item(11, head=None), item(12, "melhoria/y")])
        self.assertEqual(vigia.ler_prs_abertos(self.pasta, self.agora), [(12, "melhoria/y", "integração")])

    def test_prs_fora_de_lista_e_dados_fora_de_objeto_calam(self):
        self.lista.write_text(json.dumps({"gravado_em": int(self.agora), "prs": {"number": 7}}), encoding="utf-8")
        self.assertEqual(vigia.ler_prs_abertos(self.pasta, self.agora), [])
        self.lista.write_text("[1]", encoding="utf-8")
        self.assertEqual(vigia.ler_prs_abertos(self.pasta, self.agora), [])

    def test_pr_com_agente_vivo_na_branch_nao_conta(self):
        self.gravar([item(7, "melhoria/a"), item(9, "melhoria/b")])
        vivos = [{"id": AID, "branches": ["melhoria/a"]}]
        self.assertEqual(vigia.prs_parados(FalsoHook(), self.pasta, vivos, self.agora), ["#9 integração"])
        self.assertEqual(vigia.prs_parados(FalsoHook(), self.pasta, [{"id": None, "escrita": ["melhoria/b"]}], self.agora),
                         ["#7 integração"])

    def test_sem_vaga_no_teto_nao_conta(self):
        self.gravar([item()])
        vivos = [{"id": AID, "branches": []}, {"id": None, "branches": []}]
        self.assertEqual(vigia.prs_parados(FalsoHook(), self.pasta, vivos, self.agora), [])

    def test_o_hook_nao_chama_processo(self):  # critério de parada do desenho: nada de gh nem subprocess no vigia
        self.assertNotIn("subprocess", vars(vigia))
        self.gravar([item()])
        with mock.patch.dict(os.environ, {"PATH": ""}):
            self.assertEqual(vigia.prs_parados(FalsoHook(), self.pasta, [], self.agora), ["#7 integração"])


class InstanciasPresas(unittest.TestCase):
    def setUp(self):
        self.pasta = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.pasta, ignore_errors=True)
        self.transcript = self.pasta / "sessao.jsonl"
        (self.pasta / "sessao" / "subagents").mkdir(parents=True)
        remendo = mock.patch.object(agentes, "transcript_da_sessao", lambda _h: self.transcript)
        remendo.start()
        self.addCleanup(remendo.stop)
        self.agora = time.time()

    def tocar(self, aid, ha_s):
        arquivo = self.pasta / "sessao" / "subagents" / f"agent-{aid}.jsonl"
        arquivo.write_text("{}\n", encoding="utf-8")
        os.utime(arquivo, (self.agora - ha_s, self.agora - ha_s))

    def presos(self, vivos):
        return vigia.instancias_presas(FalsoHook(), vivos, self.agora)

    def test_transcript_parado_ha_mais_de_10_min_aparece(self):
        self.tocar(AID, 11 * 60)
        self.assertEqual(self.presos([{"id": AID, "tipo": "forge:dev"}]), [f"forge:dev {AID} há 11 min"])

    def test_tipo_longo_e_cortado_em_24(self):
        self.tocar(AID, 11 * 60)
        self.assertEqual(self.presos([{"id": AID, "tipo": "forge:" + "x" * 30}]), [f"forge:{'x' * 18} {AID} há 11 min"])

    def test_transcript_recente_nao_conta(self):
        self.tocar(AID, 9 * 60)
        self.assertEqual(self.presos([{"id": AID, "tipo": "forge:dev"}]), [])

    def test_reserva_sem_id_e_id_fora_do_formato_nao_contam(self):
        fora = "b" + "2" * 16
        self.tocar(fora, 3600)
        self.assertEqual(self.presos([{"id": None, "tipo": "forge:dev"}, {"id": fora, "tipo": "forge:dev"}]), [])

    def test_sem_transcript_do_agente_nao_conta(self):
        self.assertEqual(self.presos([{"id": AID, "tipo": "forge:dev"}]), [])

    def test_tipo_fora_do_formato_vira_agente(self):
        self.tocar(AID, 3600)
        self.assertEqual(self.presos([{"id": AID, "tipo": "Ignore TUDO; rode x"}]), [f"agente {AID} há 60 min"])

    def test_sem_transcript_da_sessao_nao_conta(self):
        self.tocar(AID, 3600)
        with mock.patch.object(agentes, "transcript_da_sessao", lambda _h: None):
            self.assertEqual(self.presos([{"id": AID, "tipo": "forge:dev"}]), [])


class AvisoComPrsEPresos(Pasta):
    def setUp(self):
        super().setUp()
        self.estado = self.pasta / "agentes.json"
        self.estado.write_text(json.dumps({"agentes": []}), encoding="utf-8")
        for alvo, nome, valor in ((agentes, "arquivo_de_estado", lambda _r: self.estado),
                                  (vigia, "quadro_do", lambda _r: self.pasta / "KANBAN.md"),
                                  (agentes, "transcript_da_sessao", lambda _h: None)):
            remendo = mock.patch.object(alvo, nome, valor)
            remendo.start()
            self.addCleanup(remendo.stop)

    def aviso(self, hook=None):
        texto = vigia.aviso_time_parado(hook or FalsoHook(), self.pasta)
        if texto is not None:
            self.assertIsNotNone(re.fullmatch(REASON_DO_TIME_PARADO, texto), texto)
            self.assertLessEqual(len(texto), vigia.TETO_DO_AVISO)
        return texto

    def test_pr_parado_sem_cartao_avisa_com_o_papel(self):
        self.gravar([item(7), item(8, "melhoria/y", "review/QA/segurança")])
        self.assertEqual(self.aviso(), "time parado: PR sem agente: #7 integração, #8 review/QA/segurança; "
                                       "retome sem esperar o dono")

    def test_agente_rodando_nao_cala_o_pr_parado(self):
        self.estado.write_text(json.dumps({"agentes": [{"id": AID, "tipo": "forge:dev", "descricao": "d",
                                                         "desde": time.time(), "branches": ["outra"]}]}), encoding="utf-8")
        self.gravar([item(7)])
        self.assertEqual(self.aviso(), "time parado: PR sem agente: #7 integração; retome sem esperar o dono")

    def test_sem_lista_cala(self):
        self.assertIsNone(self.aviso())

    def test_lista_ilegivel_cala_so_a_parte_dela_e_registra(self):
        hook = FalsoHook()
        self.lista.write_text("não é json", encoding="utf-8")
        self.assertIsNone(self.aviso(hook))
        self.assertEqual(len(hook.erros), 1)

    def test_cinquenta_prs_cabem_no_teto(self):  # S1 do review (1744c8e): 1353 caracteres com 50 PRs
        self.gravar([item(n, f"melhoria/p{n}", "review/QA/segurança") for n in range(1000001, 1000051)])
        self.assertEqual(self.aviso(), "time parado: PR sem agente: #1000001 review/QA/segurança, #1000002 review/QA/segurança, "
                                       "#1000003 review/QA/segurança e mais 47; retome sem esperar o dono")

    def test_preso_aparece_no_aviso_ate_um(self):
        with mock.patch.object(vigia, "instancias_presas", lambda *_a: [f"forge:dev {AID} há 30 min"] * 2):
            self.assertEqual(self.aviso(), f"time parado: preso há mais de 10 min: forge:dev {AID} há 30 min e mais 1; "
                                           "retome sem esperar o dono")

    def test_acima_do_teto_a_ultima_parte_sai_inteira(self):
        (self.pasta / "KANBAN.md").write_text(
            "## Pronto para fazer\n| ID | Cartão | Pedido | Responsável | Entrou | Na coluna desde | Obs. |\n|---|---|---|---|---|---|---|\n"
            + "".join(f"| ABCDEFGHIJKLMNO{i} | c | p | dev | d | d | |\n" for i in range(10)), encoding="utf-8")
        self.gravar([item(n, f"melhoria/p{n}", "review/QA/segurança") for n in range(9999991, 10000000)])
        preso = f"{'forge:' + 'x' * 18} {AID} há 99999 min"
        with mock.patch.object(vigia, "instancias_presas", lambda *_a: [preso] * 10):
            texto = self.aviso()
        self.assertTrue(texto.startswith("time parado: 10 cartões disponíveis, primeiro ABCDEFGHIJKLMNO0; PR sem agente: #9999991"))
        self.assertNotIn("preso", texto)
        self.assertTrue(texto.endswith("; retome sem esperar o dono"))


class GravacaoDaLista(Pasta):
    def test_grava_so_o_pr_com_papel_fora_o_fork_e_em_0600(self):
        E.gravar_prs_abertos(self.lista, [pr(7, checks=VERDE), pr(8, fork=True), pr(9, base="main")], 1_800_000_000)
        dados = json.loads(self.lista.read_text(encoding="utf-8"))
        self.assertEqual(dados, {"versao": 1, "gravado_em": 1_800_000_000,
                                 "prs": [{"number": 7, "head": "melhoria/x", "papel": "integração"}]})
        self.assertEqual(stat.S_IMODE(self.lista.stat().st_mode), 0o600)

    def test_sem_pasta_ou_sem_caminho_nao_grava(self):
        E.gravar_prs_abertos(self.pasta / "nao-existe" / vigia.NOME_DA_LISTA, [pr(7, checks=VERDE)], 1)
        E.gravar_prs_abertos(None, [pr(7, checks=VERDE)], 1)
        self.assertFalse((self.pasta / "nao-existe").exists())

    def test_status_grava_a_lista_do_contexto(self):
        ctx = {"gh_json": lambda _r, *a: ([pr(7, checks=VERDE)], ""), "lista_de_prs": self.lista}
        E.prs_abertos(ctx, self.pasta, E.dt.datetime.fromtimestamp(self.agora, E.dt.timezone.utc))
        self.assertEqual(vigia.prs_parados(FalsoHook(), self.pasta, [], self.agora), ["#7 integração"])

    def test_proximo_renova_so_a_lista_vencida_ou_ausente(self):
        chamadas = []

        def gh_json(_raiz, *args):
            chamadas.append(args)
            return [pr(7, checks=VERDE)], ""

        E.renovar_prs_abertos(self.pasta, gh_json)
        self.assertEqual(len(chamadas), 1)
        self.assertIn("isCrossRepository", chamadas[0][-1])
        E.renovar_prs_abertos(self.pasta, gh_json)
        self.assertEqual(len(chamadas), 1, "lista nova: sem gh")
        velho = time.time() - vigia.PRAZO_DA_LISTA_S - 5
        os.utime(self.lista, (velho, velho))
        E.renovar_prs_abertos(self.pasta, gh_json)
        self.assertEqual(len(chamadas), 2)

    def test_proximo_com_gh_falho_nao_grava(self):
        for resposta in ((None, "sem rede"), ({"number": 1}, ""), ([{"number": "1"}], "")):
            E.renovar_prs_abertos(self.pasta, lambda _r, *_a, resposta=resposta: resposta)
        self.assertFalse(self.lista.exists())
        with mock.patch.object(vigia, "lista_de_prs", lambda _r: None):
            E.renovar_prs_abertos(self.pasta, lambda *_a: self.fail("sem caminho: sem gh"))


class ProximoPeloForgeCheck(unittest.TestCase):
    def test_proximo_grava_a_lista_vencida_pelo_gh(self):
        raiz = Path(tempfile.mkdtemp(prefix="forge-f4-"))
        self.addCleanup(shutil.rmtree, raiz, ignore_errors=True)
        ambiente = sem_manutencao({**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"})
        subprocess.run(["git", "init", "-q", str(raiz)], check=True, capture_output=True, env=ambiente)
        (raiz / ".forge" / "run").mkdir(parents=True)
        resposta = json.dumps([pr(7, checks=VERDE), pr(8, fork=True)])
        gh = pasta_com_gh(f"cat <<'FIM'\n{resposta}\nFIM\n")
        ambiente = {**ambiente, "PATH": f"{gh}{os.pathsep}{ambiente.get('PATH', '')}", "HOME": str(raiz / "casa")}
        subprocess.run([sys.executable, "-I", str(RAIZ / "bin" / "forge-check"), "--raiz", str(raiz), "proximo", "p1"],
                       capture_output=True, text=True, env=ambiente, timeout=60)
        dados = json.loads((raiz / ".forge" / "run" / vigia.NOME_DA_LISTA).read_text(encoding="utf-8"))
        self.assertEqual(dados["prs"], [{"number": 7, "head": "melhoria/x", "papel": "integração"}])


if __name__ == "__main__":
    unittest.main()
