"""SESSAO-AUTOMATICA (diretriz 28, v047 E1.198): todo atalho e instrução de abrir ou retomar o Jarvis usa --permission-mode auto;
DIR-31: visão de foco por padrão e linguagem fácil no Jarvis;
GH-VERSAO-MINIMA: o preparar-estacao.sh exige gh >= 2.47 e instala pelo repositório oficial."""
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_forge as tf  # noqa: E402  (o módulo, não as classes: elas seriam coletadas de novo aqui)

RAIZ = tf.RAIZ
MODO = "--permission-mode auto"


class AtalhosAbremNoAutomatico(unittest.TestCase):
    setUp, chamadas = tf.JarvisForgeVigente.setUp, tf.JarvisForgeVigente.chamadas

    def rodar(self, *args, **env):
        return tf.JarvisForgeVigente.rodar(self, *args, **env)

    def claude(self):
        return [c for c in self.chamadas() if c.startswith("claude --")][0]

    def test_jarvis_forge_abre_em_automatico(self):
        r = self.rodar("--sem-tmux")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(f"{MODO} ", self.claude() + " ")

    def test_jarvis_forge_dev_e_retomada_tambem(self):
        pasta = self.home / ".claude/projects" / str(self.home / "Forge").replace("/", "-")
        pasta.mkdir(parents=True)
        r = self.rodar("--sem-tmux", "--dev")
        self.assertEqual(r.returncode, 0, r.stderr)
        linha = self.claude()
        self.assertIn("--continue", linha)
        self.assertIn(f"{MODO} ", linha + " ")

    def test_jarvis_do_projeto_abre_em_automatico(self):
        projeto = self.home / "meu-projeto"
        projeto.mkdir()
        r = subprocess.run(["bash", str(RAIZ / "scripts/jarvis"), "--sem-tmux"], cwd=projeto, env={**self.env}, capture_output=True,
                           text=True, stdin=subprocess.DEVNULL)
        self.assertEqual(r.returncode, 0, r.stderr)
        linha = self.claude()
        self.assertIn("--continue", linha)
        self.assertIn(f"{MODO} ", linha + " ")

    def abrir_projeto(self, settings=None, local=None):
        projeto = Path(tempfile.mkdtemp(dir=self.home))  # um por chamada: subTest que falha não deixa pasta para a próxima
        (projeto / ".claude").mkdir()
        for nome, corpo in (("settings.json", settings), ("settings.local.json", local)):
            if corpo is not None:
                (projeto / ".claude" / nome).write_text(corpo, encoding="utf-8")
        return subprocess.run(["bash", str(RAIZ / "scripts/jarvis"), "--sem-tmux"], cwd=projeto, env={**self.env}, capture_output=True,
                              text=True, stdin=subprocess.DEVNULL)

    def test_projeto_sem_settings_avisa_sem_sandbox_e_segue_no_automatico(self):
        r = self.abrir_projeto()  # sonda S1 do parecer de segurança
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("sandbox desligado neste projeto", r.stderr)
        self.assertIn(f"{MODO} ", self.claude() + " ")

    def test_sandbox_desligado_ou_settings_quebrado_tambem_avisa(self):
        for corpo in ('{"sandbox": {"enabled": false}}', '{"sandbox": {}}', "{isso nao e json", '{"sandbox": {"enabled": "true"}}'):
            with self.subTest(corpo=corpo):
                self.assertIn("sandbox desligado", self.abrir_projeto(settings=corpo).stderr)

    def test_sandbox_ligado_nao_avisa(self):
        for kw in ({"settings": '{"sandbox": {"enabled": true}}'}, {"local": '{"sandbox": {"enabled": true}}'}):
            with self.subTest(kw=kw):
                r = self.abrir_projeto(**kw)
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertNotIn("sandbox desligado", r.stderr)

    def test_nenhuma_instrucao_manda_abrir_o_claude_sem_o_modo(self):
        """Linha de código com o `claude` solto (não subcomando) tem de trazer o modo; vale para README, modelo e preparar-estacao."""
        solto = re.compile(r"(?:^|`)claude(?: (?!plugin\b|mcp\b|config\b|update\b|doctor\b|--version\b)[^`]*)?(?:`|$)")
        achou = 0
        for rel in ("README.md", "templates/projeto/CLAUDE.md", "scripts/preparar-estacao.sh"):
            for n, linha in enumerate((RAIZ / rel).read_text(encoding="utf-8").splitlines(), 1):
                if "/login" in linha and "abra" not in linha.lower():
                    continue
                if solto.search(linha):
                    achou += 1
                    self.assertIn(MODO, linha, f"{rel}:{n} abre o claude sem {MODO}: {linha.strip()[:120]}")
        self.assertGreaterEqual(achou, 3)  # o README (uso num projeto), o modelo e o roteiro do preparar-estacao

    def test_modelo_de_projeto_manda_conferir_o_sandbox(self):
        texto = (RAIZ / "templates/projeto/CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn(MODO, texto)
        self.assertIn("confere o sandbox", texto)


# DIR-31 (diretriz 31, v0478 E67.1): visão de foco (Focus view) ligada por padrão no atalho `jarvis` e no modelo de projeto,
# sem decidir pelo dono quando um arquivo dele já decide; e a regra de linguagem fácil no texto do Jarvis.
FOCO_E_TELA = '--settings {"viewMode":"focus","tui":"fullscreen"}'


class AtalhoAbreNaVisaoDeFoco(unittest.TestCase):
    setUp, chamadas = tf.JarvisForgeVigente.setUp, tf.JarvisForgeVigente.chamadas

    def abrir(self, usuario=None, projeto=None, local=None, **env):
        """Roda scripts/jarvis num projeto novo com os três arquivos dados (None: ausente); devolve a linha do `claude` aberto."""
        pasta = Path(tempfile.mkdtemp(dir=self.home))
        (pasta / ".claude").mkdir()
        (self.home / ".claude").mkdir(exist_ok=True)
        for arquivo, corpo in ((self.home / ".claude/settings.json", usuario), (pasta / ".claude/settings.json", projeto),
                               (pasta / ".claude/settings.local.json", local)):
            arquivo.unlink(missing_ok=True)
            if corpo is not None:
                arquivo.write_text(corpo, encoding="utf-8")
        self.registro.unlink(missing_ok=True)
        ambiente = {k: v for k, v in self.env.items()
                    if k not in ("CLAUDE_CONFIG_DIR", "CLAUDE_CODE_NO_FLICKER", "CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN")}
        r = subprocess.run(["bash", str(RAIZ / "scripts/jarvis"), "--sem-tmux"], cwd=pasta, env={**ambiente, **env},
                           capture_output=True, text=True, stdin=subprocess.DEVNULL)
        self.assertEqual(r.returncode, 0, r.stderr)
        abertos = [c for c in self.chamadas() if c.startswith("claude --")]
        self.assertEqual(len(abertos), 1, self.chamadas())
        return abertos[0] + " "

    def test_sem_nenhum_arquivo_liga_a_visao_e_a_tela_cheia(self):
        linha = self.abrir()
        self.assertIn(FOCO_E_TELA + " ", linha)
        self.assertNotIn("--verbose", linha)  # o --verbose venceria o viewMode

    def test_viewmode_em_qualquer_arquivo_do_dono_nao_e_passado(self):
        for onde in ("usuario", "projeto", "local"):
            with self.subTest(onde=onde):
                linha = self.abrir(**{onde: '{"viewMode": "default"}'})
                self.assertNotIn("--settings", linha)

    def test_viewmode_focus_ja_gravado_so_acrescenta_a_tela_cheia(self):
        linha = self.abrir(projeto='{"viewMode": "focus"}')
        self.assertIn('--settings {"tui":"fullscreen"} ', linha)
        self.assertNotIn("viewMode", linha)

    def test_tui_decidido_por_arquivo_ou_variavel_nao_e_passado(self):
        casos = ({"local": '{"tui": "default"}'}, {"usuario": '{"tui": "default"}'},
                 {"CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN": "1"}, {"CLAUDE_CODE_NO_FLICKER": "1"})
        for caso in casos:
            with self.subTest(caso=caso):
                self.assertIn('--settings {"viewMode":"focus"} ', self.abrir(**caso))

    def test_arquivo_ilegivel_nao_decide_pelo_dono(self):
        for onde in ("usuario", "projeto", "local"):
            with self.subTest(onde=onde):
                self.assertNotIn("--settings", self.abrir(**{onde: "{isso nao e json"}))

    def test_arquivo_local_vence_o_projeto(self):
        linha = self.abrir(projeto='{"viewMode": "focus"}', local='{"viewMode": "default"}')
        self.assertNotIn("--settings", linha)

    def test_python_que_falha_nao_impede_a_abertura(self):
        falso = self.home / "py-falso"
        falso.mkdir()
        (falso / "python3").write_text("#!/bin/sh\nexit 3\n")
        (falso / "python3").chmod(0o755)
        self.assertNotIn("--settings", self.abrir(PATH=f"{falso}:{self.env['PATH']}"))


class ModeloELinguagem(unittest.TestCase):
    def test_modelo_de_projeto_liga_a_visao_sem_trocar_o_renderizador(self):
        modelo = json.loads((RAIZ / "templates/projeto/.claude/settings.json").read_text(encoding="utf-8"))
        self.assertEqual(modelo.get("viewMode"), "focus")
        self.assertNotIn("tui", modelo)  # a tela cheia muda seleção e rolagem de quem clona: fica só no atalho do dono

    def test_jarvis_tem_a_regra_de_linguagem_facil_uma_vez(self):
        linhas = [l for l in (RAIZ / "agents/jarvis.md").read_text(encoding="utf-8").splitlines() if "**Linguagem fácil:**" in l]
        self.assertEqual(len(linhas), 1)
        for trecho in ("frases curtas", "sem nome de branch, pasta nem jargão"):
            self.assertIn(trecho, linhas[0])

class EstacaoExigeGh(unittest.TestCase):
    def rodar(self, versao):
        """preparar-estacao.sh --simular com um gh falso da `versao` (None: saída ilegível); sudo, curl e apt-get falsos registram a chamada."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            home, bin_falso, registro = tmp / "home", tmp / "bin", tmp / "chamadas"
            home.mkdir()
            bin_falso.mkdir()
            falsos = {n: f'echo "{n} $*" >> "{registro}"\nexit 1\n' for n in ("sudo", "curl", "apt-get")}
            # sem versão legível o gh conta como antigo (o PATH do teste ainda enxerga o gh real da máquina, que não pode valer)
            saida = f'echo "gh version {versao} (2026-01-01)"' if versao else 'echo "lixo"'
            falsos["gh"] = f'case "$1" in --version) {saida}; exit 0 ;; esac\nexit 1\n'
            falsos["dpkg-query"] = "exit 1\n"
            falsos["claude"] = "exit 1\n"
            for nome, corpo in falsos.items():
                (bin_falso / nome).write_text("#!/bin/sh\n" + corpo)
                (bin_falso / nome).chmod(0o755)
            env = tf.ambiente_limpo()
            env.update(HOME=str(home), NVM_DIR=str(home / ".nvm"), PATH=f"{bin_falso}:{env['PATH']}")
            r = subprocess.run(["bash", str(RAIZ / "scripts/preparar-estacao.sh"), "--simular"], env=env, capture_output=True,
                               text=True, stdin=subprocess.DEVNULL)
            self.assertFalse(registro.exists(), "o --simular chamou comando que altera o sistema")
            return r

    def test_gh_2_45_do_apt_do_ubuntu_manda_instalar_pelo_repositorio_oficial(self):
        r = self.rodar("2.45.0")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("apt-get install -y -qq gh", r.stdout)
        self.assertIn("fez: instalou o gh >= 2.47", r.stdout)

    def test_gh_logo_abaixo_do_minimo_tambem(self):
        self.assertIn("apt-get install -y -qq gh", self.rodar("2.46.9").stdout)

    def test_versao_ilegivel_conta_como_antiga(self):
        self.assertIn("apt-get install -y -qq gh", self.rodar(None).stdout)

    def test_gh_na_versao_minima_ou_acima_nao_mexe(self):
        for versao in ("2.47.0", "2.104.0", "3.1.0"):
            with self.subTest(versao=versao):
                r = self.rodar(versao)
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertNotIn("apt-get install -y -qq gh", r.stdout)
                self.assertIn(f"fez: gh {versao} (>= 2.47)", r.stdout)

    def test_o_apt_comum_nao_trata_o_gh_do_ubuntu(self):
        r = self.rodar("2.45.0")
        self.assertNotRegex(r.stdout, r"faltam: [^\n]*\bgh\b")


if __name__ == "__main__":
    unittest.main()
