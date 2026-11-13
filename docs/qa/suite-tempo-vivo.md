---
tipo: qa
contrato: 1
pedido: v0457
branch: melhoria/suite-tempo-vivo
commit: 7a27f6e6f5869460d3c47789f08345eb4b56c070
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-12
---
# QA: suite-tempo-vivo (v0457, E23.26)

Diff 8b5a44d5..5c067124: `scripts/suite-paralela.py` grava `p<i>.saida.json.tempos`; `TemposAoVivo` imprime a linha por unidade e o resumo no sinal. Veredito, ordem e stdout final não mudaram (conferido: o teste novo lê `OK` na última linha do stdout).

## Achados

- A1 (resolvido) tests/test_suite_paralela.py:956 · instabilidade corrigida: 12 de 12 rodadas OK (causa: readline seguido de communicate perdia linha do buffer; helper `termina(p)`).
- A2 (resolvido) tests/test_suite_paralela.py:253 · o flush da linha da unidade tem teste (M6 e M8 morreram).
- A3 (resolvido) tests/mutantes/v0457-suite-tempo-vivo.json:M7 · o mutante M7 (scripts/suite-paralela.py:549, `except OSError` trocado por `ZeroDivisionError`) saía inválido (BrokenPipeError como erro). Corrigido em 7a27f6e6: o teste captura o OSError e chama `self.fail`; M7 morre por falha.

## Revalidação por delta 5c067124..076dcc80 (E23.32)
## Revalidação por delta fab4c482..7a27f6e6 (E23.39, volta 2)
Delta no domínio: só `tests/test_suite_paralela.py` (test_stderr_quebrado_nao_derruba_e_a_linha_sai_com_flush captura OSError e chama `self.fail`).
`forge-mutante tests/mutantes/v0457-suite-tempo-vivo.json` (rev=7a27f6e6f586): M1 a M8 morreram (M7 por falha), rc 0.
`python3 -m unittest tests.test_suite_paralela.TemposAoVivoLogica`: 5 testes, OK.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Linha por unidade sai ao vivo, antes do fim | test_linha_por_modulo_sai_antes_do_fim | suíte ainda rodando (módulo bloqueado) | passou (12 de 12) |
| SIGTERM deixa o resumo de quem rodava e não lista quem terminou | test_sigterm_deixa_o_resumo_de_quem_rodava | `rodando test_a` ausente | passou |
| Saída final e código de saída iguais | mesmos testes (`OK`, rc 0 / rc != 0) | n/a | passou |

## Cenários e resultado real
`python3 -m unittest tests.test_suite_paralela`: 63 testes, OK (1m27, carga baixa).
Mutantes em cópia (só os 2 testes novos): sem resumo do SIGTERM, morreu (1 teste cai); buffering do arquivo de tempos do filho trocado, morreu (2 caem); sem `atualizar()` no laço de espera, sem veredito (trava até o timeout, não conta como morto); sem flush da linha da unidade, sobreviveu (A2); sem flush de `rodando`, sobreviveu numa rodada e morreu noutra (carga).
SIGINT e SIGHUP não têm teste próprio (mesma rota de `Interrompido`); sem mutante.
