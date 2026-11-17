---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v047-idioma-dono
commit: 8321ae381950e89c93d72fc8f2c906bb42f7c406
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v0474 (E2.3, lote IDIOMA: SIEG-G4 texto, JARVIS-SO-PORTUGUES, JARVIS-ENCERRA-RODADA)

Diff `45615e20..8321ae38`: 3 commits, 4 arquivos, 75+/1-. Conta para M14 só `tests/evals/test_erros_por_papel.py` (60 linhas), abaixo do teto de 150.

## Entregar contra os commits
- SIEG-G4 texto em `skills/falar-com-o-dono/toda-mensagem.md` e ponteiro no `SKILL.md`: commit 39e11b06.
- Eval `MensagemEmOutroIdioma` (2 travados, 1 `expectedFailure` para a nota entre ferramentas): commit ab4d715e.
- Texto JARVIS-ENCERRA-RODADA e eval `RodadaQueNaoEncerra`, todo `expectedFailure`: commit 8321ae38.
- Fragmento `changelog.d/v047-idioma-dono.md` com as três entradas. Nada pendente.

## Ferramentas citadas
- `bin/forge-check pr v047-idioma-dono`: classe C (skill `falar-com-o-dono`); review, QA e segurança pela classe. Sem linha `sem teste:`.
- Suíte inteira: roda no CI do PR (ainda sem PR); não rerrodada aqui.
- Rodados por mim: os 4 casos novos (`python3 -m unittest evals.test_erros_por_papel -k MensagemEmOutroIdioma -k RodadaQueNaoEncerra` em `tests/`): `OK (expected failures=2)`; `test_jarvis_nucleo` e `test_jarvis_n_jar_a` (leem a skill): 45 OK.
- Mutante: `idioma != dono` → `idioma == dono` em `hooks/meta.py` (`medir_mensagem`): `failures=2, unexpected successes=1`, morto. O eval trava a medida que diz travar.
- Guardas do diff: nenhuma linha de guarda em código de controle (o diff só toca texto `.md` e um arquivo de teste); sem `tests/mutantes/` a declarar.

## Leitura (regras "leitura" que alcançam o diff)
- Faz o que o pedido pede (E2.2), nem mais: a regra de idioma é uma só e cita a medida existente (`outro_idioma` do hook `meta`, `idioma_do_dono`, padrão português), conferida em `hooks/meta.py:205-231`. A regra da rodada aponta a skill `esperar-estado`, regra 6, sem duplicar o laço.
- Evals: `PAPEL = "jarvis"`, fonte citada (ORDEM DO DONO 16/11 21:36), o que a ferramenta já barra é teste comum e o que não barra é `expectedFailure`, como manda a docstring do módulo. O subprocesso limpa o ambiente e chama Python com `-I`. O falso de hook devolve `run()` numa pasta temporária e `raiz=None`, que cai no padrão português: mesma regra do script, não mais frouxa.
- Módulo existente ou novo: o lugar certo é o arquivo existente, mas pelo contrato dele ("cada erro real de um papel ... vira um caso executável aqui", linha 1), não pela contagem: o `forge-placar` (`evals_por_papel`) lê por AST todo `tests/evals/test_*.py`, então um módulo novo também seria contado. Ver A1.
- `R-NEUTRO`: nenhum nome de projeto; o idioma vem do config do projeto. Segurança: só texto e teste, sem comando montado a partir de entrada (o parecer é do `security-engineer`, `R-SEGURANCA`).

## Achados
- A1 (recomendado) tests/evals/test_erros_por_papel.py:184 · o motivo dado para o arquivo existente (contagem do forge-placar) não se sustenta: evals_por_papel conta todo tests/evals/test_*.py; a escolha vale pelo contrato da docstring do módulo. Só registro, nada a mudar.
- A2 (recomendado) tests/evals/test_erros_por_papel.py:238 · o expectedFailure falha hoje porque o subcomando `transcricao fila` não existe (argparse, código 2); o teste já fixa nome e saída ("acima de 10 min: 1"). Quem fizer a medida segue essa interface ou a ajusta na mesma entrega, ao tirar o decorador.
- A3 (recomendado) skills/falar-com-o-dono/toda-mensagem.md:9 · os dois parágrafos novos têm quebra de linha fixa, e o parágrafo anterior do arquivo está numa linha só; alinhar o formato numa próxima edição do arquivo.

## Sondas

## Parecer
Aprovado no head 8321ae38. Entrega completa, um comportamento (texto da skill mais os evals que o medem), dentro do teto M14, evals que passam como declarado e mutante da medida morto. Os três achados são recomendados e não devolvem (`R-REVIEW`).
