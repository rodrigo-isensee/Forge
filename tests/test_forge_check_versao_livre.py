"""AV4(b) (0.45.6, E2.1): a revalidação do parecer (bin/forge-check, `commit_vale` e `forge-check pr`) não pede parecer novo
quando o delta depois dele é só versão ou changelog: no `.claude-plugin/plugin.json`, só o campo `version`; o `CHANGELOG.md`; e o
fragmento de `changelog.d/` apagado pela release. Qualquer outro campo do plugin.json, o modo dele, JSON ilegível ou com chave
repetida, e o fragmento de outro pedido mudado (não apagado) seguem desatualizando."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_manutencao  # noqa: E402

AQUI = Path(__file__).resolve().parent
fc = SourceFileLoader("forge_check_versao_livre", str(AQUI.parent / "bin" / "forge-check")).load_module()

PLUGIN = ".claude-plugin/plugin.json"
MANIFESTO = {"name": "forge", "version": "1.0.0", "description": "a fábrica", "hooks": "./hooks/hooks.json"}


class VersaoLivre(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.git("init", "-q", "-b", "develop")
        self.manifesto(MANIFESTO)
        self.escreve("src.txt", "código\n")
        self.escreve("CHANGELOG.md", "# Changelog\n\n## [Não publicado]\n\n## [1.0.0]\n")
        self.commit("base")
        self.git("switch", "-q", "-c", "ramo")
        self.escreve("src.txt", "código da branch\n")
        self.escreve("changelog.d/outra.md", "- Corrigido: de outro pedido\n")
        self.parecer = self.commit("trabalho revisado")

    def git(self, *args):
        env = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith("GIT_")})
        r = subprocess.run(["git", "-C", str(self.dir), "-c", "user.name=t", "-c", "user.email=t@t",
                            "-c", "commit.gpgsign=false", *args], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def escreve(self, nome, texto):
        (self.dir / nome).parent.mkdir(parents=True, exist_ok=True)
        (self.dir / nome).write_text(texto)

    def manifesto(self, objeto, nome=PLUGIN):
        self.escreve(nome, json.dumps(objeto, indent=2, ensure_ascii=False) + "\n")

    def commit(self, msg):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", msg)
        return self.git("rev-parse", "HEAD")

    def vale(self):
        return fc.commit_vale(self.dir, self.parecer, "HEAD")

    def desatualizados_no_pr(self):
        self.escreve("docs/reviews/ramo.md", f"---\ntipo: review\ncontrato: 1\npedido: ramo\nbranch: ramo\ncommit: {self.parecer}\n"
                                             "parecer: aprovado\nrevisor: forge:tech-lead\ndata: 2026-11-10\n---\n# x\n")
        self.commit("parecer")
        return [l for l in fc.cmd_pr(self.dir, "ramo", "HEAD") if "desatualizado" in l]

    def test_so_a_versao_do_plugin_nao_pede_parecer(self):
        self.manifesto({**MANIFESTO, "version": "1.0.1"})
        self.commit("versão")
        self.assertIsNone(self.vale())

    def test_versao_e_outro_campo_pedem_parecer(self):
        self.manifesto({**MANIFESTO, "version": "1.0.1", "hooks": "./outro.json"})
        self.commit("versão e hooks")
        self.assertIn(f"desatualizado: {PLUGIN} mudou", self.vale() or "")

    def test_booleano_trocado_por_numero_pede_parecer(self):
        """Segurança A1 (junção 0.45.6): no dict do Python true == 1 == 1.0; a troca de tipo é mudança de campo."""
        for antes, depois in ((True, 1), (1, 1.0)):
            with self.subTest(antes=antes, depois=depois):
                self.manifesto({**MANIFESTO, "strict": antes})
                self.parecer = self.commit(f"strict {antes!r}")
                self.manifesto({**MANIFESTO, "version": "1.0.1", "strict": depois})
                self.commit(f"versão e strict {depois!r}")
                self.assertIn(f"desatualizado: {PLUGIN} mudou", self.vale() or "")

    def test_outro_campo_sem_versao_pede_parecer(self):
        self.manifesto({**MANIFESTO, "description": "outra"})
        self.commit("descrição")
        self.assertIn(f"desatualizado: {PLUGIN} mudou", self.vale() or "")

    def test_ordem_e_espaco_do_json_nao_contam(self):
        self.escreve(PLUGIN, json.dumps(dict(reversed(list({**MANIFESTO, "version": "2.0.0"}.items()))), ensure_ascii=False))
        self.commit("versão, outra forma")
        self.assertIsNone(self.vale())

    def test_chave_repetida_pede_parecer(self):  # o último valor vence no json.loads: a chave escondida não passa
        texto = json.dumps({**MANIFESTO, "version": "1.0.1"}, ensure_ascii=False)
        self.escreve(PLUGIN, texto[:-1] + ', "hooks": "./hooks/hooks.json"}')
        self.commit("hooks repetido")
        self.assertIn(f"desatualizado: {PLUGIN} mudou", self.vale() or "")

    def test_json_ilegivel_pede_parecer(self):
        self.escreve(PLUGIN, '{"name": "forge", "version": "1.0.1",\n')
        self.commit("quebrado")
        self.assertIn(f"desatualizado: {PLUGIN} mudou", self.vale() or "")

    def test_json_ilegivel_dos_dois_lados_pede_parecer(self):  # ilegível não vira objeto vazio igual nos dois lados
        self.escreve(PLUGIN, '{"name": "forge",\n')
        self.parecer = self.commit("quebrado no parecer")
        self.escreve(PLUGIN, '{"hooks": "./outro.json",\n')
        self.commit("quebrado de outro jeito")
        self.assertIn(f"desatualizado: {PLUGIN} mudou", self.vale() or "")

    def test_versao_que_nao_e_texto_pede_parecer(self):
        self.manifesto({**MANIFESTO, "version": 2})
        self.commit("versão número")
        self.assertIn(f"desatualizado: {PLUGIN} mudou", self.vale() or "")

    def test_outro_json_so_com_versao_pede_parecer(self):  # só o caminho exato do plugin.json da raiz
        self.git("switch", "-q", "develop")
        self.manifesto(MANIFESTO, "package.json")
        self.manifesto(MANIFESTO, f"sub/{PLUGIN}")
        self.commit("outros manifestos")
        self.git("switch", "-q", "ramo")
        self.git("merge", "-q", "--no-edit", "develop")
        self.parecer = self.git("rev-parse", "HEAD")
        for nome in ("package.json", f"sub/{PLUGIN}"):
            with self.subTest(nome):
                self.manifesto({**MANIFESTO, "version": "1.0.1"}, nome)
                self.commit(f"versão de {nome}")
                self.assertIn(f"desatualizado: {nome} mudou", self.vale() or "")
                self.git("reset", "-q", "--hard", self.parecer)

    def test_modo_do_plugin_mudado_pede_parecer(self):
        self.manifesto({**MANIFESTO, "version": "1.0.1"})
        (self.dir / PLUGIN).chmod(0o755)
        self.commit("versão e executável")
        self.assertIn(f"desatualizado: {PLUGIN} mudou", self.vale() or "")

    def test_plugin_invariante_pede_parecer(self):
        self.git("switch", "-q", "develop")
        self.escreve("tests/config.json", json.dumps({"invariantes": [PLUGIN]}))
        self.commit("invariante")
        self.git("switch", "-q", "ramo")
        self.git("merge", "-q", "--no-edit", "develop")
        self.parecer = self.git("rev-parse", "HEAD")
        self.manifesto({**MANIFESTO, "version": "1.0.1"})
        self.commit("versão do invariante")
        self.assertIn(f"desatualizado: {PLUGIN} mudou", self.vale() or "")

    def test_release_versao_changelog_e_fragmento_apagado_no_pr(self):
        self.manifesto({**MANIFESTO, "version": "1.1.0"})
        self.escreve("CHANGELOG.md", "# Changelog\n\n## [Não publicado]\n\n## [1.1.0]\n- Corrigido: de outro pedido\n\n## [1.0.0]\n")
        self.git("rm", "-q", "changelog.d/outra.md")
        self.commit("release 1.1.0")
        self.assertEqual(self.desatualizados_no_pr(), [])

    def test_fragmento_de_outro_pedido_mudado_pede_parecer_no_pr(self):  # D4 segue: só o apagado é leve
        self.escreve("changelog.d/outra.md", "- Corrigido: outro texto\n")
        self.commit("fragmento de outro pedido")
        self.assertIn("desatualizado: changelog.d/outra.md mudou", " ".join(self.desatualizados_no_pr()))

    def test_removidos_com_git_que_falha_e_vazio(self):  # falha fechada: sem a lista, o fragmento segue estrito
        self.assertEqual(fc.removidos_do_intervalo(self.dir, "nao-existe", "HEAD"), set())


if __name__ == "__main__":
    unittest.main()
