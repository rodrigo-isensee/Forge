---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-ordens-hook
commit: cf679683033698c8ca97f8ec587c008c00cd0a9f
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0478 (E123.7, revalidação do hook ordens)

Revalidação pelo delta (H3, `R-REVIEW`): `forge-check parecer delta docs/reviews/v0480-ordens-hook.md`, intervalo `c63e96158..cf679683`, sem o que veio da `develop`; 15 arquivos no domínio, lidos só no delta. Parecer anterior: reprovado em `c63e9615` (gravado no commit `dc2554ec`).

## Delta lido
- A1 (bloqueante, resolvido): `templates/projeto/.forge/ordens-em-vigor.md` apagado; `test_o_modelo_de_projeto_nao_traz_o_arquivo_de_ordens` afirma a ausência e confere que a pasta existe (`config.json`), então não passa por pasta errada. A emenda (item 1) passa a dizer que o modelo não traz o arquivo e que o Jarvis o cria na 1.ª ordem.
- A2 (recomendado, resolvido): a seção "Afrouxa" da emenda da ADR 0003 lista o ramo `contexto` do laço das fixtures; o texto bate com `tests/test_hooks.py:891-895` (só o `ordens`, linha fixa primeiro, igual ao esperado).
- A3 (recomendado, resolvido): `hooks/ordens.py:63` `sem_controle` por `groupby` junta cada sequência de controle num espaço; `test_sequencia_de_controles_vira_um_espaco_so` (`a\t\x1b b` dá `a b`) e o mutante M20.
- Também no delta (A1 e A2 da segurança E123.3, cujo mérito é do `security-engineer`): fonte do projeto pela cópia principal (`diretorio_comum`), base `docs/kanban/` no Forge e o arquivo de ordens no `CAMINHOS_DO_CONTROLE` e no `CONTROLE_NO_TEXTO`, com 8 fixtures (7 bloqueiam, 1 libera o jarvis) e os mutantes M15 a M19. Cito, sem refazer.
- Nenhum teste afrouxado: as únicas linhas de teste removidas são as 3 de `test_fonte_do_projeto_e_do_clone_do_forge`, trocadas pela nova assinatura (`fontes` devolve lista) e pela base `contrib/docs/kanban`, que é mais estrita. O `setUp` ganha `.git` para a cópia principal. `tests/config.json` intocado.

## Provas
- `python3 -s -E -m unittest tests.test_hooks.OrdensEmVigor` (ambiente limpo por `env -i`): `Ran 21 tests in 3.175s OK`.
- As 10 fixtures de `tests/hooks/ordens` pelo `executar_em_lote`: `Ran 1 test in 1.388s OK` (10 fixtures), com o `sem_controle` novo.
- `bin/forge-mutante --ids M20 tests/mutantes/v0480-ordens-hook-3.json`: `M20 · morreu · hooks/ordens.py:65`.
- Suíte inteira: fica no CI do PR (não rerrodada).

## Parecer
Aprovado: os três achados de `c63e9615` foram resolvidos no delta, cada um com teste de comportamento, e nenhum teste foi afrouxado. Os dois pontos abertos pelo autor viram cartão depois do merge, sem bloquear: a remoção da pasta mãe, que já acontecia na base, e a mediana de 106 ms, quase toda gasta na carga do interpretador.
