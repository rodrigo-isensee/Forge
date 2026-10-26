---
tipo: review
contrato: 1
pedido: lote-leitura-hook
branch: melhoria/lote-leitura-hook
commit: d67f31fdeb1b66b85771a7687b2f2a88e2a63c9a
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-26
---
# Review: lote-leitura-hook (revalidação 16, volta I: só testes e specs)

Pedido RET-LEITURA-HOOK-H-REV, E1.1. Sou revisor independente e não implementei esta volta (`R-REVIEW`). O parecer anterior (revalidação 15, `aprovado`, A1 a A3 recomendados) está em `96cf447`, sobre `0e8776d`. A volta I responde ao QA `7f378b0` (A1 bloqueante: X5 e X6 sobreviviam; A2: X1 e X3 fora da spec).

**Delta lido.** O `forge-check delta --parecer docs/reviews/lote-leitura-hook.md` deu `0e8776d..d67f31f`: `tests/mutantes/lote-leitura-hook-volta.json:1-46` (novo) e `tests/test_hooks.py:3432-3447` e `3453-3463`. Os pareceres de `941a0dc` e `7f378b0` entram no intervalo e não são código. Os commits do autor são `bb21376` e `d67f31f`. Li inteiro, além do delta, as rotas que os mutantes apontam: `hooks/_comum.py:1893-1900`, `hooks/conformidade.py:850-862` e `1706-1716`, e o teste `test_texto_dividido_aberto_com_mais_de_uma_leitura_recusa` (`tests/test_hooks.py:3335-3359`). Fica como "já lido" tudo o que vem até `0e8776d` (revalidações 1 a 15).

**`hooks/` não mudou:** `git diff 7f378b0..d67f31f -- hooks/` sai vazio.

**Critério.** O A1 e o A2 do QA `7f378b0`, a seção 2.B da rev14 (decisão "B" do dono, 2026-10-24), a decisão técnica do Jarvis de 2026-10-24 (volta I só em `tests/test_hooks.py` e nas specs, segunda spec pelo teto de 8) e a decisão "A" de 2026-10-22 (voltas por classe).

## Achados
- A1 (recomendado) hooks/conformidade.py:1714 · segue de 96cf447: a regra do tee só vê a palavra tee solta, e env -uS'"' -S'tee docs/reviews/x.md' dá []; sem efeito hoje (o PreToolUse recusa a linha e a autoria ausente falha fechado)
- A2 (recomendado) tests/mutantes/lote-leitura-hook.json:4 · segue de 96cf447 em parte: com a segunda spec, 12 mutantes declarados; M4 a M8 e M10 do QA da revalidação 14 seguem fora das specs (mortos pela suíte; cartão MUTANTE-TETO)
- A3 (recomendado) tests/test_hooks.py:3032 · segue de 96cf447: teto de 60 s em tempo de relógio, instável sob a carga da rodada M6 (cartão PROP-TEMPO-CPU)

## Parecer
**Aprovado.** A volta fecha o A1 bloqueante e o A2 do QA `7f378b0` só com teste e spec, como a decisão técnica manda. Nenhum achado bloqueia. Os três recomendados são os de `96cf447`, fora do delta, e não devolvem.

**Teste novo** (`test_alvos_do_tee_atras_do_texto_dividido_aberto`, `tests/test_hooks.py:3432`). Os cinco casos passam por `env -aS'"' tee`, isto é, pela rota `TextoAbertoComLeituras` de `alvos_de_escrita` (`conformidade.py:1712-1715`). Eles cobrem dois alvos, `-a`, `--append`, `-i` com dois alvos e opções misturadas entre os alvos. O teste compara a lista inteira, em ordem. Um `tee` com só a primeira palavra (X5) erra o 1.º, o 4.º e o 5.º caso. Um `tee` que toma a opção como alvo (X6) erra o 2.º a 5.º caso. O teste afirma o comportamento que a seção 2.B pede ("cada palavra depois de um `tee`") e não fixa nada além dela.

**Segunda spec** (`tests/mutantes/lote-leitura-hook-volta.json`). Conferi a linha de cada `de` no `hooks/` de `d67f31f` e rodei a ferramenta:

| Mutante | Linha | Rota do teste | `forge-mutante` |
|---|---|---|---|
| X1 (`gasto` → `0` no texto dividido adiado) | `hooks/_comum.py:1899` | `separar_lancadores(["env", "-uS'", "cat"])` deve levantar `TextoAbertoComLeituras`; com `0`, sai `TextoDivididoAberto` (`test_hooks.py:3350-3352`) | morreu |
| X3 (`except TextoDivididoAberto` → `ZeroDivisionError`) | `hooks/conformidade.py:859` | o controle `env -S'"' cat .env` (uma leitura só) deve sair 0 por `ilegivel` (`test_hooks.py:3347`) | morreu |
| X5 (`[:1]` nos alvos do `tee`) | `hooks/conformidade.py:1714` | o teste novo, casos com dois alvos | morreu |
| X6 (sem o filtro de `-`) | `hooks/conformidade.py:1714` | o teste novo, casos com opção | morreu |

Saída: `bin/forge-mutante tests/mutantes/lote-leitura-hook-volta.json --rev d67f31fdeb1b66b85771a7687b2f2a88e2a63c9a`, rc 0, `X1 · morreu · hooks/_comum.py:1899`, `X3 · morreu · hooks/conformidade.py:859`, `X5 · morreu · hooks/conformidade.py:1714`, `X6 · morreu · hooks/conformidade.py:1714`. Cada mutante aponta a linha certa e morre por um teste que passa pela rota mutada. Os ids das duas specs não se repetem (B, M e X).

**`test_spec_de_mutantes_do_lote_e_valida`** (`tests/test_hooks.py:3448`). Agora valida a forma das duas specs, e cada `de` aparece uma vez no arquivo de hoje. A checagem das quatro trocas de B segue sobre a primeira spec (`specs[0]`), onde B1 a B4 estão. Ela continua pegando uma spec que perca B1 a B4.

### O QA `7f378b0`: o que fechou
| Achado | Estado | Evidência |
|---|---|---|
| A1 (bloqueante: X5 e X6 sobrevivem) | fechou | teste novo; X5 e X6 morrem |
| A2 (X1 e X3 fora da spec) | fechou | segunda spec; X1 e X3 morrem |
| A3 (teto sem alvo do `tee`) | fora da volta | cartão TEE-TETO-ALVO (decisão técnica de 2026-10-24) |

### Fora do bloco
- **Testes que rodei** em `d67f31f`, na worktree de review: o teste novo, `test_spec_de_mutantes_do_lote_e_valida` e `test_texto_dividido_aberto_com_mais_de_uma_leitura_recusa`. Deu `Ran 3 tests in 0.477s`, `OK`. Rodei também o `forge-mutante` da segunda spec (acima). A suíte completa não rodou, porque o brief limita a execução aos testes do lote. O pre-push da entrega rodou a suíte (1986 OK, histórico do pedido).
- **Teto M14:** não vale para o `lote-leitura-hook` (decisão M14).
- O Forge não tem `docs/engineering/praticas.md`, então não há regra de ferramenta nem de leitura a citar. O PA-7 (`docs/engineering/achados-recorrentes.md`) está sem linhas, e não há item a conferir.
- **Commits:** `bb21376` e `d67f31f` estão em Conventional Commits em português, com o pedido.
- **Segurança:** é do E2.1 e não foi refeita aqui. Sem `hooks/` no delta, não há achado novo para o `security-engineer`.
