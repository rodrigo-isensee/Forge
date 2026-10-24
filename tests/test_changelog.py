"""Fragmentos de changelog: `bin/forge-changelog` (novo, release, conferir) e o uso dele no CI."""
import importlib.machinery
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
FERRAMENTA = RAIZ / "bin" / "forge-changelog"
CABECALHO = "# Changelog\n\nFormato.\n\n## [Não publicado]\n\n## [0.1.0] - 2026-01-01\n### Adicionado\n- **Antigo:** x\n"


def git(cwd, *args):
    ambiente = sem_manutencao({**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null",
                               "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                               "GIT_COMMITTER_EMAIL": "t@t"})
    return subprocess.run(["git", *args], cwd=cwd, env=ambiente, capture_output=True, text=True, check=True).stdout


def forge_changelog(cwd, *args):
    return subprocess.run([sys.executable, str(FERRAMENTA), *args], cwd=cwd, capture_output=True, text=True)


class Base(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.dir = Path(self._t.name)
        git(self.dir, "init", "-q", "-b", "develop")
        (self.dir / "CHANGELOG.md").write_text(CABECALHO, encoding="utf-8")
        (self.dir / "agents").mkdir()
        (self.dir / "agents" / "a.md").write_text("a\n", encoding="utf-8")
        (self.dir / ".claude-plugin").mkdir()
        (self.dir / ".claude-plugin" / "plugin.json").write_text('{"version": "0.1.0"}\n', encoding="utf-8")
        git(self.dir, "add", "-A")
        git(self.dir, "commit", "-qm", "base")
        git(self.dir, "switch", "-q", "-c", "melhoria/minha-mudanca")

    def commitar(self):
        git(self.dir, "add", "-A")
        git(self.dir, "commit", "-qm", "mudanca")

    def mudar_fabrica(self):
        (self.dir / "agents" / "a.md").write_text("b\n", encoding="utf-8")


class Novo(Base):
    def test_grava_o_fragmento_da_branch_atual(self):
        r = forge_changelog(self.dir, "novo", "Corrigido", "**CI:** conserta o que quebrava.")
        self.assertEqual(r.returncode, 0, r.stderr)
        arquivo = self.dir / "changelog.d" / "minha-mudanca.md"
        self.assertEqual(arquivo.read_text(encoding="utf-8"), "### Corrigido\n- **CI:** conserta o que quebrava.\n")

    def test_segunda_linha_do_mesmo_tipo_e_de_outro_tipo(self):
        forge_changelog(self.dir, "novo", "Corrigido", "um")
        forge_changelog(self.dir, "novo", "Corrigido", "dois")
        forge_changelog(self.dir, "novo", "Adicionado", "tres")
        texto = (self.dir / "changelog.d" / "minha-mudanca.md").read_text(encoding="utf-8")
        self.assertEqual(texto, "### Corrigido\n- um\n- dois\n\n### Adicionado\n- tres\n")

    def test_tipo_invalido_e_texto_vazio_recusados(self):
        self.assertNotEqual(forge_changelog(self.dir, "novo", "Removido", "x").returncode, 0)
        self.assertNotEqual(forge_changelog(self.dir, "novo", "Corrigido", "  ").returncode, 0)
        self.assertFalse((self.dir / "changelog.d").exists())

    def test_branch_com_subpasta_vira_nome_de_arquivo_seguro(self):
        git(self.dir, "switch", "-q", "-c", "melhoria/a/b")
        self.assertEqual(forge_changelog(self.dir, "novo", "Alterado", "x").returncode, 0)
        self.assertTrue((self.dir / "changelog.d" / "a-b.md").is_file())

    def test_branch_protegida_recusada(self):
        git(self.dir, "switch", "-q", "develop")
        self.assertNotEqual(forge_changelog(self.dir, "novo", "Alterado", "x").returncode, 0)


class Release(Base):
    def test_junta_agrupa_por_tipo_e_apaga_os_fragmentos(self):
        d = self.dir / "changelog.d"
        d.mkdir()
        (d / "b-segundo.md").write_text("### Corrigido\n- B\n", encoding="utf-8")
        (d / "a-primeiro.md").write_text("### Adicionado\n- A\n\n### Corrigido\n- A2\n", encoding="utf-8")
        (d / "c-terceiro.md").write_text("### Alterado\n- C\n", encoding="utf-8")
        r = forge_changelog(self.dir, "release", "0.2.0", "2026-02-02")
        self.assertEqual(r.returncode, 0, r.stderr)
        texto = (self.dir / "CHANGELOG.md").read_text(encoding="utf-8")
        esperado = ("## [Não publicado]\n\n## [0.2.0] - 2026-02-02\n### Adicionado\n- A\n### Alterado\n- C\n"
                    "### Corrigido\n- A2\n- B\n\n## [0.1.0]")
        self.assertIn(esperado, texto)
        self.assertEqual(list(d.glob("*.md")), [])

    def test_leva_tambem_as_linhas_antigas_de_nao_publicado(self):
        texto = (self.dir / "CHANGELOG.md").read_text(encoding="utf-8")
        (self.dir / "CHANGELOG.md").write_text(texto.replace("[Não publicado]\n", "[Não publicado]\n- Velha\n"), encoding="utf-8")
        (self.dir / "changelog.d").mkdir()
        (self.dir / "changelog.d" / "x.md").write_text("### Alterado\n- Nova\n", encoding="utf-8")
        self.assertEqual(forge_changelog(self.dir, "release", "0.2.0", "2026-02-02").returncode, 0)
        texto = (self.dir / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn("## [Não publicado]\n\n## [0.2.0] - 2026-02-02\n- Velha\n### Alterado\n- Nova\n\n## [0.1.0]", texto)

    def test_sem_nada_a_publicar_falha_sem_mexer(self):
        r = forge_changelog(self.dir, "release", "0.2.0", "2026-02-02")
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual((self.dir / "CHANGELOG.md").read_text(encoding="utf-8"), CABECALHO)

    def test_fragmento_malformado_falha_sem_apagar(self):
        d = self.dir / "changelog.d"
        d.mkdir()
        (d / "x.md").write_text("sem titulo\n", encoding="utf-8")
        self.assertNotEqual(forge_changelog(self.dir, "release", "0.2.0", "2026-02-02").returncode, 0)
        self.assertTrue((d / "x.md").exists())

    def _com_fragmento(self):
        (self.dir / "changelog.d").mkdir()
        (self.dir / "changelog.d" / "x.md").write_text("### Corrigido\n- X\n", encoding="utf-8")

    def test_sobe_a_versao_dos_dois_manifestos_quando_o_dev_existe(self):
        dev = self.dir / "dev" / ".claude-plugin"
        dev.mkdir(parents=True)
        (dev / "plugin.json").write_text('{\n  "name": "d",\n  "version": "0.1.0"\n}\n', encoding="utf-8")
        self._com_fragmento()
        r = forge_changelog(self.dir, "release", "0.2.0", "2026-02-02")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual((dev / "plugin.json").read_text(encoding="utf-8"), '{\n  "name": "d",\n  "version": "0.2.0"\n}\n')
        self.assertEqual((self.dir / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"), '{"version": "0.2.0"}\n')

    def test_sem_o_manifesto_dev_a_release_nao_cria_nada(self):
        self._com_fragmento()
        r = forge_changelog(self.dir, "release", "0.2.0", "2026-02-02")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse((self.dir / "dev").exists())

    def _dev_com(self, conteudo):
        dev = self.dir / "dev" / ".claude-plugin"
        dev.mkdir(parents=True)
        (dev / "plugin.json").write_text(conteudo, encoding="utf-8")
        self._com_fragmento()
        return dev / "plugin.json"

    def _nada_gravado(self, r, arquivo=None):
        self.assertNotEqual(r.returncode, 0)
        if arquivo:
            self.assertIn(arquivo, r.stderr)
        self.assertEqual((self.dir / "CHANGELOG.md").read_text(encoding="utf-8"), CABECALHO)
        self.assertEqual((self.dir / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"), '{"version": "0.1.0"}\n')
        self.assertTrue((self.dir / "changelog.d" / "x.md").exists())

    def test_manifesto_que_nao_e_json_falha_sem_gravar_nada(self):
        self._dev_com('{"version": "0.1.0",\n')
        self._nada_gravado(forge_changelog(self.dir, "release", "0.2.0", "2026-02-02"), "dev/.claude-plugin/plugin.json")

    def test_manifesto_sem_version_de_topo_falha_sem_gravar_nada(self):
        self._dev_com('{"name": "d", "extra": {"version": "9"}}\n')
        self._nada_gravado(forge_changelog(self.dir, "release", "0.2.0", "2026-02-02"), "dev/.claude-plugin/plugin.json")

    def test_manifesto_link_simbolico_e_recusado_sem_gravar_nada(self):
        alvo = self.dir / "fora.json"
        alvo.write_text('{"version": "0.1.0"}\n', encoding="utf-8")
        dev = self.dir / "dev" / ".claude-plugin"
        dev.mkdir(parents=True)
        (dev / "plugin.json").symlink_to(alvo)
        self._com_fragmento()
        self._nada_gravado(forge_changelog(self.dir, "release", "0.2.0", "2026-02-02"), "dev/.claude-plugin/plugin.json")
        self.assertEqual(alvo.read_text(encoding="utf-8"), '{"version": "0.1.0"}\n')

    def test_manifesto_que_resolve_fora_da_raiz_e_recusado_sem_gravar_nada(self):
        with tempfile.TemporaryDirectory() as fora:
            (Path(fora) / ".claude-plugin").mkdir()
            alvo = Path(fora) / ".claude-plugin" / "plugin.json"
            alvo.write_text('{"version": "0.1.0"}\n', encoding="utf-8")
            (self.dir / "dev").symlink_to(fora)
            self._com_fragmento()
            self._nada_gravado(forge_changelog(self.dir, "release", "0.2.0", "2026-02-02"))
            self.assertEqual(alvo.read_text(encoding="utf-8"), '{"version": "0.1.0"}\n')

    def test_chave_version_aninhada_antes_da_de_topo_falha_sem_gravar_nada(self):
        antes = '{"extra": {"version": "9"}, "version": "0.1.0"}\n'
        arq = self._dev_com(antes)
        self._nada_gravado(forge_changelog(self.dir, "release", "0.2.0", "2026-02-02"), "dev/.claude-plugin/plugin.json")
        self.assertEqual(arq.read_text(encoding="utf-8"), antes)

    def test_chave_version_repetida_falha_sem_gravar_nada(self):
        antes = '{"version": "0.1.0", "version": "0.1.1"}\n'
        arq = self._dev_com(antes)
        self._nada_gravado(forge_changelog(self.dir, "release", "0.2.0", "2026-02-02"), "dev/.claude-plugin/plugin.json")
        self.assertEqual(arq.read_text(encoding="utf-8"), antes)

    def test_chave_version_repetida_com_a_versao_nova_no_ultimo_valor_falha_sem_gravar_nada(self):
        # Sem o gancho de chave repetida, o último valor (a versão nova) passaria nas duas conferências de `version`.
        antes = '{"version": "0.1.0", "k": 1, "version": "0.2.0"}\n'
        arq = self._dev_com(antes)
        self._nada_gravado(forge_changelog(self.dir, "release", "0.2.0", "2026-02-02"), "dev/.claude-plugin/plugin.json")
        self.assertEqual(arq.read_text(encoding="utf-8"), antes)

    def test_aspa_escapada_no_valor_da_version_falha_sem_gravar_nada(self):
        antes = '{"version": "0.1\\"0"}\n'
        arq = self._dev_com(antes)
        self._nada_gravado(forge_changelog(self.dir, "release", "0.2.0", "2026-02-02"), "dev/.claude-plugin/plugin.json")
        self.assertEqual(arq.read_text(encoding="utf-8"), antes)

    def test_changelog_link_simbolico_e_recusado_sem_gravar_nada(self):
        alvo = self.dir / "fora.md"
        alvo.write_text(CABECALHO, encoding="utf-8")
        (self.dir / "CHANGELOG.md").unlink()
        (self.dir / "CHANGELOG.md").symlink_to(alvo)
        self._com_fragmento()
        r = forge_changelog(self.dir, "release", "0.2.0", "2026-02-02")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("CHANGELOG.md", r.stderr)
        self.assertEqual(alvo.read_text(encoding="utf-8"), CABECALHO)
        self.assertEqual((self.dir / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"), '{"version": "0.1.0"}\n')
        self.assertTrue((self.dir / "changelog.d" / "x.md").exists())

    def test_changelog_que_resolve_fora_da_raiz_e_recusado_sem_gravar_nada(self):
        # O link simbólico cai no ramo `is_symlink()` de `conferir_caminho` (a mensagem é a mesma para os dois ramos).
        with tempfile.TemporaryDirectory() as fora:
            alvo = Path(fora) / "CHANGELOG.md"
            alvo.write_text(CABECALHO, encoding="utf-8")
            (self.dir / "CHANGELOG.md").unlink()
            (self.dir / "CHANGELOG.md").symlink_to(alvo)
            self._com_fragmento()
            r = forge_changelog(self.dir, "release", "0.2.0", "2026-02-02")
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("fora da raiz", r.stderr)
            self.assertEqual(alvo.read_text(encoding="utf-8"), CABECALHO)
            self.assertEqual((self.dir / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"), '{"version": "0.1.0"}\n')
            self.assertTrue((self.dir / "changelog.d" / "x.md").exists())

    def test_changelog_link_simbolico_quebrado_e_recusado(self):
        (self.dir / "CHANGELOG.md").unlink()
        (self.dir / "CHANGELOG.md").symlink_to(self.dir / "nao-existe.md")
        self._com_fragmento()
        r = forge_changelog(self.dir, "release", "0.2.0", "2026-02-02")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("link simbólico", r.stderr)
        self.assertFalse((self.dir / "nao-existe.md").exists())

    def test_versao_ja_existente_recusada(self):
        (self.dir / "changelog.d").mkdir()
        (self.dir / "changelog.d" / "x.md").write_text("### Alterado\n- N\n", encoding="utf-8")
        self.assertNotEqual(forge_changelog(self.dir, "release", "0.1.0", "2026-02-02").returncode, 0)


class ConferirNoCI(Base):
    def conferir(self):
        return forge_changelog(self.dir, "conferir", "--base", "develop")

    def test_aceita_fragmento_novo(self):
        self.mudar_fabrica()
        forge_changelog(self.dir, "novo", "Corrigido", "x")
        self.commitar()
        r = self.conferir()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_aceita_a_linha_antiga_em_nao_publicado(self):
        self.mudar_fabrica()
        texto = (self.dir / "CHANGELOG.md").read_text(encoding="utf-8")
        (self.dir / "CHANGELOG.md").write_text(texto.replace("[Não publicado]\n", "[Não publicado]\n- Nova\n"), encoding="utf-8")
        self.commitar()
        r = self.conferir()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_recusa_pr_sem_fragmento_nem_linha(self):
        self.mudar_fabrica()
        self.commitar()
        r = self.conferir()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("changelog.d", r.stdout + r.stderr)

    def test_recusa_fragmento_malformado(self):
        self.mudar_fabrica()
        (self.dir / "changelog.d").mkdir()
        (self.dir / "changelog.d" / "x.md").write_text("texto solto\n", encoding="utf-8")
        self.commitar()
        self.assertNotEqual(self.conferir().returncode, 0)

    def test_fragmento_em_subpasta_nao_conta(self):
        self.mudar_fabrica()
        (self.dir / "changelog.d" / "sub").mkdir(parents=True)
        (self.dir / "changelog.d" / "sub" / "x.md").write_text("### Alterado\n- v\n", encoding="utf-8")
        self.commitar()
        self.assertNotEqual(self.conferir().returncode, 0)

    def test_marcador_sem_texto_nao_conta(self):
        for conteudo in ("### Alterado\n- \n", "### Alterado\n-\n"):
            with self.subTest(conteudo=conteudo):
                git(self.dir, "switch", "-q", "-C", "melhoria/minha-mudanca", "develop")
                self.mudar_fabrica()
                (self.dir / "changelog.d").mkdir(exist_ok=True)
                (self.dir / "changelog.d" / "x.md").write_text(conteudo, encoding="utf-8")
                self.commitar()
                self.assertNotEqual(self.conferir().returncode, 0)

    def test_fragmento_que_ja_existia_na_base_nao_conta(self):
        (self.dir / "changelog.d").mkdir()
        (self.dir / "changelog.d" / "velho.md").write_text("### Alterado\n- v\n", encoding="utf-8")
        git(self.dir, "add", "-A")
        git(self.dir, "commit", "-qm", "frag velho")
        git(self.dir, "branch", "-f", "develop", "HEAD")
        self.mudar_fabrica()
        self.commitar()
        self.assertNotEqual(self.conferir().returncode, 0)

    def test_sem_mudanca_na_fabrica_nao_exige(self):
        (self.dir / "outro.txt").write_text("x\n", encoding="utf-8")
        self.commitar()
        self.assertEqual(self.conferir().returncode, 0)

    def _base_com_fragmento(self, texto="### Corrigido\n- Linha do fragmento\n"):
        (self.dir / "changelog.d").mkdir()
        (self.dir / "changelog.d" / "dv-x.md").write_text(texto, encoding="utf-8")
        git(self.dir, "add", "-A")
        git(self.dir, "commit", "-qm", "frag")
        git(self.dir, "branch", "-f", "develop", "HEAD")

    def test_fechamento_com_todas_as_linhas_no_changelog_passa(self):
        self._base_com_fragmento()
        (self.dir / "changelog.d" / "dv-x.md").unlink()
        texto = (self.dir / "CHANGELOG.md").read_text(encoding="utf-8")
        (self.dir / "CHANGELOG.md").write_text(texto + "- Linha do fragmento\n", encoding="utf-8")
        self.commitar()
        r = self.conferir()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("fechamento de 1 fragmento(s)", r.stdout)

    def test_fechamento_sem_a_linha_no_changelog_reprova(self):
        self._base_com_fragmento()
        (self.dir / "changelog.d" / "dv-x.md").unlink()
        self.commitar()
        r = self.conferir()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("dv-x.md", r.stdout + r.stderr)
        self.assertIn("Linha do fragmento", r.stdout + r.stderr)

    def test_apagar_fragmento_com_outra_mudanca_da_fabrica_exige_fragmento_novo(self):
        self._base_com_fragmento()
        (self.dir / "changelog.d" / "dv-x.md").unlink()
        texto = (self.dir / "CHANGELOG.md").read_text(encoding="utf-8")
        (self.dir / "CHANGELOG.md").write_text(texto + "- Linha do fragmento\n", encoding="utf-8")
        self.mudar_fabrica()
        self.commitar()
        r = self.conferir()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("fragmento novo", r.stdout + r.stderr)

    def _fechar_com_arquivo(self, caminho):
        self._base_com_fragmento()
        (self.dir / "changelog.d" / "dv-x.md").unlink()
        texto = (self.dir / "CHANGELOG.md").read_text(encoding="utf-8")
        (self.dir / "CHANGELOG.md").write_text(texto + "- Linha do fragmento\n", encoding="utf-8")
        (self.dir / caminho).parent.mkdir(parents=True, exist_ok=True)
        (self.dir / caminho).write_text("x\n", encoding="utf-8")
        self.commitar()
        return self.conferir()

    def test_fechamento_com_parecer_em_docs_reviews_passa(self):
        r = self._fechar_com_arquivo("docs/reviews/dv-x.md")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_fechamento_com_docs_regras_continua_exigindo_fragmento(self):
        r = self._fechar_com_arquivo("docs/regras/R-X.md")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("fragmento novo", r.stdout + r.stderr)

    def test_pr_de_release_passa_sem_fragmento(self):
        self.mudar_fabrica()
        (self.dir / ".claude-plugin" / "plugin.json").write_text('{"version": "0.2.0"}\n', encoding="utf-8")
        self.commitar()
        self.assertEqual(self.conferir().returncode, 0)


class ConferirRelease(Base):
    def test_recusa_fragmento_pendente_e_aceita_pasta_limpa(self):
        self.assertEqual(forge_changelog(self.dir, "conferir-release").returncode, 0)
        (self.dir / "changelog.d").mkdir()
        (self.dir / "changelog.d" / "x.md").write_text("### Alterado\n- v\n", encoding="utf-8")
        (self.dir / "changelog.d" / "README.md").write_text("leia\n", encoding="utf-8")
        r = forge_changelog(self.dir, "conferir-release")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("changelog.d", r.stdout + r.stderr)


def carregar_ferramenta():
    carregador = importlib.machinery.SourceFileLoader("forge_changelog_teste", str(FERRAMENTA))
    modulo = importlib.util.module_from_spec(importlib.util.spec_from_loader(carregador.name, carregador))
    carregador.exec_module(modulo)
    return modulo


def fragmentos_com_outro_nome(branch, novos):
    """Fragmentos novos de changelog.d/ cujo nome não é o da branch (`<branch-sem-prefixo>.md`)."""
    esperado = f"{carregar_ferramenta().slug_da_branch(branch)}.md"
    return [n for n in novos if Path(n).name != esperado]


class FragmentoTemONomeDaBranch(unittest.TestCase):
    """S-6: o fragmento de uma branch chama-se `<branch-sem-prefixo>.md`; outro nome falha."""

    def test_nome_certo_passa_e_nome_errado_falha(self):
        self.assertEqual(fragmentos_com_outro_nome("melhoria/conferente-k2", ["changelog.d/conferente-k2.md"]), [])
        self.assertEqual(fragmentos_com_outro_nome("melhoria/conferente-k2", ["changelog.d/conferente-k1.md"]),
                         ["changelog.d/conferente-k1.md"])
        self.assertEqual(fragmentos_com_outro_nome("melhoria/a", ["changelog.d/a.md", "changelog.d/b.md"]),
                         ["changelog.d/b.md"])

    def test_forge_changelog_novo_grava_com_o_nome_da_branch(self):
        with tempfile.TemporaryDirectory() as d:
            git(d, "init", "-q", "-b", "melhoria/minha-mudanca")
            git(d, "commit", "-q", "--allow-empty", "-m", "base")
            r = forge_changelog(d, "novo", "Adicionado", "x")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(sorted(p.name for p in (Path(d) / "changelog.d").glob("*.md")), ["minha-mudanca.md"])

    def test_fragmentos_novos_desta_branch_tem_o_nome_dela(self):
        branch = os.environ.get("GITHUB_HEAD_REF") or subprocess.run(
            ["git", "-C", str(RAIZ), "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True).stdout.strip()
        if not branch.startswith("melhoria/"):
            self.skipTest(f"branch '{branch}' não é de melhoria; a regra vale para melhoria/*")
        r = subprocess.run(["git", "-C", str(RAIZ), "diff", "--name-only", "--no-renames", "--diff-filter=A",
                            "origin/develop...HEAD", "--", "changelog.d"], capture_output=True, text=True)
        if r.returncode != 0:
            self.skipTest("sem origin/develop para comparar")
        novos = [n for n in r.stdout.split() if n.endswith(".md") and Path(n).name.lower() != "readme.md"]
        self.assertEqual(fragmentos_com_outro_nome(branch, novos), [],
                         f"fragmento de changelog.d/ sem o nome da branch '{branch}' (esperado <branch-sem-prefixo>.md)")


class CIUsaOsFragmentos(unittest.TestCase):
    def test_ci_chama_a_ferramenta_e_instrucoes_apontam_para_ela(self):
        ci = (RAIZ / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertIn("bin/forge-changelog conferir", ci)
        script = (RAIZ / "scripts" / "conferir-release.py").read_text(encoding="utf-8")
        self.assertIn("scripts/conferir-release.py", ci)  # o passo de release (main e homolog) chama o script
        self.assertIn('"conferir-release"', script)  # e o script chama a mesma listagem de fragmentos
        self.assertNotIn("__import__", ci)
        for caminho in ("agents/tech-lead.md", "skills/contribuir-com-o-forge/SKILL.md", "CONTRIBUTING.md",
                        ".github/pull_request_template.md", ".claude/CLAUDE.md"):
            with self.subTest(arquivo=caminho):
                self.assertIn("changelog.d", (RAIZ / caminho).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
