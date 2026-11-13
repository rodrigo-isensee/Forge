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


def forge_changelog(cwd, *args, head_ref=None):
    ambiente = {k: v for k, v in os.environ.items() if k not in ("GITHUB_HEAD_REF", "CI")}  # o PR do CI não vaza
    if head_ref is not None:
        ambiente["GITHUB_HEAD_REF"] = head_ref
    return subprocess.run([sys.executable, "-I", str(FERRAMENTA), *args], cwd=cwd, env=ambiente,
                          capture_output=True, text=True)


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

    def test_versao_aninhada_antes_da_de_topo_com_o_manifesto_ja_na_versao_alvo_falha_sem_gravar_nada(self):
        # CHANGELOG-D-LINK: o topo já vale 0.2.0; a troca textual editava o campo aninhado e saía com 0
        antes = '{"extra": {"version": "9"}, "version": "0.2.0"}\n'
        arq = self._dev_com(antes)
        self._nada_gravado(forge_changelog(self.dir, "release", "0.2.0", "2026-02-02"), "dev/.claude-plugin/plugin.json")
        self.assertEqual(arq.read_text(encoding="utf-8"), antes)

    def test_changelog_d_como_link_para_fora_da_raiz_nao_publica_nem_apaga_os_md_externos(self):
        with tempfile.TemporaryDirectory() as fora:
            (Path(fora) / "externo.md").write_text("### Corrigido\n- EXTERNO\n", encoding="utf-8")
            (self.dir / "changelog.d").symlink_to(fora)
            r = forge_changelog(self.dir, "release", "0.2.0", "2026-02-02")
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("changelog.d", r.stderr)
            self.assertTrue((Path(fora) / "externo.md").exists())
        self.assertEqual((self.dir / "CHANGELOG.md").read_text(encoding="utf-8"), CABECALHO)
        self.assertEqual((self.dir / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"), '{"version": "0.1.0"}\n')

    def test_fragmento_que_e_link_para_fora_da_raiz_e_recusado_e_o_alvo_fica(self):
        self._com_fragmento()
        with tempfile.TemporaryDirectory() as fora:
            alvo = Path(fora) / "externo.md"
            alvo.write_text("### Corrigido\n- EXTERNO\n", encoding="utf-8")
            (self.dir / "changelog.d" / "y.md").symlink_to(alvo)
            r = forge_changelog(self.dir, "release", "0.2.0", "2026-02-02")
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("y.md", r.stderr)
            self.assertTrue(alvo.exists())
        self.assertEqual((self.dir / "CHANGELOG.md").read_text(encoding="utf-8"), CABECALHO)

    def test_novo_com_changelog_d_como_link_e_recusado_sem_gravar_fora(self):
        with tempfile.TemporaryDirectory() as fora:
            (self.dir / "changelog.d").symlink_to(fora)
            r = forge_changelog(self.dir, "novo", "Corrigido", "x")
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("changelog.d", r.stderr)
            self.assertEqual(list(Path(fora).iterdir()), [])

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


class ReleaseAvisaAvaliacaoDeFora(Base):
    """0.45.3: o fim da release avisa a avaliação de fora pendente (5 versões desde a última docs/avaliacoes/*.md); só avisa."""

    def preparar(self, versoes):
        texto = "".join(f"## [0.1.{i}] - 2026-01-0{i}\n### Corrigido\n- v{i}\n\n" for i in range(versoes, 0, -1))
        (self.dir / "CHANGELOG.md").write_text("# Changelog\n\n## [Não publicado]\n\n" + texto, encoding="utf-8")
        (self.dir / "changelog.d").mkdir()
        (self.dir / "changelog.d" / "x.md").write_text("### Alterado\n- Nova\n", encoding="utf-8")

    def test_quinta_versao_avisa_e_a_release_sai_com_0(self):
        self.preparar(4)
        r = forge_changelog(self.dir, "release", "0.2.0", "2026-02-02")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("aviso: avaliação de fora pendente: 5 versões", r.stdout)
        self.assertIn("## [0.2.0] - 2026-02-02", (self.dir / "CHANGELOG.md").read_text(encoding="utf-8"))

    def test_quarta_versao_nao_avisa(self):
        self.preparar(3)
        r = forge_changelog(self.dir, "release", "0.2.0", "2026-02-02")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("aviso:", r.stdout)


class ReleaseAvisaMedidasDaVersao(Base):
    """v046 E7 (decisão do dono de 12/11): placar de mutação e bench uma vez por versão, na release; nunca no PR."""

    def preparar(self, forge=True, tag="v0.1.0"):
        if tag:
            git(self.dir, "tag", tag)
        if forge:
            (self.dir / "scripts").mkdir()
            (self.dir / "scripts" / "placar-mutacao.py").write_text("", encoding="utf-8")
        (self.dir / "changelog.d").mkdir()
        (self.dir / "changelog.d" / "x.md").write_text("### Alterado\n- Nova\n", encoding="utf-8")
        r = forge_changelog(self.dir, "release", "0.2.0", "2026-02-02")
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def test_no_forge_imprime_o_placar_desde_a_tag_anterior_e_o_bench(self):
        saida = self.preparar()
        self.assertIn("placar: scripts/placar-mutacao.py --desde v0.1.0 --versao 0.2.0", saida)
        self.assertIn("bench: a linha da 0.2.0 em bench-versoes.md e metricas-velocidade.md", saida)

    def test_sem_tag_pede_a_tag_anterior_a_mao(self):
        self.assertIn("--desde <tag da release anterior> --versao 0.2.0", self.preparar(tag=None))

    def test_tag_com_metacaractere_sai_citada_no_comando(self):  # segurança A3 da v046 E7
        self.assertIn("--desde 'v9$(id)' --versao 0.2.0", self.preparar(tag="v9$(id)"))

    def test_fora_do_forge_nao_avisa(self):
        self.assertNotIn("medida da versão", self.preparar(forge=False))

    def test_nem_o_ci_nem_o_envio_rodam_o_placar(self):
        fontes = [*(RAIZ / ".github" / "workflows").glob("*.yml"), *(RAIZ / ".githooks").iterdir()]
        self.assertGreaterEqual(len(fontes), 3)
        for fonte in fontes:
            with self.subTest(fonte.name):
                self.assertNotIn("placar-mutacao", fonte.read_text(encoding="utf-8"))


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
        (self.dir / "changelog.d" / "minha-mudanca.md").write_text("texto solto\n", encoding="utf-8")
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
                (self.dir / "changelog.d" / "minha-mudanca.md").write_text(conteudo, encoding="utf-8")
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

    def _so_arquivo(self, caminho):
        (self.dir / caminho).parent.mkdir(parents=True, exist_ok=True)
        (self.dir / caminho).write_text("x\n", encoding="utf-8")
        self.commitar()
        return self.conferir()

    def test_pr_so_de_pareceres_passa_sem_fragmento(self):
        """RELEASE-PR-SO-PARECER: o PR só de pareceres da release (#399) não tem o que registrar."""
        (self.dir / "docs" / "reviews").mkdir(parents=True)
        (self.dir / "docs" / "reviews" / "a.md").write_text("x\n", encoding="utf-8")
        r = self._so_arquivo("docs/qa/a.md")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("só de parecer", r.stdout)

    def test_pr_de_parecer_com_modelo_ameacas_ou_aceites_continua_exigindo_fragmento(self):
        for caminho in ("docs/security/_modelo.md", "docs/security/ameacas/x.md", "docs/security/aceites/x.md"):
            with self.subTest(caminho=caminho):
                git(self.dir, "reset", "-q", "--hard", "develop")
                r = self._so_arquivo(caminho)
                self.assertNotEqual(r.returncode, 0)
                self.assertIn("fragmento novo", r.stdout + r.stderr)

    def test_renomear_codigo_para_pasta_de_parecer_continua_exigindo_fragmento(self):
        """A1 do review: o diff com detecção de renomeação lista só o destino e deixava o código sair como se fosse parecer."""
        (self.dir / "docs" / "reviews").mkdir(parents=True)
        git(self.dir, "mv", "agents/a.md", "docs/reviews/a.md")
        self.commitar()
        r = self.conferir()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("fragmento novo", r.stdout + r.stderr)

    def test_so_o_nome_do_arquivo_com_underline_e_modelo(self):
        """Limite da regra (A2 do review), igual ao gate do ci.yml (`/_[^/]*$`): `docs/qa/_modelo.md` é modelo e exige fragmento;
        `docs/qa/_x/a.md` (pasta com `_`, arquivo comum) é parecer."""
        r = self._so_arquivo("docs/qa/_modelo.md")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("fragmento novo", r.stdout + r.stderr)
        git(self.dir, "reset", "-q", "--hard", "develop")
        r = self._so_arquivo("docs/qa/_x/a.md")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_parecer_mais_fragmento_malformado_reprova(self):
        """Regressão do QA: o atalho de "só parecer" não pode pular a validação de um fragmento presente no PR."""
        (self.dir / "changelog.d").mkdir()
        (self.dir / "changelog.d" / "minha-mudanca.md").write_text("isto não é um fragmento\n", encoding="utf-8")
        r = self._so_arquivo("docs/qa/a.md")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("formato inválido", r.stdout + r.stderr)

    def test_parecer_mais_fragmento_valido_passa(self):
        forge_changelog(self.dir, "novo", "Corrigido", "x")
        r = self._so_arquivo("docs/qa/a.md")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_pr_de_parecer_com_outro_arquivo_da_fabrica_continua_exigindo_fragmento(self):
        (self.dir / "docs" / "devops").mkdir(parents=True)
        (self.dir / "docs" / "devops" / "a.md").write_text("x\n", encoding="utf-8")
        self.mudar_fabrica()
        self.commitar()
        r = self.conferir()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("fragmento novo", r.stdout + r.stderr)

    def test_pr_de_release_passa_sem_fragmento(self):
        self.mudar_fabrica()
        (self.dir / ".claude-plugin" / "plugin.json").write_text('{"version": "0.2.0"}\n', encoding="utf-8")
        self.commitar()
        self.assertEqual(self.conferir().returncode, 0)


class ConferirNomeDaBranch(Base):
    """CHANGELOG-BRANCH: em melhoria/*, o `conferir` recusa fragmento novo com outro nome (antes de todo atalho)."""

    def fragmento(self, nome, versao=None):
        self.mudar_fabrica()
        (self.dir / "changelog.d").mkdir(exist_ok=True)
        (self.dir / "changelog.d" / nome).write_text("### Alterado\n- v\n", encoding="utf-8")
        if versao:
            (self.dir / ".claude-plugin" / "plugin.json").write_text(f'{{"version": "{versao}"}}\n', encoding="utf-8")
        self.commitar()

    def conferir(self, *extra, head_ref=None):
        return forge_changelog(self.dir, "conferir", "--base", "develop", *extra, head_ref=head_ref)

    def test_branch_explicita_nome_errado_reprova_e_nome_certo_passa(self):
        self.fragmento("b.md")
        r = self.conferir("--branch=melhoria/a")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("changelog.d/b.md", r.stderr)
        self.assertIn("CHANGELOG-BRANCH", r.stderr)
        self.assertEqual(self.conferir("--branch=melhoria/b").returncode, 0)

    def test_nome_com_o_slug_como_prefixo_reprova(self):
        self.fragmento("a-velho.md")
        self.assertEqual(self.conferir("--branch=melhoria/a").returncode, 1)

    def test_versao_mudada_nao_pula_a_regra(self):
        self.fragmento("b.md", versao="0.2.0")
        r = self.conferir("--branch=melhoria/a")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertEqual(self.conferir("--branch=melhoria/b").returncode, 0)

    def test_github_head_ref_vale_sem_branch_explicita(self):
        self.fragmento("a.md")
        self.assertEqual(self.conferir(head_ref="melhoria/a").returncode, 0)
        self.assertEqual(self.conferir(head_ref="melhoria/b").returncode, 1)

    def test_branch_explicita_vence_o_github_head_ref(self):
        self.fragmento("a.md")
        r = self.conferir("--branch=melhoria/a", head_ref="melhoria/b")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_sem_branch_nem_ambiente_vale_o_head(self):
        self.fragmento("b.md")
        r = self.conferir()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("melhoria/minha-mudanca", r.stderr)

    def test_branch_fora_de_melhoria_nao_aplica_a_regra(self):
        self.fragmento("b.md")
        self.assertEqual(self.conferir("--branch=fix/a").returncode, 0)


class ConferirFragmentoDaBranchDeBaixo(Base):
    """CHANGELOG-FRAGMENTO-BASE: na branch empilhada, o fragmento `<s>.md` da branch de baixo (`melhoria/<s>`, local ou de
    origin, ancestral do HEAD e que o tem) não conta como fragmento com outro nome; sem essa branch, segue reprovado."""

    def fragmento(self, nome):
        self.mudar_fabrica()
        (self.dir / "changelog.d").mkdir(exist_ok=True)
        (self.dir / "changelog.d" / nome).write_text("### Alterado\n- v\n", encoding="utf-8")
        self.commitar()

    def empilhar(self):
        git(self.dir, "checkout", "-q", "-b", "melhoria/a")
        self.fragmento("a.md")
        git(self.dir, "checkout", "-q", "-b", "melhoria/a-2")
        self.fragmento("a-2.md")

    def conferir(self):
        return forge_changelog(self.dir, "conferir", "--base", "develop", "--branch=melhoria/a-2")

    def test_fragmento_da_branch_de_baixo_ancestral_passa(self):
        self.empilhar()
        r = self.conferir()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_fragmento_sem_a_branch_de_baixo_reprova(self):
        self.empilhar()
        git(self.dir, "branch", "-q", "-D", "melhoria/a")
        r = self.conferir()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("changelog.d/a.md", r.stderr)

    def test_branch_de_baixo_que_andou_depois_reprova(self):
        self.empilhar()
        git(self.dir, "checkout", "-q", "melhoria/a")
        git(self.dir, "commit", "-q", "--allow-empty", "-m", "andou")
        git(self.dir, "checkout", "-q", "melhoria/a-2")
        self.assertEqual(self.conferir().returncode, 1)

    def test_branch_de_baixo_sem_o_fragmento_reprova(self):
        self.empilhar()
        git(self.dir, "branch", "-q", "-f", "melhoria/a", "develop")
        self.assertEqual(self.conferir().returncode, 1)

    def test_branch_de_baixo_de_origin_passa(self):
        self.empilhar()
        git(self.dir, "update-ref", "refs/remotes/origin/melhoria/a", "melhoria/a")
        git(self.dir, "branch", "-q", "-D", "melhoria/a")
        r = self.conferir()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class ConferirSaidaDeErro(Base):
    """CL-1 (adendo E1.3): rc 1 é só reprovação; erro de git ou exceção sai com 2 (o pré-voo do pre-push não barra)."""

    def test_fora_de_repositorio_git_sai_com_2(self):
        with tempfile.TemporaryDirectory() as fora:
            r = forge_changelog(fora, "conferir", "--base", "develop")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("git diff", r.stderr)

    def test_plugin_json_sem_version_sai_com_2(self):
        (self.dir / ".claude-plugin" / "plugin.json").write_text('{"nome": "x"}\n', encoding="utf-8")
        self.mudar_fabrica()
        self.commitar()
        r = forge_changelog(self.dir, "conferir", "--base", "develop")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("AttributeError", r.stderr)

    def test_fragmento_com_outro_nome_continua_1(self):
        self.mudar_fabrica()
        (self.dir / "changelog.d").mkdir()
        (self.dir / "changelog.d" / "b.md").write_text("### Alterado\n- v\n", encoding="utf-8")
        self.commitar()
        r = forge_changelog(self.dir, "conferir", "--base", "develop", "--branch=melhoria/a")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)


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
    return carregar_ferramenta().fragmentos_com_outro_nome(branch, novos)


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
