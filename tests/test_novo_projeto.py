"""Primeiro uso (F1): `forge novo-projeto` de ponta a ponta, sem rede.

Um `gh` falso cria repositórios bare locais e um `claude` falso só registra como foi chamado.
HOME, estado e git são temporários: nada toca a máquina de quem roda os testes.
"""
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

GH_FALSO = r"""#!/usr/bin/env bash
echo "gh $*" >> "$FAKE_DIR/gh.log"
remoto() { echo "$FAKE_DIR/remotos/$1.git"; }
case "$1 $2" in
  "auth status") [ ! -e "$FAKE_DIR/sem-auth" ] || { echo "You are not logged into any GitHub hosts." >&2; exit 1; } ;;
  "api user") echo "pessoa-teste" ;;
  "repo view") [ -d "$(remoto "$3")" ] ;;
  "repo create")
    [ ! -d "$(remoto "$3")" ] || { echo "GraphQL: Name already exists on this account" >&2; exit 1; }
    mkdir -p "$(dirname "$(remoto "$3")")"; git init -q --bare -b main "$(remoto "$3")" ;;
  "repo clone")
    if [ -e "$FAKE_DIR/falha-clone" ]; then rm "$FAKE_DIR/falha-clone"; echo "network error" >&2; exit 1; fi
    git clone -q "$(remoto "$3")" "$4" 2>/dev/null ;;
  *) echo "gh falso: $*" >&2; exit 64 ;;
esac
"""

CLAUDE_FALSO = r"""#!/usr/bin/env bash
printf 'cwd=%s\nargs=%s\n' "$PWD" "$*" >> "$FAKE_DIR/claude.log"
"""


class NovoProjeto(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="novo-projeto-"))
        self.fake = self.tmp / "fake"
        self.home = self.tmp / "home"
        bin_falso = self.fake / "bin"
        bin_falso.mkdir(parents=True)
        self.home.mkdir()
        for nome, corpo in (("gh", GH_FALSO), ("claude", CLAUDE_FALSO)):
            (bin_falso / nome).write_text(corpo, encoding="utf-8")
            (bin_falso / nome).chmod(0o755)
        (self.home / "gitconfig").write_text("[user]\n\tname = Pessoa Teste\n\temail = pessoa@exemplo.test\n",
                                             encoding="utf-8")
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_") and k != "CLAUDE_PROJECT_DIR"}
        self.env.update(HOME=str(self.home), FAKE_DIR=str(self.fake), GIT_CONFIG_NOSYSTEM="1",
                        GIT_CONFIG_GLOBAL=str(self.home / "gitconfig"),
                        PATH=f"{bin_falso}:{os.environ['PATH']}")
        self.env.pop("XDG_STATE_HOME", None)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def forge(self, *args, entrada=""):
        return subprocess.run(["bash", str(RAIZ / "bin/forge"), *args], input=entrada, env=self.env,
                              cwd=self.tmp, capture_output=True, text=True, timeout=60)

    def log(self, arquivo):
        p = self.fake / arquivo
        return p.read_text(encoding="utf-8") if p.exists() else ""

    def remoto(self, nome="meu-app"):
        return self.fake / "remotos" / "pessoa-teste" / f"{nome}.git"

    def estados(self):
        pasta = self.home / ".local/state/forge/novo-projeto"
        return sorted(pasta.glob("*.json")) if pasta.exists() else []

    def test_caminho_feliz(self):
        pasta = self.tmp / "projetos" / "meu-app"
        r = self.forge("novo-projeto", entrada=f"meu-app\n{pasta}\n")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        gh = self.log("gh.log")
        self.assertRegex(gh, r"repo create pessoa-teste/meu-app .*--private")
        self.assertLess(gh.index("repo create"), gh.index("repo clone"))
        self.assertNotIn("auth token", gh, "o token nunca é lido pelo script")
        ramos = subprocess.run(["git", "-C", str(self.remoto()), "branch", "--format=%(refname:short)"],
                               env=self.env, capture_output=True, text=True, check=True).stdout.split()
        self.assertEqual(sorted(ramos), ["develop", "homolog", "main"])
        autor = subprocess.run(["git", "-C", str(pasta), "log", "-1", "--format=%an <%ae>", "main"],
                               env=self.env, capture_output=True, text=True, check=True).stdout.strip()
        self.assertEqual(autor, "Pessoa Teste <pessoa@exemplo.test>")
        atual = subprocess.run(["git", "-C", str(pasta), "branch", "--show-current"], env=self.env,
                               capture_output=True, text=True, check=True).stdout.strip()
        self.assertEqual(atual, "develop")
        self.assertIn(".forge/perfil", (pasta / ".gitignore").read_text(encoding="utf-8").splitlines())
        self.assertFalse((pasta / ".forge/versao").exists(), "a adoção é da skill, no fim do roteiro")
        claude = self.log("claude.log")
        self.assertIn(f"cwd={pasta}", claude)
        self.assertIn("--agent forge:jarvis", claude)
        self.assertIn("forge:novo-projeto", claude)

    def test_estado_de_retomada_nao_guarda_segredo(self):
        pasta = self.tmp / "meu-app"
        self.assertEqual(self.forge("novo-projeto", entrada=f"meu-app\n{pasta}\n").returncode, 0)
        arquivos = self.estados() + [pasta / ".forge/novo-projeto.json"]
        self.assertTrue(arquivos[0].exists())
        for arq in arquivos:
            estado = json.loads(arq.read_text(encoding="utf-8"))
            self.assertEqual(estado["nome"], "meu-app")
            self.assertEqual(estado["dono"], "pessoa-teste")
            self.assertTrue({"repo_criado", "clonado", "commit_inicial", "branches"} <= set(estado["etapas"]))
            self.assertNotRegex(arq.read_text(encoding="utf-8"), r"(?i)token|senha|ghp_")

    def test_sem_gh_auth_nao_cria_nada(self):
        (self.fake / "sem-auth").write_text("")
        pasta = self.tmp / "meu-app"
        r = self.forge("novo-projeto", entrada=f"meu-app\n{pasta}\n")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("gh auth login", r.stderr)
        self.assertNotIn("repo create", self.log("gh.log"))
        self.assertFalse(pasta.exists())
        self.assertEqual(self.log("claude.log"), "")

    def test_nome_existente_pergunta_outro_e_nao_escreve_no_existente(self):
        subprocess.run(["git", "init", "-q", "--bare", str(self.remoto())], env=self.env, check=True)
        pasta = self.tmp / "outro-app"
        r = self.forge("novo-projeto", entrada=f"meu-app\noutro-app\n{pasta}\n")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("já existe", r.stdout + r.stderr)
        criados = re.findall(r"repo create (\S+)", self.log("gh.log"))
        self.assertEqual(criados, ["pessoa-teste/outro-app"])
        existente = subprocess.run(["git", "-C", str(self.remoto()), "branch"], env=self.env,
                                   capture_output=True, text=True).stdout.strip()
        self.assertEqual(existente, "", "o repositório existente não pode receber commits")

    def test_nome_invalido_e_recusado(self):
        r = self.forge("novo-projeto", entrada="../x\n")
        self.assertNotEqual(r.returncode, 0)
        self.assertNotIn("repo create", self.log("gh.log"))

    def test_retomada_depois_de_parar_no_meio(self):
        (self.fake / "falha-clone").write_text("")
        pasta = self.tmp / "meu-app"
        entrada = f"meu-app\n{pasta}\n"
        primeira = self.forge("novo-projeto", entrada=entrada)
        self.assertNotEqual(primeira.returncode, 0)
        self.assertEqual(self.log("claude.log"), "")
        estado = json.loads(self.estados()[0].read_text(encoding="utf-8"))
        self.assertEqual(estado["etapas"], ["repo_criado"])
        segunda = self.forge("novo-projeto", entrada=entrada)
        self.assertEqual(segunda.returncode, 0, segunda.stderr + segunda.stdout)
        self.assertIn("retomando", (segunda.stdout + segunda.stderr).lower())
        self.assertEqual(len(re.findall(r"repo create", self.log("gh.log"))), 1, "o repositório não é recriado")
        self.assertIn(f"cwd={pasta}", self.log("claude.log"))
        ramos = subprocess.run(["git", "-C", str(self.remoto()), "branch", "--format=%(refname:short)"],
                               env=self.env, capture_output=True, text=True, check=True).stdout.split()
        self.assertEqual(sorted(ramos), ["develop", "homolog", "main"])

    def test_rodar_de_novo_com_tudo_pronto_so_reabre_o_claude(self):
        pasta = self.tmp / "meu-app"
        entrada = f"meu-app\n{pasta}\n"
        self.assertEqual(self.forge("novo-projeto", entrada=entrada).returncode, 0)
        self.assertEqual(self.forge("novo-projeto", entrada=entrada).returncode, 0)
        self.assertEqual(len(re.findall(r"repo create", self.log("gh.log"))), 1)
        self.assertEqual(self.log("claude.log").count("cwd="), 2)


