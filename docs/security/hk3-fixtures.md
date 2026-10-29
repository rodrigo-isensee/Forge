---
tipo: revisao-seguranca
contrato: 1
pedido: hk3-fixtures
branch: melhoria/hk3-fixtures
commit: 7c4c7968fe4683837207875e80eeac40970b4dc3
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-29
---
# Review de segurança: hk3-fixtures

## Gatilhos
Controle do Forge (`R-SEGURANCA`): as três fixtures são o corpus do hook `parecer`, que barra o merge de branch sem parecer. O delta contra a develop 5ce822d é só dado de teste (7 linhas trocadas `home/wtx` por `ctx/wtx` em `tests/hooks/parecer/`) e o fragmento do changelog; nenhum arquivo de `hooks/`, `scripts/` ou workflow muda.

## Achados

## Detalhe dos achados
- Sem alteração no que o hook barra: o diff de `hooks/` contra a base é vazio, e a troca é consistente dentro de cada fixture (worktree, comando e cwd usam o mesmo `ctx/wtx`). O teste `tests.test_hooks_parecer_pasta` passa (1 teste, OK), com as três fixtures mantendo o esperado de recusa.
- `scripts/verificar-contribuicao.sh origin/develop` sai com rc=0 (nenhum segredo nem caminho pessoal no diff).
- Recomendação não bloqueante: outras fixtures `pasta-passa-*` e `pasta-barra-*` ainda usam `{tmp}/home/wtx`; hoje o verificador só lê linhas adicionadas no diff e o padrão exige `/home/<nome>/` com barra final, então só novas edições nelas voltariam a acusar. Vale neutralizá-las em lote próprio, sem urgência.
- PA-7 (`docs/engineering/achados-recorrentes.md`): conferido; nenhum item aplicável a dado de teste sem segredo, sem caminho pessoal e sem mudança de comportamento.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `verificar-contribuicao.sh` e o teste do item; gitleaks, osv-scanner e semgrep não rodados (sem superfície: só JSON de teste).
