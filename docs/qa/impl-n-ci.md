---
tipo: qa
contrato: 1
pedido: impl-n-ci
branch: melhoria/impl-n-ci-c1
commit: 9ad6be5f52333f8f7d8149f4eb28ec8c7b9f54ae
parecer: aprovado
escopo: completo
revisor: forge:qa-engineer
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-31
---
# QA: impl-n-ci (c1)

## Achados
- A1 (recomendado) tests/apoio_volta_unica.py:422 · mutante Q7 (pool do lote com o divisor do limite de CPU, conta antiga) sobreviveu: só muda a velocidade, e o teste de fonte única só procura a conta antiga. Sem teste de tempo (instável); justificado, não devolve.
- A2 (recomendado) tests/test_hooks.py:1970 · a prova de mutação da conta do pool é à mão (forge-mutante recusa arquivo de teste); mover `trabalhadores_do_pool` para um módulo de apoio deixaria o mutante declarável numa próxima vez.

## O que a branch entrega e a M14
- Itens do pedido: E1 (item 55 b: pool de threads por subprocesso, `trabalhadores_do_pool(nucleos_do_processo())` em fonte única, afinidade com recuo, piso 2, teto 4) e E3 (pesos regravados em `tests/pesos-d4.json`, 79 módulos = 79 arquivos `tests/test_*.py`, sem faltar nem sobrar). O limite de CPU do corpus fica como era, em `trabalhadores_do_limite_de_cpu` (C-3).
- M14 (agents/tech-lead.md:19): cumpre. Contam 70 linhas (`tests/test_hooks.py` 47, `tests/apoio_volta_unica.py` 15, `tests/test_hooks_volta_corpus.py` 8); pesos, fragmento e spec de mutantes ficam fora. Sem `hooks/` nem `PROTEGIDOS`. Um comportamento (o pool); o E3 é dado só, pela decisão técnica registrada no pedido.
- O escopo do pedido não mudou desde o plano: CA do pedido = E1 e E3, cada um com teste abaixo.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 / C-1 pool por núcleos, 2 a 4 | `PoolDosFixtures.test_pool_por_nucleos_e_limites` | 1, 2, 4, 16 núcleos; `None`, 0, negativo, texto | passou |
| E1 / C-1 afinidade, sem `FORGE_NPROC`, sem leitura = piso | `test_pool_le_a_afinidade_e_ignora_o_forge_nproc` | afinidade 2 em máquina de 16; `OSError` | passou |
| E1 fonte única | `test_pool_uma_fonte_so` | só a conta do limite de CPU resta | passou |
| E1 / C-3 limite de CPU não afrouxa | `tests.test_medida_cpu` (limite 90 s por trabalhador) | divisor antigo mantido | passou |
| E3 pesos | `test_suite_paralela` (peso só equilibra, módulo sem peso entra), conferência 79 = 79 | módulo sem peso, módulo a mais | passou |

## Vermelho antes do verde
- `forge-testes --vermelho 234dbe0… --modulos test_hooks,test_hooks_volta_corpus,test_medida_cpu`: sem veredito. A cópia reverte à base e a saída abre com `vermelho: base=234dbe0fb90b head=7281541ef128` (o head da worktree está à frente, com o parecer de segurança); o `test_hooks` dura mais que o prazo de 590 s (timeout, rc 124), e uma segunda tentativa em segundo plano morreu com a chamada. Não vale como vermelho.
- Recuo manual: `git archive 234dbe0` mais o `tests/test_hooks.py` do head, `python3 -m unittest tests.test_hooks.PoolDosFixtures`: `FAIL: test_pool_uma_fonte_so`, lista `['apoio_volta_unica.py', 'apoio_volta_unica.py', 'test_hooks_volta_corpus.py'] != ['apoio_volta_unica.py']`, `FAILED (failures=1)`. Os outros dois testes chamam a função nova, que a base não tem: não existem sem a implementação. No head: `Ran 3 tests`, `OK`.

## Mutação (a mão; o §5.1 do desenho pede o pool de volta a `nproc // 2`)
- Q1 pool = `nucleos // 2`: morreu (5 falhas). Q2 sem teto 4: morreu (2). Q3 sem piso 2: morreu (1). Q4 ignora a afinidade: morreu (1).
- `forge-mutante` (spec fora da árvore): `Q5 · morreu · tests/apoio_volta_unica.py:43` (limite de CPU acompanhando o pool, C-3); `Q7 · sobreviveu · tests/apoio_volta_unica.py:422` (A1, justificado). Q1 a Q4 e Q6 o `forge-mutante` recusa (arquivo de teste), por isso à mão.

## Cenários e resultado real
- `python3 -m unittest tests.test_medida_cpu tests.test_pesos_teto tests.test_suite_paralela tests.test_changelog`: `Ran 76 tests`, `OK`.
- `tests.test_hooks.PoolDosFixtures`: `Ran 3`, `OK`. O `test_hooks` inteiro e o corpus rodam no pre-push do envio; o resultado dele vale como a suíte completa desta branch.
- Sem interface nem API: acessibilidade e contrato não se aplicam. Sem bugs abertos.
