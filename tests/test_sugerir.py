"""Primeiro uso (F6): `forge sugerir`, sugestão anônima ao Forge, com `gh` falso e sem rede.

HOME, estado e git são temporários. As confirmações são respondidas num terminal de verdade (pty).
"""
import os
import pty
import select
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SUGERIR = RAIZ / "bin" / "forge-sugerir"
TOKEN = "ghp_" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8"
TEXTO = f"""Problema observado: o hook recusou editar /home/fulano/meu-projeto-secreto/.claude/settings.json no projeto meu-projeto-secreto.
Quem relatou: fulano@empresa.com.br (login fulano-dev), repositório https://github.com/fulano-dev/meu-projeto-secreto.git.
Usei o token {TOKEN} e git@github.com:fulano-dev/meu-projeto-secreto.git sem sucesso.
Proposta: hooks/conformidade.py explicar o motivo da recusa.
Como medir: quantas recusas viram pedido de ajuda.
"""
GH_FALSO = """#!/usr/bin/env bash
{ echo "gh $*"; } >> "$FAKE_DIR/gh.log"
if [ "$1 $2" = "issue create" ]; then
  [ ! -e "$FAKE_DIR/sem-rede" ] || { echo "error connecting to api.github.com" >&2; exit 1; }
  while [ $# -gt 0 ]; do
    [ "$1" != "--body-file" ] || { { echo "--- corpo"; cat "$2"; echo "--- fim"; } >> "$FAKE_DIR/gh.log"; }
    [ "$1" != "--title" ] || echo "titulo: $2" >> "$FAKE_DIR/gh.log"
    shift
  done
  echo "https://github.com/rodrigo-isensee/Forge/issues/999"
  exit 0
fi
echo "gh falso: comando inesperado $*" >&2; exit 64
"""


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="sugerir-"))
        self.home = self.tmp / "home"
        self.fake = self.tmp / "fake"
        bin_falso = self.tmp / "bin"
        for p in (self.home, self.fake, bin_falso):
            p.mkdir()
        (bin_falso / "gh").write_text(GH_FALSO, encoding="utf-8")
        (bin_falso / "gh").chmod(0o755)
        (self.home / "gitconfig").write_text("[user]\n\tname = Fulano de Tal\n\temail = fulano@empresa.com.br\n", encoding="utf-8")
        self.env = {k: v for k, v in os.environ.items()
                    if not k.startswith(("GIT_", "CLAUDE", "XDG_", "FORGE_")) and k not in ("USER", "LOGNAME")}
        self.env.update(HOME=str(self.home), USER="fulano", GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=str(self.home / "gitconfig"),
                        PATH=f"{bin_falso}:{os.environ['PATH']}", FAKE_DIR=str(self.fake))
        self.proj = self.home / "meu-projeto-secreto"
        (self.proj / ".forge").mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(self.proj)], env=self.env, check=True)
        (self.proj / ".forge" / "novo-projeto.json").write_text(
            '{"nome": "meu-projeto-secreto", "pasta": "/home/fulano/meu-projeto-secreto", "dono": "fulano-dev", "etapas": []}\n',
            encoding="utf-8")
        self.fila = self.home / ".local/state/forge/sugestoes"

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def rodar(self, *args, respostas=None, env=None):
        """Com `respostas`, num terminal (pty); sem elas, sem terminal."""
        env = env or self.env
        if respostas is None:
            r = subprocess.run([sys.executable, str(SUGERIR), *args], env=env, cwd=self.proj, capture_output=True, text=True,
                               timeout=60, stdin=subprocess.DEVNULL)
            return r.returncode, r.stdout + r.stderr
        mestre, escravo = pty.openpty()
        os.write(mestre, "".join(r + "\n" for r in respostas).encode())
        p = subprocess.Popen([sys.executable, str(SUGERIR), *args], env=env, cwd=self.proj, stdin=escravo, stdout=escravo,
                             stderr=escravo, close_fds=True)
        os.close(escravo)
        saida, limite = b"", time.time() + 25
        while time.time() < limite:
            if not select.select([mestre], [], [], 1)[0]:
                continue
            try:
                bloco = os.read(mestre, 4096)
            except OSError:
                break
            if not bloco:
                break
            saida += bloco
        if p.poll() is None:
            p.kill()
            saida += b"\n[TRAVOU esperando resposta]"
        p.wait(timeout=30)
        os.close(mestre)
        return p.returncode, saida.decode("utf-8", "replace").replace("\r", "")

    def log_gh(self):
        arq = self.fake / "gh.log"
        return arq.read_text(encoding="utf-8") if arq.exists() else ""

    def na_fila(self):
        return sorted(self.fila.glob("*.md")) if self.fila.is_dir() else []

    def sem_dados(self, texto):
        for dado in ("/home/fulano", "fulano@empresa", "fulano-dev", "fulano", "meu-projeto-secreto", TOKEN, "A1b2C3d4E5f6", "empresa.com.br"):
            self.assertNotIn(dado, texto)
        self.assertIn("hooks/conformidade.py", texto, "o que é do Forge fica")
        self.assertIn("Como medir", texto)


