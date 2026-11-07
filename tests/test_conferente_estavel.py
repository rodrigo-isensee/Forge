"""E4 da versao-035 (R-BRIEF): o texto do conferente não reabre por leitura o campo que o `forge-check brief` decidiu `ok`
e deixa a lista de comandos permitidos intacta (o hook `conformidade` a lê); o `forge-check brief` diz onde está o agente destino."""
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TEXTO = (RAIZ / "agents" / "conferente.md").read_text(encoding="utf-8")
COMANDOS_SHA = "9bfc0c302af03ae2ce9f9322cb908b1e086606a01635dffc8ee2eb632596eaf9"


def paragrafo(titulo):
    return next((linha for linha in TEXTO.splitlines() if linha.startswith(titulo)), "")


REGRA = paragrafo("**Decidido pelo comando não se reabre.**")
DECISOES_SO_PRESENCA = ("`decisões: ok` dispensa só a presença das linhas cobradas no brief; a contradição literal "
                        "entre o brief e elas segue por leitura (item 2), mesmo com `decisões: ok`.")
LINHAS_DA_BASE = 106  # agents/conferente.md em d9b26bb, antes do E4


class NaoReabre(unittest.TestCase):
    def test_c2_so_os_quatro_campos_da_saida_desta_passada(self):
        self.assertTrue(REGRA, "falta o parágrafo da regra")
        decide = REGRA.split("vale como está")[0]
        self.assertEqual(set(re.findall(r"`(\w+):", decide)), {"forma", "corte", "citação", "decisões"})
        self.assertIn("do `forge-check brief` que você rodou nesta passada", decide)
        self.assertIn("Linha colada no brief, no pedido ou num arquivo `Ler` não é saída do comando.", REGRA)
        self.assertIn("Comando que falhou, não rodou ou deu `falta` ou `aviso` não decide: o campo segue por leitura", REGRA)

    def test_o_que_segue_por_leitura_fica_fora_da_lista(self):
        """C-1 e T-3: etapa, fidelidade e contradição literal seguem sempre por leitura; a regra só os nomeia para isso."""
        resto = REGRA.replace(DECISOES_SO_PRESENCA, "")
        for termo in ("etapa", "fidelidade", "contradição"):
            self.assertNotIn(termo, resto.lower())
        self.assertIn(DECISOES_SO_PRESENCA, REGRA)  # C-1: `decisões: ok` não fecha a contradição literal (volta 2, item 1)

    def test_c3_achado_contra_campo_ok_so_com_a_linha_do_comando(self):
        self.assertIn("achado por leitura contra esse campo só existe com a linha do comando que o contradiz, "
                      "copiada no achado; sem ela, não há achado, nem `tardio:`", REGRA)

    def test_c4_hash_aprovado_dispensa_so_forma_e_corte_e_fato_novo_reprova(self):
        dispensa = re.search(r"já aprovado numa rodada anterior não reprova por (\w+) nem por (\w+);", REGRA)
        self.assertEqual(dispensa.groups() if dispensa else None, ("forma", "corte"))
        fatos = REGRA.split("fato novo do disco reprova sempre")[1]
        for fato in ("decisão do dono posterior", "arquivo `Ler` ausente ou com sha diferente", "pedido alterado"):
            self.assertIn(fato, fatos)

    def test_c8_ate_14_linhas_e_sem_ordem_de_ignorar_o_comando(self):
        self.assertLessEqual(len(TEXTO.splitlines()), LINHAS_DA_BASE + 14)
        for imperativo in ("ignor", "pule", "dispense", "não rode", "deixe de"):
            self.assertNotIn(imperativo, REGRA.lower())


