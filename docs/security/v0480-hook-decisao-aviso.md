---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-hook-decisao-aviso
commit: 2ecd153cf6433fab911a286b4fb5bf19ede4cde6
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0478 (E172.12, PR #857)

Escopo: diff `5f1c6e97..2ecd153c` (E172.6): `hooks/decisao.py`, `hooks/hooks.json`, `tests/test_hook_decisao.py`, mutantes, `docs/hooks.md`, índice e fragmento do changelog.

## Gatilhos
Gatilhos: hook novo do plugin (código que roda em todo projeto no `Stop`), saída ao usuário (ADR 0003, item 1)

## Achados
- A1 (bloqueante) tests/test_hooks.py:1545 · A lista de hooks permitidos no Stop não traz decisao.py: test_hooks_json falha (CI e local, S1). Acrescente decisao.py só no Stop (nunca SessionStart nem UserPromptSubmit) e uma checagem estática de que decisao.py não contém additionalContext nem decision.
- A2 (bloqueante) tests/test_hooks.py:1530 · Faltam as fixtures tests/hooks/decisao/ (ADR 0003, item 8): sem-forge-versao, erro-interno, um caso que avisa e um que cala, todos com código 0; e decisao entra no conjunto dos que nunca bloqueiam (vigia, doutor, ambiente, ordens). Falha em S1.
- A3 (bloqueante) tests/test_forge.py:7313 · CI vermelho fora do domínio de segurança: módulo test_hook_decisao sem peso em tests/pesos-d4.json, e tests/test_testes_tocados.py:488 sem o mapa de hooks/decisao.py e hooks/hooks.json para o módulo. Sem CI verde não há aprovação (R-SEGURANCA).

## Sondas
- S1 · python3 -m unittest tests.test_hooks.Hooks.test_hooks_json tests.test_hooks.Hooks.test_cada_hook_tem_caso_que_passa_e_que_bloqueia (no head 2ecd153c) · espera: OK · obtido: FAILED (failures=2), decisao.py fora da lista do Stop e sem fixtures

## Detalhe dos achados
**Conclusão por escrito sobre o hook em si: neutro.** Não afrouxa nenhum portão e não cria caminho novo de saída ao modelo; a reprovação é só pelo que falta para o PR ficar verde (A1 a A3), não por defeito no comportamento.

- **Nunca bloqueia.** `executar("decisao", principal)` sem `critico` nem `regra_do_prazo` (`hooks/decisao.py:44`; `hooks/_comum.py:2891-2911`): toda saída é código 0, inclusive em erro interno. Não há `stop_hook_active` nem `decision`, então não há laço no Stop.
- **Só ao usuário, texto fixo.** A única escrita no stdout é `{"systemMessage": AVISO}` com a constante de `hooks/decisao.py:20-21`; nada da mensagem do Jarvis volta ecoado (sem injeção de texto livre no aviso). `systemMessage` no Stop é o mesmo canal do `vigia` e do `doutor`, não contexto do modelo: compatível com o item 1 da ADR 0003 sem emenda. O teste `assertAvisa` (`tests/test_hook_decisao.py:48-54`) prova a chave única, uma linha e até 200 caracteres.
- **Não grava.** Nenhuma escrita além do `erros.log` do `executar` em erro interno (ADR 0003, item 4); `assertCala` confere que o silêncio não cria o log.
- **Escopo.** Só `Stop`, só projeto do Forge ou clone (`hooks/decisao.py:33-36`), só a sessão com `agent_type` do papel `jarvis` (`hooks/vigia.py:545-548`); sessão sem `agent_type` cala (teste próprio).
- **Tempo e tamanho.** Leitura de até 20.000 caracteres (`hooks/decisao.py:29`); o fallback do transcrito lê até 4 MiB do fim (`hooks/meta.py:42`, `:133-141`). `grupos_de_opcoes` é quadrático no número de grupos (`bin/forge_transcricao.py:301`), mas, dentro do teto, o pior caso medido foi 0,54 s (texto `A)\nB)\n` repetido; 0,27 s com perguntas; linha de 100 mil caracteres e 20 mil espaços: 0,000 s), longe do prazo de 10 s (`hooks/hooks.json`, timeout 10). `RE_OPCAO` não tem quantificadores aninhados ambíguos. Se o prazo vencer, o Claude Code encerra o hook sem bloquear.
- **Import.** `sys.path.insert` usa `PLUGIN` derivado de `__file__` (`hooks/_comum.py:28`), não do ambiente; `bin/` não tem módulo com nome da biblioteca padrão; o hook roda com `python3 -s -E`.
- **Correção de A1 a A3:** dono `developer` (o mesmo autor de E172.6); esforço P. A1 aumenta a lista do Stop, que é invariante de teste: é neutro porque o hook só usa `systemMessage`, desde que venha com a checagem estática pedida (como a do `meta` em `tests/test_hooks.py:1547`). Na volta, revalido só o delta.
- **Testes dos arquivos tocados:** `python3 -m unittest tests.test_hook_decisao` no head: 11 testes, OK. Suíte inteira: CI do PR #857 no head 2ecd153c vermelho (suíte 3.12 e 3.14 partes 1 e 3, bateria); `bateria (pareceres)` falha só pela falta dos pareceres, esperado nesta etapa.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, sonda de tempo local (arquivo próprio, só a função `viola`), testes do módulo tocado e anotações do CI. As ferramentas de varredura de segredo e SAST não estão no PATH deste ambiente (lacuna registrada; o diff não traz credencial nem dependência).