class Anonimizar(Base):
    def test_remove_caminho_email_token_url_usuario_e_nome_do_projeto_e_nada_sai_sem_sim(self):
        codigo, saida = self.rodar(TEXTO, respostas=["n"])
        self.assertEqual(codigo, 0, saida)
        (arq,) = self.na_fila()
        self.sem_dados(arq.read_text(encoding="utf-8"))
        self.sem_dados(saida)  # o que a pessoa vê é o texto final, já anonimizado
        self.assertNotIn("issue create", self.log_gh())

    def test_texto_pelo_arquivo(self):
        (self.tmp / "s.txt").write_text(TEXTO, encoding="utf-8")
        codigo, saida = self.rodar("--arquivo", str(self.tmp / "s.txt"), respostas=["n"])
        self.assertEqual(codigo, 0, saida)
        self.sem_dados(self.na_fila()[0].read_text(encoding="utf-8"))

    def test_sem_texto_e_erro_de_uso(self):
        codigo, saida = self.rodar(respostas=[])
        self.assertEqual(codigo, 2, saida)
        self.assertEqual(self.na_fila(), [])


class Envio(Base):
    def test_confirmada_envia_como_issue_no_forge_com_o_texto_mostrado_e_avisa_do_nome_no_github(self):
        codigo, saida = self.rodar(TEXTO, respostas=["s"])
        self.assertEqual(codigo, 0, saida)
        log = self.log_gh()
        self.assertIn("gh issue create -R rodrigo-isensee/Forge", log)
        self.assertNotIn("--label", log)
        corpo = log.split("--- corpo")[1].split("--- fim")[0]
        self.sem_dados(corpo)
        self.assertIn("issues/999", saida)
        self.assertIn("nome de usuário", saida)
        self.assertIn("GitHub", saida)
        self.assertEqual(self.na_fila(), [], "enviou: nada fica na fila")
        self.assertIn(corpo.strip().splitlines()[0], saida, "a pessoa viu o texto que foi enviado")

    def test_recusada_nao_envia_e_guarda_na_fila(self):
        codigo, saida = self.rodar(TEXTO, respostas=[""])
        self.assertEqual(codigo, 0, saida)
        self.assertNotIn("issue create", self.log_gh())
        self.assertEqual(len(self.na_fila()), 1)
        self.assertIn("forge sugerir --fila", saida)

    def test_sem_rede_vai_para_a_fila(self):
        (self.fake / "sem-rede").write_text("")
        codigo, saida = self.rodar(TEXTO, respostas=["s"])
        self.assertEqual(codigo, 1, saida)
        self.assertEqual(len(self.na_fila()), 1)
        self.sem_dados(self.na_fila()[0].read_text(encoding="utf-8"))
        self.assertIn("forge sugerir --fila", saida)

    def test_sem_terminal_nao_envia_e_guarda_na_fila(self):
        codigo, saida = self.rodar(TEXTO)
        self.assertEqual(codigo, 0, saida)
        self.assertNotIn("issue create", self.log_gh())
        self.assertEqual(len(self.na_fila()), 1)

    def test_dentro_do_claude_nao_envia_e_guarda_na_fila_para_a_pessoa_enviar(self):
        codigo, saida = self.rodar(TEXTO, respostas=["s"], env={**self.env, "CLAUDECODE": "1"})
        self.assertEqual(codigo, 0, saida)
        self.assertNotIn("issue create", self.log_gh())
        self.assertEqual(len(self.na_fila()), 1)
        self.assertIn("forge sugerir --fila", saida)


class Fila(Base):
    def test_fila_envia_o_que_ficou_pendente_e_esvazia(self):
        self.rodar(TEXTO, respostas=["n"])
        self.assertEqual(len(self.na_fila()), 1)
        codigo, saida = self.rodar("--fila", respostas=["s"])
        self.assertEqual(codigo, 0, saida)
        self.assertIn("gh issue create -R rodrigo-isensee/Forge", self.log_gh())
        self.assertEqual(self.na_fila(), [])

    def test_fila_anonimiza_de_novo_o_que_o_jarvis_guardou_na_mao(self):
        self.fila.mkdir(parents=True)
        (self.fila / "20261014-hook.md").write_text(TEXTO, encoding="utf-8")
        codigo, saida = self.rodar("--fila", respostas=["s"])
        self.assertEqual(codigo, 0, saida)
        self.sem_dados(self.log_gh().split("--- corpo")[1].split("--- fim")[0])

    def test_fila_recusada_mantem_o_arquivo(self):
        self.rodar(TEXTO, respostas=["n"])
        codigo, saida = self.rodar("--fila", respostas=["n"])
        self.assertEqual(codigo, 0, saida)
        self.assertNotIn("issue create", self.log_gh())
        self.assertEqual(len(self.na_fila()), 1)

    def test_fila_sem_rede_mantem_o_arquivo(self):
        self.rodar(TEXTO, respostas=["n"])
        (self.fake / "sem-rede").write_text("")
        codigo, saida = self.rodar("--fila", respostas=["s"])
        self.assertEqual(codigo, 1, saida)
        self.assertEqual(len(self.na_fila()), 1)

    def test_fila_vazia(self):
        codigo, saida = self.rodar("--fila", respostas=[])
        self.assertEqual(codigo, 0, saida)
        self.assertIn("Nada pendente", saida)

    def test_fila_dentro_do_claude_recusa(self):
        self.rodar(TEXTO, respostas=["n"])
        codigo, saida = self.rodar("--fila", respostas=["s"], env={**self.env, "CLAUDECODE": "1"})
        self.assertEqual(codigo, 2, saida)
        self.assertNotIn("issue create", self.log_gh())


if __name__ == "__main__":
    unittest.main()
