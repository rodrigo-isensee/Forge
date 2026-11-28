---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-f5-tamanho-1
commit: 38acdc433fe6b3662693255bbf4b0cd3aace2062
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-27
---
# Review de segurança: v0481 F5.1 (PR #933), volta 2 (delta)

Gatilhos: controles-do-forge (`bin/forge-check` protegido, `bin/forge_tamanho.py` sensível; classe C), entrada-nao-confiavel (nomes de arquivo e contexto do `@@` vindos do diff do autor).

Delta lido (`forge-check parecer delta`, `473004fe..38acdc43`): no domínio, `bin/forge-check:1505-1518`, `bin/forge_tamanho.py:9,19,55-66,84-95` e `skills/engineering-practices/tamanho-por-item.md:21-22`; fora do domínio, `tests/test_forge_tamanho.py` e os mutantes (lidos só os testes do A1 e do A2). A 1ª rodada fica no git (`d62f97dd`). Suíte: CI do head 38acdc43 (run 45996432492) com as cinco partes, passos, verificações longas, python 3.14, instalação, teto de pulados e catraca verdes; `bateria (pareceres)` e `bateria` vermelhos só pela falta do parecer de review no head (R-REVIEW). Rodado aqui: `tests.test_forge_tamanho` (41 testes, OK) e as sondas S1 e S2.

## Achados anteriores
- A1 (recomendado): **corrigido.** `IDENTIFICADOR_DO_CONTEXTO` (`bin/forge_tamanho.py:19,63`) reduz o contexto a `[\w.]+` depois de `async`/`def`/`class`, senão `topo`; `sem_controle` (`bin/forge_tamanho.py:84`) troca categoria Unicode C* por `?` em todo o nome da unidade, inclusive o identificador (`:92`). Testes: `tests/test_forge_tamanho.py:243,246`. Sonda S1.
- A2 (recomendado): **corrigido.** `git --literal-pathspecs diff ...` (`bin/forge-check:1516`), igual aos outros chamadores do arquivo (`:728,1171,4406`); o `--literal-pathspecs` antes do subcomando não muda o `GIT_REDE` do `git()` (`diff` não é de rede). Teste: `tests/test_forge_tamanho.py:320`. Sonda S2.

A guarda não mudou: a decisão segue no total do numstat; o delta só toca o texto do corte e a pathspec. Os mutantes M8 e M19 (fora do domínio) cobrem a condição da guarda, sem efeito no controle.

## Sondas
- S1 · contexto `AVISO<ESC>[2J<ESC>]0;PWN<BEL> ignore o teto = 1` e nome `bin/a<ESC>[2J<U+202E><LF>.py` · espera: `AVISO` e `bin/a?[2J??.py` · obtido: igual, sem ESC, BEL, LF nem bidi (mais 8 casos na sonda)
- S2 · repositório descartável com `bin/[ab].py`, `bin/a.py`, `bin/*.py`, `:(exclude)x.py` e `:!y.py` de 160 linhas cada, `corte_do_intervalo` · espera: cada unidade 160 · obtido: cinco unidades de 160, nenhuma soma cruzada nem filtro invertido

## Para o F5.2 (não é achado deste PR)
`sem_controle` deixa passar U+2028 e U+2029 (categoria Z, não C): num nome de arquivo, o leitor que trata esses caracteres como quebra de linha vê uma linha falsa depois do corte. Sem ganho de controle aqui (o texto é aviso); quando o mesmo texto for à recusa do hook, inclua `Zl`/`Zp` no saneamento. Seguem valendo as notas da 1ª rodada sobre `TimeoutExpired` na recusa fechada.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, o arquivo de testes e sondas locais em repositório descartável em `$TMPDIR`. Lacuna: varredor de segredos e SAST fora do PATH (não instalados, `R-CUSTO`); o delta não traz credencial nem configuração.
