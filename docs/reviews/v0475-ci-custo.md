---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0475-ci-custo
commit: f59f7766bfcecbb1887cce0b6c0aff6ab31880cd
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v0474 (E3.64, melhoria/v0475-ci-custo)

## Achados
- A1 (bloqueante) templates/projeto/.github/workflows/ci.yml:21 · grupo `ci-<branch>` junta o push de develop com o PR develop→homolog (head_ref=develop): um push na develop com o PR de promoção aberto cancela uma das duas rodadas, e o agregador `if: always()` vira `ci` vermelho. Use `github.event.pull_request.number || github.ref`.
- A2 (recomendado) templates/projeto/.github/workflows/ci-docs.yml:8 · `paths:` roda se QUALQUER arquivo casa: PR misto (código e .md) roda os dois e põe dois `ci` no mesmo SHA, o leve verde antes da suíte; a proteção pode ler o verde. Preferir um workflow com job de detecção de mudança e o agregador aceitando `skipped`.
- A3 (recomendado) skills/ci-cd/SKILL.md:59 · o texto justifica juntar push e PR no grupo; com push só nas branches do fluxo isso não evita duplicata nenhuma e só causa o A1. Corrigir junto com o A1.

## Sondas

## Parecer
Reprovado (`R-REVIEW`), pelo A1.

Foco pedido, item a item:
- **Run duplicado de push e PR:** resolvido pelo filtro `push.branches: [develop, homolog, main]` (ci.yml:13-14). Branch de trabalho só dispara `pull_request`; não há mais par push+PR na mesma mudança de trabalho.
- **Só documento sem travar o check exigido:** no PR só de `.md`/`docs/**`, o ci.yml não roda e o ci-docs.yml entrega o job `ci` verde: o check não fica pendente. Resta o A2 no PR misto (o filtro `paths` não é o inverso de `paths-ignore`; o inverso exato, "todos os arquivos são documento", não se expressa com filtro de caminho).
- **Cancelar rodada repetida:** funciona entre pushes seguidos do mesmo PR. Mas a chave do grupo (`head_ref || ref_name`) dá o mesmo valor `ci-develop` a duas validações distintas que acontecem juntas no fluxo normal: o push na develop (valida a develop) e o `synchronize` do PR develop→homolog (valida o merge com a homolog, outra árvore). Com `cancel-in-progress`, a segunda cancela a primeira; o agregador com `if: always()` roda mesmo na rodada cancelada, lê `cancelled` e falha. O mesmo vale para homolog com o PR homolog→main. Evidência pela semântica documentada dos contextos (`github.head_ref` = branch de origem no `pull_request`; `github.ref_name` = branch no `push`); não executei Actions (sem custo, `R-CUSTO`). Correção sugerida: `group: ci-${{ github.event.pull_request.number || github.ref }}` (idem no ci-docs.yml), com teste e mutante atualizados (M8).

Ferramentas e provas citadas, sem refazer:
- `python3 -m unittest tests.test_modelo_ci`: 13 testes OK no head (rodei o teste novo).
- Mutação: specs `tests/mutantes/v0475-ci-custo.json` (M1-M15) e `-2.json` (M16-M17) declaradas, uma por guarda; não rerrodei (trava `pesado` de outra sessão, `R-TETO`); vale o PQ do autor.
- CI: sem PR aberto para a branch (entrega sem PR neste passo); a suíte completa fica no CI do PR.
- Tamanho (M14): 180 linhas contadas (bin 4, modelos 78, teste 100), um comportamento; passa da orientação de 150, então o corpo do PR traz `teto: excedido, 180 linhas, <motivo>` (o teste do modelo é a maior parte; risco baixo, só modelo e texto).

Neutralidade (`R-NEUTRO`) e ADR 0001: o modelo usa `{{COMANDO_PRONTO}}` e não nomeia ferramenta de stack; `forge-init` substitui o marcador (teste `Entrega`). Ações fixadas por SHA, permissões mínimas, timeout em todo job: ok.
