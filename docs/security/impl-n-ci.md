---
tipo: revisao-seguranca
contrato: 1
pedido: impl-n-ci
branch: melhoria/impl-n-ci-c1
commit: 9ad6be5f52333f8f7d8149f4eb28ec8c7b9f54ae
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-31
---
# Review de segurança: IMPL-N-CI, branch c1 (E1.3, rodada 1)

Diff lido: `234dbe0..9ad6be5`. Revisão estática e local, em paralelo ao code review, contra o modelo de ameaças `docs/security/ameacas/n-ci.md` (C-1 a C-5, C-13 a C-15, AB-8 a AB-11).

**O que a branch entrega:** o E1 do pedido (item 55 b, o pool de threads dos fixtures e do corpus por subprocesso, numa fonte só) e o E3 (os pesos de `tests/pesos-d4.json` regravados, depois do E1), na divisão decidida pelo Jarvis em 2026-10-30 15:30 e 15:39.

**M14 (`agents/tech-lead.md:19`):** cumpre. Contam `tests/*.py`: `tests/apoio_volta_unica.py` 15, `tests/test_hooks.py` 47, `tests/test_hooks_volta_corpus.py` 8, total 70 linhas, abaixo de 150, sem exceção de teto. Ficam fora `tests/pesos-d4.json` (dado, não é `tests/*.py` nem `tests/config.json`), `tests/mutantes/`, `changelog.d/` e os pareceres. A branch não toca `hooks/` nem caminho de `PROTEGIDOS`. Comportamento, um só: o tamanho do pool. Os pesos são só dados de equilíbrio da divisão, sem comportamento novo, e o desenho os põe depois do E1.

## Gatilhos
Controles do Forge (`R-SEGURANCA`): o pool dimensiona os testes dos hooks, e o limite de CPU do corpus é um limite decidido pelo dono (PROP-TEMPO-CPU). Os pesos alimentam a divisão da suíte, que decide o veredito do portão no pre-push e no CI.

## Achados
- A1 (recomendado) tests/test_hooks.py:1993 · A guarda de fonte única só reconhece a grafia `cpu_count() or 2) // 2`. Um pool novo com outra conta escapa, como o de `tests/apoio_volta_unica.py:1061` (já na base, fora do C-1). Sugestão: procurar `ThreadPoolExecutor(max_workers=` fora da função.

## Detalhe dos achados
**O que foi conferido.**
- *C-1, AB-8 (uma fonte, entre 2 e 4, sem `FORGE_NPROC`).* `nucleos_do_processo` (`tests/test_hooks.py:521`) lê `os.sched_getaffinity(0)` e recua para `os.cpu_count()`; em `OSError` devolve `None`. Não lê o ambiente. `trabalhadores_do_pool` (`:530`) devolve 2 para `None`, `bool`, não inteiro, zero e negativo, e limita a 4 por cima: nenhuma entrada passa do teto de 4 (`R-TETO`). As 4 contas da base (`tests/test_hooks.py:592`, `tests/test_hooks_volta_corpus.py:75`, `tests/apoio_volta_unica.py:422` e `:530`) usam a função. `test_pool_por_nucleos_e_limites` cobre 1, 2, 4, 16, `None`, 0, -3 e `"x"`. `test_pool_le_a_afinidade_e_ignora_o_forge_nproc` usa `FORGE_NPROC=64` com afinidade 2 e confere 2, ou seja, a variável é ignorada.
- *C-3, AB-9 (o limite de CPU não acompanha o pool).* `trabalhadores_do_limite_de_cpu` (`tests/apoio_volta_unica.py:40`) mantém a conta de antes, `max(1, min(4, nproc // 2))`, e `limite_de_cpu_do_corpus` continua `90 ×` esse valor. Subir o pool para 4 num runner de 4 núcleos não sobe o limite (continua 180 s). `tests/test_medida_cpu.py` não está no diff: a tabela da contraprova está intacta. O mutante M4 (`tests/mutantes/prop-tempo-cpu.json:39`) acompanhou o nome novo, então continua aplicável. A asserção do corpus (`tests/test_hooks_volta_corpus.py:115`-`116`) usa o divisor do limite, não o pool.
- *C-2, C-4 (série e prazos).* O critério de série dos fixtures não muda. O diff não cria espera nova sem prazo: só muda o `max_workers` de pools que já existiam. Não há retentativa nova nem `timeout-minutes` (nenhum workflow no diff).
- *C-13, AB-11 (pesos).* O commit `5e01e83` toca só `tests/pesos-d4.json`. Conferido no `9ad6be5`: 79 chaves, iguais aos 79 módulos `tests/test_*.py` vivos (nenhuma chave órfã, nenhum módulo sem peso), todos os valores finitos e ≥ 0 (o maior é `test_hooks`, 218,3). Peso adulterado só desequilibra: a guarda de completude compara com a descoberta inteira e não usa os pesos. Que a medição saiu de árvore limpa e suíte verde é evidência do autor, não refeita aqui.
- *C-15.* O `bin/forge-testes` não tem regra para `tests/pesos-d4.json`, então o push roda a suíte inteira.
- *C-5 (3 rodadas com pool 4, falhas novas no PR).* É evidência do corpo do PR, conferida no merge. Não está neste diff.
- *Segredos, rede, custo (`R-CUSTO`).* O diff não traz rede, segredo nem dependência nova.

**A1 em prosa.** Evidência: `tests/test_hooks.py:1993`. Caminho: não há ataque. É deriva: um autor futuro escreve um pool com `min(8, ...)` ou outra grafia, e a guarda de fonte única não vê. O risco é carga acima do `R-TETO` nos testes, não fuga do portão. Severidade: informativa. Correção mínima: a guarda passa a procurar `ThreadPoolExecutor(max_workers=` cujo argumento não seja `trabalhadores_do_pool(`, com uma lista explícita de exceções justificadas (hoje, só `tests/apoio_volta_unica.py:1061`, o pool do `bash` com prazo de 30 s). Esforço: P. Dono: tech-lead, num lote futuro.

**Evidência própria em 9ad6be5 (árvore limpa):** `python3 -m unittest tests.test_hooks.PoolDosFixtures tests.test_medida_cpu`: `Ran 8 tests in 2.748s`, `OK`. Os pesos foram conferidos por um script local que lê o JSON do commit e compara com `git ls-tree` de `tests/`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do diff e do modelo de ameaças, os testes acima e a conferência dos pesos. Ausentes no PATH, nada instalado (`R-CUSTO`): `gitleaks`, `zizmor`, `actionlint`, `semgrep`, `osv-scanner`, `trivy`. O diff não muda workflow, dependência nem shell.
