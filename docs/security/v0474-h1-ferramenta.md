---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0474-h1-ferramenta
commit: 7924b25bd1fc5dbd50213c6cf303cbfce774a365
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v0474 (E2.35, revalidação do H1 no forge-check)

Volta por delta: `forge-check parecer delta docs/security/v0474-h1-ferramenta.md`, intervalo `4ddaa68b..7924b25b`. No domínio: bin/forge-check (`tamanho_do_pr`) e bin/forge_tamanho.py (`tem_motivo`, `falta_de_motivo`); fora do domínio: specs de mutantes e tests/test_forge_tamanho.py. A rodada anterior (head 4ddaa68b) fica no git e não é recopiada; o que ela conferiu e o delta não tocou (subprocesso do `gh` sem shell, falha fechada do módulo, catraca do CI) continua valendo.

## Gatilhos
Gatilhos: controle do Forge (bin/forge-check pr), entrada externa (corpo do PR lido do gh), subprocesso de rede.

## Conferência do delta
- A2 resolvido: `tamanho_do_pr` só confere o corpo com `state == "OPEN"` (bin/forge-check:1428); o `state` já vinha no `--json` do `gh pr view` (bin/forge-check:8466) e é convertido em `str` (bin/forge-check:8476). Sem PR (`{}`), fechado ou mesclado, só o aviso, coerente com a decisão do dono H1.
- A1 resolvido: `tem_motivo(corpo, total)` exige `int(<n>) >= total` em alguma linha de motivo (bin/forge_tamanho.py:39), e `falta_de_motivo` passa o total medido (bin/forge_tamanho.py:44). O padrão `total=0` só serve a quem chama sem total; o único chamador do controle passa o total.
- Regex sem mudança (bin/forge_tamanho.py:13); `finditer` sobre 20 mil linhas de motivo hostis em 0,07 s.
- Nada afrouxou: o delta não toca `.github/`, `.githooks/` nem `tests/config.json`; mutantes M13, M21, M22 (e M17 no `finditer`) cobrem a troca de `>=`, o `state` e o laço.

## Achados
- A1 (recomendado) bin/forge_tamanho.py:13 · resolvido em 7924b25b: o <n> da linha de motivo agora cobre o total medido (bin/forge_tamanho.py:39).
- A2 (recomendado) bin/forge-check:1428 · resolvido em 7924b25b: só o PR com state OPEN tem o corpo conferido.
- A3 (recomendado) bin/forge_tamanho.py:39 · `int()` de um <n> com mais de 4300 dígitos levanta ValueError (limite de conversão da linguagem) e o `forge-check pr` cai com traceback em vez da violação; falha fechada, sem desvio. Limitar `\d{1,9}` ou capturar o erro.

## Sondas

## Detalhe dos achados
A3: evidência bin/forge_tamanho.py:13 (`(\d+)`) e :39 (`int(m.group(1))`); sonda local: `tem_motivo('teto: excedido, ' + '9'*5000 + ' linhas, x', 160)` levanta ValueError. Caminho: quem escreve o corpo do PR (o próprio time) põe um número enorme; ganho: nenhum, o controle quebra em vez de liberar (o `pr` sai com erro, não aprova). Severidade informativa. Correção mínima: `(\d{1,9})` na regex ou `try/except ValueError` tratando a linha como sem motivo. Esforço P. Dono: o autor do item.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Teste rodado: `python3 -m unittest tests.test_forge_tamanho` (23 testes, OK) e as sondas de `tem_motivo` acima (9 contra 160: False; 160 contra 160: True; linha menor seguida de linha suficiente: True). A suíte inteira fica com o CI do PR. Ferramentas de varredura de segredo, SAST e de workflow ausentes no PATH (lacuna registrada; o delta não toca workflow).
