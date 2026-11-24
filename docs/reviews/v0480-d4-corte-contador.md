---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-d4-corte-contador
commit: c9b5d269018c90f24d6414aa5e523adb88fbd41e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Code review: forge-fechar --corte, o corte da versão pelo contador (D4, CORTE-PELO-CONTADOR)

Escopo: pedido v0478, etapa E174.27, PR #869 (`R-REVIEW`), rodada 2, revisão por delta. O parecer anterior (E174.19, head `bf598d2f`) reprovou por A1 e A2.

## Delta lido
Li a saída de `forge-check parecer delta` sobre o parecer anterior. Intervalo `bf598d2f..c9b5d269`, um commit (`c9b5d269`, E174.26). Seis arquivos estão no domínio: `bin/forge-fechar` (+8 −1), `docs/fechamento-integrador.md` (1 linha), `tests/mutantes/v0480-d4-corte-contador-2.json` (M9 reajustado), `tests/mutantes/v0480-d4-corte-contador-5.json` (M35 a M37), `tests/test_fechar_corte.py` (teste novo e asserção `sem_merge`) e `tests/test_reval_delta.py` (1 entrada). Não reli o que ficou fora do delta.

## Parecer
Aprovado. Os dois bloqueantes da rodada 1 foram corrigidos, e o comportamento novo tem teste e um mutante por guarda.

- **A1, corrigido.** `bin/forge-fechar:1484` virou `if [ -z ... ] || [ -z ... ] || [ -z ... ]; then die ...; fi`. A semântica é a mesma (qualquer versão vazia para) e saiu a forma `A && B || C`. `test_fechar.Fechar.test_fechar_sem_a_e_b_ou_c_solto` passa localmente.
- **A2, corrigido.** `tests/test_fechar_corte.py` ganhou 2 linhas na `_NOME` (`tests/test_reval_delta.py:124`) com o motivo `nome`. Esse motivo está certo: o arquivo é um `README.md` sintético da `changelog.d/` do projeto de teste, o mesmo caso de `tests/test_forge_contador.py`. Minha sugestão de `teste-le` na rodada 1 era imprecisa. `test_caminho_de_texto_so_e_citado_como_a_lista_conhece` passa. A conferência dessa lista é da segurança (C-2) e eu não a refaço.
- **Guarda nova: a main à frente da homolog para no V1** (`bin/forge-fechar:1490-1492`). O `sort -V` com a desigualdade antes só dispara quando a versão da `main` é estritamente maior que a da `homolog`. No fluxo normal, depois do merge do dono, as duas são iguais e a guarda não dispara. A guarda vem antes do V2 e do V3, então não abre PR de versão mais velha para a `main`. Isso cobre o recomendado do QA (A1) e os da segurança (A2 e A3). A documentação em `docs/fechamento-integrador.md` acompanha a mudança.
- **Guardas do diff com um mutante por linha.** Rodei `forge-mutante --processos 1 --ids M9,M35,M36,M37` no `c9b5d269`, e os quatro morreram: M35 em `:1484`, M9 em `:1485`, M36 em `:1490` e M37 em `:1491`. O `--cobertura --base bf598d2f` só aponta `não coberto: bin/forge-fechar`, que é o esperado para shell, porque a ferramenta não analisa esse tipo de arquivo. Por isso conferi a lista das guardas à mão, contra o diff.
- **R-MAIN reforçado no teste.** `sem_merge()` afirma que nenhuma chamada do falso do `gh` contém `pr merge` nem `--auto`. Ele roda no caminho da promoção com abertura do PR da main e no caminho do PR da main já aberto. O código do delta não acrescenta nenhum merge.
- **Testes.** `tests.test_fechar_corte` (18 testes, com o novo `test_main_a_frente_da_homolog_para`) e os dois testes de A1 e A2 deram 20 OK, rodados com ambiente limpo e `TMPDIR` próprio.
- **Tamanho.** O delta tem 8 linhas de código, e o item segue dentro do teto H1.
- **CI.** O run 45489524527 do head `c9b5d269` estava com a suíte em andamento quando escrevi este parecer. O `bateria (pareceres)` vermelho é a falta dos pareceres. O merge depende do CI verde (`R-FLUXO`), e quem confere isso é o integrador.

O A3 da rodada 1 (o V3 reabre o PR `release <v>` se o dono o fechar sem mesclar) continua recomendado e vira cartão depois do merge. Não o promovo.
