"""PORTAO-DEVOPS-FERRAMENTAS (v0478 E6.1): `preparar-estacao.sh --ferramentas` instala as ferramentas dos portões sem
credencial, só com o sha256 batendo, e diz o que falta. Sem rede: o curl e o pipx são falsos."""
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / "scripts" / "preparar-estacao.sh"


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

    def test_soma_errada_nao_instala(self):
        self.curl_falso("0" * 64)
        r = rodar(self.home, self.falsos, "--ferramentas")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("falta: actionlint: o sha256 do download não bate", r.stdout)
        self.assertFalse((self.home / ".local" / "bin" / "actionlint").exists())

    def test_soma_certa_instala_o_binario(self):
        import hashlib
        self.curl_falso(hashlib.sha256(b"conteudo\n").hexdigest())
        r = rodar(self.home, self.falsos, "--ferramentas", ARQ="osv-scanner_linux_amd64")
        self.assertIn("fez: instalou osv-scanner", r.stdout)
        self.assertTrue((self.home / ".local" / "bin" / "osv-scanner").stat().st_mode & stat.S_IXUSR)

    def test_sem_pipx_zizmor_e_semgrep_viram_falta(self):
        self.curl_falso("0" * 64)
        r = rodar(self.home, self.falsos, "--ferramentas", "--simular")
        self.assertIn("falta: instalar zizmor (sem pipx", r.stdout)
        self.assertIn("falta: instalar semgrep (sem pipx", r.stdout)

    def test_modo_container_nao_baixa_ferramenta(self):
        texto = SCRIPT.read_text(encoding="utf-8")
        container = texto.split("preparar_container() {", 1)[1].split("\n}\n", 1)[0]
        self.assertNotIn("garantir_ferramentas", container)


if __name__ == "__main__":
    unittest.main()
