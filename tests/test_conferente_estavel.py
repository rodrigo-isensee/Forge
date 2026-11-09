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
COMANDOS_SHA = "d4073204714c6cc0852d2f8ae1c08baffe999e82f8ab508fed56884d9824151b"  # 0.43.1: + `entrega --pedido ... --sem-gravar`


def paragrafo(titulo):
    return next((linha for linha in TEXTO.splitlines() if linha.startswith(titulo)), "")


class ConferenteOpcional(unittest.TestCase):
    """0.43.1 (decisões 1 e 3 do dono): a forma é do `forge-check brief selar` e a entrega conferida é do `forge-check entrega`;
    o conferente fica opcional, para dúvida de conteúdo. Os testes do E4 da versao-035 (o que o conferente não reabre por leitura
    na saída do `forge-check brief`, as ferramentas do destino) descreviam o conferente que conferia a forma e saem com ele."""

    def test_nao_reabre_o_que_o_selo_decidiu(self):
        passo = paragrafo("1. `cat` do `Arquivo:` e do pedido.")
        self.assertIn("O resto da saída já foi decidido no selo: não o reabra.", passo)
        self.assertIn("forma: brief diferente do arquivo", passo)
        self.assertIn("Você não refaz o que elas decidem e não reprova por forma.", TEXTO)

    def test_fidelidade_e_contradicao_seguem_por_leitura(self):
        self.assertIn("**Fidelidade:**", TEXTO)
        self.assertIn("`decisões: contradiz \"<trecho>\" (<arquivo>:<linha>)`", TEXTO)

    def test_nao_grava_a_entrega_conferida_nem_roda_a_suite(self):
        self.assertIn("`forge-check entrega --pedido` sem `--sem-gravar` grava a linha `entrega conferida`, que não é sua (o hook barra).", TEXTO)
        self.assertIn("Não rode a suíte (`python3 -m unittest`)", TEXTO)

    def test_texto_curto(self):  # decisão 11: de 29,9 mil caracteres para menos de um terço
        self.assertLess(len(TEXTO), 9000)

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
                    "plugin/stacks/s/agents/dup.md", "plugin/stacks/t/vazio", "fora/d.md", "raiz/docs/pedidos/p.md", "raiz/b.md"):
            tmp.joinpath(rel).parent.mkdir(parents=True, exist_ok=True)
            tmp.joinpath(rel).write_text("---\nid: p\n---\n", encoding="utf-8")
        (plugin / "agents" / "c.md").symlink_to("a.md")  # link dentro do plugin
        (plugin / "stacks" / "t" / "agents").symlink_to(tmp / "fora")  # pasta que resolve fora do plugin
        shutil.copy(RAIZ / "bin" / "forge-check", plugin / "bin" / "forge-check")
        esperado = {"a": str(plugin / "agents" / "a.md"), "b": str(plugin / "stacks" / "s" / "agents" / "b.md")}
        for nome in ("a", "b", "c", "d", "dup", "ausente", "../x", ""):  # "": sem --destino nem `Agente destino:`
            with self.subTest(nome):
                r = subprocess.run([sys.executable, "-I", str(plugin / "bin" / "forge-check"), "--raiz", str(raiz), "brief", str(raiz / "b.md"),
                                    "--pedido", "p", *(["--destino", f"forge:{nome}"] if nome else [])], capture_output=True, text=True, timeout=60,
                                   env={"PATH": os.defpath, "HOME": str(tmp)}, cwd=raiz)
                linha = f"destino: forge:{nome} (agente: {esperado.get(nome, 'não encontrado no plugin')})" if nome else "destino: não verificável"
                self.assertIn(linha, r.stdout)


class ComandosPermitidos(unittest.TestCase):
    def test_secao_identica(self):
        """C-7 e T-1: a seção que o hook `conformidade` lê não muda."""
        ini = TEXTO.index("## Comandos permitidos")
        secao = TEXTO[ini:TEXTO.index("\n## ", ini)]
        self.assertEqual(hashlib.sha256(secao.encode("utf-8")).hexdigest(), COMANDOS_SHA)


if __name__ == "__main__":
    unittest.main()
