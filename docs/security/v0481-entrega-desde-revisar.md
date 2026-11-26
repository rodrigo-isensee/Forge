---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-entrega-desde-revisar
commit: 3b5fde5f4ebfeb4a70792575d7ea6506d530134f
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 E16.6 (volta do Desde a partir do Revisar-sha), revalidação por delta

Delta lido: `forge-check parecer delta` de `c056f38d..3b5fde5f`; no domínio só `bin/forge-check` (`desde_do_parecer_aprovado` e o texto do `--desde` no cabeçalho). Fora do domínio, lidos só para conferir a correção: `tests/test_selo_e_entrega.py` (`CicloDo878`, 18 testes), `tests/mutantes/v0481-entrega-desde-revisar.json` (ED1, ED6, ED7) e o fragmento do changelog. A rodada anterior fica no git (parecer no `c056f38d`).

Gatilhos: controle do Forge (conferência de entrega do `forge-check`, R-SEGURANCA).

## Achados anteriores
- A1 (bloqueante) corrigido. `bin/forge-check:2746` roda `veredito_trocado(raiz, base_sha, head, None, revisado, "aprovado", branch, t)` em todas as pastas de `PASTA_E_REGRA`, desde o Base-sha (mais largo que o `revisado..head` pedido). A função lê todas as versões de cada pasta com `--full-history`, inclusive `_*.md`, subpastas e arquivos apagados, lê o frontmatter sem olhar o `contrato:` e falha fechada quando o git falha. A sonda S1 a S4 da rodada anterior (`_sec78-v0481-desde-sonda.py`) rodou de novo no `3b5fde5f`: S1, S2 (`contrato: 0`), S3 (`_x.md`) e S4 (apagado) deram todas rc=1, com `docs/indice.md` fora do declarado. Os testes delas agora estão em `CicloDo878`: `test_reprovado_com_contrato_zero_…`, `test_reprovado_renomeado_para_sublinhado_…`, `test_reprovado_apagado_depois_…`, e mais `test_reprovado_sem_brief_selado_apagado_…`. O mutante ED6 tira a linha e morre.

## O que aperta, o que é neutro, o que afrouxa
- **Aperta:** (1) `bin/forge-check:2744` passa a exigir que o conjunto dos portões com o revisado selado como `Revisar-sha:` seja igual ao conjunto dos pareceres no head (antes bastava estar contido nele). Um portão pedido cujo parecer falta no head devolve o Desde de sempre (`test_portao_selado_sem_parecer_…`, ED7). (2) `bin/forge-check:2746` faz contar qualquer versão de parecer da branch sobre o revisado com outro veredito, desde o Base-sha e em qualquer pasta de portão: o reprovado apagado, o renomeado para `_*.md`, o regravado com `contrato: 0`, o de portão sem brief selado e o reprovado depois trocado por aprovado no mesmo `commit:`. O filtro é só `branch:`, sem `pedido:`, o que o deixa mais largo que a lista do head. (3) ED1 ganhou o teste `test_sem_conferida_pela_entrega_o_intervalo_parte_do_base_sha`.
- **Neutro:** a guarda antiga (`parecer != "aprovado"` na lista do head) saiu, mas o que ela cobria continua coberto: o parecer do head é uma versão do último commit de `base_sha..head` que toca a pasta e tem `branch:` igual, então `veredito_trocado` o vê. Prova: `test_parecer_nao_aprovado_mantem_o_desde_da_conferida`, verde e listado em ED6. O texto do cabeçalho do `--desde`, a docstring e o fragmento do changelog só descrevem o código novo. Continuam como estavam: os PQ, a worktree, `base_sha_como_desde`, `commit_vale` e as âncoras de ancestral e de base.
- **Afrouxa:** nada além do que já foi escrito na rodada anterior como opção A do dono, ou seja, o trecho conferida..revisado deixa de ser relido quando os portões selados aprovaram o revisado. O "afrouxa sem querer" daquela rodada (A1) ficou fechado.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Verificação local: `python3 -m unittest tests.test_selo_e_entrega.CicloDo878` (18 testes, OK); `forge-mutante --ids ED1,ED6,ED7` (os três morreram); `forge-mutante --cobertura --base 34ab6714` (toda condição mudada tem mutante declarado). Ferramentas usadas: leitura do diff e a sonda local, sem varredura externa.
- ci: 3b5fde5f4ebfeb4a70792575d7ea6506d530134f verde

CI no head exato (run 45759626052): verdes as 10 partes da suíte (3.12 e 3.14), `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, `instalação (python 3.14)`, os tetos de pulados e `árvore já provada na develop`. Três vermelhos não vêm do código. `bateria (pareceres)` e `bateria`, que agrega o de pareceres, esperam os pareceres desta volta. A `catraca` (run 45759680528) acusa só R-CONFORMIDADE por mexer em `bin/forge-check`, controle que pede aceite do dono. As seções do corpo do PR que ela cobrava na rodada anterior já não aparecem no log.