class Despachante(unittest.TestCase):
    def forge(self, *args):
        return subprocess.run(["bash", str(RAIZ / "bin/forge"), *args], capture_output=True, text=True, timeout=30)

    def test_sem_argumento_lista_os_subcomandos(self):
        r = self.forge()
        self.assertEqual(r.returncode, 0)
        self.assertIn("novo-projeto", r.stdout)

    def test_subcomando_desconhecido_ou_malformado_sai_2(self):
        for ruim in ("nao-existe", "../bin/forge-init", "-x"):
            with self.subTest(sub=ruim):
                self.assertEqual(self.forge(ruim).returncode, 2)


class PerfilEJarvis(unittest.TestCase):
    def test_forge_init_ignora_o_perfil_da_pessoa(self):
        tmp = Path(tempfile.mkdtemp(prefix="perfil-"))
        try:
            env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
            subprocess.run(["git", "init", "-q", str(tmp)], env=env, check=True)
            subprocess.run(["bash", str(RAIZ / "bin/forge-init"), "--nome", "Demo", str(tmp)],
                           env=env, check=True, capture_output=True)
            linhas = (tmp / ".gitignore").read_text(encoding="utf-8").splitlines()
            self.assertIn(".forge/perfil", linhas)
        finally:
            shutil.rmtree(tmp)

    def test_jarvis_oferece_o_roteiro_e_cita_o_perfil(self):
        texto = (RAIZ / "agents/jarvis.md").read_text(encoding="utf-8")
        self.assertIn("forge:novo-projeto", texto)
        self.assertIn(".forge/versao", texto)
        self.assertIn(".forge/perfil", texto)
        self.assertIn("forge:modo-iniciante", texto)

    def test_skills_do_primeiro_uso_existem(self):
        for nome in ("novo-projeto", "modo-iniciante"):
            with self.subTest(skill=nome):
                self.assertTrue((RAIZ / "skills" / nome / "SKILL.md").is_file())

    def test_skill_novo_projeto_chama_iniciar_projeto_e_nao_pede_segredo(self):
        texto = (RAIZ / "skills/novo-projeto/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("forge:iniciar-projeto", texto)
        self.assertIn("gh auth login", texto)
        self.assertRegex(texto, r"(?i)nunca.*(token|senha)")


if __name__ == "__main__":
    unittest.main()
