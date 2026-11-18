"""PORTAO-DEVOPS-FERRAMENTAS (v0478 E6.1): `preparar-estacao.sh --ferramentas` instala as ferramentas dos portões sem
credencial, só com o sha256 batendo, e diz o que falta. Sem rede: o curl e o pipx são falsos."""
import hashlib
import os
import re
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / "scripts" / "preparar-estacao.sh"
SOMA_FALSA = hashlib.sha256(b"conteudo\n").hexdigest()  # soma do que o curl falso grava


def executavel(caminho: Path, texto: str) -> None:
    caminho.write_text(texto, encoding="utf-8")
    caminho.chmod(caminho.stat().st_mode | stat.S_IXUSR)


def rodar(home: Path, falsos: Path, *args: str, **extra: str) -> subprocess.CompletedProcess:
    env = {"HOME": str(home), "PATH": f"{falsos}:/usr/bin:/bin", "TMPDIR": str(home), **extra}
    return subprocess.run(["bash", str(SCRIPT), *args], env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL)


class FerramentasDosPortoes(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name) / "home"
        self.falsos = Path(self.tmp.name) / "falsos"
        self.home.mkdir()
        self.falsos.mkdir()
        executavel(self.falsos / "apt-get", "#!/bin/bash\nexit 1\n")  # nunca o apt de verdade
        executavel(self.falsos / "sudo", "#!/bin/bash\nexit 1\n")

    def curl_falso(self, soma: str) -> None:
        """Grava um arquivo qualquer no -o; o arquivo de somas traz `soma` (a de verdade ou a errada)."""
        executavel(self.falsos / "curl", f"""#!/bin/bash
while [ $# -gt 0 ]; do [ "$1" = -o ] && saida="$2"; shift; done
case "$saida" in *somas) printf '%s  %s\\n' '{soma}' "${{ARQ:-x}}" > "$saida" ;; *) echo conteudo > "$saida" ;; esac
""")

    def test_simular_lista_as_tres_ferramentas_de_binario_e_nada_e_gravado(self):
        self.curl_falso("0")
        r = rodar(self.home, self.falsos, "--ferramentas", "--simular")
        self.assertEqual(r.returncode, 0, r.stderr)
        for nome in ("actionlint", "gitleaks", "osv-scanner"):
            self.assertIn(f"instalaria {nome}", r.stdout)
        self.assertFalse((self.home / ".local").exists())

    def test_ja_instalada_nao_baixa(self):
        for nome in ("actionlint", "gitleaks", "osv-scanner", "zizmor", "semgrep"):
            executavel(self.falsos / nome, "#!/bin/bash\n")
        executavel(self.falsos / "curl", "#!/bin/bash\necho baixou >&2; exit 9\n")
        r = rodar(self.home, self.falsos, "--ferramentas")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("fez: actionlint já instalado", r.stdout)
        self.assertNotIn("baixou", r.stderr)
        self.assertNotIn("falta:", r.stdout)

    def script_com_fixas(self, **somas: str) -> Path:
        """Cópia do script com as somas fixadas trocadas (ACTIONLINT, OSV), para casar com o conteúdo falso."""
        texto = SCRIPT.read_text(encoding="utf-8")
        for nome, soma in somas.items():
            texto, n = re.subn(rf'^{nome}_SHA="[0-9a-f]{{64}}"$', f'{nome}_SHA="{soma}"', texto, flags=re.M)
            self.assertEqual(n, 1, nome)
        copia = Path(self.tmp.name) / "preparar-estacao.sh"
        copia.write_text(texto, encoding="utf-8")
        return copia

    def rodar_copia(self, copia: Path, *args: str, **extra: str) -> subprocess.CompletedProcess:
        env = {"HOME": str(self.home), "PATH": f"{self.falsos}:/usr/bin:/bin", "TMPDIR": str(self.home), **extra}
        return subprocess.run(["bash", str(copia), *args], env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL)

    def test_soma_da_release_errada_nao_instala(self):
        """O arquivo existe nas somas (ARQ) e a soma diverge: o ramo de soma divergente, não o de soma ausente."""
        copia = self.script_com_fixas(OSV=SOMA_FALSA)
        self.curl_falso("0" * 64)
        r = self.rodar_copia(copia, "--ferramentas", ARQ="osv-scanner_linux_amd64")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("falta: osv-scanner: o sha256 do download não bate com as somas da release", r.stdout)
        self.assertFalse((self.home / ".local" / "bin" / "osv-scanner").exists())

    def test_soma_fixada_no_script_errada_nao_instala(self):
        """A release diz a soma certa do que baixou, mas o script fixa outra: release trocada não instala."""
        self.curl_falso(SOMA_FALSA)
        copia = self.script_com_fixas(OSV="1" * 64)
        r = self.rodar_copia(copia, "--ferramentas", ARQ="osv-scanner_linux_amd64")
        self.assertIn("falta: osv-scanner: o sha256 do download não bate com a soma fixada no script", r.stdout)
        self.assertFalse((self.home / ".local" / "bin" / "osv-scanner").exists())

    def test_falha_do_tar_vira_falta_e_nao_grava_instalou(self):
        copia = self.script_com_fixas(ACTIONLINT=SOMA_FALSA)
        self.curl_falso(SOMA_FALSA)
        r = self.rodar_copia(copia, "--ferramentas", ARQ="actionlint_1.7.12_linux_amd64.tar.gz")
        self.assertIn("falta: instalar actionlint (a extração ou a cópia falhou", r.stdout)
        self.assertNotIn("instalou actionlint", r.stdout)
        self.assertFalse((self.home / ".local" / "bin" / "actionlint").exists())

    def test_falha_do_install_sem_tar_vira_falta_e_nao_grava_instalou(self):
        """Binário solto (sem tar): o install falha com a soma certa; vira falta, sem instalou e sem arquivo."""
        copia = self.script_com_fixas(OSV=SOMA_FALSA)
        self.curl_falso(SOMA_FALSA)
        executavel(self.falsos / "install", "#!/bin/bash\nexit 1\n")
        r = self.rodar_copia(copia, "--ferramentas", ARQ="osv-scanner_linux_amd64")
        self.assertIn("falta: instalar osv-scanner (a extração ou a cópia falhou", r.stdout)
        self.assertNotIn("instalou osv-scanner", r.stdout)
        self.assertFalse((self.home / ".local" / "bin" / "osv-scanner").exists())

    def test_soma_certa_instala_o_binario(self):
        copia = self.script_com_fixas(OSV=SOMA_FALSA)
        self.curl_falso(SOMA_FALSA)
        r = self.rodar_copia(copia, "--ferramentas", ARQ="osv-scanner_linux_amd64")
        self.assertIn("fez: instalou osv-scanner", r.stdout)
        self.assertTrue((self.home / ".local" / "bin" / "osv-scanner").stat().st_mode & stat.S_IXUSR)

    def test_pipx_recebe_a_versao_fixada(self):
        registro = Path(self.tmp.name) / "pipx.log"
        executavel(self.falsos / "pipx", f'#!/bin/bash\necho "$@" >> {registro}\n')
        executavel(self.falsos / "curl", "#!/bin/bash\nexit 22\n")
        r = self.rodar_copia(SCRIPT, "--ferramentas")
        self.assertEqual(r.returncode, 0, r.stderr)
        linhas = registro.read_text(encoding="utf-8").split("\n")
        self.assertTrue(any(re.fullmatch(r"install zizmor==\d+\.\d+\.\d+", l) for l in linhas), linhas)
        self.assertTrue(any(re.fullmatch(r"install semgrep==\d+\.\d+\.\d+", l) for l in linhas), linhas)

    def test_sem_pipx_zizmor_e_semgrep_viram_falta(self):
        self.curl_falso("0" * 64)
        r = rodar(self.home, self.falsos, "--ferramentas", "--simular")
        self.assertIn("falta: instalar zizmor (sem pipx", r.stdout)
        self.assertIn("falta: instalar semgrep (sem pipx", r.stdout)

    def test_modo_container_nao_baixa_ferramenta(self):
        """O postStart roda sem o dono: --container --simular não pode chamar curl nem listar instalação de ferramenta."""
        chamadas = Path(self.tmp.name) / "curl.log"
        executavel(self.falsos / "curl", f'#!/bin/bash\necho "$@" >> {chamadas}\nexit 22\n')
        r = self.rodar_copia(SCRIPT, "--container", "--simular", FORGE_PERSISTENTE=str(self.home / "persistente"),
                             FORGE_PREPARO_ESSENCIAL="1")
        self.assertNotIn("instalaria actionlint", r.stdout)
        self.assertNotIn("instalaria gitleaks", r.stdout)
        self.assertNotIn("instalaria osv-scanner", r.stdout)
        self.assertNotIn("zizmor", r.stdout)
        self.assertFalse(chamadas.exists() and "releases/download" in chamadas.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
