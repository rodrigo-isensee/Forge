---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp1-relogio-hook
commit: b0ab26a0675cf77ba75749ca319243cc56624e9c
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: BP1, relógio injetado no vigia de prazo (E37.16)

Escopo: `git diff ef186de8..ac4d6dc7` (8 arquivos). Controle tocado: `hooks/_comum.py` (`vigia_de_prazo`, `estender_prazo`, `executar`); o resto é teste, mutantes, `docs/hooks.md` e fragmento de changelog.

Gatilhos: hook (controle do Forge, vigia de prazo dos hooks `parecer` e `conformidade`), rótulo `afrouxa-regra` pedido sob a condição do dono de que a mudança só aperta.

## Achados
- A1 (recomendado) tests/test_hooks_volta_corpus.py:136 · Resolvido em b7e2f6b5: `chamadas_do_executar` (tests/apoio_volta_unica.py:1193) resolve `from _comum import executar as X` e `import _comum [as c]` com `c.executar(...)`.
- A2 (recomendado) tests/apoio_volta_unica.py:1214 · Resolvido em b0ab26a0: `referencias_ao_executar_fora_de_chamada` acha reatribuição, getattr, importlib, atributo solto, vars e partial; hooks reais e driver com zero referências.

## Sondas

## Detalhe
Confirmação para a condição do dono: **a mudança só aperta ou mantém; nenhum hook passa a aceitar o que recusava.** Os três pontos:

1. **Relógio falso por hook real ou ambiente: não.** `relogio` e `armar` são só por palavra-chave (`hooks/_comum.py:2866-2867`), com padrão `time.monotonic` e `signal.setitimer` resolvidos na importação. Nenhuma variável de ambiente, argumento de linha ou arquivo os lê. Os dez scripts que o `hooks/hooks.json` roda (`_maquina`, `agentes`, `ambiente`, `conformidade`, `doutor`, `meta`, `parecer`, `pesado`, `quadro`, `vigia`) chamam `executar` uma vez cada, sem `relogio`, `armar` nem `**` (`hooks/parecer.py:1354`, `hooks/conformidade.py:3934` e os demais, conferidos por `grep`); o driver do lote (`tests/apoio_volta_unica.py:409-428`) repassa só `regra_do_prazo`, `clone_do_forge` e `prazo_longo`. `time` e `signal` são módulos embutidos do interpretador, então uma pasta no caminho de importação não os sombreia (igual à base). Trocar o relógio exige código no processo do hook, que já podia trocar qualquer coisa antes: superfície igual.
2. **O vigia continua falhando fechado: sim.** `PrazoVencido` (`BaseException`) e o `except PrazoVencido` → `prazo_vencido` não mudaram (`hooks/_comum.py:2890-2891`); o desarme segue no `finally` (`:2833-2835`). A condição de extensão trocou `getitimer()[0] > 0` por `armado` (`:2885`): em produção são equivalentes, porque `armado` só é `True` com o alarme armado na thread principal e, se o alarme já tivesse vencido, o `_vencer` teria lançado antes; sem `setitimer` ou fora da thread principal os dois dão "não estende", como antes. Erro levantado por `armar` cai no `except Exception` → `falhar_fechado`, como o `setitimer` de antes. A extensão continua só para cima (`PRAZO_DO_MERGE_S <= hook.prazo_s` → retorna, `:2860`) e só com a linha casando `MERGE_DE_PR`, sem mudança.
3. **Teste de AST cobre todos os chamadores: sim, nos chamadores atuais.** `tests/test_hooks_volta_corpus.py:125-146` varre `hooks/*.py` (os dez de `hooks.json` mais `_comum` e `_gh_api`, que não chamam `executar`), exige ao menos 10 chamadas e uma por hook, barra `relogio`, `armar` e `**`, confere a assinatura (palavra-chave e padrões reais) e o driver. Fora de `hooks/`, os `executar` de `bin/` e `scripts/` são funções homônimas próprias, não o de `_comum`. Lacuna (A1): reconhecimento só pelo nome; um alias passaria. Sem caminho de ataque realista (código de hook é do Forge, passa por review e por este portão), por isso recomendado.

Sondas e provas rodadas aqui (no head `ac4d6dc7`): `SondaS1ComRelogioFalso` (2 testes) e `test_hooks_reais_e_driver_nao_passam_relogio_nem_armar`: OK (3 testes, 10 s). Vigia real: `Hooks.test_prazo_do_merge`, `test_prazo_vencido_com_corpo_de_heredoc_pendente_recusa`, `test_merge_de_pr_na_duvida_fica_com_o_prazo_comum`: OK na 2.a corrida (3 testes, 51 s); a 1.a deu 1 falha com a máquina em carga 24 em 12 núcleos, não reproduzida, no caminho de carga que a própria BP1 tira da S1. Sonda do A1: o mesmo filtro do teste sobre `from _comum import executar as rodar\nrodar('x', f, relogio=lambda:0)` vê 0 chamadas. Os mutantes P7, P8 e M4 foram reescritos para o novo texto e apontam para os testes do relógio falso. A suíte inteira é do CI do PR.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Lacuna: gitleaks, osv-scanner, semgrep, zizmor e actionlint fora do PATH; o item não toca workflow nem dependência.

