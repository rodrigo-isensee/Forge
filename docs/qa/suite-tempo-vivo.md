---
tipo: qa
contrato: 1
pedido: v0457
branch: melhoria/suite-tempo-vivo
commit: 5c06712475d096d89f2cf27098fb6b12265ff5c5
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-12
---
# QA: suite-tempo-vivo (v0457, E23.26)

Diff 8b5a44d5..5c067124: `scripts/suite-paralela.py` grava `p<i>.saida.json.tempos`; `TemposAoVivo` imprime a linha por unidade e o resumo no sinal. Veredito, ordem e stdout final não mudaram (conferido: o teste novo lê `OK` na última linha do stdout).

## Achados

- A1 (bloqueante) tests/test_suite_paralela.py:845 · test_linha_por_modulo_sai_antes_do_fim instável: com carga alta (load ~10) falhou 4 de 12 rodadas, sempre sem a linha "unidade test_c"; passou 3 de 3 com carga baixa. Causa não achada (scripts/suite-paralela.py:573 ou o arquivo de tempos do filho). Teste instável bloqueia (R-QA).
- A2 (recomendado) scripts/suite-paralela.py:545 · o mutante "tirar flush=True" do print da unidade sobrevive: stderr em pipe já descarrega por linha no Python 3.12, então é equivalente na prática; o flush do `rodando` (linha 553) morre só às vezes.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Linha por unidade sai ao vivo, antes do fim | test_linha_por_modulo_sai_antes_do_fim | suíte ainda rodando (módulo bloqueado) | instável (A1) |
| SIGTERM deixa o resumo de quem rodava e não lista quem terminou | test_sigterm_deixa_o_resumo_de_quem_rodava | `rodando test_a` ausente | passou |
| Saída final e código de saída iguais | mesmos testes (`OK`, rc 0 / rc != 0) | n/a | passou |

## Cenários e resultado real
`python3 -m unittest tests.test_suite_paralela`: 63 testes, OK (1m27, carga baixa).
Mutantes em cópia (só os 2 testes novos): sem resumo do SIGTERM, morreu (1 teste cai); buffering do arquivo de tempos do filho trocado, morreu (2 caem); sem `atualizar()` no laço de espera, sem veredito (trava até o timeout, não conta como morto); sem flush da linha da unidade, sobreviveu (A2); sem flush de `rodando`, sobreviveu numa rodada e morreu noutra (carga).
SIGINT e SIGHUP não têm teste próprio (mesma rota de `Interrompido`); sem mutante.
