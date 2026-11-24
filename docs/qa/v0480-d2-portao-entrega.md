---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-d2-portao-entrega
commit: d64a506b4a01f13be0798ce2af2123cb3013a5bd
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0478 E173.2 (PR #864, patch do portão de entrega D2)

Escopo: `patches/d2-portao-entrega.patch` (índice, teto H1, pr-texto no envio), `tests/test_pre_push_d2.py`, `tests/pesos-d4.json`. Sem especificação de UX (pedido de controle do Forge): as obrigações são as do commit E173.2 (checagens baratas, sem teste local no envio, sem gh ou sem rede avisa e segue) e `ENVIO-LEVE`.

## Achados
- A1 (bloqueante) patches/d2-portao-entrega.patch:58 · mutante sobrevivente: trocar `'^(bin|hooks|scripts)/'` por `'^(bin|scripts)/'` (ou só `bin`) deixa os 15 testes verdes. O subTest acumula commits e `bin/` do 1º já dispara o índice; hooks/ e scripts/ nunca são provados sozinhos.
- A2 (bloqueante) patches/d2-portao-entrega.patch:73 · mutante sobrevivente: trocar a guarda `[ "$ponta" = "$(git rev-parse HEAD)" ] || continue` por `:` mantém tudo verde; nenhum teste envia ref cuja ponta não é o HEAD (a checagem rodaria sobre a branch errada).
- A3 (bloqueante) patches/d2-portao-entrega.patch:72 · mutante sobrevivente: trocar o filtro `case "$ref" in refs/heads/?*` por `:` mantém tudo verde; nenhum teste envia tag ou ref fora de refs/heads/ nem apagamento de branch.
- A4 (recomendado) tests/mutantes/v0480-d2-portao-entrega.json:1 · pedido de controle sem spec de mutantes do autor (`tests/mutantes/*d2*` não existe); a lista acima foi feita pelo QA e deve virar spec ao corrigir A1 a A3.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Índice confere quando bin/, hooks/ ou scripts/ mudam | Indice.test_codigo_novo_sem_indice_barra_e_com_indice_passa | pasta tocada (só bin provada de fato) | passou, mutante sobrevive (A1) |
| Índice não conferiu: avisa e segue | Indice.test_indice_que_nao_conferiu_avisa_e_segue | saída ≠ 0/1 | passou |
| Envio sem código não confere o índice | Indice.test_envio_que_nao_toca_codigo_nao_confere_o_indice | pasta não tocada | passou |
| Teto sem PR só avisa | Teto.test_sem_pr_aberto_o_teto_so_avisa | 160 > 150 | passou |
| PR aberto sem `teto: excedido` barra, com passa | Teto.test_pr_aberto_sem_teto_excedido_barra_e_com_ele_passa | teto | passou |
| Número menor que o medido não libera | Teto.test_numero_menor_que_o_medido_nao_libera | 150 vs 160 | passou |
| No teto (150) não avisa | Teto.test_no_teto_nao_avisa | máximo exato | passou |
| pr-texto: sem Como medir barra; T1 | TextoDoPr.test_pr_aberto_sem_como_medir_barra, test_codigo_sem_teste_nem_sem_teste_no_corpo_barra | seção vazia; código sem teste | passou |
| PR fechado/mesclado não conferido | TextoDoPr.test_pr_fechado_ou_mesclado_nao_e_conferido | estado ≠ OPEN | passou |
| Sem rede/gh: avisa e segue; nome exato da branch | TextoDoPr.test_sem_rede_avisa_e_segue, test_gh_e_chamado_com_o_nome_exato_da_branch | rede ausente | passou |
| Sem teste local no envio (ENVIO-LEVE) | PatchAplica.test_patch_nao_acrescenta_teste_local_ao_envio, passa() | n/a | passou |
| Patch só toca o pre-push, sintaxe e modo | PatchAplica.test_patch_so_toca_o_pre_push_e_mantem_o_modo | n/a | passou |
| Neutralidade segue barrando | Neutralidade.test_stack_no_nucleo_segue_barrando_no_remendado | n/a | passou |
| Envio de ref que não é o HEAD / não é branch | nenhum | ponta diferente, tag, apagamento | sem teste (A2, A3) |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_pre_push_d2.py`: 15 testes, OK (11,5 s). Cada checagem nova barra no remendado e passa no hook original (`compara`), o que é o vermelho sem a implementação.
- `forge-testes --vermelho 8a6f5907 --modulos test_pre_push_d2`: `contagem: sem veredito=15` (o módulo não existe na base: erro de carga em B); sem veredito não vale como vermelho, então a prova usada é a comparação com o hook original dentro do teste e os mutantes abaixo.
- Mutação à mão no patch (cópia em $TMPDIR, 15 testes cada): morreram `state != OPEN` (8 falhas), `returncode == 1` do pr-texto (2), `falta_de_motivo` (2), `rc -eq 1` do índice (3), âncora do intervalo (3), `sys.exit(1 if falhas ...)` (4), `pr is None` (2), `aviso_de_linhas` (1), sem `bin` (2). Sobreviveram: sem `hooks`, sem `scripts`, só `bin` (A1); guarda da ponta (A2); filtro `refs/heads/` (A3).
- CI: não consultei o check-run `bateria` deste sha; a suíte completa não foi rodada local (brief).
