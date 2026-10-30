---
tipo: qa
contrato: 1
pedido: worktree-orfas
branch: melhoria/worktree-orfas
commit: ecb20794664e3eedb0e4b61261ab1d55bad5d85d
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-30
---
# QA - forge-fechar, passo 7: a lista do prune vai só ao log (F1), volta 2

Links: `docs/fechamento-integrador.md` (Limpeza: registro órfão), pedido WORKTREE-ORFAS. Sem UX nem API; as obrigações são as do pedido. Offline, só disco local (`R-CUSTO`). Carga de 1 minuto abaixo de 7 em cada disparo. Commit testado: ecb2079 (merge de origin/develop 3bd1d84 sobre 167ec0d, sem mudança própria; o delta 167ec0d..ecb2079 só traz o que a develop já tinha). Revalida o parecer de 167ec0d (e590cc1).

## Resultados
| ID | Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|---|
| CT-01 | E1: lista fora da tela, contagem na tela, `limpeza:` fecha o passo 7 | `test_prune_com_centenas_de_orfas_conta_na_tela_e_a_lista_fica_so_no_log` | 300 órfãs | Passou |
| CT-02 | E1: prune negado avisa com código e log | `test_c3_prune_negado_com_diretorio_ausente_imprime_prune_e_nao_remove` | prune com erro | Passou |
| CT-03 | Lista do prune gravada no log | `test_c3_prune_automatico_lista_no_log_o_que_removeu` | log | Passou |
| CT-04 | Limpeza não muda (ordem, códigos, comandos pendentes) | demais testes de `test_fechar_orfao` | n/a | Passou |
| CT-05 | Prune só com o diretório ausente (guarda `[ ! -d "$arvore" ]`) | `test_worktree_ocupada_com_o_diretorio_presente_nao_roda_o_prune` | diretório presente | Passou; Q1 morre |

## Provas
- `python3 -m unittest tests.test_fechar_orfao` sobre ecb2079: 18 testes, OK (27 s).
- `bin/forge-mutante tests/mutantes/worktree-orfas.json`: M1 (:414), M2 (:415), M3 (:416), M4 (:414), M5 (:417), Q1 (:412), todos `morreu`; rc=0. Desde 167ec0d o diff em `bin/forge-fechar`, no teste e na spec está vazio (`git diff e590cc1 ecb2079`); em `docs/fechamento-integrador.md` só mudou a linha 28, que veio da develop. A conferência lista x diff da volta 1 segue valendo.
- `scripts/verificar-contribuicao.sh origin/develop`: rc=0.
- Vermelho: não se aplica (merge sem código novo); a prova das guardas é a spec acima.

## Achados

## Bugs
Nenhum.

## Veredito
Aprovado em ecb2079.