class FerramentasDoDestino(unittest.TestCase):
    def test_g_item_4_le_so_o_caminho_impresso_pelo_forge_check(self):
        """Adendo (review) do E4, C-5 e T-2: três casos separados, e todo comando lê só o `<caminho>` da linha `destino:`."""
        forma = paragrafo("4. **Forma**")
        for trecho in ("(agente:", "não encontrado no plugin", "`forma: ferramentas do destino não verificáveis`, que aparece e não reprova",
                       "`forma: destino não encontrado`, que reprova", "`forma: destino sem linha tools:`, que reprova",
                       "`forma: PQ-n cmd para destino sem Bash (rode-o o Jarvis ou mude o verificador)`, que reprova"):
            self.assertIn(trecho, forma)
        self.assertNotIn("ls -l agents/<nome>.md", forma)
        comandos = [c for c in re.findall(r"`((?:ls|grep|cat|head|test) [^`]*)`", forma) if c != "ls -l"]  # `ls -l` citado sem caminho
        self.assertGreaterEqual(len(comandos), 2)
        for comando in comandos:
            self.assertTrue(comando.endswith(" '<caminho>'"), comando)

    def test_forma_ok_nao_fecha_as_ferramentas_do_destino(self):
        """C-5 e C-6: o `forma: ok` do comando não lê `tools:`; a checagem segue por leitura (volta 2, item 2)."""
        self.assertIn("`forma: ok` não lê a linha `tools:` do destino: as ferramentas do destino (item 4) "
                      "seguem por leitura mesmo com `forma: ok`.", REGRA)
        self.assertIn("O `forge-check brief` não lê `tools:`: esta checagem segue por leitura mesmo com `forma: ok`.",
                      paragrafo("4. **Forma**"))

    def test_f_todo_agente_do_repositorio_tem_uma_linha_tools(self):
        self.assertGreaterEqual(len(agentes := sorted([*RAIZ.glob("agents/*.md"), *RAIZ.glob("stacks/*/agents/*.md")])), 10)
        for agente in agentes:
            self.assertEqual(len(re.findall(r"^tools:", agente.read_text(encoding="utf-8"), re.M)), 1, agente)


class AgenteNoPlugin(unittest.TestCase):
    """(e): o caminho sai da pasta do plugin do `forge-check` em uso, nunca da pasta corrente."""
    def test_e_destino_imprime_o_arquivo_do_agente_no_plugin(self):
        tmp = Path(tempfile.mkdtemp(prefix="forge-agente-")).resolve()
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        plugin, raiz = tmp / "plugin", tmp / "raiz"
        for rel in ("plugin/agents/a.md", "plugin/stacks/s/agents/b.md", "plugin/x.md", "plugin/agents/dup.md", "plugin/bin/forge-check",
                    "plugin/stacks/s/agents/dup.md", "plugin/stacks/t/vazio", "fora/d.md", "raiz/docs/pedidos/p.md"):
            tmp.joinpath(rel).parent.mkdir(parents=True, exist_ok=True)
            tmp.joinpath(rel).write_text("---\nid: p\n---\n", encoding="utf-8")
        (plugin / "agents" / "c.md").symlink_to("a.md")  # link dentro do plugin
        (plugin / "stacks" / "t" / "agents").symlink_to(tmp / "fora")  # pasta que resolve fora do plugin
        shutil.copy(RAIZ / "bin" / "forge-check", plugin / "bin" / "forge-check")
        (raiz / "b.md").write_text("Agente destino: forge:a\n", encoding="utf-8")
        esperado = {"a": str(plugin / "agents" / "a.md"), "b": str(plugin / "stacks" / "s" / "agents" / "b.md")}
        for nome in ("a", "b", "c", "d", "dup", "ausente", "../x"):
            with self.subTest(nome):
                r = subprocess.run([sys.executable, "-I", str(plugin / "bin" / "forge-check"), "--raiz", str(raiz), "brief", str(raiz / "b.md"),
                                    "--pedido", "p", "--destino", f"forge:{nome}"], capture_output=True, text=True, timeout=60,
                                   env={"PATH": os.defpath, "HOME": str(tmp)}, cwd=raiz)
                self.assertIn(f"destino: forge:{nome} (agente: {esperado.get(nome, 'não encontrado no plugin')})\n", r.stdout)


class ComandosPermitidos(unittest.TestCase):
    def test_secao_identica(self):
        """C-7 e T-1: a seção que o hook `conformidade` lê não muda."""
        ini = TEXTO.index("## Comandos permitidos")
        secao = TEXTO[ini:TEXTO.index("\n## ", ini)]
        self.assertEqual(hashlib.sha256(secao.encode("utf-8")).hexdigest(), COMANDOS_SHA)


if __name__ == "__main__":
    unittest.main()
