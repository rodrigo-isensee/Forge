---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-d5-filtro-decisao
commit: 6c4a7dcc9856c3718599c0bdb06185a58afcbdcf
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 (E173.5, D5, PR #863)

## Achados
- A1 (bloqueante) bin/forge_decisor.py:60 · A confirmação da segurança não se prende à decisão: qualquer parecer em docs/security/ que diga "só aperta" de passagem (heredoc-donos.md, lote-l10.md) confirma qualquer porta (S1). Exigir no parecer o pedido do --pedido e a porta registrada, ou o id da decisão.
- A2 (recomendado) bin/forge_decisor.py:31 · A negação só pega `não ` colado: "Não, só aperta?", "não\nsó aperta", "nem só aperta" e "verificar se só aperta" casam (S2). Com A1 resolvido por linha própria da confirmação, a busca solta pode sair.
- A3 (recomendado) skills/falar-com-o-dono/SKILL.md:1 · A skill não cita `--tipo-pergunta` nem os 7 tipos, e o R-DECISAO não cita `--so-aperta`/`--seguranca`; o PR aponta como cartão. Quem pergunta ao dono descobre a flag pela recusa (rc 2).

## Sondas
- S1 · confirmacao_escrita(raiz, "docs/security/heredoc-donos.md") (parecer de outro item, frase "o que só aperta" sobre um contador) · espera: False · obtido: True
- S2 · SO_APERTA.search("Não, só aperta?") e "não\nsó aperta" · espera: None · obtido: casa nos dois

## Parecer
Reprovado por A1. O D5 tem três partes; duas estão corretas:

- `anotar --tipo pergunta`: `recusa_da_pergunta` (tipo da lista fechada, ao menos uma questão, nenhuma com opção só) roda antes da E6, e `--tipo-pergunta` fora da pergunta é recusado sem gravar. O `tipo=<t>` entra no contexto, com valor da lista, e o O4 segue lendo a linha (`test_cada_tipo_da_lista_grava_o_tipo_antes_do_contexto`). Nenhum outro chamador de `cmd_anotar` ou `decidir` fica sem os argumentos novos (grep em bin, hooks, tests).
- `decisoes registrar`: `--so-aperta sim|nao` é obrigatório (rc 2 sem ele) e as duas condições novas só apertam. Caminho restrito a `docs/security/<nome>.md` sem link no arquivo, na pasta e na `docs/`, teto de 1 MiB.

O defeito está na terceira parte. A regra do dono de 24/11 07:43 pede que a segurança confirme por escrito que **a opção recomendada** só aperta. `confirmacao_escrita` só procura a frase em qualquer lugar do arquivo. Dez pareceres da `docs/security/` já trazem "só aperta" sobre outros itens; S1 mostra que um deles confirma qualquer porta. Como `--so-aperta` e `--reversivel` são declarados por quem registra, essa é a única condição com âncora fora do agente, e ela não segura. Sugestão de correção (o autor escolhe): o parecer passa a valer só com o `pedido:` do frontmatter igual ao `--pedido` e uma linha que traga a porta registrada (ou o id `D<n>`) junto de "só aperta". Precisa também de teste do ramo de falha (parecer de outro pedido e parecer sem a porta) e de mutante para a guarda nova.

Tamanho (H1): 64 linhas de código em `bin/`, dentro do teto. Mutantes D5M1 a D5M17, um por guarda nas três specs; cito o autor (`bin/forge-mutante`, 17 de 17 mortos; `--cobertura --base 8a6f5907` rc 0), sem refazer. Commits em Conventional Commits, com o fragmento `changelog.d/` presente.

Suíte: no CI do head 6c4a7dcc a suíte ainda estava pendente; `catraca` e `bateria (pareceres)` falham, como se espera com os pareceres pendentes. Cito o PQ local do autor (214 + 203 testes OK). Rodei aqui só os testes tocados: `tests.test_forge_dono.FiltroDaPergunta`, `tests.test_forge_dono.SoApertaComSeguranca`, `tests.test_decisor` e `tests.test_anotar`, 42 testes OK.
