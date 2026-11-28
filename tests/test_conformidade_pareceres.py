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
import test_hooks  # noqa: E402
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


class PastaDeControleDoForge(unittest.TestCase):
    """C1b-3 (v0481 E45.13; A4 da segurança e A2 do review do #938, A1 da segurança do #937): o registro M4.1
    (`~/.forge-contrib/.forge/run/pareceres-publicados.jsonl`) fica fora do alcance de todo papel no `conformidade`. Só as
    fixtures `c1b3-*`, pela máquina do `Hooks` (o módulo importado inteiro, para não recolher os testes dele aqui), para os
    mutantes de `tests/mutantes/v0481-f1p2-c1b3.json` rodarem rápido."""
    executar_em_lote = test_hooks.Hooks.executar_em_lote
    executar_fixture = test_hooks.Hooks.executar_fixture
    _pasta_temporaria = test_hooks.Hooks._pasta_temporaria
    depende_de_pid_ou_trava = staticmethod(test_hooks.Hooks.depende_de_pid_ou_trava)

    def test_fixtures_c1b3(self):
        pasta = test_hooks.FIXTURES / "conformidade"
        fixtures = test_hooks.minimo([test_hooks.Fixture(p) for p in sorted(pasta.glob("c1b3-*.json"))], 6, "c1b3-*")
        codigos = [f.dados["esperado"]["codigo"] for f in fixtures]
        self.assertEqual(sorted(set(codigos)), [0, 2], "o corpus tem os dois lados")
        self.assertGreaterEqual(codigos.count(2), 5, "escrita e acréscimo barrados por papel")
        casos = [(f"conformidade/{f.caminho.stem}", f) for f in fixtures]
        self.assertEqual(self.executar_em_lote(casos), len(fixtures), "toda fixture é verificada")


