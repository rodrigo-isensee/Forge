---
tipo: review
contrato: 1
pedido: v0457
branch: melhoria/escopo-ponto
commit: 22e6bce13053072c0c2d88da4e8b3ca04b4125e6
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-12
---
# Review: v0457 (E23.57, melhoria/escopo-ponto no 22e6bce1)

Revalidação por delta (E23.57, volta E23.56), por instância que não fez a entrega. Delta lido: `forge-check parecer delta docs/reviews/escopo-ponto.md`, intervalo 0a0a7c808607535ddfe5e2eaf715a9340d7f8b8b..22e6bce13053072c0c2d88da4e8b3ca04b4125e6, no domínio bin/forge-check, changelog.d/escopo-ponto.md, tests/mutantes/v0457-escopo-ponto-{2,3,5}.json, tests/test_selo_e_entrega.py. Testes dos arquivos tocados, um módulo por vez, numa worktree destacada própria: `test_selo_e_entrega` 98 OK em 372 s; `test_conf_escopo` 16 OK em 30 s.

## Achados
- A6 (recomendado) bin/forge-check:2348 · veredito_trocado faz um `git show` por arquivo da pasta em cada versão; com a janela no Base-sha desta volta, as versões lidas são as da branch inteira; filtrar antes com `git grep -l <commit> <sha> -- <pasta>` ou `cat-file --batch`
- A7 (recomendado) bin/forge-check:2338 · o parâmetro `nome` de veredito_trocado segue sem uso, e o parâmetro `de` agora recebe o Base-sha (a docstring ainda diz "no intervalo"); tirar `nome` e chamar o parâmetro de `base_sha` (bin/forge-check:2377 e os testes)
- A8 (recomendado) tests/test_selo_e_entrega.py:926 · MatrizDaBuscaDoVeredito herda de ParecerDoPortao e roda de novo os 21 testes dela (25 testes na classe; ParecerDoPortao sozinha leva 52 s): pôr os auxiliares numa base sem `test_` e herdar dela
- A9 (recomendado) tests/test_selo_e_entrega.py:1012 · a célula de partida (linear, raiz, outro) roda nos três laços para cada janela, e a S8 (:1007) repete a de `volta_anterior_apagada`: 7 das 34 execuções são repetidas (cerca de 3,5 s cada); rodar a de partida uma vez por janela

## Revalidação dos achados anteriores
- Segurança A10 conferido sem achado de review: a chamada de bin/forge-check:2564 passa `base_sha`, e `veredito_trocado` lê o `ls-tree` do Base-sha e `rev-list --full-history base_sha..head`. O Base-sha já é exigido ancestral do head (bin/forge-check:2460); o que vem da develop por merge entra na janela, mas só conta com `branch:` igual à conferida. A troca é a correção mínima que a segurança provou.
- Mutantes (AR-12): os 36 `de` de tests/mutantes/v0457-escopo-ponto*.json casam uma vez só com o bin/forge-check do head; M10 e M20 seguiram a assinatura nova. Sonda própria do M36 (a chamada volta a passar `de`): `test_s8_volta_anterior_tirou_o_reprovado_da_pasta` falha (FAILED, failures=1), então o mutante morre. "M1-M36 mortos, cobertura rc 0" do autor fica com o QA (os logs escopo-ponto.mutante*.log em ~/.forge-contrib/wt são da manhã, o último às 11:27).
- A matriz: as asserções (rc 1, o y.md fora do declarado, o intervalo no Desde da célula) são de comportamento; o `setUp()` dentro do subTest registra a própria limpeza (`addCleanup`, :55), sem resto em disco. A pasta `parecida_fora` passa sem a busca (o prefixo já a exclui) e serve de célula de borda.

## Custo da matriz (pedido do brief)
A classe nova leva 154 s isolada, mas só cerca de 100 s são a matriz: 52 s são os 21 testes herdados (A8) e cerca de 25 s são células repetidas (A9). Com A8 e A9, a matriz custa perto de 75 s no módulo. Fica inteira no CI: é a única prova de que a família A5/A7/A8/A10 está fechada, roda só no CI do PR e no envio quando o módulo é afetado, e cada célula é uma variante que já furou o controle. A8 e A9 vão como cartão da versão seguinte, junto com A6; não bloqueiam (custo, sem defeito).

## Tamanho (M14)
783 linhas de código e teste desde o Base-sha 8b5a44d5. O PR precisa trazer `teto: excedido, 783 linhas, <motivo>`; o motivo (consertos da mesma conferência em quatro voltas, volume nos testes dos ramos negativos e na matriz) basta.

## Parecer
Aprovado: o delta fecha o A10 da segurança com teste (S8 e a matriz) e mutante (M36, morto na sonda própria) e não traz defeito provado. A6 a A9 do review são recomendados (custo e limpeza), para a versão seguinte.
