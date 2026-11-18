---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-indice-forge
commit: bf97d62a0acbdb143f40c4af560059ab911829c8
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 (E8.7, revalidação do índice do Forge, H7 primeira parte)

## Sondas

## Parecer
Aprovado. Revalidação por delta (H3, `R-REVIEW`): li só `forge-check parecer delta docs/reviews/v0478-indice-forge.md`, intervalo 7bd4913e..bf97d62a, domínio código e testes: `bin/forge-testes`, `changelog.d/v0478-indice-forge.md`, `docs/indice-forge.md`, `scripts/indice-forge.py`, `tests/mutantes/v0478-indice-forge-2.json`, `tests/test_indice_forge.py`, `tests/test_testes_tocados.py`.

A1 (resolvido): `scripts/indice-forge.py` não carrega mais o `bin/forge-testes`; a tabela tem só arquivo e primeira linha da doc, o cabeçalho não conta os arquivos e cita `bin/forge-testes --listar <arquivo>`. As guardas da coluna de testes saíram com os mutantes M11 a M14. A S1, refeita com o script do head gerado sobre os 16 últimos commits da develop (first-parent, a1674911..4182a6b9), dá 2 mudanças em 15 merges: 31b29052 (`hooks/_maquina.py` novo) e 71f280f2 (`bin/forge_disco.py` novo). As duas são da trilha que criou o arquivo, que é a medida que o remédio pedia. Os testes `test_tabela_so_com_arquivo_e_doc_e_sem_contagem` e `test_teste_novo_nao_muda_o_indice` prendem isso.

A2 (resolvido, com desvio do remédio, e o desvio está certo): eu pedi o módulo em `VARREM_A_PASTA`, mas essa tabela só entra em `modulos_da_convencao` (`bin/forge-testes:328`). O arquivo com regra no `MAPA`, como o `bin/forge-check` do meu próprio exemplo, ou o `bin/forge-changelog`, nunca passa por ela. Meu remédio deixaria o caso do achado sem o teste. O `teste_do_indice` entra em `planejar` e em `planejar_afetados` para todo arquivo do primeiro nível das três pastas, seja qual for a regra, e só se a raiz tem `tests/test_indice_forge.py`. Um projeto ou uma raiz de teste sem o módulo segue dirigido sem ele, sem cair na suíte completa por módulo ausente. A guarda tem teste dos dois ramos (`test_o_plano_dirigido_das_pastas_roda_o_indice`, com subprocesso em `-I` e ambiente limpo, e `test_raiz_sem_o_teste_do_indice_segue_dirigida_sem_ele`) e o mutante M23. Os ajustes em `tests/test_testes_tocados.py` só somam o módulo novo aos planos esperados; a contagem de 99 do `forge-check` fica igual, com o módulo afirmado à parte.

Provas no head: `python3 -m unittest tests.test_indice_forge` dá 19 testes OK. Os três testes mudados de `test_testes_tocados` (`Mapa` e `MapaCobreOQueOsTestesLeem`) passam. `bin/forge-testes --listar bin/forge-check` traz o `test_indice_forge` (antes, 0), e `scripts/indice-forge.py --conferir` responde em dia. Não rodei o `bin/forge-mutante` do M23: a trava `R-TETO` tinha tarefa pesada de outra sessão na fila. A mutação é verificador do autor (V2), e a suíte inteira fica para o CI do PR.
