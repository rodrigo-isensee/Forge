---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp3-s1-atalho
commit: 45f429a4f2cdc300318fda6d84198f4ebce9971d
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478, BP3 S1 atalho durável (E39.11, revalidação)

Revalidação pelo delta (`forge-check parecer delta`, intervalo lido `3e53ae72..4d033ac4`, base `origin/develop` 0f6034e): `scripts/jarvis-comum.sh` novo, `scripts/jarvis` e `scripts/jarvis-forge` passam a carregá-lo por `source`, README, fragmento, `docs/indice-forge.md`, mutantes reagrupados em 2 arquivos e os testes que copiam o atalho (`test_atalho_duravel`, `test_doutor`, `test_sempre_atual`; o oráculo pelo QA em 45f429a4). O parecer anterior reprovou 3e53ae72 (A1 tamanho, A2 janela zero).

## Achados
- A1 (recomendado) scripts/jarvis-comum.sh:90 · `FORGE_QUEDA_JANELA=09` passa no filtro de dígitos, mas `$((janela / 60))` lê octal e o `set -e` do atalho encerra na 1.ª queda depois de gravar `acao=reabre` (S1): falha para o lado de parar e a variável é de teste; normalize com `10#` ou recuse zero à esquerda.
- A2 (recomendado) docs/indice-forge.md:88 · `jarvis-comum.sh` entra no índice como `—`: sem shebang, o `indice-forge.py` não lê a linha `# Forge:`; ponha a descrição onde o gerador a lê ou ensine o gerador a ler arquivo de `source`.

## Sondas
- S1 · `supervisionar` com claude falso que sai 137, `FORGE_QUEDA_ESPERA=0 FORGE_QUEDA_JANELA=09` · espera: reabre até o teto · obtido: `09: value too great for base`, rc=1, quedas.log com `tentativa=1 acao=reabre` e nenhuma reabertura

## Parecer
Aprovado. A1 anterior resolvido: `forge-check pr v0478 --previo` não emite a linha `tamanho:` (só aparece acima de 150) e o `--numstat` de código contra a `develop` soma 148 linhas (`scripts/jarvis` 22+4, `scripts/jarvis-comum.sh` 94+0, `scripts/jarvis-forge` 23+5), dentro do H1; as três funções ficam só no arquivo comum, conferido por `ArquivoComum`. A2 anterior resolvido: janela só de zeros volta a 1800 (`case *[1-9]*`), com teste do ramo (`test_janela_zero_nao_tira_o_teto_de_reaberturas`) e mutante M25. Novo no delta: 143 (`kill`) passa a parada, com teste e mutante M24; README traz como encerrar de vez. O trampolim de `instalar-atalho.sh` executa o script do `installPath` do plugin, então o `source` pelo `dirname` de `BASH_SOURCE` acha o arquivo comum ao lado. Testes do item: `bin/forge-testes tests/test_atalho_duravel.py tests/test_oraculo_sempre_atual.py tests/test_sempre_atual.py`, 272 testes, `test_atalho_duravel` sem falha; as 39 falhas e 2 erros são todos de `test_oraculo_sempre_atual`/`test_sempre_atual` com `adiado:duvida:proc` (leitura de `/proc` neste sandbox) e se repetem igual na `origin/develop` (`test_claude_vivo_sem_trabalho_em_curso_nao_adia` falha nas duas): ambiente, não o item; o CI do PR decide. `shellcheck` e a mutação ficam com o autor e o CI (`R-REVIEW`). A1 e A2 viram cartão depois do merge.
