---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-pedido-arquiva
commit: 2c61be46e408759ced4ab72cbe2509bd3643a048
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: v0481 (pedido que se arquiva sozinho, #874, E9.16, 2ª volta por delta)

Gatilhos: bin/forge-check (controle do Forge, R-CONFORMIDADE), escrita automática em docs/pedidos/ pelo `brief gerar`.

Delta lido (`forge-check parecer delta`, 8b312446..2c61be46): no domínio só bin/forge-check (`ENTREGUE_DA_ETAPA` em 8061; cabeçalho do arquivo e linha de `## Etapas arquivadas` em 8127 e 8137; variável da compreensão em 8133); fora do domínio, lidos como prova: tests/test_brief_tamanho.py (dois testes novos), mutantes M21, M23, M24, M38, M40 a M49 e os realinhados de outros pedidos, changelog.d. Já lido nas rodadas anteriores (no git): o resto da entrega, sem mudança. Diferenças só da develop (fragmentos, índice) não são do item.

Só aperta ou neutro, por escrito: **sim**.
- Aperta: `ENTREGUE_DA_ETAPA` (bin/forge-check:8061) passa de `(?![\w?])` para `(?![\w?-])`; o conjunto que fecha é subconjunto do anterior. Sonda S1 em 17 linhas de borda: só `E1.1 entregue-se` muda (fechava, não fecha); nenhuma fecha só na nova; `E1.1 entregue - falta o PR` segue fechando.
- Aperta: o nome do pedido no cabeçalho do arquivo (8127) e na linha de `## Etapas arquivadas` (8137) passa por `caminho_impresso` (3508, `sem_controle`): byte de controle no nome não chega mais cru ao Markdown gravado (S1: `\x1b` vira espaço).
- Neutro: `i` vira `j` na compreensão de 8133 (sem efeito; tira a duplicata do `de` de FC2-M2); o código das guardas de outros pedidos não muda.
- Mutantes realinhados, mesma guarda: cada `de` aparece uma vez no head e morre na linha da guarda original: est-m12-gerar M3 em 5128 (`_ler_regular`, C-1), v047 FC2-M2 em 4352 (Fora do escopo da volta), v0474 M16 em 9861 (aviso de teto do brief), v0479 M5 em 5322 (etapa fora do pedido) e M16 em 8357 (só a ordem lê as etapas). No 8b312446 esses cinco não rodavam (2 ou 0 ocorrências); `forge-mutante --conferir --todas` no head dá o mesmo conjunto de 26 pendências da develop (8d7914bc), nenhuma do item.
- Novos testes matam o que o QA E9.11 apontou: M21, M23, M24, M38 e M49 morrem no head.

Achados anteriores: nenhum aberto (A4 corrigido na E9.12). Resíduo neutro, já registrado: o parêntese do papel aceita texto livre; hífen Unicode (U+2011, U+2013) colado em `entregue` ainda fecha, como antes, e não aparece em nenhum pedido.

## Provas
- S1 · sonda em arquivo (biblioteca padrão) que carrega bin/forge-check, compara a regex anterior com a nova em 17 linhas de borda, confere a unicidade dos `de` e o `caminho_impresso` · espera: nenhuma linha fecha só na nova · obtido: lista vazia; só `entregue-se` deixa de fechar
- `bin/forge-mutante` no rev 2c61be46: v0481-pedido-arquiva M21, M23, M24, M38, M49 morreram; est-m12-gerar M3, v047 FC2-M2, v0474 M16, v0479 M5 e M16 morreram
- `python3 -m unittest tests.test_brief_tamanho`: 25 testes, OK
- ci: run 45601508436 no head 2c61be46: suíte 3.12 e 3.14 (partes 1 a 5), bateria (passos), verificações longas, python 3.14, instalação, teto de pulados e árvore provada verdes; a falha de bateria (pareceres) e da catraca é só a espera destes pareceres (R-REVIEW e R-SEGURANCA desatualizados, R-QA reprovado), não do código

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do delta, sonda local e forge-mutante; gitleaks, Semgrep e zizmor não se aplicam ao delta (sem segredo, sem workflow).
