"""LIMPAR-CLONE-NAO-LISTADO (v0478 E132.6): o --limpar do forge-fechar apaga o clone sem trabalho cujo HEAD é ancestral do head mesclado
(E128.2) e o que tem commit fora das refs remotas velhas dele, mas que as pontas lidas agora da origin alcançam (a tag local de um commit da
main, com a origin/main do clone velha); a leitura da origin é desta cópia, só por leitura. O campo `clone=` sai sempre (`nenhum` sem clone).

Reaproveita o ambiente de `test_forge_fechar.LimparClones` (HOME temporário, git e gh falsos de `test_fechar.Fechar`).
"""
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_forge_fechar as ff  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)

# ls-remote das pontas que falha (rede fora): o commit fora das refs do clone não se prova na origem
LS_REMOTE_FALHA = '''#!/usr/bin/env bash
if [ "$#" = 3 ] && [ "$1 $2 $3" = "ls-remote origin refs/*" ]; then echo "HTTP 502" >&2; exit 1; fi
exec "$GIT_DE_BAIXO" "$@"
'''


class LimparCloneNaoListado(unittest.TestCase):
    L = ff.LimparClones
    setUp, tearDown, git, fechar, resumo, clone, mesclado, limpar, fica = L.setUp, L.tearDown, L.git, L.fechar, L.resumo, L.clone, L.mesclado, L.limpar, L.fica

    def avancar_a_branch(self):  # outro commit na melhoria/x, enviado de outra cópia: o clone fica no head antigo
        self.git("switch", "-q", "melhoria/x")
        self.git("commit", "-q", "--allow-empty", "-m", "feat: mais")
        self.git("push", "-q", "origin", "melhoria/x")
        self.git("switch", "-q", "develop")

    def tag_com_ref_velha(self, d):  # E128.2: a tag local de um commit que a origin tem, numa branch que a ref remota do clone não cobre
        self.git("switch", "-q", "--detach", cwd=d)
        self.git("commit", "-q", "--allow-empty", "-m", "release", cwd=d)
        self.git("tag", "v9", cwd=d)
        self.git("push", "-q", "origin", "HEAD:refs/heads/outra", cwd=d)
        self.git("update-ref", "-d", "refs/remotes/origin/outra", cwd=d)
        self.git("switch", "-q", "melhoria/x", cwd=d)

    def test_head_ancestral_do_mesclado_e_apagado(self):
        d = self.clone()
        self.avancar_a_branch()
        r = self.limpar()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=ok branch=ok clone=ok"])
        self.assertFalse(d.exists())

    def test_head_mesclado_que_esta_copia_nao_le_e_buscado_e_o_clone_ancestral_sai(self):
        # o head mesclado veio de outra cópia e a branch já saiu da origin: só a busca dos mesclados o traz para o merge-base
        d = self.clone()
        outra = self.tmp / "outra"
        self.git("clone", "-q", str(self.remoto), str(outra), cwd=self.tmp)
        self.git("switch", "-q", "melhoria/x", cwd=outra)
        self.git("commit", "-q", "--allow-empty", "-m", "feat: de outra cópia", cwd=outra)
        self.git("push", "-q", "origin", "melhoria/x", cwd=outra)
        mesclado = self.git("rev-parse", "HEAD", cwd=outra)
        self.git("push", "-q", "origin", "--delete", "melhoria/x", cwd=outra)
        self.git("branch", "-q", "-D", "melhoria/x")  # a local, no head antigo, ficaria pendente: o teste é do clone
        objetos = self.git("cat-file", "--batch-all-objects", "--batch-check=%(objectname)").split()
        self.assertNotIn(mesclado, objetos)  # esta cópia não o lê antes do fechamento
        (self.estado / "lista_extra").write_text(f"234 MERGED develop {mesclado}\n")
        r = self.fechar("p1", "--ref", "melhoria/x", "--limpar")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertTrue(self.resumo(r)[0].endswith(" clone=ok"), r.stdout)
        self.assertFalse(d.exists())

    def test_commit_que_a_origin_tem_com_ref_velha_no_clone_e_apagado(self):
        d = self.clone()
        self.tag_com_ref_velha(d)
        r = self.limpar()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=ok branch=ok clone=ok"])
        self.assertFalse(d.exists())
        self.assertEqual(self.git("for-each-ref", "refs/remotes/origin/outra", "refs/tags"), "")  # a busca não criou ref nesta cópia

    def test_leitura_da_origin_que_falha_deixa_o_clone(self):
        d = self.clone()
        self.tag_com_ref_velha(d)
        embrulho = self.tmp / "bin2"
        embrulho.mkdir()
        (embrulho / "git").write_text(LS_REMOTE_FALHA, encoding="utf-8")
        (embrulho / "git").chmod(0o755)
        self.env.update(GIT_DE_BAIXO=str(self.tmp / "bin" / "git"), PATH=f"{embrulho}{os.pathsep}{self.env['PATH']}")
        self.fica(d, self.limpar())

    # FECHAR-LIMPAR-URL-GIT (v0478 E166.1): o origin do clone casa com o desta cópia sem o `.git` e sem a barra finais; o de outro origin
    # fica pendente, com aviso e leitura, nunca em silêncio.
    def com_origins(self, aqui, dela):  # o remoto do ambiente é `remoto.git`; `base` é ele sem o `.git`
        base = str(self.remoto)[:-len(".git")]
        d = self.clone()
        self.git("remote", "set-url", "origin", base + aqui)
        self.git("remote", "set-url", "origin", base + dela, cwd=d)
        r = self.limpar()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=ok branch=ok clone=ok"])
        self.assertFalse(d.exists())

    def test_clone_sem_ponto_git_e_da_mesma_origin(self):
        self.com_origins(".git", "")

    def test_clone_com_barra_final_e_da_mesma_origin(self):
        self.com_origins(".git", ".git/")

    def test_copia_com_ponto_git_e_barra_casa_com_o_clone_sem_os_dois(self):
        self.com_origins(".git/", "")

    def test_clone_de_outro_origin_fica_pendente_e_avisa(self):
        d = self.clone()
        self.git("remote", "set-url", "origin", str(self.tmp / "outro.git"), cwd=d)
        r = self.limpar()
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertTrue(d.is_dir())
        self.assertTrue(self.resumo(r)[0].endswith(" clone=pendente"), r.stdout)
        self.assertIn(f"o clone {d} está na branch melhoria/x, mas o origin dele não é o desta cópia", r.stderr)
        self.assertIn(f"git -C {d} remote -v", r.stdout)
        self.assertNotIn("rm -rf", r.stdout)
        self.assertNotIn("outro.git", r.stdout + r.stderr)  # a URL não sai na tela

    def test_sem_clone_o_campo_sai_nenhum(self):
        r = self.limpar()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=ok branch=ok clone=nenhum"])


if __name__ == "__main__":
    unittest.main()
