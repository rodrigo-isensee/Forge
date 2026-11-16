---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-fixture-pid-sandbox
commit: 32f1628aae7bffa63a590a218b88c18ed4c73738
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: v047 · fixtures de pid puladas fora do CI (E1.109, deltas E1.123 e E1.149)

## Gatilhos
Toca guarda de teste (R-SEGURANCA): um pulo novo de teste que pode enfraquecer a prova do registro de pid e sessão do hook. O hook (`hooks/agentes.py`) não muda; só `tests/test_hooks.py`, o mutante `tests/mutantes/v047-fixture-pid-sandbox.json` e o fragmento de changelog.

Conclusão: o pulo só vale com o namespace de pid do pai ilegível E sem `CI` nem `GITHUB_ACTIONS` (`tests/test_hooks.py:739` e `:718`, via `sinais_de_ci()`, que junta o ambiente da carga e o de agora). No CI o motivo vira `None` e as 4 fixtures rodam; num CI com leitura quebrada elas reprovam, não pulam. O pulo é conservador: sonda legível com hook ilegível reprova, nunca pula. Os pulos reais saem como `subTest` com motivo, sem `exigir`, e por isso não inflam o contador do `teto_pulados`, que só vale para o CI, onde nada pula.

## Delta E1.123 (b47610cc..b645e83c)
Domínio: `bin/forge-testes` e `tests/test_hooks.py`. (1) O pulo virou função do módulo `pular_sem_ns_de_pid(teste, casos, motivo)` (`tests/test_hooks.py:678`), mesmo corpo; a chamada em `executar_em_lote` mantém `None if sinais_de_ci() else sem_ns_de_pid_do_pai()`, então o pulo continua só com ns ilegível e nunca com CI; sem motivo nada pula. Nenhuma outra referência a `self.pular_sem_ns_de_pid` resta. (2) `JUNTO_DO_MODULO` (`bin/forge-testes`) só amplia a lista de módulos que rodam ao pedir `tests/test_hooks.py` (mais testes, nunca menos); as demais entradas seguem `sorted` do próprio módulo; sem entrada de entrada externa em shell nem caminho novo de execução. Nenhum afrouxamento de guarda. A1 e A2 seguem recomendados e inalterados (o delta não os agrava).
Rodados: os 2 testes novos (OK, skipped=1 pela sonda ilegível do sandbox); suíte inteira no CI do PR 547 (rascunho).

## Delta E1.149 (b645e83c..32f1628a)
Domínio: só `tests/test_fechar.py` e `tests/test_prepush_so_docs.py`; nenhum hook, script, workflow ou guarda de produção muda. (1) `tests/test_fechar.py:945-946`: a parada passa a ser procurada na última linha `[err]` antes do `fim:` em vez de numa das três últimas; continua exigindo "parou no passo 1" e o `fim: código 1` na última linha (mesma força, sem depender da ordem entre stdout e stderr). (2) `tests/test_prepush_so_docs.py:520-542`: a espera por arquivo na pasta da fila virou leitura do stderr até a linha inteira do primeiro aviso, com teto de 20 s e `killpg` do grupo (o processo nasce com `start_new_session=True`, `:385`), sem `shell` nem entrada externa; o texto lido é somado ao do `communicate` e as asserções de ordem e de contagem seguem iguais. Nenhum afrouxamento de guarda nem pulo novo. A1 e A2 seguem recomendados e inalterados.
Rodados: os 2 testes alterados (OK); suíte inteira no CI do PR 547 (verde no código, conforme o brief).

## Correção E1.152
Só o `commit:` muda: passa ao Revisar-sha 32f1628a (head de código); 8fa244a6 e edac705c são commits só de parecer. `forge-check parecer delta` de 8fa244a6..edac705c: nenhum arquivo do domínio mudou. Veredito da E1.149 mantido.

## Achados
- A1 (recomendado) tests/test_hooks.py:739 · nenhum teste distingue o ramo de CI do pulo: com sonda ilegível e CI definido, `test_fixtures` pula 4 no mutante e reprova no original, mas só num ambiente ilegível, que o CI não é; num CI legível o mutante é equivalente.
- A2 (recomendado) tests/mutantes/v047-fixture-pid-sandbox.json:5 · só há o mutante M1 do hook (morre só no CI, aceito no brief); faltam mutantes da guarda de CI (linhas 718 e 739) e da lista FIXTURES_DE_PID_E_SESSAO.

## Sondas

## Detalhe dos achados
A1. Evidência: mutante de `if motivo and not sinais_de_ci():` para `if motivo:` (linha 718), rodado com `CI=true` no sandbox (ns de pid ilegível): original `FAILED (failures=4)`; mutante `OK (skipped=1)`. O mutante só é detectável com a sonda ilegível e CI definido. Caminho de ataque: nenhum realista (o CI é do workflow; exigiria alterar a guarda ou o workflow, que passam por review); risco é regressão silenciosa futura que pule as 4 fixtures no CI. Severidade baixa. Correção mínima: um teste que passa CI definido (patch do ambiente) e sonda ilegível injetada, e afirma que `pular_sem_ns_de_pid` não é chamado com motivo e que `executar_em_lote` não pula. Esforço P. Dono: qa-engineer.
A2. Mesma lacuna, pelo lado do mutante. Esforço P. Dono: qa-engineer.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Lacuna: o M1 só morre no CI (decisão do brief). A suíte inteira não foi rodada local (diretriz de carga); roda no CI do PR. Rodados: os 2 testes novos (sem CI: OK, skipped=1) e dois mutantes manuais de guarda (descartados; árvore restaurada).
