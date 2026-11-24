---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-bp13-desenho
commit: 2df4f0c1e8a3f28dae8a46ed7c3d29fadbdbfe79
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 (E154.2, desenho BP13, PR #838)

Diff `e15c8566..2df4f0c1`: `docs/propostas/bp13-atualizacao-em-lote.md` (novo, 63 linhas) e `changelog.d/v0480-bp13-desenho.md`. `forge-check classe`: T, "só documentação fora dos caminhos de controle"; pareceres: review. Sem código, sem guarda, sem mutante.

## Conferência contra a develop (e15c8566)
- F1: `git tag -l 'v*'` por data de criação dá 30 tags de 2026-11-07 (v0.42.0) a 2026-11-22 (v0.47.15), 16 dias: confere. A abertura lê `origin/develop:.forge/versao` e só pula a branch do mesmo nome (`bin/forge_sempre_atual.py:807-816`), então a da versão seguinte nasce da develop antiga: o conflito em `.forge/versao` descrito procede.
- F2: `PARECERES_DA_CLASSE` em `bin/forge-check:1071` e `classe_das_mudancas` em `:1120-1152` conferem com a tabela (só `.forge/versao` dá T por até 20 linhas; controle dá C). "22 atualizações em 40 dias, 4 pareceres" confere com a linha BP13 da fonte, que está fora do git (A1).
- F3: `git diff --name-only v0.47.1 e15c8566 -- templates/projeto migrations` lista 19 arquivos, todos em `templates/projeto`, e nenhum em `migrations/`: confere.
- Referências de linha (`bin/forge-init:4,166,216-218`, `bin/forge-upgrade:37-42,175,188-202`, `bin/forge-check:10966-10970`, ADR 0005 itens 2 e 3): todas batem com o código citado.
- D2 (`:41`): marcada como afrouxamento da quantidade de pareceres, para o dono e com confirmação escrita da segurança (`R-DECISAO`), com critério de reversão explícito (um defeito escapado atribuído à atualização, ou dois em 30 dias, volta à (c)). Atende.
- D4 cita a D8 da BP1 (DECISÃO DO DONO 2026-11-20 07:47) corretamente.

## Testes dos arquivos tocados
`test_changelog`, `test_clareza`, `test_modelos_citados`: OK. `test_citacao`: 2 falhas em `test_fonte_fora_da_raiz_nao_e_lida`, iguais na base e15c8566 (rodadas com `env -i` e `python3 -I` no clone em `/workspaces/.forge-contrib`): não vêm deste diff, que não toca o analisador. A suíte inteira fica com o CI do PR.

## Achados
- A1 (recomendado) docs/propostas/bp13-atualizacao-em-lote.md:3 · a origem `docs/propostas/boas-praticas-1911.md` não existe na develop e15c8566 (está só nos docs locais do Forge); os números da fonte em :18 e :56 não são conferíveis pelo repositório. Citar como fonte externa ou versionar a proposta.
- A2 (recomendado) docs/propostas/bp13-atualizacao-em-lote.md:43 · D4 libera a C2 após 7 dias de uso no Forge, mas a classe U só existe em `forge/upgrade-*` (C2 f), que o Forge não gera para si; a medida da :56 lê o projeto. Nomear o projeto-piloto ou a medida que vale no Forge.
- A3 (recomendado) docs/propostas/bp13-atualizacao-em-lote.md:5 · o item 3 da DECISÃO DO DONO 2026-11-21 20:54 diz que trava nova só entra se tirar ou simplificar outra; "nenhuma fatia cria trava nova" parafraseia mais estrito. Citar a regra como está e dizer qual sai com a C2.

## Parecer
Aprovado. Desenho só de documentação, dentro do escopo da E154.1, com números F1 a F3 reproduzidos na develop, referências de código exatas e a D2 corretamente levada ao dono e à segurança com critério de reversão. Os três achados são de precisão de texto e viram cartão depois do merge (`R-REVIEW`).
