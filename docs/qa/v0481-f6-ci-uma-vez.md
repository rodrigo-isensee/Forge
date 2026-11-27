---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-f6-ci-uma-vez
commit: 700a2fc497a0ea79e47961794a0fb76f0c3d655d
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-27
---
# QA: v0481 (E32.22, #929, F6: o CI do PR roda a suíte uma vez), delta da volta 5

- ci: 700a2fc497a0ea79e47961794a0fb76f0c3d655d verde

Detalhe lido em gh pr checks 929 no sha revisado: verdes `bateria (passos)`, `bateria (python 3.14)`, `bateria (verificações longas)`, `instalação (python 3.14)`, suíte 3.12 partes 1 a 5, árvore e teto de pulados; fora os que esperam parecer: `bateria`, `bateria (pareceres)` e `catraca`.

## Delta da volta 5 (e8998527..700a2fc4)
O A3 da volta anterior está fechado: a spec foi dividida em `v0481-f6-ci-uma-vez.json` (CI-M1 a M8) e `-2.json` (CI-M9 a M15), 8 + 7, mesmo `pedido`, ids únicos. A concatenação das duas é idêntica, mutante a mutante, à spec de 15 do head e8998527 (comparada em JSON: igual). O V2 (`test_os_ids_da_spec_do_f6_nao_repetem_os_de_outra_spec_do_pedido`, no máximo 8 por spec) passa, e a parte 4/5 do CI ficou verde.
- `bin/forge-mutante tests/mutantes/v0481-f6-ci-uma-vez.json tests/mutantes/v0481-f6-ci-uma-vez-2.json --base e8998527 --processos 2` (trava obtida; rc=0): linha `base=e89985279c7a... mb=e89985279c7a... rev=700a2fc497a0`; CI-M1 a CI-M15 todos `morreu` (15 de 15).
- `python3 -m unittest tests.test_suite_partes.FiacaoDoCI` no head: Ran 17, OK (inclui os 4 testes de comportamento do diário e da fumaça do 3.14).
- Vermelho antes do verde: os 4 testes de comportamento foram vistos falhando sem a implementação na volta 4 (cópia com o ci.yml da base e sem diario.yml); a prova de mutação do delta (M9 a M15 mortos no head) cobre a regressão. Esta volta não mudou comportamento de CI, só a divisão da spec.
- Nenhum outro defeito no delta.

## Critério → teste → resultado
O pedido não tem docs/ux com CA-n para esta etapa; os critérios vêm do objetivo do brief.
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Suíte do PR roda uma vez (3.12), sem job da suíte no 3.14 | `FiacaoDoCI.test_f6_o_pr_roda_a_suite_uma_vez` + os da matriz e agregadores | 5 partes; nenhum job `*-quatorze` fora instalação e agregador | passou; vermelho na base |
| 3.14 só instalação e fumaça | `MatrizNeedsEAgregadorTest`, CI-M1, X3, X4 | needs e `always()` do agregador | passou; mutantes mortos |
| Fumaça do 3.14 de fato roda | `test_f6_fumaca_do_python_3_14_roda_de_fato`, CI-M15 | passo da fumaça | passou; M15 morreu |
| Verificações longas e mutantes saem do PR | `test_f6_o_pr_roda_a_suite_uma_vez`, CI-M1 | texto do ci.yml | passou; M1 morreu |
| diario.yml diário, só leitura, escreve só issue | `test_f6_diario_roda_o_que_saiu_do_pr_na_develop_e_abre_o_cartao`, CI-M2, CI-M3 | `issues: write` único, `always()` do cartão | passou; M2 e M3 morreram |
| Fatia do dia, uma spec por chamada, pendentes de fora | `test_f6_diario_roda_uma_spec_por_chamada_sem_os_pendentes_conhecidos`, CI-M4 a M8 | dia % 30, pendentes, spec sem mutante | passou; M4 a M8 morreram |
| Jobs do diário usam a develop, 5 partes, mutante vivo reprova | `test_f6_diario_cada_job_le_a_develop_*`, `test_f6_diario_mutante_vivo_reprova_*`, CI-M9 a M13 | `ref: develop` por job, matriz, falha do job | passou; M9 a M13 morreram |
| Issue só para quebra nova | `test_f6_diario_cartao_comenta_na_issue_aberta_*`, CI-M14 | issue aberta recebe comentário | passou; M14 morreu |
| Push na develop roda a suíte no 3.12 | `test_agregador_da_develop_exige_as_cinco_pernas_e_o_teto_sem_rodar_codigo` | agregador `rapida` | passou |
| Nomes dos checks exigidos não mudam | `Workflows` em test_catraca, `test_agregadores_*` | `bateria`, `bateria (python 3.14)` | passou |
| Spec de mutantes dentro do teto de 8 | V2 em test_forge_mutante | 8 por spec | passou |

## Observações
- O `schedule` do diario.yml só dispara com o arquivo na branch padrão; o diário só começa a rodar depois de homolog para main. Até lá, só `workflow_dispatch`.
- Acessibilidade e E2E de interface: não se aplicam (mudança só de workflow e testes).
