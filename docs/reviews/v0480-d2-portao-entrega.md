---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-d2-portao-entrega
commit: d64a506b4a01f13be0798ce2af2123cb3013a5bd
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 (E173.9, PR #864, D2 portão de entrega)

Escopo: `patches/d2-portao-entrega.patch`, `tests/test_pre_push_d2.py`, `tests/pesos-d4.json`, `changelog.d/v0480-d2-portao-entrega.md` no head d64a506b (base 8a6f5907).

Ferramentas citadas, sem refazer: `git apply --check patches/d2-portao-entrega.patch` aplica na develop do head; `python3 -m unittest tests.test_pre_push_d2`: 15 testes OK em 10,8 s; `forge-check pr v0478`: classe C, faltam só os pareceres. CI do PR #864 pendente na hora do review (a suíte inteira fica para ele).

Conferido por leitura: as funções chamadas existem com a assinatura usada (`contagens_do_intervalo(..., estrito=True)`, `e_codigo`, `pr_da_branch(..., corpo=True)`, `forge_tamanho.linhas_de_codigo/aviso_de_linhas/falta_de_motivo`, `catraca.py --modo pr-texto --base`); as variáveis do bloco shell já são `local` em `checagens_baratas`; nenhum teste local entra no envio (ENVIO-LEVE); o `gh` falso confere o nome exato da branch (checklist 12).

## Achados
- A1 (bloqueante) patches/d2-portao-entrega.patch:70 · Teto e pr-texto barram todo envio da ponta com PR aberto, até o commit só de parecer: o revisor não envia o parecer reprovado que aponta o defeito do corpo (R-REVIEW; S1, S2). Com delta só em docs/{reviews,qa,security,devops}/, só avise; com teste.
- A2 (recomendado) patches/d2-portao-entrega.patch:20 · Os ramos de aviso (import de bin/forge-check falho, numstat None na linha 24, catraca com saída fora de 0/1 na linha 46) não têm teste; o código de controle mora num .patch que o e_codigo não classifica, e a regra de mutantes da catraca não o alcança.

## Sondas
- S1 · item com bin/grande.py de 160 linhas, PR #7 aberto com as seções e sem `teto: excedido`, depois commit só de docs/reviews/x.md; envio da ponta pelo hook remendado · espera: rc=0 (envio de parecer passa) · obtido: rc=1, "pr: tamanho: 160 linhas ... sem a linha `teto: excedido`"; hook original rc=0
- S2 · PR #7 aberto sem "## Como medir", depois commit só de docs/reviews/x.md; envio da ponta pelo hook remendado · espera: rc=0 · obtido: rc=1, "texto do PR #7 reprovado pelo pr-texto da catraca"

## Parecer
Reprovado. O patch faz o que a D2 pede e o teste prova cada checagem contra o hook original, mas o A1 é defeito provado (S1, S2): o portão do autor passa a travar o envio dos pareceres na mesma branch, o que quebra o fluxo do R-REVIEW (parecer só na árvore não vale) justamente no caso em que o parecer reprova o corpo ou o tamanho. Sugestão: no bloco PORTAO-D2 do shell, só rodar o `PORTAO_D2_PY` quando o delta do envio (remoto..ponta, ou `alterados`) tem arquivo fora de `docs/{reviews,qa,security,devops}/`, a mesma fronteira do `so_parecer`; com o delta só de parecer, imprimir aviso e seguir; e um teste com o commit só de parecer sobre o PR defeituoso. O A2 vira cartão depois do merge.
