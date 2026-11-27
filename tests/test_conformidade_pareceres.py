"""M9.2 do G2 (pedido v0481, E21.1; docs/security/ameacas/g2-parecer-status.md, T9): o hook `conformidade` registra a autoria
do parecer a publicar (`.forge/pareceres/<pedido>/<tipo>.md`), e o `forge-check parecer publicar` (G2.1, #878) aceita o parecer
gravado pelo papel do tipo e recusa sem o registro. De ponta a ponta: o hook de verdade num subprocesso, o `gh` falso de
`test_forge_pareceres` (sem rede)."""
import contextlib
import io
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge_pareceres import PEDIDO, GhFalso, fc, fp, parecer  # noqa: E402
from test_hooks import rodar  # noqa: E402


class AutoriaDoPublicar(GhFalso):
    def setUp(self):
        super().setUp()
        (self.repo / ".forge").mkdir(exist_ok=True)
        (self.repo / ".forge" / "versao").write_text("0.5.0\n", encoding="utf-8")

    def grava(self, texto, rel=f".forge/pareceres/{PEDIDO}/review.md"):
        arq = self.repo / rel
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(texto, encoding="utf-8")
        return arq

    def hook(self, arq, papel="forge:tech-lead"):
        """O PostToolUse do Write, como o Claude Code o chama depois da gravação."""
        entrada = {"tool_name": "Write", "tool_input": {"file_path": str(arq)}, "agent_type": papel,
                   "hook_event_name": "PostToolUse", "tool_use_id": "toolu_1"}
        r = rodar("conformidade", entrada, self.repo, extra={"CLAUDE_PROJECT_DIR": str(self.repo)})
        self.assertEqual(r.returncode, 0, r.stderr)

    def registros(self):
        arq = self.repo / ".forge" / "run" / "autoria.jsonl"
        return [json.loads(x) for x in arq.read_text(encoding="utf-8").splitlines()] if arq.exists() else []

    def publicar(self, arq):
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida), contextlib.redirect_stderr(io.StringIO()):
            rc = fc().cmd_parecer_publicar(self.repo, str(arq))
        return rc, saida.getvalue()

    def test_autoria_registra_forge_pareceres(self):
        self.hook(self.grava(parecer(self.sha)))
        self.assertEqual([(r["caminho"], r["papel"]) for r in self.registros()],
                         [(f".forge/pareceres/{PEDIDO}/review.md", "tech-lead")])

    def test_caminho_por_papel_em_forge_pareceres(self):
        """O registro leva o papel de quem gravou: o QA que grava o `review.md` não vira autoria do tech-lead."""
        self.hook(self.grava(parecer(self.sha)), papel="forge:qa-engineer")
        self.assertEqual([r["papel"] for r in self.registros()], ["qa"])

    def test_fora_de_pedido_e_tipo_nao_registra(self):
        for rel in (".forge/pareceres/review.md", f".forge/pareceres/{PEDIDO}/velho/review.md",
                    f".forge/pareceres/{PEDIDO}/review.txt", f".forge/outros/{PEDIDO}/review.md"):
            with self.subTest(rel=rel):
                self.hook(self.grava(parecer(self.sha), rel))
                self.assertEqual(self.registros(), [])

    def test_ponta_a_ponta_publica_com_autoria_do_hook(self):
        arq = self.grava(parecer(self.sha))
        self.hook(arq)
        rc, saida = self.publicar(arq)
        self.assertEqual(rc, 0, saida)
        self.assertIn(f"parecer publicado: parecer-review aprovado {self.sha[:7]}", saida)

    def test_ponta_a_ponta_recusa_sem_autoria(self):
        rc, saida = self.publicar(self.grava(parecer(self.sha)))
        self.assertEqual(rc, 1, saida)
        self.assertIn("autoria: sem registro de que o papel `tech-lead` gravou este texto (M9.1)", saida)
        self.assertEqual(self.chamadas(), [], "recusado antes de chamar o gh")

    def test_ponta_a_ponta_recusa_autoria_de_outro_papel(self):
        arq = self.grava(parecer(self.sha))
        self.hook(arq, papel="forge:qa-engineer")
        rc, saida = self.publicar(arq)
        self.assertEqual(rc, 1, saida)
        self.assertIn("papel `tech-lead`", saida)

    def test_s1_texto_de_docs_reviews_publicado_de_fora_do_projeto(self):
        """S1 da segurança do #914: o texto gravado em docs/reviews/ e copiado fora do projeto (sem hook) não publica."""
        texto = parecer(self.sha)
        self.hook(self.grava(texto, f"docs/reviews/{PEDIDO}.md"))
        fora = self.tmp / "fora" / ".forge" / "pareceres" / PEDIDO / "review.md"
        fora.parent.mkdir(parents=True)
        fora.write_text(texto, encoding="utf-8")
        rc, saida = self.publicar(fora)
        self.assertEqual(rc, 1, saida)
        self.assertIn("use .forge/pareceres/", saida)
        self.assertEqual(self.chamadas(), [], "recusado antes de chamar o gh")

    def test_s1_texto_de_docs_reviews_copiado_para_o_parecer_a_publicar(self):
        """S1 dentro do projeto: o registro de docs/reviews/ com o mesmo sha256 e papel não vale para .forge/pareceres/."""
        texto = parecer(self.sha)
        self.hook(self.grava(texto, f"docs/reviews/{PEDIDO}.md"))
        rc, saida = self.publicar(self.grava(texto))
        self.assertEqual(rc, 1, saida)
        self.assertIn(f"como o último de `.forge/pareceres/{PEDIDO}/review.md`", saida)
        self.assertEqual(self.chamadas(), [], "recusado antes de chamar o gh")

    def test_s2_veredito_superado_nao_volta_a_publicar(self):
        """S2 da segurança do #914: aprovado, depois reprovado no mesmo caminho; o aprovado reposto sem hook não publica."""
        aprovado = parecer(self.sha)
        arq = self.grava(aprovado)
        self.hook(arq)
        self.hook(self.grava(parecer(self.sha, "reprovado", achados="## Achados\n- A1 (bloqueante) x.py:1 · defeito\n\n")))
        arq.write_text(aprovado, encoding="utf-8")
        rc, saida = self.publicar(arq)
        self.assertEqual(rc, 1, saida)
        self.assertIn("como o último de", saida)
        self.assertEqual(self.chamadas(), [], "recusado antes de chamar o gh")
        self.hook(arq)  # o aprovado regravado pelo papel volta a ser o último registro e publica
        rc, saida = self.publicar(arq)
        self.assertEqual(rc, 0, saida)


