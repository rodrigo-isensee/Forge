---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-develop-verde-ordens
commit: 6ce3a41a8ec8219ace8da853b0540eaaea47edd9
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-23
---
# Review de segurança: v0478 (E127.3, PR #814)

Escopo: o delta `0e59c446..6ce3a41a` (`hooks/conformidade.py:1612-1613`, o arquivo de mutantes da guarda das ordens e o fragmento do changelog). A guarda das ordens pela cópia principal passa a exigir, antes de ler o `.git` do disco, que o caminho resolvido contenha `/.forge/ordens/` no texto.

Gatilhos: controle do Forge (hook `conformidade`, guarda de caminho protegido).

## Veredito: neutro (não afrouxa nem aperta)

O item é **neutro**: decide igual ao `0e59c446` em toda entrada; não deixa passar nenhum caminho que a guarda barrava, nem barra caminho novo. Prova (`hooks/conformidade.py:990-1010`, `1638-1646`):

1. A cláusula antiga barrava só quando `relativo_ao_pai(posix, base)` devolvia `rel` com `casa(rel, ".forge/ordens/")`, isto é, `rel` começa com `.forge/ordens/` ou é `.forge/ordens`.
2. `relativo_ao_pai` é pelo texto: devolve `rel` só se `posix == base + "/" + rel` (ou `base` é `/` e `posix == "/" + rel`). Logo `posix + "/"` contém `/.forge/ordens/` literalmente, que é o que `em_qualquer_lugar(posix, ".forge/ordens/")` testa.
3. Então a condição antiga implica a nova; a nova é `filtro AND antiga`, e as duas são iguais. O filtro e o casamento leem o **mesmo texto** `posix` (já resolvido por quem chama), com a mesma caixa e as mesmas barras: link, `..`, barra dupla, caixa e caminho relativo já foram (ou não foram) normalizados antes, de forma idêntica para os dois lados; o filtro não introduz normalização própria.
4. `diretorio_comum` (`hooks/_comum.py:153-176`) não tem efeito colateral nem falha fechada (erro vira `None`, que dava `[]`, nada barrado): pular a chamada não remove bloqueio nenhum por via de exceção.

O mutante que troca a condição nova por `False` continua morto pelo `test_conformidade_recusa_a_pasta_das_ordens_e_a_copia_principal` (o teste da guarda roda verde no head).

## Achados

## Sondas

## Detalhe dos achados
Sem achado. Sonda de equivalência (não prova bloqueante, por isso fora do bloco): 239.876 pares (base, caminho) gerados de pedaços com `/`, `//`, `.`, `..`, `.forge`/`.Forge`/`.FORGE`, `ordens`/`Ordens`, `.forge//ordens`, espaço, quebra de linha e `*`, mais bases `/`, `//w` e com barra final; a decisão antiga barrava 167; contraexemplos entre antiga e nova: 0.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes rodados no head `6ce3a41a`: `tests.test_hooks.GuardaDasOrdens` (4 testes, OK) e `tests.test_hooks.Hooks.test_muitos_heredocs_recusam_dentro_do_orcamento` (OK; 3000 gravações em 0,89 s de CPU, teto 3 s). Suíte inteira: no CI do PR #814 (run 45269689053; instalação e bateria verdes, partes da suíte em andamento na hora deste parecer). Sem ferramenta externa: a análise é leitura e sonda local da biblioteca padrão.
