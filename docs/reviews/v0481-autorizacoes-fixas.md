---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-autorizacoes-fixas
commit: 39b5b066122f8f6c1883aef2bd692b147d05d8a1
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 (AUTORIZACOES-FIXAS, E14.52; #901)

Revalidação por delta (H3, G1.2), etapa E14.75. A 1.ª rodada completa (E14.65) aprovou o 4c88ca81 com os achados A1 e A2 abaixo, que seguem como recomendados para cartão.

Delta lido: `forge-check parecer delta docs/reviews/v0481-autorizacoes-fixas.md`, intervalo `4c88ca81..39b5b066`, domínio só `bin/forge-fechar`: a linha `comum=` de `limpar_clones` (`:674`, commit 39b5b066, E14.68) troca `cd X && pwd -P || true` por `if cd X; then pwd -P || true; else :; fi`. Os outros dois commits do intervalo são os pareceres de review e de segurança, fora do domínio.

## Achados
- A1 (recomendado) bin/forge-fechar:1587 · seção de versão sem " - <data>" dá `ultima` vazia e passa como "não é de hoje" (sonda: "## [0.9.0]" sem data deu saída vazia). O forge-changelog sempre grava a data, então o risco é baixo; tratar vazio como erro fecha a falha.
- A2 (recomendado) docs/adr/0018-autorizacao-do-dono-gravada.md:185 · o F4 diz que a so-aperta-com-seguranca não libera o rótulo, mais estreito que a decisão do dono de 25/11 21:52. Correto agora, por R-CONFORMIDADE, mas citar o cartão ROTULO-SO-APERTA-PELO-TIME no F4 deixa a divergência à vista.

## Parecer
Aprovado no head 39b5b066.

- ci: 39b5b066122f8f6c1883aef2bd692b147d05d8a1 verde
- CI do #901 no head exato (check-runs do 39b5b066): suíte 3.12 e 3.14 (partes 1 a 5), bateria (passos), bateria (verificações longas), instalação, teto de pulados (3.12), árvore já provada e catraca verdes. Vermelhos só `bateria (pareceres)` e o agregador `bateria`, que esperam este parecer. `teto de pulados (python 3.14)` e `bateria (python 3.14)` foram cancelados pelo push dos pareceres de segurança e QA (6a9b5955, 3a13bec4), que só mudam `docs/`; rodam de novo no head seguinte com o mesmo código.
- Comportamento igual ao de antes: com `cd` bem-sucedido, a saída é o `pwd -P`; com `cd` falho, nada é impresso e o código é 0, como no `|| true` antigo. Sonda local, as duas formas lado a lado: no repositório, as duas deram o mesmo caminho de `.git`; com `git-common-dir` apontando para pasta inexistente, as duas deram vazio.
- `shellcheck bin/forge-fechar` no 39b5b066: limpo (o SC2015 da 1.ª rodada sumiu).
- Módulos tocados rodados aqui: `tests.test_fechar` e `tests.test_fechar_limpar_clone`, 126 testes OK.
- Mutantes: a linha não muda guarda, só a forma (o ramo de falha continua sendo "comum vazio"); a catraca está verde no head, sem mutante novo exigido.
- Tamanho (H1): 1 linha trocada. O commit segue Conventional Commits em português.
