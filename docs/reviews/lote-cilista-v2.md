---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/lote-cilista-v2
commit: 0ad1ad79e463bd2afd6dcc163f40ca6d4e692ae5
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Review: lote-cilista-v2

Escopo: retomada do LOTE-CILISTA (CI-LINT-LISTA-ABERTA) sobre a develop, pedido versao-033. Lido: `git diff origin/develop...HEAD` inteiro (`tests/test_ci_local.py` +224/-13, `changelog.d/lote-cilista-v2.md`) e os três pareceres reprovados de `origin/melhoria/lote-cilista` (review 79fb816, QA e segurança). Rodada 2 (confirmação do A1): delta lido `git diff 82471d2 6f7a9d1`, só `tests/test_ci_local.py` (:75, :97 e as 6 variantes novas em :371-377). Já lido na rodada 1 (59d034c), sem mudança: o resto do arquivo e o fragmento. Rodada 3: delta lido `git diff 6f7a9d1 0ad1ad7` em `tests/test_ci_local.py` (:38-39, :59, :66-67, :77, :93-101, :129-130 e 8 variantes em :384-391); os pareceres de QA e de segurança do delta não são meus e não os refaço.

## Achados
- A1 (recomendado) tests/test_ci_local.py:75 · fechado em 6f7a9d1 (era bloqueante): defeito provado e segurança com gatilho: `env` de passo com as chaves em recuo diferente de 10 não é lido; `env:` e `PATH: ./scripts:/usr/bin:/bin` (ou `LD_PRELOAD`) em recuo 12 no download dá lista vazia, e o `curl` roda da branch antes do lint
- A2 (recomendado) tests/test_ci_local.py:111 · o env do gate é conferido só pelas chaves, não pelos valores; hoje os valores são expressões `${{ }}` sem efeito no shell, então não devolve; se quiser, comparar chave e valor como pediu o A5 da segurança
- A3 (recomendado) tests/test_ci_local.py:1 · fechado na rodada 3: o diff de código e teste em 0ad1ad7 tem 258 linhas (245+13), e a linha `teto: excedido` do corpo do PR foi corrigida para 258
- A4 (recomendado) tests/test_ci_local.py:39 · `ANCORA_OU_ALIAS` roda no arquivo inteiro, incluindo o corpo dos `run`; um `- *x` ou `, &x` num script novo do CI reprova o teste sem âncora YAML. Falha fechada, não devolve; se acontecer, o erro já diz a causa

## Detalhe do A1
Sonda em `/tmp/claude-0/-workspaces/b37d1e9f-be92-464b-b166-7229b98dd0fa/scratchpad/tl-cilista/sonda.py`, sobre o `ci.yml` real com uma alteração cada, chamando `passos_antes_do_lint_fora_da_lista`: `env:\n            PATH: ./scripts:/usr/bin:/bin` antes do `run` do download resulta em `[]`; idem `LD_PRELOAD: ./bin/x.so`. O laço de `passos_da_bateria` só registra chave de env em `recuo == 10` (:75); em recuo 12 nenhum ramo casa e o passo sai com `env == set()`, igual ao esperado para o download e para os setups. YAML aceita qualquer recuo maior que o da chave-mãe no mapa em bloco, então a forma é válida (sem parser YAML no ambiente para executar; a leitura é pela especificação). É a mesma classe do A4 do review e do A1 do QA anteriores (a trava lê uma forma só da sintaxe), agora pela indentação. O gate e o job não têm o furo: com as chaves fora do recuo lido, o conjunto fica vazio e difere do esperado. Correção mínima: com `em_env`, toda linha de recuo maior que 8 conta como chave (ou recuo diferente de 10 reprova), e somar os subcasos "download com env em recuo 12" e "setup com env em recuo 12" à tabela `variantes`.

