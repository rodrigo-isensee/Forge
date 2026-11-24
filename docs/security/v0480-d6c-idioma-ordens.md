---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-d6c-idioma-ordens
commit: 0c7e8f0c09c3347f8f0e32cf02635ebb2fee359e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0478 (E174.15, revalidação por delta do PR #866)

Segunda rodada, por delta. A rodada anterior (E174.8, `748f2975`, reprovado por A1) fica no git.

Gatilhos: hook que injeta contexto a cada fala do dono (`hooks/ordens.py`), leitura de arquivo de configuração do projeto.

## Delta lido
`forge-check parecer delta` e `git diff 748f2975..0c7e8f0c`: no código, só `hooks/ordens.py:78` (o except passa a pegar `RecursionError`); nos testes, um caso aninhado em `test_idioma_torto_sai_none_sem_erro` (`tests/test_hooks.py:4091-4092`), a fixture `tests/hooks/ordens/idioma-config-aninhada-no-forge-ordens-seguem.json` e o mutante M8 (M2 e M3 só reescritos para a linha nova); o resto é o índice de fixtures e os pareceres de review e QA. Nada em controle do Forge além do hook.

## Achados anteriores
- A1 (bloqueante, rodada E174.8): **corrigido**. `hooks/ordens.py:78` pega `RecursionError`; a sonda S1, rodada de novo, dá no head a linha fixa sem idioma e as ordens, sem erros.log; em `748f2975` reproduz o defeito; na base `aabc476c`, as ordens. O mutante M8 (tirar `RecursionError`) volta a levantar o erro em `idioma_do_dono`, e o caso novo do teste o mata.

## Sondas
- S1 · clone do Forge com ordens-em-vigor.md, config.json da raiz = '[' * 20000 + ']' * 20000, UserPromptSubmit · espera: linha fixa sem idioma e as ordens · obtido: 0c7e8f0c dá as ordens, código 0, sem erros.log; 748f2975 cala com RecursionError; aabc476c dá as ordens

## Só aperta ou neutro, por escrito
O item fica **neutro**: a linha fixa só ganha texto da fábrica (um dos três nomes de `IDIOMAS`), nunca texto da config, e nenhuma config torta conhecida cala mais as ordens no clone do Forge. A correção do delta só aperta (fecha o A1) e não abre caminho novo: o except ganha só `RecursionError`, e o retorno segue `None` (linha sem idioma). `json.loads` sobre `str` só levanta `ValueError` (inclui a decodificação) ou `RecursionError`; `OSError` cobre a leitura.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum.
Ferramentas: leitura do delta; sondas em arquivo pelo Write, fora do repositório (hooks extraídos por `git archive`). No head: `python3 -m unittest tests.test_hooks.OrdensEmVigor`, 23 testes OK. A suíte inteira roda só no CI: `gh pr checks 866` não trouxe checagem na hora deste parecer, e o CI verde do PR segue obrigatório para o merge.
