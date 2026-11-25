---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-hook-decisao-aviso
commit: f2db561b4e2220f4ae8411f1f4432e3a35b813f0
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0478 (E172.30, PR #857, revalidação por delta)

Escopo: o delta saiu de `forge-check parecer delta`, no intervalo `2ecd153c..f2db561b` (E172.15). No domínio: `bin/forge-testes`, `tests/test_hooks.py` (controle) e as quatro fixtures de `tests/hooks/decisao/`. Fora do domínio: `docs/hooks-fixtures.md` (índice gerado) e `tests/pesos-d4.json`. Nenhum arquivo de `hooks/` mudou no delta, então `hooks/decisao.py` e `hooks/hooks.json` estão iguais aos da rodada anterior. Depois de f2db561b a branch só recebeu os pareceres de review e QA (`docs/reviews/`, `docs/qa/`).

Gatilhos: hook novo do plugin no `Stop`, saída ao usuário (ADR 0003, item 1), lista de hooks permitidos no Stop (invariante de teste)

## Estado dos achados anteriores
- A1 (bloqueante): corrigido. Em `tests/test_hooks.py:1546`, `decisao.py` entra só no conjunto do `Stop`. O `SessionStart` continua com `ambiente.py` e `ordens.py`. A checagem estática pedida está em `tests/test_hooks.py:1549-1551`: `decisao.py` não pode conter `additionalContext` nem `decision`. Só a frase da docstring que nega as duas chaves fica de fora.
- A2 (bloqueante): corrigido. `tests/hooks/decisao/` agora traz quatro fixtures:
  - `sem-forge-versao` (`sem_run`);
  - `erro-interno` (`erros_log`, código 0);
  - `duas-decisoes-avisa` (avisa);
  - `uma-com-recomendo-silencio` (cala; sem `saida`, o teste exige stdout vazio, `tests/test_hooks.py:898`).
  O `decisao` entrou no conjunto dos hooks que nunca bloqueiam (`tests/test_hooks.py:1531`).
- A3 (bloqueante): corrigido. O peso está em `tests/pesos-d4.json`. O mapa está em `bin/forge-testes:227`: `hooks/decisao.py` e `hooks/hooks.json` rodam `RODAM_OS_HOOKS` e `test_hook_decisao`. O CI do head passou (abaixo).

## Detalhe
**Cada mudança aperta ou é neutra (por escrito).**
- `tests/test_hooks.py:1546` (lista do Stop): **neutro**. A lista se abre só para `decisao.py`, só no `Stop`, junto com a checagem estática de A1. O hook não ganhou canal novo: usa `systemMessage`, o mesmo do `vigia`.
- `tests/test_hooks.py:859-860` (fixtures com `saida`): **aperta**. Antes só o `vigia` podia ter `saida`. Agora o `decisao` também pode, mas só no evento `Stop` e sem `reason` (nem `decision`). A regex de `:875` ainda exige o prefixo fixo `Forge decisao: `.
- `tests/test_hooks.py:1531` (conjunto que nunca bloqueia): **aperta**. Toda fixture do `decisao` tem de sair com código 0.
- `bin/forge-testes:227` (mapa dos testes tocados): **aperta**. Mudar `hooks/decisao.py` ou `hooks/hooks.json` agora roda os módulos que executam os hooks e o módulo do próprio hook. Nenhuma entrada antiga saiu.
- Fixtures: só dados de teste, sem segredo nem caminho fora de `{tmp}`.
- **Testes dos arquivos tocados** no head f2db561b, rodados aqui:
  - `python3 -m unittest tests.test_hook_decisao tests.test_hooks.Hooks.test_hooks_json tests.test_hooks.Hooks.test_cada_hook_tem_caso_que_passa_e_que_bloqueia`: 13 testes, OK (a sonda S1 da rodada anterior agora passa);
  - `-k decisao tests.test_hooks`: OK.
  O `test_hooks` inteiro passou do prazo local de 900 s e fica para o CI.
- **Suíte inteira:** CI do PR #857 no head f2db561b:
  - verdes: suíte 3.12 e 3.14 (partes 1 a 5), `instalação`, `bateria (passos)`, `bateria (verificações longas)` e `catraca`;
  - vermelho esperado: `bateria (pareceres)`, que falha só porque faltam os pareceres desta rodada.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas usadas: `forge-check parecer delta`, leitura estática, testes dos módulos tocados e checks do CI. As ferramentas de varredura de segredo e de SAST não estão no PATH deste ambiente. A lacuna fica registrada; o delta não traz credencial nem dependência.