class PeloTerminal(GhFalso):
    """C1b da F1 parte 2 (M4.2 e M10.1; casos C21 e C12 de `docs/security/ameacas/g2-parecer-status.md`): o hook barra o
    status e o comentário de parecer gravados pelo `gh` do terminal e o `publicar` pelo `bin/` de uma cópia; o `Corrigir`
    aponta o `forge-check parecer publicar` do plugin. Aqui na sessão de projeto; `PeloTerminalNoForge`, no clone do Forge."""

    def setUp(self):
        super().setUp()
        (self.repo / ".forge").mkdir(exist_ok=True)
        (self.repo / ".forge" / "versao").write_text("0.5.0\n", encoding="utf-8")

    def bash(self, comando):
        entrada = {"tool_name": "Bash", "tool_input": {"command": comando}, "hook_event_name": "PreToolUse",
                   "tool_use_id": "toolu_9", "agent_type": "forge:tech-lead"}
        return rodar("conformidade", entrada, self.repo, extra={"HOME": str(self.tmp), "CLAUDE_PROJECT_DIR": str(self.repo)})

    def barra(self, comandos, trecho):
        for comando in comandos:
            with self.subTest(comando=comando):
                r = self.bash(comando)
                self.assertEqual(r.returncode, 2, r.stderr)
                self.assertTrue(r.stderr.startswith("R-REVIEW: "), r.stderr)
                self.assertIn(trecho, r.stderr)
                self.assertIn("forge-check parecer publicar", r.stderr)

    def libera(self, comandos):
        for comando in comandos:
            with self.subTest(comando=comando):
                r = self.bash(comando)
                self.assertEqual(r.returncode, 0, r.stderr)

    def test_c21_gh_api_statuses_barrado(self):
        self.barra([f"gh api -X POST repos/dono/repo/statuses/{self.sha} -f state=success -f context=parecer-review",
                    f"gh api repos/{{owner}}/{{repo}}/statuses/{self.sha} -f state=success",
                    "gh api --method POST /repos/dono/repo/issues/7/comments -F body=@nota.md",
                    "gh api https://api.github.com/repos/dono/repo/issues/7/comments --input corpo.json",
                    "gh api -X PATCH repos/dono/repo/issues/comments/99 -f body=x",
                    "gh api -X DELETE repos/{owner}/{repo}/issues/comments/99"],
                   "gh api que grava status ou comentário")
        self.libera([f"gh api repos/dono/repo/commits/{self.sha}/statuses",
                     "gh api repos/{owner}/{repo}/issues/7/comments --paginate",
                     "gh api repos/dono/repo/issues/comments/99",
                     "gh api graphql -f query='query { viewer { login } }'"])

    def test_c21_gh_pr_comment_com_marcador_barrado(self):
        (self.repo / "parecer.md").write_text(parecer(self.sha), encoding="utf-8")
        (self.repo / "nota.md").write_text("revisado, sem achados\n", encoding="utf-8")
        (self.repo / "-").write_text("inofensivo\n", encoding="utf-8")  # o `-F -` lê a entrada, nunca este arquivo
        (self.tmp / "nota.md").write_text("revisado, sem achados\n", encoding="utf-8")  # o `$HOME` do hook
        self.barra(["gh pr comment 7 --body \"$(cat <<'EOF'\n---\ntipo: review\nparecer: aprovado\n---\nEOF\n)\"",
                    "gh pr comment 7 -F parecer.md", "gh issue comment 7 --body-file=parecer.md",
                    "gh pr comment 7 -b '---\ntipo: revisao-seguranca\n---'"], "comment: comentário com o marcador de parecer")
        self.barra(["gh pr comment 7 -F -", "gh pr comment 7 -F ausente.md", "gh pr comment 7 --body \"$CORPO\"",
                    "gh pr comment 7 -F \"$HOME/nota.md\""],
                   "gh pr comment: comentário cujo corpo o hook não lê")
        self.libera(["gh pr comment 7 --body 'revisado: tipo: review fica no texto, não no começo da linha'",
                     "gh pr comment 7 --body \"$(cat <<'EOF'\nrevisado, sem achados\nEOF\n)\"",
                     "gh pr comment 7 -F nota.md", "gh pr view 7 --comments"])

    def test_c21_tipos_do_marcador_sao_os_contextos_do_publicar(self):
        """O marcador do hook e a lista fechada do `publicar` (M2.1) andam juntos: tipo novo no `publicar` entra no hook."""
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hooks"))
        import conformidade
        self.assertEqual(set(conformidade.TIPOS_DE_PARECER), set(fp().CONTEXTOS))

    def test_c12_publicar_pela_copia_barrado(self):
        rel = f".forge/pareceres/{PEDIDO}/review.md"
        self.barra([f"bin/forge-check parecer publicar {rel}", f"./bin/forge-check --raiz . parecer publicar {rel}",
                    f"python3 bin/forge-check parecer publicar {rel}",
                    f"python3 -I {self.repo}/bin/forge-check parecer publicar {rel}",
                    f"cd bin && ./forge-check parecer publicar ../{rel}", f"$HOME/extraido/bin/forge-check parecer publicar {rel}"],
                   "forge-check parecer publicar pelo `bin/` de uma cópia")
        fora = self.tmp / "extraido" / "bin" / "forge-check"  # a extração da base fora de cópia de trabalho (M10.1)
        self.libera([f"forge-check parecer publicar {rel}", f"python3 -I {fora} parecer publicar {rel}",
                     f"bin/forge-check pr {PEDIDO}"])


