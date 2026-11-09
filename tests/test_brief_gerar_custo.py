"""BRIEF-GERAR-TIMEOUT (0.43.3): o `brief gerar` num registro grande levava 4 a 5 s porque o autorrelato (`falhas_de_autorrelato`)
lia cada pedido por `ler_registro` sem as raízes já calculadas, e cada leitura rodava um `git rev-parse` (`raiz_principal`): um
processo git por pedido do registro. A não regressão conta as chamadas ao git, nunca o relógio: com 1 ou com 40 pedidos, o mesmo
número. Sem rede."""
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402
from test_selo_e_entrega import PEDIDO, fc  # noqa: E402

ERRO = "- 2026-01-01 10:00: ERRO-JARVIS: escopo: o brief cortou um item sem a marca. Prevenção: eval do corte.\n"


class Custo(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-custo-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        env = sem_manutencao({"PATH": "/usr/bin:/bin", "HOME": str(self.tmp), "GIT_CONFIG_NOSYSTEM": "1"})
        subprocess.run(["git", "init", "-q", "-b", "develop", str(self.tmp)], check=True, env=env, timeout=60)
        (self.tmp / "docs" / "pedidos").mkdir(parents=True)
        (self.tmp / "docs" / "pedidos" / "exemplo.md").write_text(PEDIDO, encoding="utf-8")
        sem_host = mock.patch.object(fc, "RAIZES_DE_BRIEF", ())  # o ~/.forge-contrib da máquina não entra na conta
        sem_host.start()
        self.addCleanup(sem_host.stop)

    def pedidos(self, n):
        for i in range(n):
            (self.tmp / "docs" / "pedidos" / f"p{i:03d}.md").write_text(PEDIDO.replace("id: exemplo", f"id: p{i:03d}") + ERRO,
                                                                         encoding="utf-8")

    def chamadas_ao_git(self, funcao):
        original, contagem = fc.git, []

        def contar(*a, **k):
            contagem.append(a[1:3])
            return original(*a, **k)
        with mock.patch.object(fc, "git", contar), redirect_stderr(io.StringIO()):
            resultado = funcao()
        return len(contagem), resultado

    def test_autorrelato_nao_roda_git_por_pedido(self):
        self.pedidos(1)
        uma, (falhas, _) = self.chamadas_ao_git(lambda: fc.falhas_de_autorrelato(self.tmp, dias=100000))
        self.assertEqual(len(falhas), 1)
        self.pedidos(40)
        quarenta, (falhas, _) = self.chamadas_ao_git(lambda: fc.falhas_de_autorrelato(self.tmp, dias=100000))
        self.assertEqual(len(falhas), 40)  # leu os 40: o corte não veio de pular pedido
        self.assertEqual(quarenta, uma)

    def test_brief_gerar_custa_o_mesmo_com_registro_grande(self):
        gerar = lambda: fc.montar_brief(self.tmp, "exemplo", "forge:node-backend", None, "develop", "codigo")  # noqa: E731
        self.pedidos(1)
        uma, (texto, rc, _) = self.chamadas_ao_git(gerar)
        self.assertEqual(rc, 0)
        self.pedidos(40)
        quarenta, _ = self.chamadas_ao_git(gerar)
        self.assertEqual(quarenta, uma)


if __name__ == "__main__":
    unittest.main()
