---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-brief-sonda-escrita
commit: 68d498057dfd8d376cc63ac4f326b99293656adb
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-28
---
# Review de segurança: v0481 (BRIEF-SONDA-ESCRITA, #952), delta da volta 1

Gatilhos: controle do Forge (barreira de escrita do `brief selar`, R-BRIEF; analisador de brief)

Delta lido (`forge-check parecer delta`, `61ab461e..68d49805`): no domínio, só `bin/forge-check` (`pareceres_da_ref`, `sondas_do_pedido`, `sondas_conferidas`, `sem_entrada_de_sonda` com o conjunto conferido, `caminhos_do_entregar`, `conferir_escrita` e `conferir_brief` recebendo `sondas` no lugar do booleano, `avaliar_brief`). Fora do domínio: o teste, os mutantes e o fragmento. A 1ª rodada (`61ab461e`) fica no git.

## Estado dos achados anteriores
- A1 (bloqueante) · fechado. A isenção só tira da escrita a entrada cuja tripla (tipo, id, entrada) está em `sondas_do_pedido` (`bin/forge-check:4853`), que filtra `pedido == pedido_id` e `not problemas`; `sem_entrada_de_sonda` (`bin/forge-check:9077`) só corta a entrada com a tripla nesse conjunto, então a linha forjada com o prefixo de sonda deixa de sair da barreira mesmo antes de a `conferir_volta` reprovar. `sondas_conferidas` (`bin/forge-check:4859`) devolve conjunto vazio sem `Volta-de:` no formato (`VOLTA_DE`, mais estrito que o `^Volta-de:` anterior), com `--ref` que não é commit ou com erro de leitura. Teste: `tests/test_brief_sonda_escrita.py:59-86`.

Sondas rodadas no head `68d49805` (módulo descartável fora da branch, sobre o harness `SondaComCaminhoDeHook`; linha `(sonda review <sha> S7)` com `.git/hooks/pre-push` copiada do parecer `docs/reviews/outro.md`):
- S1 de novo (`pedido: outro-pedido`, `--parecer docs/reviews/outro.md`): rc=1, `escrita: barrada ".git/hooks/pre-push"`;
- `--parecer` misto (o do pedido e o de outro): rc=1, a sonda do outro pedido segue barrada;
- outro pedido sem `--parecer` (seleção padrão): rc=1, barrada;
- parecer com problema (linha de achado fora do formato): rc=1, barrada, com `volta: parecer ...: linha do bloco ## Achados fora do formato`;
- ref ilegível (`--ref nada/aqui`): rc=1, barrada, com `volta: --ref "nada/aqui" não é um commit`;
- `pedido:` forjado em variantes que não batem (maiúsculas, com sufixo, entre aspas, ausente, chave duplicada com o do pedido primeiro): rc=1, barrada;
- `Volta-de:` fora do formato: rc=1, barrada;
- `pedido:` igual ao do pedido (ou chave duplicada com o do pedido por último, que o leitor de frontmatter resolve do mesmo jeito em todo o Forge) num parecer commitado na ref: a entrada sai da escrita, como no parecer legítimo. É a confiança de projeto (o parecer na ref da entrega, em pasta de parecer que o hook `conformidade` reserva ao revisor), não regressão: quem já escreve parecer do pedido na branch não ganha nada novo, e o vetor amplo segue com a GIT-CONTROLE (v048).
- As formas já vistas barradas na 1ª rodada (id sem par, entrada trocada, tipo trocado, caminho no `espera:`, sem `--ref`, sem `Volta-de:`, linha comum com o caminho) seguem cobertas por `tests/test_brief_sonda_escrita.py:27-57`, que rodei no head (7 testes, OK).

Suíte: CI do head `68d49805` (run 46109255587): partes 1 a 5, verificações longas, passos, instalação e teto de pulados passaram; os vermelhos (`bateria`, `bateria (pareceres)`, `catraca`) são os portões de parecer (R-REVIEW e R-CONFORMIDADE pedindo os pareceres de `bin/forge-check`), que este parecer e os paralelos alimentam.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão estática e sondas locais com a biblioteca padrão; sem varredura de segredo nem de dependência (o delta não toca credencial, dependência nem workflow).
