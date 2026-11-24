---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-d1-integrador-laco
commit: 8b056d4d81fc3c68596c10afb7ba41f8003efe19
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478

## Achados
- A1 (bloqueante) docs/fechamento-integrador.md:10 · O manual do forge-fechar não traz o --laco: falta a forma de uso (linha 10), a seção do laço ao lado da do lote (101) e a reversão com a medida (118). Requisito: definição de pronto (doc afetada na entrega) e critério de reversão de mecanismo novo (R-DECISAO).
- A2 (recomendado) bin/forge-fechar:1303 · mergeable UNKNOWN (o GitHub calcula sob demanda; hoje #857 e #859 saem assim na lista) nunca recebe o aviso de conflito: o PR em conflito não lido fica fora do aviso de 2 h. Sugestão: reler o mergeable pelo pr view do PR em UNKNOWN.
- A3 (recomendado) bin/forge-fechar:1277 · O check bateria (pareceres) reprovado conta como vermelho (hoje o #865 tem 1 ruim só por ele): PR à espera dos portões há mais de 2 h recebe o aviso de parado sem estar. Sugestão: separar esse check na contagem ou dizer no aviso que é parecer pendente.

## Sondas

## Parecer
Reprovado só pelo A1, de documentação; o código está correto no que li e nada nele volta.

O que foi conferido, no head 8b056d4d contra a base 8a6f5907:
- Escopo e tamanho: cerca de 90 linhas de código no bin/forge-fechar (H1 dentro do teto); o laço chama o mesmo script por item ou pelo --lote, sem passo nem portão novo no merge; a recusa de opções fora do laço vem antes de qualquer leitura; o --dry-run lê e não fecha.
- forge-check pr com --ref refs/remotes/origin/<branch>: o branch_da_ref tira o prefixo e acha a branch, então os pareceres são os da branch do PR (lido em bin/forge-check:1945).
- O filtro JQ_LACO rodou no gh real, só leitura: devolve número, branch, mergeable e checks ruins por PR (5 PRs abertos hoje).
- O falso do gh no teste confere os argumentos exatos do pr view (checklist 12); o pedido_da_branch só aceita `branch:` do frontmatter com o nome inteiro, e o teste cobre o prefixo, o corpo e o arquivo sem frontmatter.
- Teste novo: tests.test_fechar_laco, 10 testes, OK em 9,9 s.
- Mutantes: as cinco specs rodaram com 1 processo, M1 a M33 morreram todos. O --cobertura só lista o bin/forge-fechar e o tests/pesos-d4.json como `não coberto`, que é o que ele diz de todo arquivo que não é Python.
- shellcheck: não tem nesta máquina; fica com o CI do PR, que segue em andamento no head 898c9f6e (os commits depois do 8b056d4d são só os pareceres de QA e de segurança).
- Commit em Conventional Commits, fragmento em changelog.d, módulo no mapa do bin/forge-testes e peso em tests/pesos-d4.json.

A1: o docs/fechamento-integrador.md é o manual do script, com a forma de uso de cada modo, a seção do lote e a linha de reversão com a medida. O --laco é um modo novo e precisa entrar nos três lugares: a forma (`bin/forge-fechar --laco [--base B] [--espera S] [--espera-ci S] [--dry-run]`), uma seção com C1 e C2, os códigos 5, 1, 3 e 0 e o aviso de 2 h, e, na reversão, a função `fechar_laco` e a opção `--laco`, com a medida (tempo do PR aprovado até a develop). A linha do `--lote` no agents/tech-lead.md:35 pode ganhar o `--laco` se couber no teto do agente; não é bloqueante.

A2 e A3 são recomendados e viram cartão depois do merge: só mudam quando o aviso sai, não o que se mescla.
- suíte: 8b056d4d81fc3c68596c10afb7ba41f8003efe19 rc=0 módulos=test_fechar_laco
