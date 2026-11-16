---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-pr-hook-rapido
commit: 8eebc2a51576f5d9957653f4ad55bbdf7682f12b
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-15
---
# QA: v047 · hook R-REVIEW rápido (E2.117 / E2.143)

Só os testes do item (`tests/test_pr_hook_rapido.py`, `tests/test_pr_hook_prazo.py`) e a leitura em lote do `bin/forge-check`. A suíte inteira roda no CI do PR (check-run `bateria` do mesmo sha).

## Achados
- A1 (recomendado) bin/forge-check:1581 · `escritor` é o sha256 do próprio forge-check, público: quem grava em `.git/forge/pr/<head>/` forja um aprovado. Já valia para a abertura do PR; agora vale também para ready e merge. O `conformidade` barra citar `.git/forge`; o CI segue sendo o portão.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Aprovado do mesmo head libera só lendo (ready e merge), dentro de 3 s | test_aprovado_do_mesmo_head_libera_so_lendo_no_prazo | prazo da decisão | passou |
| Reprovado do mesmo head recusa só lendo | test_reprovado_do_mesmo_head_recusa_so_lendo | recusa com R-REVIEW | passou |
| Head diferente refaz a conferência (falha fechada) | test_head_diferente_roda_de_novo | head velho não libera | passou |
| Base diferente refaz a conferência | test_base_diferente_roda_de_novo | base | passou |
| Prazo vencido sem resultado recusa e diz o comando | test_head_diferente_com_prazo_vencido_recusa_e_diz_o_comando | prazo | passou |
| Sem resultado e sem violação, a conferência de hoje libera (só a abertura exige) | test_sem_resultado_e_sem_violacao_a_conferencia_de_hoje_libera | ausência do gravado | passou |
| Lote devolve o mesmo texto do `git show` | test_mesmo_texto_do_git_show, test_documentos_da_ref_iguais_aos_do_disco | CRLF, espaço nas pontas, subpasta `.md`, não-`.md` | passou |
| Chamadas git por pasta (ausente: só rev-parse; sem `.md`: sem cat-file; cache) | test_chamadas_git_por_pasta | pasta ausente ou vazia | passou |
| Lote fora do pedido não lê nada | test_lote_fora_do_pedido_nao_le_nada | objeto ausente, vazio, truncado, outro id | passou |

## Cenários e resultado real
- Suíte do item: `python3 -m unittest tests.test_pr_hook_rapido tests.test_pr_hook_prazo` → `Ran 28 tests in 85.306s · OK`.
- Mesma saída do forge-check (comparação direta de `documentos()` em lote × `git show` por arquivo, no repositório real): `HEAD 975 975 True`, `origin/develop 975 975 True`, `origin/main 965 965 True`.
- Vermelho antes do verde: `forge-testes --vermelho bf475209` cai na suíte completa (o diff mexe em `bin/forge-testes`) e passou de 570 s: rc=124, sem veredito, não vale como vermelho. Feito à mão: árvore da base (`git archive bf475209`) mais só `tests/test_pr_hook_rapido.py` → `Ran 10 tests · FAILED (failures=6, errors=4)`: os 4 de `DocumentosEmLote` erram (sem `textos_da_arvore`) e ready e merge falham em aprovado, reprovado e prazo vencido. Os 3 de falha fechada (head, base, sem resultado) passam na base por desenho: guardam que o atalho não afrouxa.
- Mutantes (`bin/forge-mutante tests/mutantes/v047-pr-hook-rapido.json`): `PHR1..PHR8 · morreu` (8 de 8; PHR5 morreu por erro do teste declarado, que passa sem o mutante). `--cobertura --base bf475209`: toda condição mudada `coberta` ou `isenta`.
- Forja do aprovado: lido em `resultado_gravado_do_pr` e `escritor_do_resultado`; o escritor é um hash público, sem segredo, então não prova autoria (A1). Não reproduzi a escrita: a pasta está atrás do `conformidade`.

## Pendências
Nenhuma bloqueante. Médios e baixos: nenhum.