class PeloTerminalNoForge(PeloTerminal):
    """Os mesmos casos na sessão do Forge (o clone com o manifesto, sem `.forge/versao`), onde o papel sem lista só passa
    pelas travas: o M4.2 e o M10.1 são travas (`TRAVA`). A mutação de comentário do GraphQL só se vê aqui: na sessão de
    projeto, o R-CONTRIB já a barra (ID global)."""

    def setUp(self):
        super().setUp()
        (self.repo / ".forge" / "versao").unlink()
        (self.repo / ".claude-plugin").mkdir()
        (self.repo / ".claude-plugin" / "plugin.json").write_text('{"name": "forge"}', encoding="utf-8")

    def test_c21_graphql_de_comentario_barrado(self):
        self.barra(["gh api graphql -f query='mutation { addComment(input: {subjectId: \"x\", body: \"y\"}) { clientMutationId } }'",
                    "gh api graphql -f query='mutation { updateIssueComment(input: {id: \"x\", body: \"y\"}) { clientMutationId } }'",
                    "gh api graphql -f query='mutation { deleteIssueComment(input: {id: \"x\"}) { clientMutationId } }'"],
                   "gh api que grava status ou comentário")
        self.libera(["gh api graphql -f query='query { viewer { login } }'",
                     "gh api graphql -f query='mutation { addReaction(input: {subjectId: \"x\", content: HOORAY}) { clientMutationId } }'"])


if __name__ == "__main__":
    unittest.main()
