---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-g3-testes-uma-vez
commit: 55f87ffd19d79ad27a20521c45ee65004521bc00
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: v0481 (G3 primeira fatia, volta única, delta ef45eec5..55f87ffd, E8.7)

Delta lido: `bin/forge-check` (+26/-11: constante `CHECKS_FORA_DA_LINHA_DO_CI`, `FORA_DA_LINHA_DO_CI`, `cobra_a_linha_do_ci`), duas skills, `test_forge_check_pr`, `test_pre_envio_brief` (classe `ChecksForaDaLinhaDoCi`), spec M5 realinhada e specs novas M15 e M16 (`-2`) e M17 a M19 (`-3`). O A1 do parecer anterior está resolvido: os três checks vermelhos por construção saem da linha, e o merge segue exigindo todos.

## Achados
- A1 (recomendado) agents/tech-lead.md:16 · Ainda diz "cite o CI verde ou o PQ do autor"; a regra PARECER-LE-O-CI não admite o PQ do autor (o agents/qa-engineer.md:15 idem). Texto desalinhado; vira cartão depois do merge.

## Critério → teste → resultado
| Critério (do brief) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A1: constante única citada por brief, recusa do pr, esqueleto e skills | `ChecksForaDaLinhaDoCi` (4 testes, inclui cada check ser job real dos workflows) | lista com 3 itens; check a mais ou a menos | passou; M18 morreu |
| A3: só cobra a linha do parecer cujo `commit:` traz a regra | `test_commit_anterior_a_regra_nao_cobra_a_linha`, `..._segue_com_o_ci_verde_do_head` | commit anterior à regra, com e sem prova `- suíte:` | passou; M15 morreu |
| A3: `commit:` fora da forma de sha ou erro do git cobra | `test_cobra_a_linha_com_commit_fora_da_forma_ou_erro_do_git` | vazio, ausente, `--cached`, sha inexistente | passou; M16, M17, M19 morreram |
| A isenção não solta nada que a develop barra | leitura de `suite_do_parecer`: a isenção só zera `sem_ci`; o ramo `falta_na_prova` (PARECER-SO-COM-CI-VERDE) roda igual | parecer isento sem CI verde no head | passou: 1 violação `PARECER-SO-COM-CI-VERDE` |
| Não forjar `commit:` antigo em parecer novo | sonda local `commit_vale(raiz, 220ba3fa, dominio="qa")` | `commit:` pré-regra com a regra no HEAD | `cobra=False`, mas `desatualizado: bin/forge-check mudou depois do parecer ... é do domínio do parecer de qa`: o `forge-check pr` o recusa por outro caminho |
| Enxugamento da skill qa-testing sem perder regra | diff da linha `Parecer:` e invariantes de `tests/config.json` | 12 trechos invariantes da qa-testing | passou: a linha manteve "numa passada", "no mesmo head do review"; só o texto do CI foi fundido; nenhum invariante tocado |

## Cenários e resultado real
- Módulos tocados: `test_forge_check_pr` 61 `OK`; `test_pre_envio_brief` 28 `OK`; `test_fechar_forge_check_real` 5 `OK`.
- Mutantes (`--processos 3`, `rev=55f87ffd19d7`, as três specs numa chamada): M1 a M19 todos `morreu` (M13 e M19 com `(erro)` do teste sob o mutante, controle verde). Nenhum sobrevivente nem equivalente. `--cobertura --base 220ba3fa`: toda condição mudada `coberta`; sem `não coberto`.
- `forge-mutante --conferir --todas`: 26 linhas, rc 1, idêntico ao rodado com `--rev 220ba3fa` (base); nenhuma linha dos `v0481-g3` (os trechos duplicados são de specs antigas, pré-existentes).
- Vermelho: provado no parecer anterior (`forge-testes --vermelho 220ba3fa`, rc 0); os testes novos deste delta têm o vermelho nos mutantes M15 a M19 (cada um troca a guarda e derruba o teste declarado).
- CI do head `55f87ffd` (PR #893, run 45575428813), lido por `gh pr checks`: 6 `pass`, 7 `skipping`, 0 `pending`, as 10 partes da suíte (python 3.12 e 3.14) verdes; só `bateria (pareceres)`, `bateria` e `catraca` em `fail`, os três fora da linha (esperam o parecer ou o rótulo; o merge exige todos).
- ci: 55f87ffd19d79ad27a20521c45ee65004521bc00 verde
