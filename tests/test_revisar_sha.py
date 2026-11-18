"""E3.49 (v0474): o `Revisar-sha:` sai do head remoto da branch (`origin/<branch>`), não da ref local que ficou na base; e o `brief
gerar` com o PR já mesclado diz o que fazer (branch nova a partir da integração, sem recriar a apagada). Sem rede (`gh` falso)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_selo_e_entrega import Repositorio, fc  # noqa: E402
from test_estado_da_branch import GH_MERGED, Repo  # noqa: E402
from gh_falso import com_gh_falso  # noqa: E402


class HeadRemoto(Repositorio):
    def publicar_codigo(self):
        self.gravar("bin/app", "y\n")
        self.git("add", "bin/app")
        codigo = self.commit("feat: código")
        self.git("push", "-q", "origin", "melhoria/x")
        return codigo

    def test_ref_local_na_base_usa_o_head_remoto(self):
        codigo = self.publicar_codigo()
        self.git("reset", "-q", "--hard", self.base)  # a ref local ficou na base
        self.assertEqual(fc.sha_a_revisar(self.proj, "melhoria/x"), codigo)

    def test_sem_branch_publicada_vale_a_local(self):
        self.gravar("bin/app", "z\n")
        self.git("add", "bin/app")
        local = self.commit("feat: só local")
        self.assertEqual(fc.sha_a_revisar(self.proj, "melhoria/x"), local)

    def test_head_nunca_vira_o_origin_head(self):  # origin/HEAD é a branch padrão do remoto, não o head desta cópia
        codigo = self.publicar_codigo()
        self.git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/develop")
        self.assertEqual(fc.sha_a_revisar(self.proj, "HEAD"), codigo)
        self.assertEqual(fc.sha_a_revisar(self.proj, None), codigo)


class PrMesclado(Repo):
    def test_recusa_diz_como_continuar_sem_recriar_a_branch(self):
        rc, saida, _ = self.gerar("--etapa", "codigo", env=com_gh_falso(script=GH_MERGED))
        self.assertEqual(rc, 1, saida)
        self.assertIn("continue em branch nova a partir da integração (`git switch --no-track -c <branch nova> origin/develop`)", saida)
        self.assertIn("não recrie melhoria/x", saida)
