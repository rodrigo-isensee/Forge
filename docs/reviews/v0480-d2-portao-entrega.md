---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-d2-portao-entrega
commit: 5cac29190646ed60b36cfe8f704b948bc920ee69
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 (E173.22, PR #864, D2 portão de entrega, volta E173.16)

Revalidação por delta: `forge-check parecer delta` sobre o parecer anterior (reprovado no head d64a506b, A1 bloqueante, A2 recomendado) deu `revalida: sim`. Delta lido d64a506b..5cac2919: `patches/d2-portao-entrega.patch` (+21/-8: função `d2_so_avisa` e as duas chamadas `d2_so_avisa || falhas=1`), `tests/test_pre_push_d2.py` (classes `Ponta` e `SoParecer`, `roda` com `remoto`, `ref` e `sha`), `tests/mutantes/v0480-d2-portao-entrega{,-2}.json` (M1 a M16), `changelog.d/v0480-d2-portao-entrega.md`; o resto do delta são os pareceres.

Ferramentas citadas, sem refazer a suíte (fica no CI do PR): `git apply --check patches/d2-portao-entrega.patch` aplica; `python3 -m unittest tests.test_pre_push_d2`: 22 testes OK em 27,3 s; `bin/forge-mutante --processos 1 --ids M5,M6,M7` (as guardas novas do delta): M5, M6 e M7 morreram (patch:59, :76, :88); `bin/forge-mutante --conferir --base 8a6f5907`: o trecho de cada spec está no lugar; `--cobertura` lista o `.patch` como `não coberto` (não é Python: o caso do A2 anterior, já cartão). `shellcheck` ausente nesta cópia; o shell do patch não entra no shellcheck do CI enquanto não for aplicado.

A1 resolvido (conferido por leitura e pelas sondas S1 e S2 do parecer anterior, que viraram `SoParecer.test_teto_estourado_so_avisa` e `test_texto_do_pr_reprovado_so_avisa`): o portão D2 só avisa quando toda ref enviada já existe no remoto e o delta remoto..ponta só toca `docs/{reviews,qa,security,devops}/`, a mesma fronteira do `so_parecer`. O lado frouxo é fechado: ref nova (remoto zero), sha remoto desconhecido e delta vazio dão linha vazia fora da fronteira e barram (`test_ref_nova_ou_sha_remoto_desconhecido_barra`); arquivo fora dos pareceres barra (`test_delta_com_arquivo_fora_dos_pareceres_barra`); `--no-renames` põe os dois caminhos de um rename no delta, e nome com quebra de linha só pode cair fora da fronteira (barra). `envios` nunca chega vazio ao portão (o PREPUSH-DELETE sai antes). Os testes de comportamento cobrem o ramo de falha de cada guarda nova (M5 a M7), sem ler o texto da fonte. O A2 anterior segue recomendado: os ramos de aviso do import falho e do numstat None seguem sem teste; M10 e M13 cobrem o PR não verificável e o índice fora de 0 e 1.

## Parecer
Aprovado no head 5cac2919. A correção faz só o que o A1 pedia, com a fronteira já usada pelo `so_parecer`, e cada guarda nova tem mutante declarado que morre no teste do ramo de falha. O A2 do parecer anterior vira cartão depois do merge.
