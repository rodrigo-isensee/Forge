---
tipo: qa
contrato: 1
pedido: worktree-orfas
branch: melhoria/worktree-orfas
commit: e590cc1b62e4488e2ad0ae99ab9b70cb0580b418
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-30
---
# QA - forge-fechar, passo 7: a lista do prune vai só ao log (F1), volta 1

Links: `docs/fechamento-integrador.md` (Limpeza: registro órfão), pedido WORKTREE-ORFAS. Sem UX nem API; as obrigações são as do pedido. Offline, só disco local (`R-CUSTO`). Carga de 1 minuto abaixo de 7 em cada disparo. Commit testado: e590cc1 (delta 049ab3d..e590cc1: um teste e o mutante Q1 na spec; o código de produção não mudou).

## Resultados
| ID | Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|---|
| CT-01 | E1: lista fora da tela, contagem na tela, `limpeza:` fecha o passo 7 | `test_prune_com_centenas_de_orfas_conta_na_tela_e_a_lista_fica_so_no_log` | 300 órfãs; tradução do git | Passou |
| CT-02 | E1: prune negado avisa com código e log | `test_c3_prune_negado_com_diretorio_ausente_imprime_prune_e_nao_remove` | prune com erro | Passou |
| CT-03 | Lista do prune gravada no log | `test_c3_prune_automatico_lista_no_log_o_que_removeu` | log | Passou |
| CT-04 | Limpeza não muda (ordem, códigos, comandos pendentes) | demais testes de `test_fechar_orfao` (verificados na volta 0 junto das suítes `test_fechar*`: 201 OK) | n/a | Passou |
| CT-05 | Prune só roda com o diretório da worktree presente ausente (guarda `[ ! -d "$arvore" ]`) | `test_worktree_ocupada_com_o_diretorio_presente_nao_roda_o_prune` | diretório presente (remove falhou) | Passou; mutante Q1 morre |

## Provas
- `python3 -m unittest tests.test_fechar_orfao` sobre e590cc1: 18 testes, OK (36 s).
- `bin/forge-mutante tests/mutantes/worktree-orfas.json`: `M1 · morreu · bin/forge-fechar:414`, `M2 · morreu · :415`, `M3 · morreu · :416`, `M4 · morreu · :414`, `M5 · morreu · :417`, `Q1 · morreu · bin/forge-fechar:412`. Todos morreram.
- Conferência da lista contra o diff: as guardas mudadas (412, 414 a 417) têm mutante cada uma; a 412, que faltava, agora tem o Q1 (`if [ ! -d "$arvore" ]` para `if true`), que cai no teste novo.
- `scripts/verificar-contribuicao.sh origin/develop`: rc=0.
- Vermelho: nesta volta só entra teste de guarda; a prova de que ele pega a regra é o Q1 morto.

## Achados
(nenhum)

## Bugs
Nenhum.

## Veredito
Aprovado em e590cc1. O A1 do parecer anterior (049ab3d) está resolvido: teste de diretório presente sem prune e mutante Q1 morto.
