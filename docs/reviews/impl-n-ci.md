---
tipo: review
contrato: 1
pedido: impl-n-ci
branch: melhoria/impl-n-ci-c1
commit: 655ae8c8a6f56ac44c78e241ee570dcebbd39222
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-31
---
# Review: impl-n-ci (c1)

## Achados
- A1 (recomendado) tests/test_hooks_volta_corpus.py:11 · `import os` ficou sem uso: o único uso era a conta do pool trocada na linha 75. Tirar o import num próximo PR que toque o arquivo.
- A2 (recomendado) tests/test_hooks.py:521 · `nucleos_do_processo` colado em `PRAZO_DA_DECISAO_NOS_TESTES`, sem as 2 linhas em branco antes do `def`; a docstring fala em recuo para `cpu_count`, mas com `OSError` devolve `None` (piso 2).
- A3 (recomendado) tests/pesos-d4.json:1 · o desenho (§3.3) pede a máquina, o load e o `nproc` da medida no PR; o commit 5e01e83 só diz árvore limpa e suíte verde. Registrar no corpo do PR.

## Parecer
Aprovado. Li o diff inteiro de `234dbe0` a `655ae8c` (4 commits).

O que entrega: o E1 do pedido (item 55 b, pool de threads por subprocesso) e o E3 (pesos regravados, depois do E1, como o desenho §3.3 pede). A conta do pool sai para uma fonte só, `trabalhadores_do_pool(nucleos_do_processo())` em `tests/test_hooks.py`, usada nas 4 cópias que a base tinha (`test_hooks.py`, `test_hooks_volta_corpus.py` e as duas de `apoio_volta_unica.py`); a afinidade é lida como no hook `agentes`, e `FORGE_NPROC` fica de fora (C-1). O limite de CPU do corpus segue com a conta de antes, separado em `trabalhadores_do_limite_de_cpu` (C-3, P-CI-2 = A): subir o pool não afrouxa o limite. O mutante M4 de `tests/mutantes/prop-tempo-cpu.json` acompanhou o nome novo. Teto 4 do `R-TETO` mantido.

Testes: `PoolDosFixtures` cobre os casos da tabela do desenho (1, 2, 4 e 16 núcleos, afinidade 2 numa máquina de 16, `None`, zero, negativo, texto) e guarda a fonte única (`test_pool_uma_fonte_so` exige exatamente uma cópia da conta antiga, a do limite de CPU). Rodei `python3 -m unittest tests.test_hooks.PoolDosFixtures` na worktree: `Ran 3 tests`, `OK`. O mutante do desenho (§5.1, pool de volta a `nproc // 2`) fica com o QA.

M14 (agents/tech-lead.md, Teto por PR): cumpre. Contam 70 linhas (`tests/test_hooks.py` 47, `tests/apoio_volta_unica.py` 15, `tests/test_hooks_volta_corpus.py` 8); `tests/pesos-d4.json`, o fragmento de `changelog.d/` e a spec em `tests/mutantes/` ficam fora da conta. Sem `hooks/` nem caminho de `PROTEGIDOS`. Comportamento: um só (o pool); o E3 é só dado de equilíbrio, sem código, e entra aqui pela DECISÃO TÉCNICA do Jarvis de 2026-10-30 15:30 registrada no pedido.

Ferramentas: o Forge não tem `docs/engineering/praticas.md` com regras por ferramenta; a suíte do item roda no pre-push e no CI do PR. Pipeline: parecer de devops aprovado em `docs/devops/impl-n-ci.md`. Segurança (E1.3) é parecer à parte.

Riscos: mais hooks ao mesmo tempo no CI de 4 núcleos (de 2 para 4 threads); o desenho §3.1 pede olhar os 3 primeiros runs do CI depois do merge.
