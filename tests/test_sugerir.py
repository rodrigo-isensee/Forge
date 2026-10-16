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

from ambiente_git import sem_manutencao

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
        self.env = sem_manutencao(self.env)
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


class Higiene(Base):
    def guardado(self, texto):
        codigo, saida = self.rodar("--guardar", texto)
        self.assertEqual(codigo, 0, saida)
        (arq,) = self.na_fila()
        return arq.read_text(encoding="utf-8"), saida

    def test_guardar_anonimiza_grava_600_e_nao_envia_nem_pergunta(self):
        texto, saida = self.guardado(TEXTO)
        self.sem_dados(texto)
        self.assertEqual(self.na_fila()[0].stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.fila.stat().st_mode & 0o777, 0o700)
        self.assertNotIn("issue create", self.log_gh())

    def test_guardar_nunca_chama_o_gh_nem_com_terminal_e_resposta_s(self):
        codigo, saida = self.rodar("--guardar", TEXTO, respostas=["s", "s"])
        self.assertEqual(codigo, 0, saida)
        self.assertEqual(self.log_gh(), "")
        self.assertEqual(len(self.na_fila()), 1)

    def test_guardar_so_vale_como_primeiro_argumento(self):
        for args in (("texto", "--guardar"), ("x", "--guardar", "y"), ("--arquivo", "/dev/null", "--guardar")):
            codigo, saida = self.rodar(*args, respostas=["s", "s"])
            self.assertEqual(codigo, 2, saida)
            self.assertEqual(self.log_gh(), "", saida)

    def test_guardar_dentro_do_claude_funciona(self):
        codigo, saida = self.rodar("--guardar", TEXTO, env={**self.env, "CLAUDECODE": "1"})
        self.assertEqual(codigo, 0, saida)
        self.sem_dados(self.na_fila()[0].read_text(encoding="utf-8"))

    def test_remove_controle_e_direcao_unicode_do_texto_e_do_titulo(self):
        sujo = "\x1b[8mSEGREDO\x1b[0m\rfalso\u202eoculto\u2066x\u2069\u200bz\x07fim\nlinha 2\tcom tab"
        texto, _ = self.guardado(sujo)
        for ruim in ("\x1b", "\r", "\u202e", "\u2066", "\u2069", "\u200b", "\x07"):
            self.assertNotIn(ruim, texto)
        self.assertIn("linha 2\tcom tab", texto)
        codigo, saida = self.rodar(sujo, respostas=["s"])
        self.assertEqual(codigo, 0, saida)
        enviado = self.log_gh()
        for ruim in ("\x1b", "\r", "\u202e", "\u200b"):
            self.assertNotIn(ruim, enviado)

    def test_remove_controle_tambem_do_que_ja_estava_na_fila(self):
        self.fila.mkdir(parents=True)
        (self.fila / "x.md").write_text("ok\x1b[8mescondido\u202e\n", encoding="utf-8")
        self.rodar("--fila", respostas=["s"])
        self.assertNotIn("\x1b", self.log_gh())
        self.assertNotIn("\u202e", self.log_gh())

    def casos(self, pares):
        for entrada, proibido in pares:
            with self.subTest(entrada=entrada):
                self.setUp_limpa()
                texto, saida = self.guardado("antes " + entrada + " depois")
                self.assertNotIn(proibido, texto)
                self.assertIn("antes", texto)
                self.assertIn("depois", texto)

    def setUp_limpa(self):
        shutil.rmtree(self.fila, ignore_errors=True)

    def test_pem_inteiro(self):
        pem = "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEAxyz1234567890abcdef\nQWERTYUIOPasdfghjkl\n-----END RSA PRIVATE KEY-----"
        self.casos([(pem, "MIIEowIBAAKCAQEA"), (pem, "QWERTYUIOP"), (pem, "BEGIN RSA")])

    def test_chaves_aws(self):
        self.casos([("AKIAIOSFODNN7EXAMPLE", "AKIAIOSFODNN7"),
                    ("aws_secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY", "wJalrXUtnFEMI"),
                    ("a chave wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY sozinha", "wJalrXUtnFEMI")])

    def test_pares_de_segredo_com_aspas_e_espacos(self):
        self.casos([('password:"p4ss w0rd"', "w0rd"), ("secret = 'meu segredo grande'", "grande"),
                    ('token: "abc def ghi"', "ghi"), ('apikey="x y z 123"', "123"), ("db_password=hunter22", "hunter22"),
                    ("api_key: 'k k k'", "k k k"), ("Authorization: Basic dXNlcjpwYXNzd29yZA==", "dXNlcjpwYXNzd29yZA")])

    def test_chave_em_json_escapado(self):
        self.casos([('{\\"api_key\\": \\"AbCdEf123456\\"}', "AbCdEf123456"), ('{\\"password\\":\\"hunter2\\"}', "hunter2"),
                    ('{\\\\\\"secret\\\\\\": \\\\\\"zzzqq\\\\\\"}', "zzzqq")])

    def test_nome_do_projeto_com_ponto_ou_repetido(self):
        self.casos([("o meu.projeto.secreto caiu", "meu.projeto"), ("o meu--projeto-secreto caiu", "projeto-secreto"),
                    ("o Meu.Projeto_Secreto caiu", "Projeto_Secreto")])

    def test_segredo_em_url_codificada(self):
        self.casos([("?token%3Dabcdef123456", "abcdef123456"), ("password%3Dhunter2", "hunter2"), ("api_key%3Aabc999zz", "abc999zz")])

    def test_segredo_codificado_duas_vezes_e_chaves_curtas(self):
        self.casos([("password%253Dhunter2", "hunter2"), ("token%253Aabcdef123456", "abcdef123456"), ("key=abc12345", "abc12345"),
                    ("pass=hunter22", "hunter22"), ("?key=zzz999&x=1", "zzz999")])

    def test_basic_auth_em_url(self):
        self.casos([("postgres://admin:s3nha@db.exemplo.com:5432/x", "s3nha"), ("https://user:pw123@exemplo.org/a", "pw123")])

    def test_ips(self):
        self.casos([("host 10.20.30.40 caiu", "10.20.30.40"), ("v6 2001:db8:85a3::8a2e:370:7334 caiu", "8a2e:370"),
                    ("loop ::1 e fe80::1ff:fe23:4567:890a", "fe80")])

    def test_hostnames_internos(self):
        self.casos([("db01.corp.local", "db01"), ("api.interno.internal", "api.interno"), ("nas.lan", "nas.lan"),
                    ("wiki.meu-projeto-secreto.com.br", "wiki."), ("meuprojetosecreto.dev", "meuprojetosecreto")])

    def test_toda_url_vira_url_menos_as_do_forge(self):
        texto, _ = self.guardado("veja https://intranet.empresa.local/wiki/Sistema e www.empresa.local/x e "
                                 "https://exemplo.com/docs e https://github.com/rodrigo-isensee/Forge/issues/12 fim")
        self.assertNotIn("empresa.local", texto)
        self.assertNotIn("exemplo.com", texto)
        self.assertIn("<url>", texto)
        self.assertIn("https://github.com/rodrigo-isensee/Forge/issues/12", texto)

    def test_url_que_foge_do_repositorio_do_forge_nao_fica(self):
        texto, _ = self.guardado("https://github.com/rodrigo-isensee/Forge/../../outro/repo e https://github.com/rodrigo-isensee/Forge-x")
        self.assertNotIn("outro/repo", texto)
        self.assertNotIn("Forge-x", texto)

    def test_variantes_do_nome_do_projeto(self):
        self.casos([("meu-projeto-secreto", "secreto"), ("Meu Projeto Secreto", "Secreto"), ("meu_projeto_secreto", "secreto"),
                    ("MEUPROJETOSECRETO", "SECRETO"), ("MeuProjetoSecreto", "Secreto"), ("meuprojetosecreto", "secreto")])

    def test_variantes_sem_acento_do_nome_com_acento(self):
        (self.proj / ".forge" / "novo-projeto.json").write_text('{"nome": "Sistema Ação", "dono": "x-y"}\n', encoding="utf-8")
        self.casos([("Sistema-Acao", "Acao"), ("sistema acao", "acao"), ("SistemaAção", "Ação"), ("sistema_acao", "acao"),
                    ("SISTEMA-AÇÃO", "AÇÃO")])

    def test_caminhos_windows_e_unc(self):
        self.casos([("C:\\Users\\bob\\app", "bob"), ("C:/Users/bob/app", "bob"), ("\\\\servidor\\share\\dir", "servidor")])

    def test_aviso_nao_afirma_que_o_texto_esta_limpo(self):
        _, saida = self.rodar(TEXTO, respostas=["n"])
        self.assertNotIn("já não tem dados do seu projeto", saida)
        self.assertIn("removi o que reconheci; confira o texto abaixo antes de confirmar", saida)

    def test_nao_estraga_texto_comum_do_forge(self):
        texto, _ = self.guardado("hooks/conformidade.py na versão 0.12.0 falha às 10:30 com R-CONTRIB; veja docs/regras/R-CONTRIB.md")
        self.assertIn("hooks/conformidade.py", texto)
        self.assertIn("0.12.0", texto)
        self.assertIn("10:30", texto)
        self.assertIn("R-CONTRIB", texto)


if __name__ == "__main__":
    unittest.main()