## Revalidação no head b7e2f6b5
Delta lido (`forge-check parecer delta`): só `tests/test_hooks_volta_corpus.py` está no domínio (o helper em `tests/apoio_volta_unica.py` e o mutante ficam fora do domínio e li o helper por ser o que o teste chama); nenhum arquivo de `hooks/`, `bin/`, `scripts/` mudou desde `ac4d6dc7`. O aviso do delta sobre o merge de 2c4af41 fora da develop é só de um merge de outra branch (documentação e parecer).

A1 corrigido: o teste agora resolve o apelido de `from _comum import executar as X` e o módulo importado, com ou sem apelido; o teste novo cobre os três casos e o negativo (`from outro import executar`).

Outras formas de escapar, sondadas com o próprio `chamadas_do_executar` (a saída é o número de chamadas achadas; o certo seria 1): reatribuição `x = r; x('a', relogio=1)` dá 0; `getattr(_comum, 'executar')(...)` dá 0; `importlib.import_module('_comum').executar(...)` dá 0; `functools.partial(executar, relogio=1)('a')` dá 0; `from _comum import *` com `executar(...)` dá 1 (pego). Nenhuma tem caminho realista: o AST é uma trava contra descuido em código de hook do Forge, que passa por review e por este portão, e nenhum hook usa `getattr`, `importlib` (só `_comum.py:2479-2491`, carregando `forge-check` e `forge-doutor`), `partial` de `executar` ou reatribuição (`grep` em `hooks/*.py`). Quem escreve hook já podia trocar o relógio no processo. Registrado como A2 recomendado, sem bloquear.

Condição do dono para o rótulo `afrouxa-regra`, reconfirmada: **a mudança só aperta ou mantém.** Desde o parecer anterior o delta é só teste que torna a trava mais estrita (reconhece mais formas de chamada); código de controle idêntico ao já revisado, relógio e `armar` seguem só por palavra-chave, sem origem em ambiente, argumento ou arquivo, e o vigia segue falhando fechado. Nenhum hook passa a aceitar o que recusava.

Prova rodada: `chamadas_do_executar` nas cinco sondas acima (saídas 0, 0, 0, 0, 1). Teste novo `test_chamada_com_apelido_do_import_e_pega_com_relogio` e o de AST dos hooks reais: OK os dois (1 teste cada, sem `-I` por causa do caminho de importação do teste). A suíte inteira é do CI do PR.

## Revalidação no head b0ab26a0
Delta lido (`forge-check parecer delta`, intervalo b7e2f6b5..b0ab26a0): só `tests/test_hooks_volta_corpus.py` no domínio; o helper `tests/apoio_volta_unica.py:1214` e o mutante ficam fora do domínio e li o helper por ser o que o teste chama. Nenhum arquivo de `hooks/`, `bin/`, `scripts/` ou `.githooks/` mudou (`git diff --stat b7e2f6b5 HEAD` vazio nesses caminhos).

A2 corrigido: `referencias_ao_executar_fora_de_chamada` marca o nome ou apelido fora de chamada direta, qualquer atributo `.executar` e a cadeia `"executar"`. O teste novo cobre as seis formas e os seis negativos, e `test_hooks_reais_e_driver_so_chamam_o_executar_direto` exige zero referências nos `hooks/*.py` e no driver.

Sondas rodadas no head (saída: referências achadas / chamadas diretas achadas): reatribuição 1/0; `getattr(_comum, 'executar')(...)` 1/0; `importlib.import_module('_comum').executar(...)` 1/0; `x = c.executar` 1/0; `functools.partial(executar, relogio=r)` 1/0; `vars(_comum)['executar'](...)` 1/0; `from _comum import *` com `x = executar` 1/0; chamada direta com `relogio=` via `import *` 0/1 (pega pelo teste de chamadas); chamada direta sem `relogio` 0/1 (sem falso positivo). Resíduo: `getattr(_comum, 'exec' + 'utar')` dá 0/0; sem caminho realista (nenhum hook usa `getattr` sobre `_comum`; código de hook é do Forge e passa por review e por este portão), nada a bloquear.
Provas rodadas: os 4 testes (`-k executar_fora -k so_chamam -k outro_nome_do_comum -k apelido`): OK, 2,6 s. A suíte inteira é do CI do PR.

Condição do dono para o rótulo `afrouxa-regra`, reconfirmada por escrito: **a mudança só aperta ou mantém.** O delta é só teste que torna a trava mais estrita (reconhece mais formas de referência ao `executar`); o código de controle é idêntico ao revisado, `relogio` e `armar` seguem só por palavra-chave sem origem em ambiente, argumento ou arquivo, e o vigia segue falhando fechado. Nenhum hook passa a aceitar o que recusava.