class PeloTerminal(GhFalso):
    """C1b da F1 parte 2 (M4.2 e M10.1; casos C21 e C12 de `docs/security/ameacas/g2-parecer-status.md`): o hook barra o
    status e o comentário de parecer gravados pelo `gh` do terminal e o `publicar` pelo `bin/` de uma cópia; o `Corrigir`
    aponta o `forge-check parecer publicar` do plugin. Aqui na sessão de projeto; `PeloTerminalNoForge`, no clone do Forge."""

    def setUp(self):
        super().setUp()
        (self.repo / ".forge").mkdir(exist_ok=True)
        (self.repo / ".forge" / "versao").write_text("0.5.0\n", encoding="utf-8")
        # o `$HOME` do hook fora do `GhFalso`, que põe o repositório em `<tmp>/.forge-contrib/wt/` (C1a): com o mesmo HOME,
        # o projeto seria o clone de contribuição e o R-CONTRIB da sessão de projeto barraria antes do M4.2 e do M10.1
        self.casa = self.tmp / "casa"
        self.casa.mkdir()

    def bash(self, comando, extra=None):
        entrada = {"tool_name": "Bash", "tool_input": {"command": comando}, "hook_event_name": "PreToolUse",
                   "tool_use_id": "toolu_9", "agent_type": "forge:tech-lead"}
        return rodar("conformidade", entrada, self.repo,
                     extra={"HOME": str(self.casa), "CLAUDE_PROJECT_DIR": str(self.repo), **(extra or {})})

    def barra(self, comandos, trecho, extra=None):
        for comando in comandos:
            with self.subTest(comando=comando):
                r = self.bash(comando, extra)
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
                     "gh api graphql -f query='query { viewer { login } }'",
                     "gh pr create --draft --base develop --title t --body b"])  # outro subcomando: sem endpoint

    def test_c21_gh_pr_comment_com_marcador_barrado(self):
        (self.repo / "parecer.md").write_text(parecer(self.sha), encoding="utf-8")
        (self.repo / "nota.md").write_text("revisado, sem achados\n", encoding="utf-8")
        (self.repo / "-").write_text("inofensivo\n", encoding="utf-8")  # o `-F -` lê a entrada, nunca este arquivo
        (self.casa / "nota.md").write_text("revisado, sem achados\n", encoding="utf-8")  # o `$HOME` do hook
        self.barra(["gh pr comment 7 --body \"$(cat <<'EOF'\n---\ntipo: review\nparecer: aprovado\n---\nEOF\n)\"",
                    "gh pr comment 7 -F parecer.md", "gh issue comment 7 --body-file=parecer.md",
                    "gh pr comment 7 -b '---\ntipo: revisao-seguranca\n---'"], "comment: comentário com o marcador de parecer")
        self.barra(["gh pr comment 7 -F -", "gh pr comment 7 -F ausente.md", "gh pr comment 7 --body \"$CORPO\"",
                    "gh pr comment 7 -F \"$HOME/nota.md\""],
                   "gh pr comment: comentário cujo corpo o hook não lê")
        self.libera(["gh pr comment 7 --body 'revisado: tipo: review fica no texto, não no começo da linha'",
                     "gh pr comment 7 --body \"$(cat <<'EOF'\nrevisado, sem achados\nEOF\n)\"",
                     "gh pr comment 7 --body \"$(cat <<'EOF'\ncusto em $HOME e `crase` no texto\nEOF\n)\"",
                     "gh issue comment 70 --body 'cite `afrouxa-regra` e $HOME, entre aspas simples'",
                     "gh pr comment 7 -F nota.md", "gh pr view 7 --comments"])

    def test_c21_volta1_corpo_repetido_ou_com_expansao_barrado(self):
        """Volta 1 (review A1, segurança A1; sondas S1 e S2 do review, S1 a S4 da segurança): o hook lê todo `--body` e
        `--body-file` (o gh usa o último), o literal pela palavra do parser e o heredoc sem aspas como expansão."""
        (self.repo / "parecer.md").write_text(parecer(self.sha), encoding="utf-8")
        (self.repo / "nota.md").write_text("revisado, sem achados\n", encoding="utf-8")
        self.barra(["gh pr comment 7 -F nota.md -F parecer.md", "gh pr comment 7 -F nota.md -Fparecer.md", "gh pr comment 7 -b ok -b '---\ntipo: review\n---'",
                    "gh pr comment 7 --body ok --body=\"$(cat <<'EOF'\n---\ntipo: qa\n---\nEOF\n)\""],
                   "comment: comentário com o marcador de parecer")
        self.barra(["gh pr comment 7 --body \"$B\" # '$B'", "gh pr comment 7 --body \"$CORPO\" # '$CORPO'",
                    "echo '$CORPO'; gh pr comment 7 --body \"$CORPO\"",
                    "gh pr comment 7 --body \"$(cat <<EOF\n$B\nEOF\n)\"",
                    "gh pr comment 7 --body \"$(cat <<EOF\n$(cat parecer.md)\nEOF\n)\"",
                    "gh pr comment 7 --body ok -F -", "gh pr comment 7 --body \"$(cat)\" < parecer.md"],
                   "comment: comentário cujo corpo o hook não lê")
        self.libera(["gh pr comment 7 --body \"$(cat <<EOF\nrevisado, sem achados\nEOF\n)\"",
                     "gh pr comment 7 -b ok -F nota.md"])

    def test_c21_volta2_cat_sem_o_seu_heredoc_barrado(self):
        """Volta 2 (segurança A7, sonda S7): o `$(cat)` só vale como corpo quando o heredoc nasce dentro dele; o heredoc
        de outro comando da linha não é o corpo, e o `$(cat)` sem o seu lê a entrada (o pipe)."""
        (self.repo / "parecer.md").write_text(parecer(self.sha), encoding="utf-8")
        self.barra(["cat parecer.md | gh pr comment 7 --body \"$(cat)\"; cat <<'X'\nnada\nX",
                    "cat <<'X'\nnada\nX\ncat parecer.md | gh pr comment 7 --body \"$(cat)\"",
                    "cat parecer.md | gh pr comment 7 --body \"$(cat)\" && wc -l <<'X'\nnada\nX",
                    "cat parecer.md | gh pr comment 7 --body \"$(cat <<'EOF'\nok\nEOF\n)\" --body \"$(cat)\""],
                   "comment: comentário cujo corpo o hook não lê")
        self.libera(["gh pr comment 7 --body \"$(cat <<'EOF'\nok\nEOF\n)\"; cat <<'X'\nnada\nX",
                     "gh pr comment 7 --body \"$(cat <<'EOF'\ncita $(cat) no texto\nEOF\n)\""])

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
        (self.repo / "bin").mkdir()
        (self.repo / "bin" / "forge-check").write_text("#!/usr/bin/env python3\n", encoding="utf-8")
        (self.tmp / "fora").mkdir()
        (self.tmp / "fora" / "forge-check").symlink_to(self.repo / "bin" / "forge-check")  # S5: link de arquivo
        self.barra([f"python3 -I {self.tmp}/fora/forge-check parecer publicar {rel}",
                    f"{self.tmp}/fora/forge-check parecer publicar {rel}"], "forge-check parecer publicar pelo `bin/` de uma cópia")
        self.barra([f"PATH={self.repo}/bin:$PATH forge-check parecer publicar {rel}",
                    f"PATH=bin:/usr/bin forge-check parecer publicar {rel}"], "com o `PATH` trocado na linha")
        fora = self.casa / "extraido" / "bin" / "forge-check"  # a extração da base fora de cópia de trabalho (M10.1)
        self.libera([f"forge-check parecer publicar {rel}", f"python3 -I {fora} parecer publicar {rel}",
                     f"bin/forge-check pr {PEDIDO}"])


def parecer_hook():
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hooks"))
    import parecer as modulo
    return modulo


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
        dono = self.tmp / "gh-do-dono"  # segurança A5: na conta do dono, o R-CONTRIB do rótulo não barra antes
        dono.mkdir()
        (dono / "gh").write_text(f"#!/bin/sh\necho {parecer_hook().slug_do_forge().split('/')[0]}\n", encoding="utf-8")
        (dono / "gh").chmod(0o755)
        for comando in ("gh api graphql --input ausente.json", "gh api graphql -X POST -F query=@ausente.graphql"):
            with self.subTest(comando=comando):  # o GraphQL mutante ilegível já recusa pelo GH-MERGE-ADMIN, trava
                r = self.bash(comando, {"PATH": f"{dono}:/usr/bin:/bin"})
                self.assertEqual((r.returncode, r.stderr[:10]), (2, "R-MAIN: gh"), r.stderr)
        self.libera(["gh api graphql -f query='query { viewer { login } }'",
                     "gh api graphql -f query='mutation { addReaction(input: {subjectId: \"x\", content: HOORAY}) { clientMutationId } }'"])


    def test_c21_endpoint_ilegivel_barrado(self):
        """Segurança A3 (S6): o `gh api` que muda algo sem o endpoint na linha (pela entrada do `xargs`) falha fechado."""
        self.barra(["echo repos/o/r/issues/comments/9 | xargs gh api -X DELETE",
                    "echo repos/o/r/statuses/abc | xargs gh api -f state=success"],
                   "gh api que muda algo com endpoint que o hook não lê")
        self.libera(["echo repos/o/r/issues/comments/9 | xargs gh api"])


if __name__ == "__main__":
    unittest.main()
