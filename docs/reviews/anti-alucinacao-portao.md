---
tipo: review
contrato: 1
pedido: anti-alucinacao-portao
branch: melhoria/anti-alucinacao-portao
commit: 6f71cf5
parecer: aprovado
revisor: forge:tech-lead (autor)
data: 2026-10-15
---
# Parecer de autor: portão do parecer no Forge (fatia 3 do anti-alucinação)

Escopo: `git diff origin/melhoria/anti-alucinacao-regras..6f71cf5` (00b3042, 0f389dd, 6f71cf5). Referência: a seção 9 e a linha "| 3 |" da seção 11 da proposta anti-alucinação, com as decisões do dono P1 = B, P2 = A, P3 = A e §14 = B, e a seção 7 ("O clone do Forge") da proposta de retomada sem perda. PR empilhado sobre a fatia 2 (#125). Este é o parecer **de autor**: o review independente de outro `tech-lead`, o do `security-engineer` e o QA continuam obrigatórios antes de o PR sair do rascunho.

Parecer: **aprovado como autor**, com as pendências abaixo. **O PR precisa do rótulo `afrouxa-regra`**: `hooks/parecer.py`, `hooks/_comum.py` e `tests/catraca.py` estão em `PROTEGIDOS`. A mudança endurece e não remove nenhum invariante.

## O que mudou
- `hooks/_comum.py`: `copia_de_trabalho` e `raiz_de_estado` (raiz única do projeto ou do clone do Forge, para as fatias 4 e 5 e a retomada); `Hook.projeto(..., clone_do_forge=True)` aceita o clone e lá ignora `hooks_desligados`; `sessao_vigiada`, `falhar_fechado` e `executar` ganham `clone_do_forge` para a falha fechada valer no clone. Sem o parâmetro, o comportamento é o de antes.
- `hooks/parecer.py`: age no clone do Forge (cópia principal e worktrees). Lá, `gh pr create --draft`/`-d` passa sem parecer; sem rascunho, exige o parecer e ensina o `--draft`; `--head` de branch não buscada barra; `gh pr ready` exige o parecer como o merge, barra só com número e libera `--undo`. `--draft=false` e `-d` como valor de opção não contam como rascunho.
- `tests/catraca.py`: o modo `pareceres` acumula as violações de todos os pedidos (seção 9, item 4).
- `agents/tech-lead.md`, `docs/hooks.md`, `CHANGELOG.md`.

## Critério de raiz: divergência alinhada
A proposta anti-alucinação pedia `e_clone_do_forge(raiz) and em_contrib(raiz)`. O brief manda valer também a sessão do dono em `~/Forge`, como na retomada. Ficou só `e_clone_do_forge` pela pasta da ação. O manifesto pode ser forjado em qualquer pasta, mas aqui ele só **acrescenta** guarda (`tem_manifesto_do_forge`): um projeto (`.forge/versao`) vem antes e não muda, e uma pasta alheia com manifesto forjado passa a ser conferida, nunca liberada.

## Provas (PQ)
- **PQ-1:** `forge-clone-pr-create-reprovado-bloqueia` rc=2 e `forge-clone-pr-merge-reprovado-bloqueia` rc=2 (também na worktree: `forge-clone-worktree-pr-create-reprovado-bloqueia` rc=2). No hook anterior, as três saíam com rc=0.
- **PQ-2:** `forge-clone-pr-create-draft-sem-parecer-libera` rc=0; `forge-clone-pr-ready-sem-parecer-bloqueia` rc=2 ("R-REVIEW: PR sai do rascunho só com parecer: nenhum parecer...").
- **PQ-3:** `tests/catraca.py --modo pareceres` com `a-ok` aprovado e `b-ruim` reprovado: rc=1, "R-REVIEW: PR toca hooks/novo.py (e outros 0) sem parecer aprovado de review (docs/reviews/b-ruim.md: ...)"; antes da correção, rc=0. Testes `test_um_pedido_reprovado_barra_mesmo_com_outro_aprovado` (falham sem a correção) e `test_dois_pedidos_aprovados_passam`.
- **PQ-4:** suíte inteira "Ran 565 tests in 218.285s / OK", iniciada com load 2,00; as fixtures de projeto seguem verdes, mais `pr-draft-em-projeto-sem-parecer-bloqueia` (rc=2) e `pr-ready-em-projeto-libera` (rc=0) provando que nada muda nos projetos. `scripts/validar-plugin.sh`: "Validation passed".

## Checklist (leitura)
1. Escopo: o da linha "| 3 |"; os hooks `decisao`, `brief` e `prova`, a retomada e o cartão S8 não foram tocados.
2. Regras: `R-NEUTRO` (nenhum nome de projeto; o slug nas fixtures é o do próprio Forge, já usado), `R-CUSTO` (sem rede, sem IA), ADR 0003 e ADR 0009, seção 7, preservadas.
3. a 4. Funções pequenas; `bandeira` cobre a forma desconhecida (`-dw`) como desligada, para o portão nunca afrouxar.
7. Testes: 19 fixtures novas (todas conferidas também contra o hook antigo) e um teste de unidade de `raiz_de_estado`, `copia_principal` na worktree e falha fechada no clone.
9. Três commits por tema, Conventional Commits.

## Pendências e riscos (para o review independente e o `security-engineer`)
- **Latência:** o caminho comum fica abaixo de 100 ms no `~/Forge` (mediana em 20 execuções: comando sem `gh` 29 ms, `gh pr create --draft` 24 ms, `gh pr create` 44 ms). `gh pr ready` e `gh pr merge` levam cerca de 160 ms, iguais entre si. O custo é do `forge-check` (`documentos` faz um `git show` por parecer, 61 no Forge), que é o mesmo caminho do `gh pr merge` de hoje. Baixar disso pede mudar `bin/forge-check` (`git cat-file --batch`), fora desta fatia.
- **Ainda passa (sem servidor, §14 = B):** `gh api graphql` com `markPullRequestReadyForReview` numa sessão do Forge (o `conformidade` só barra para sessão de outro projeto), `--input` com a mutação num arquivo e o botão da interface. A guarda é o rascunho: tirá-lo é um ato consciente. Registrado em `docs/hooks.md`, "Limites".
- **Pareceres da fatia 2 no diff:** enquanto o #125 não for mesclado, o `forge-check pr anti-alucinacao-portao` contra a `develop` também cobra o parecer de segurança pelos arquivos da fatia 2 (`docs/regras/R-BRIEF.md`). O parecer de segurança desta fatia é exigido de qualquer forma (seção 11).
