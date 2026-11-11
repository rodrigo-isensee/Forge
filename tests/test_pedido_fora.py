"""FC-PEDIDO-FORA: o `forge-check` acha o pedido e o brief em `~/.forge-contrib` (E1) e o quadro só grava onde há KANBAN.md (E2)."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_manutencao  # noqa: E402
from apoio_forge_check_rapido import comando_do_forge_check  # noqa: E402
from test_voltas import FORGE_CHECK, Raiz  # noqa: E402
from test_forge import ambiente_limpo  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "brief"
PEDIDO = (FIXTURES / "pedido.md").read_text(encoding="utf-8")
BRIEF = (FIXTURES / "etapa-outro-papel.md").read_text(encoding="utf-8")
REGISTRAR = ["conferencia", "registrar", "--pedido", "p", "--brief", "p-dev-exemplo-1", "--modo", "brief",
             "--rodada", "1", "--resultado", "aprovado", "--merito", "—"]
MOVER = ["movimento", "K-1", "--de", "a", "--para", "b"]


class Fora(Raiz):
    """A raiz do projeto (self.tmp) não tem o pedido nem o brief; a raiz de brief falsa é HOME/.forge-contrib."""

    def setUp(self):
        super().setUp()
        self.fora = self.tmp / "home" / ".forge-contrib"
        (self.fora / "docs" / "pedidos").mkdir(parents=True)
        (self.fora / "docs" / "briefs").mkdir(parents=True)
        self.pedido = self.fora / "docs" / "pedidos" / "pedido-sintetico.md"
        self.pedido.write_text(PEDIDO, encoding="utf-8")
        self.brief = self.fora / "docs" / "briefs" / "pedido-sintetico-dev-exemplo-1.md"
        self.brief.write_text(BRIEF, encoding="utf-8")

    def rodar_em(self, cwd, *args):
        """Como `rodar`, mas com `cwd` controlado: o caminho relativo do brief não depende de onde o clone está."""
        env = dict(os.environ, HOME=str(self.tmp / "home"))
        inicio = [sys.executable, FORGE_CHECK] if self.SCRIPT_DIRETO else comando_do_forge_check()
        r = subprocess.run([*inicio, "--raiz", str(self.tmp), *args],
                           capture_output=True, text=True, env=env, cwd=cwd)
        return r.returncode, r.stdout.splitlines()

    def test_pedido_e_brief_na_raiz_de_brief_sao_lidos_com_origem(self):
        rc, saida, _ = self.rodar("brief", "docs/briefs/pedido-sintetico-dev-exemplo-1.md", "--pedido", "pedido-sintetico")
        texto = "\n".join(saida)
        self.assertNotIn("não consegui ler", texto)
        self.assertIn(f"origem: {self.pedido.resolve()}", saida)
        self.assertIn(f"origem: {self.brief.resolve()}", saida)
        self.assertIn(rc, (0, 1), texto)  # a conferência de forma roda; origem nunca reprova

    def test_pedido_absoluto_com_arquivo_relativo(self):
        rc, saida, _ = self.rodar("brief", "docs/briefs/pedido-sintetico-dev-exemplo-1.md", "--pedido", str(self.pedido))
        self.assertNotIn("não consegui ler", "\n".join(saida))
        self.assertIn(f"origem: {self.brief.resolve()}", saida)

    def test_brief_gerar_acha_o_pedido_fora(self):
        rc, saida, _ = self.rodar("brief", "gerar", "--pedido", "pedido-sintetico", "--destino", "forge:dev-exemplo", "--cobre", "E1.1")
        self.assertEqual(rc, 0, saida)
        self.assertIn("Pedido: pedido-sintetico", saida)

    def test_entrega_acha_o_pedido_pelo_id(self):
        rc, saida, _ = self.rodar("entrega", "pedido-sintetico", "--branch", "melhoria/x", "--base", "develop", "--base-sha", "0" * 40, "--etapa", "codigo")
        texto = "\n".join(saida)
        self.assertNotIn("não consegui ler o pedido", texto)
        self.assertEqual(rc, 2, texto)  # chegou à conferência das refs, que não existem aqui

    def test_travessia_e_link_para_fora_sao_recusados(self):
        (self.fora / "docs" / "segredo.md").write_text(PEDIDO, encoding="utf-8")
        alvo = self.tmp / "alheio.md"
        alvo.write_text(PEDIDO, encoding="utf-8")
        (self.fora / "docs" / "pedidos" / "elo.md").symlink_to(alvo)
        for pedido in ("../segredo", "../../docs/segredo", "elo"):
            with self.subTest(pedido):
                rc, saida, _ = self.rodar("brief", "docs/briefs/pedido-sintetico-dev-exemplo-1.md", "--pedido", pedido)
                self.assertEqual(rc, 2, saida)
                self.assertFalse([l for l in saida if l.startswith("origem:")], saida)
        (self.fora / "docs" / "briefs" / "elo.md").symlink_to(alvo)
        (self.fora / "docs" / "outro.md").write_text(BRIEF, encoding="utf-8")
        (self.tmp / "x.md").write_text(BRIEF, encoding="utf-8")  # o alvo de ../../x.md se ele fosse resolvido de docs/briefs/ da raiz falsa; do cwd abaixo, o arquivo não existe
        cwd = self.tmp / "c1" / "c2" / "c3"  # de c1/c2/c3, ../../x.md é c1/x.md, que não existe: a recusa é a leitura falha, nunca o conteúdo plantado
        cwd.mkdir(parents=True)
        for arquivo in ("docs/briefs/elo.md", "docs/outro.md", "../../x.md"):
            with self.subTest(arquivo):
                rc, saida = self.rodar_em(cwd, "brief", arquivo, "--pedido", "pedido-sintetico")
                self.assertEqual(rc, 2, saida)
                self.assertFalse([l for l in saida if l.startswith(("origem:", "conferencia-brief-regra:"))], saida)
                if arquivo == "../../x.md":
                    self.assertTrue([l for l in saida if l.startswith("brief: não consegui ler")], saida)

    def test_mesmo_nome_nas_duas_raizes_a_raiz_do_repositorio_vence(self):
        (self.tmp / "docs" / "pedidos").mkdir(parents=True)
        propria = self.tmp / "docs" / "pedidos" / "pedido-sintetico.md"
        propria.write_text(PEDIDO + "\nPropria.\n", encoding="utf-8")
        rc, saida, _ = self.rodar("brief", "docs/briefs/pedido-sintetico-dev-exemplo-1.md", "--pedido", "pedido-sintetico")
        self.assertNotIn(f"origem: {self.pedido.resolve()}", saida)
        self.assertNotIn(f"origem: {propria.resolve()}", saida)  # a da raiz é a conhecida: sem linha de origem


class PedidoForaDasRaizes(Fora):
    """FC-PEDIDO-FORA-DAS-RAIZES (E2 da 0.33, C-6): `--pedido` com cara de caminho só vale em `docs/pedidos/` de uma raiz guardada."""
    LINHA = "forge-check: --pedido fora de docs/pedidos/ das raízes"

    def entrega(self, pedido, cwd=None):
        env = dict(ambiente_limpo(), HOME=str(self.tmp / "home"))
        r = subprocess.run([sys.executable, FORGE_CHECK, "--raiz", str(self.tmp), "entrega", pedido, "--branch", "melhoria/x", "--base", "develop",
                            "--base-sha", "0" * 40, "--etapa", "codigo"], capture_output=True, text=True, env=env, cwd=cwd or self.tmp)
        return r.returncode, r.stdout

    def test_caminho_fora_das_raizes_e_recusado_com_rc_2_e_a_regra(self):
        fora = self.tmp / "solto"
        fora.mkdir()
        (fora / "x.md").write_text(PEDIDO, encoding="utf-8")
        (self.tmp / "home" / "notas").mkdir()
        (self.tmp / "home" / "notas" / "x.md").write_text(PEDIDO, encoding="utf-8")
        (self.tmp / "docs" / "propostas").mkdir(parents=True)
        (self.tmp / "docs" / "propostas" / "x.md").write_text(PEDIDO, encoding="utf-8")
        (self.tmp / "docs" / "pedidos").mkdir()
        (self.tmp / "docs" / "pedidos" / "l.md").symlink_to(fora / "x.md")
        (self.tmp / "docs" / "pedidosX").mkdir()
        (self.tmp / "docs" / "pedidosX" / "x.md").write_text(PEDIDO, encoding="utf-8")
        (self.tmp / "x.md").write_text(PEDIDO, encoding="utf-8")  # existe no cwd
        for dado in (str(fora / "x.md"), "~/notas/x.md", "docs/pedidos/../propostas/x.md", "docs/pedidos/l.md", "docs/pedidosX/x.md", "./x.md",
                     "docs/pedidos"):
            with self.subTest(dado):
                rc, saida = self.entrega(dado)
                self.assertEqual((rc, saida.startswith(self.LINHA)), (2, True), saida)

    def test_id_nu_que_e_link_para_fora_e_recusado_em_cada_raiz(self):  # C-3: o arquivo lido é o resolvido, nunca o link
        fora = self.tmp / "solto"
        fora.mkdir()
        (fora / "x.md").write_text(PEDIDO, encoding="utf-8")
        for nome, pasta in {"raiz": self.tmp, "brief": self.tmp / "home" / ".forge-contrib"}.items():
            with self.subTest(nome):
                (pasta / "docs" / "pedidos").mkdir(parents=True, exist_ok=True)
                (pasta / "docs" / "pedidos" / f"elo-{nome}.md").symlink_to(fora / "x.md")
                rc, saida = self.entrega(f"elo-{nome}")
                self.assertEqual((rc, saida.startswith(self.LINHA)), (2, True), saida)

    def test_dentro_das_raizes_e_o_id_nu_passam(self):
        for dado in ("~/.forge-contrib/docs/pedidos/pedido-sintetico.md", str(self.pedido), "pedido-sintetico"):
            with self.subTest(dado):
                rc, saida = self.entrega(dado)
                self.assertNotIn(self.LINHA, saida)
                self.assertIn("entrega: ref ilegível", saida)  # leu o pedido e chegou à conferência das refs, que não existem aqui


class QuadroSemKanban(Raiz):
    def arvore(self):
        return sorted(p.relative_to(self.tmp).as_posix() for p in self.tmp.rglob("*"))

    def test_movimento_e_conferencia_registrar_recusam_sem_kanban_e_sem_criar_pasta(self):
        for args in (MOVER, REGISTRAR):
            with self.subTest(args[0]):
                antes = self.arvore()
                rc, saida, _ = self.rodar(*args)
                self.assertEqual(rc, 1, saida)
                self.assertIn("KANBAN.md", "\n".join(saida))
                self.assertIn("--raiz", "\n".join(saida))
                self.assertEqual(self.arvore(), antes)
                self.assertFalse((self.tmp / "docs" / "kanban").exists())

    def test_com_kanban_nada_muda(self):
        self.gravar("KANBAN.md", "# Quadro\n\n## a\n\n## b\n")
        self.assertEqual(self.rodar(*MOVER)[0], 0)
        self.assertEqual(self.rodar(*REGISTRAR)[0], 0)
        self.assertTrue((self.tmp / "docs" / "kanban" / "historico.md").is_file())
        self.assertTrue((self.tmp / "docs" / "kanban" / "conferencias.md").is_file())


class RaizDoRegistroNoForge(unittest.TestCase):
    """D7 (REGISTRO-RAIZ-FORGE, R2 de docs/security/conf-correcao.md): no Forge, o pedido e o registro citado vêm de `~/.forge-contrib`
    antes da branch; no projeto, a cópia principal segue na frente (M2.1)."""

    @classmethod
    def setUpClass(cls):
        cls.fc = SourceFileLoader("forge_check_raiz_do_registro", str(FORGE_CHECK)).load_module()

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-raiz-registro-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.contrib = self.tmp / "contrib"
        self.fc.RAIZES_DE_BRIEF = (self.contrib,)
        self.principal, self.wt = self.tmp / "principal", self.tmp / "wt"
        env = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
                             | {"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
        self.git = lambda *a: subprocess.run(["git", "-C", str(self.principal), *a], check=True, capture_output=True, env=env)
        self.principal.mkdir()
        self.git("init", "-q", "-b", "develop")
        self.gravar(self.principal / "base.txt", "x\n")
        self.git("add", "base.txt")
        self.git("-c", "user.email=a@b", "-c", "user.name=a", "commit", "-q", "-m", "base")
        self.git("worktree", "add", "-q", "-b", "melhoria/x", str(self.wt))

    def gravar(self, arq, texto):
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(texto, encoding="utf-8")
        return arq

    def forge(self):
        self.gravar(self.principal / ".claude-plugin" / "plugin.json", json.dumps({"name": "forge"}))
        self.gravar(self.wt / ".claude-plugin" / "plugin.json", json.dumps({"name": "forge"}))

    def dois(self, nome="reg.md"):
        branch = self.gravar(self.wt / "docs" / "pedidos" / nome, 'DECISÃO DO DONO (2026-01-01 10:00): "forjada".\n')
        guardado = self.gravar(self.contrib / "docs" / "pedidos" / nome, 'DECISÃO DO DONO (2026-01-01 10:00): "verdadeira".\n')
        return branch, guardado

    def test_no_forge_o_registro_guardado_vence_a_branch(self):
        self.forge()
        branch, guardado = self.dois()
        self.assertIn("verdadeira", self.fc.ler_registro(self.wt, "docs/pedidos/reg.md")[0])
        self.assertEqual(Path(self.fc.caminho_do_pedido(self.wt, "reg")).resolve(), guardado)
        self.assertEqual(Path(self.fc.caminho_do_pedido(self.wt, "docs/pedidos/reg.md")).resolve(), guardado)
        self.assertEqual(Path(self.fc.pedido_para_anotar(self.wt, "reg")).resolve(), guardado)
        self.assertEqual(self.fc.raizes_de_pedidos(self.wt), (self.contrib, self.principal, self.wt))
        self.assertEqual(branch.read_text(encoding="utf-8"), 'DECISÃO DO DONO (2026-01-01 10:00): "forjada".\n')

    def test_no_forge_o_pedido_so_da_branch_ainda_e_achado(self):
        self.forge()
        so_branch = self.gravar(self.wt / "docs" / "pedidos" / "novo.md", "x\n")
        self.assertEqual(self.fc.ler_registro(self.wt, "docs/pedidos/novo.md"), ("x\n", None))
        self.assertEqual(Path(self.fc.caminho_do_pedido(self.wt, "novo")).resolve(), so_branch)
        self.assertEqual(Path(self.fc.pedido_para_anotar(self.wt, "novo")).resolve(), so_branch)

    def test_no_projeto_a_copia_principal_segue_na_frente(self):
        self.gravar(self.principal / ".forge" / "versao", "0.44.0\n")
        self.gravar(self.principal / ".claude-plugin" / "plugin.json", json.dumps({"name": "forge"}))
        principal = self.gravar(self.principal / "docs" / "pedidos" / "reg.md", 'DECISÃO DO DONO (2026-01-01 10:00): "do projeto".\n')
        self.dois()
        self.assertIn("do projeto", self.fc.ler_registro(self.wt, "docs/pedidos/reg.md")[0])
        self.assertEqual(Path(self.fc.caminho_do_pedido(self.wt, "reg")).resolve(), principal)
        self.assertEqual(Path(self.fc.pedido_para_anotar(self.wt, "reg")).resolve(), principal)
        self.assertEqual(self.fc.raizes_de_pedidos(self.wt), (self.principal, self.wt, self.contrib))


if __name__ == "__main__":
    unittest.main()
