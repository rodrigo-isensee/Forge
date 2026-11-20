---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-parecer-mesclado
commit: 8cff35a0a8a65134b83fbd3841c4f3bb290269bc
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 E50.8 (ENTREGA-PARECER-MESCLADO, volta E50.6 e E50.7)

Revalidação pelo delta (`forge-check parecer delta`, intervalo `cdf62e0a..8cff35a0`; H3, `R-REVIEW`): bin/forge-check, hooks/conformidade.py, docs/hooks.md, changelog.d, tests/test_hooks.py, tests/test_selo_e_entrega.py, as 20 fixtures `pp-sessao-forge-*` de PARECER-PELO-PAPEL e as specs `-2`, `-3` e `-4`. Código da volta: cerca de 40 linhas, dentro do teto (H1). Rodadas anteriores: aprovado em 48153733 (A1, A2) e em cdf62e0a.

## Achados
- A1 (bloqueante) tests/hooks/conformidade/pp-sessao-forge-outro-repo-dev-write-reviews-libera.json:15 · `{tmp}/home/outro/docs/...` casa o padrão de caminho pessoal: `scripts/verificar-contribuicao.sh 8a503799` barra o delta, o pre-push recusa e o passo "Segredo, .env ou caminho pessoal no diff" do CI reprova igual (`R-CONTRIB`). Troque a pasta (fora de `home/`) ou marque `forge:exemplo`.

## Sondas
- S1 · `scripts/verificar-contribuicao.sh 8a503799299d189c8c35eb8bcf4bf850d9f7d5a0` no head 8cff35a0 · espera: `ok: nenhum segredo nem caminho pessoal` · obtido: `pp-sessao-forge-outro-repo-dev-write-reviews-libera.json:15: caminho pessoal` e `Contribuição barrada: 1 achado(s)`

## Parecer
Reprovado no head 8cff35a0 só por A1; o código da volta está aprovado na leitura abaixo e, corrigido o A1, a revalidação lê só o delta.

E50.6 (A4 da segurança): `parecer_mesclado_na_volta` passa a exigir o blob do último `parecer conferido` do Jarvis (`parecer_trazido`) quando o papel dono da pasta é autor da volta ou quando nenhum autor é lido (falha fechada). `autores_da_volta` lê o `Agente destino` só dos briefs selados de codigo desta branch e deste pedido; `nome_do_papel` devolve o mesmo nome de `PAPEL_DO_BRIEF_DO_PARECER`. A chamada fica atrás do `and` dos outros testes, então só roda para arquivo de parecer. `ParecerDoMesmoPapelDoAutor` cobre o sem linha, o com linha, a linha de outro blob, o sem autor e o brief de outro pedido.

E50.7 (A3 da segurança): `GuardaDaProva.parecer_no_topo` aplica as regras das pastas de parecer pela forma relativa ao topo da cópia do Forge que contém o alvo, e `recusa_do_estado` deixa valer no clone só as recusas dessas pastas (M24 prova que as outras regras de caminho seguem fora). A ordem da política põe `docs/security/aceites/` antes de `docs/security/`, então o `seguranca` não grava aceite (fixture própria). `CAMINHOS_DE_PARECER` não sombreia a `PASTAS_DE_PARECER` de `hooks/conformidade.py:251`, que segue com o uso antigo. As 20 fixtures cobrem papel × pasta × forma (Write, Edit, MultiEdit, NotebookEdit, `>`, `cp`, `python`, `git show >`), clone e `wt/*`, o vizinho `docs/reviewsx/` e o repositório que não é do Forge. docs/hooks.md e o fragmento do changelog acompanham.

Rodei com ambiente limpo: `ParecerMescladoNaVolta` 14 OK e `ParecerDoMesmoPapelDoAutor` 5 OK; `forge-mutante` nas specs `-3` e `-4`: M17 a M24 morreram; `--cobertura --base cdf62e0a` cobre toda guarda mudada e `--conferir` acusa os trechos no lugar. Classes alcançadas pela troca de nome para `CAMINHOS_DE_PARECER`: `test_conformidade_verde` inteiro (43) OK; `test_hooks.Hooks` com 114 testes, 112 OK e 2 falhas só na fixture `pesado/mesma-sessao-libera` (tempo esgotado no subprocesso do hook `pesado`, que a branch não toca desde o Base-sha, com o aviso de pid de outro namespace do sandbox); fica para o CI do PR conferir. A suíte inteira fica com o CI do PR (`R-REVIEW`).
