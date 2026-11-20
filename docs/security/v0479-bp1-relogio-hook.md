---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp1-relogio-hook
commit: ac4d6dc7325b437958cbf61505259b20d90bfe1a
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: BP1, relógio injetado no vigia de prazo (E37.16)

Escopo: `git diff ef186de8..ac4d6dc7` (8 arquivos). Controle tocado: `hooks/_comum.py` (`vigia_de_prazo`, `estender_prazo`, `executar`); o resto é teste, mutantes, `docs/hooks.md` e fragmento de changelog.

Gatilhos: hook (controle do Forge, vigia de prazo dos hooks `parecer` e `conformidade`), rótulo `afrouxa-regra` pedido sob a condição do dono de que a mudança só aperta.

## Achados
- A1 (recomendado) tests/test_hooks_volta_corpus.py:136 · O teste por AST reconhece só a chamada com o nome `executar`; `from _comum import executar as x`, `functools.partial(executar, relogio=...)` ou `getattr` escapariam. Hoje nenhum hook faz isso (10 de 10 chamadas diretas); barrar também o import com alias de `executar` nos hooks.

## Sondas

## Detalhe
Confirmação para a condição do dono: **a mudança só aperta ou mantém; nenhum hook passa a aceitar o que recusava.** Os três pontos:

1. **Relógio falso por hook real ou ambiente: não.** `relogio` e `armar` são só por palavra-chave (`hooks/_comum.py:2866-2867`), com padrão `time.monotonic` e `signal.setitimer` resolvidos na importação. Nenhuma variável de ambiente, argumento de linha ou arquivo os lê. Os dez scripts que o `hooks/hooks.json` roda (`_maquina`, `agentes`, `ambiente`, `conformidade`, `doutor`, `meta`, `parecer`, `pesado`, `quadro`, `vigia`) chamam `executar` uma vez cada, sem `relogio`, `armar` nem `**` (`hooks/parecer.py:1354`, `hooks/conformidade.py:3934` e os demais, conferidos por `grep`); o driver do lote (`tests/apoio_volta_unica.py:409-428`) repassa só `regra_do_prazo`, `clone_do_forge` e `prazo_longo`. `time` e `signal` são módulos embutidos do interpretador, então uma pasta no caminho de importação não os sombreia (igual à base). Trocar o relógio exige código no processo do hook, que já podia trocar qualquer coisa antes: superfície igual.
2. **O vigia continua falhando fechado: sim.** `PrazoVencido` (`BaseException`) e o `except PrazoVencido` → `prazo_vencido` não mudaram (`hooks/_comum.py:2890-2891`); o desarme segue no `finally` (`:2833-2835`). A condição de extensão trocou `getitimer()[0] > 0` por `armado` (`:2885`): em produção são equivalentes, porque `armado` só é `True` com o alarme armado na thread principal e, se o alarme já tivesse vencido, o `_vencer` teria lançado antes; sem `setitimer` ou fora da thread principal os dois dão "não estende", como antes. Erro levantado por `armar` cai no `except Exception` → `falhar_fechado`, como o `setitimer` de antes. A extensão continua só para cima (`PRAZO_DO_MERGE_S <= hook.prazo_s` → retorna, `:2860`) e só com a linha casando `MERGE_DE_PR`, sem mudança.
3. **Teste de AST cobre todos os chamadores: sim, nos chamadores atuais.** `tests/test_hooks_volta_corpus.py:125-146` varre `hooks/*.py` (os dez de `hooks.json` mais `_comum` e `_gh_api`, que não chamam `executar`), exige ao menos 10 chamadas e uma por hook, barra `relogio`, `armar` e `**`, confere a assinatura (palavra-chave e padrões reais) e o driver. Fora de `hooks/`, os `executar` de `bin/` e `scripts/` são funções homônimas próprias, não o de `_comum`. Lacuna (A1): reconhecimento só pelo nome; um alias passaria. Sem caminho de ataque realista (código de hook é do Forge, passa por review e por este portão), por isso recomendado.

Sondas e provas rodadas aqui (no head `ac4d6dc7`): `SondaS1ComRelogioFalso` (2 testes) e `test_hooks_reais_e_driver_nao_passam_relogio_nem_armar`: OK (3 testes, 10 s). Vigia real: `Hooks.test_prazo_do_merge`, `test_prazo_vencido_com_corpo_de_heredoc_pendente_recusa`, `test_merge_de_pr_na_duvida_fica_com_o_prazo_comum`: OK na 2.a corrida (3 testes, 51 s); a 1.a deu 1 falha com a máquina em carga 24 em 12 núcleos, não reproduzida, no caminho de carga que a própria BP1 tira da S1. Sonda do A1: o mesmo filtro do teste sobre `from _comum import executar as rodar\nrodar('x', f, relogio=lambda:0)` vê 0 chamadas. Os mutantes P7, P8 e M4 foram reescritos para o novo texto e apontam para os testes do relógio falso. A suíte inteira é do CI do PR.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Lacuna: gitleaks, osv-scanner, semgrep, zizmor e actionlint fora do PATH; o item não toca workflow nem dependência.
