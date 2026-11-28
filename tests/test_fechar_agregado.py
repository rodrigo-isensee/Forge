"""C3 da F1 parte 2 (pedido v0481, E45.88): o passo 3b do `forge-fechar` roda o `forge-check parecer agregar` só com a lista
fechada na develop do servidor (base_2b) e as linhas `Parecer:` dele fecham o `--body` do merge (M15.1); agregado fora de `success`
ou corpo ilegível param antes do merge. Reaproveita o ambiente de `test_fechar.Fechar` com `gh` e `forge-check` falsos próprios."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as tf  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)


# gh do passo 3b: o corpo do PR ($ESTADO/corpo) para a mensagem do merge; o resto vai ao gh falso do `test_fechar`.
GH_COM_CORPO = r'''#!/usr/bin/env bash
if [ "$1 $2" = "pr view" ] && [ "${*:4}" = "--json body --jq .body" ]; then echo "gh $*" >> "$REGISTRO"; cat "$ESTADO/corpo"; exit; fi
exec "$GH_BASE" "$@"
'''
# forge-check do passo 3b: `parecer agregar` imprime $ESTADO/agregar e sai com $ESTADO/agregar_rc (padrão 0); o resto, como o do `test_fechar`.
CHECK_AGREGAR = r'''#!/usr/bin/env bash
echo "forge-check $*" >> "$REGISTRO"
if [ "$1 $2" = "parecer agregar" ]; then cat "$ESTADO/agregar" 2>/dev/null; exit "$(cat "$ESTADO/agregar_rc" 2>/dev/null || echo 0)"; fi
exit "${CHECK_RC:-0}"
'''
LINHAS = "Parecer: review aprovado https://github.com/o/r/pull/7#issuecomment-1 origem " + "a" * 40


class FecharAgregado(unittest.TestCase):
    """O passo 3b do `forge-fechar`: só com a lista fechada na develop do servidor; as linhas fecham o `--body` do merge."""
    tearDown, git, fechar, chamadas = tf.Fechar.tearDown, tf.Fechar.git, tf.Fechar.fechar, tf.Fechar.chamadas

    def setUp(self):
        tf.Fechar.setUp(self)
        (self.tmp / "gh").rename(self.tmp / "gh_base")
        for nome, texto in (("gh", GH_COM_CORPO), ("check", CHECK_AGREGAR)):
            (self.tmp / nome).write_text(texto, encoding="utf-8")
            (self.tmp / nome).chmod(0o755)
        self.env.update(GH_BASE=str(self.tmp / "gh_base"))
        (self.estado / "corpo").write_text("Objetivo do PR.\n")

    def com_a_lista(self):
        self.git("switch", "-q", "develop")
        (self.proj / ".github").mkdir()
        (self.proj / ".github" / "pareceres-lista-fechada.json").write_text("[]\n")
        self.git("add", ".github")
        self.git("commit", "-q", "-m", "feat(ci): a virada")
        self.git("push", "-q", "origin", "develop")
        self.git("switch", "-q", "melhoria/x")
        self.git("merge", "-q", "--no-edit", "develop")
        self.git("push", "-q", "origin", "melhoria/x")
        self.git("switch", "-q", "develop")

    def merge(self):
        texto = self.registro.read_text()
        return texto[texto.index("gh pr merge"):] if "gh pr merge" in texto else ""

    def test_sem_a_lista_o_passo_nem_roda(self):
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertFalse([c for c in self.chamadas() if "parecer agregar" in c])
        self.assertNotIn("--body", self.merge())

    def test_com_a_lista_as_linhas_fecham_o_corpo_do_merge(self):
        self.com_a_lista()
        (self.estado / "agregar").write_text(LINHAS + "\n")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("forge-check parecer agregar p1 --ref refs/heads/melhoria/x --base origin/develop --branch melhoria/x",
                      self.chamadas())
        self.assertIn(f"--body Objetivo do PR.\n\n{LINHAS}\n", self.merge())

    def test_com_a_lista_e_nenhuma_linha_o_merge_segue_sem_body(self):
        self.com_a_lista()
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertNotIn("--body", self.merge())

    def test_agregado_fora_de_success_para_antes_do_merge(self):
        self.com_a_lista()
        (self.estado / "agregar_rc").write_text("1")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo 3b: o agregado pareceres não ficou success", r.stderr)
        self.assertEqual(self.merge(), "")

    def test_corpo_ilegivel_para_antes_do_merge(self):
        self.com_a_lista()
        (self.estado / "agregar").write_text(LINHAS + "\n")
        (self.estado / "corpo").unlink()
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo 3b: não consegui ler o corpo do PR", r.stderr)
        self.assertEqual(self.merge(), "")


if __name__ == "__main__":
    unittest.main()