## Bloqueantes dos pareceres reprovados (volta 1)
- Review A4 (regex ancorado, sem aspas, sem fluxo): **fechado**. `ENV_QUE_EXECUTA` sem âncora, com aspas e fluxo; subcasos "gate com env inline", "chave BASH_ENV entre aspas", "defaults entre aspas no job", "env no topo do workflow".
- QA A1 (env não conferido): **fechado nas formas listadas** (inline, aspas, PATH, GIT_EXTERNAL_DIFF, LD_PRELOAD no gate; env do job), com lista positiva por passo e por job; **aberto na forma de recuo**, que é o A1 deste parecer.
- Segurança A5 (env por lista negativa): mesma situação do QA A1. Sonda P2h (`BASH_FUNC_git%%` no gate) agora reprova.
- Recomendados: Segurança A6 fechado (`CHAVES_DO_LINT`); Review A6 ajustado (comentário diz "ao menos um item"); Review A5 e QA A2 não feitos, aceitos (A2 é por desenho, como os três pareceres já registraram).

## Revalidação do A1 (rodada 2)
**Fechado.** `passos_da_bateria` conta como chave do env toda linha de recuo maior que 8 (:75), e `env_do_job` toda linha de recuo maior que 4 (:97), pulando comentário. A sonda da rodada 1, rodada de novo sem mudança, agora reprova: download com `PATH` e com `LD_PRELOAD` em recuo 12 dão `['Baixa actionlint ...']`. As 6 variantes novas cobrem recuo 12, 14 e misto no download, setup e gate em recuo 12 e o job em recuo 8. Efeito colateral lido: valor em bloco (`X: |` com linhas abaixo) ou mapa aninhado no env passa a contar linhas como chave e reprova; é mais estrito, e o `ci.yml` atual não tem essa forma (teste do arquivo real verde). `env:` seguido de fluxo na linha de baixo vira chave `{...` e reprova.

## Revalidação da rodada 3
O delta é correto e legível. Âncora, alias, merge YAML e tab no recuo reprovam antes da leitura por linha (:129-130), o que fecha em falha a classe "forma que o leitor não segue" sem modelar o YAML. Comentário deixa de decidir recuo e fim de bloco nos dois leitores (:59, :66-67, :93-94). As 8 variantes cobrem cada caminho novo. A sonda das rodadas 1 e 2, rodada de novo sem mudança, segue reprovando o download com env em recuo 12. O `ci.yml` real segue com a lista vazia.

## Teto M14
258 linhas em 0ad1ad7 (245+13; eram 237 na rodada 1 e 244 na 2), todas em `tests/test_ci_local.py`; não toca `hooks/` nem `PROTEGIDOS`; corpo do PR corrigido para `teto: excedido, 258 linhas, ...`. **Exceção aceita**: um comportamento só (a trava de ordem do lint), só teste, e dividir deixaria a develop com uma trava que os próprios pareceres provaram furada na forma parcial (a lista e o leitor do env só fazem sentido juntos). A correção do A1 deve caber em poucas linhas e não muda a conta.

## Parecer
**Aprovado** na rodada 3 sobre 0ad1ad7: o delta não trouxe bloqueante (rodada 2 aprovada; na rodada 1, reprovado por A1). O resto está correto e legível: a lista fechada, o hash do `run` e a lista positiva do env são o desenho que os pareceres pediram; o comentário das constantes explica o custo de manutenção do hash. Commit 59d034c em Conventional Commits em português, com o motivo no corpo; fragmento em `changelog.d/` presente. `R-NEUTRO` e `R-CUSTO`: sem termo de projeto nem serviço pago. Sem `docs/engineering/praticas.md`, sem regra "ferramenta" a citar. Achados recorrentes: a classe do A1 é vizinha da AR-3 (trava de ambiente), registro fica para quem fechar o pedido.

Teste dos arquivos tocados: `python3 -I -m unittest discover -s tests -p test_ci_local.py` → `Ran 53 tests ... OK` no 0ad1ad7 (os testes do head 59221aa são iguais), e antes no 6f7a9d1 e no 59d034c. Suíte inteira não rodada (D-5).
