---
tipo: review
contrato: 1
pedido: v0457
branch: melhoria/escopo-ponto
commit: 73e4848c3d431b8ac2e99beff0d0b63f2d054284
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-12
---
# Review: v0457 (E23.49, melhoria/escopo-ponto no 73e4848c)

Revalidação por delta (E23.49), por instância que não fez a entrega. Delta lido: `forge-check parecer delta docs/reviews/escopo-ponto.md`, intervalo c51ecb4847bcac295a72bf42f0dec8ab44f1538e..73e4848c3d431b8ac2e99beff0d0b63f2d054284, no domínio bin/forge-check, changelog.d/escopo-ponto.md, tests/mutantes/v0457-escopo-ponto-{3,4,5}.json, tests/test_selo_e_entrega.py. Testes dos arquivos tocados, um módulo por vez: `test_selo_e_entrega` 70 OK; `test_conf_escopo` 16 OK.

## Achados
- A6 (recomendado) bin/forge-check:2351 · veredito_trocado faz um `git show` por arquivo da pasta em cada versão (docs/reviews/ tem 310): 7,9 s medidos no próprio repositório para 4 versões; filtrar antes com `git grep -l <commit> <sha> -- <pasta>` ou `cat-file --batch`

## Sondas
- S2 · refeita: só o brief de devops selado como o real (Etapa: review, Agente destino: forge:devops-engineer, Revisar-sha = head) e docs/devops/x.md revisao-devops · espera: escopo ok (anexo do portão) · obtido: rc 0, escopo ok anexo de devops (no c51ecb48, rc 1)
- S4 · o mesmo com o brief selado `Etapa: devops` (a etapa antiga, fora do vocabulário do brief selar) · espera: fora do declarado · obtido: fora do declarado "docs/devops/x.md"

## Revalidação dos achados anteriores
- A4 resolvido: ETAPA_DO_PORTAO leva revisao-devops a `review` (bin/forge-check:2321) e revisados_selados exige o `Agente destino:` do papel do tipo (bin/forge-check:2331), com teste nos dois sentidos (review não ancora devops e o inverso) e M29, M30; a fixture sela a etapa real com o papel (tests/test_selo_e_entrega.py:718).
- A5 (segurança) conferido sem achado de review: a busca do veredito trocado cobre todos os arquivos da pasta com `branch:` igual, na base e em cada commit do intervalo; rev-list e ls-tree que falham contam como trocado, cada um com teste por mock (M22, M32), e o S3 da segurança virou teste (M31). O mérito da âncora fica com o parecer do security-engineer.
- Specs de mutantes (AR-12): os 33 `de` de tests/mutantes/v0457-escopo-ponto*.json casam uma vez só com o bin/forge-check do head. Não achei log do forge-mutante sobre o 73e4848c (os escopo-ponto.mutante*.log são da manhã); "M1 a M33 mortos, cobertura rc 0" é declaração do autor e fica com o QA.
- forge-check pr (bin/forge-check:1610) escolhe o parecer vigente por (data, nome) e não detecta um parecer forjado na pasta: não é bloqueante desta branch. A linha não está no diff desde o Base-sha (o comportamento é anterior), o `forge-check pr` já cobra autoria por papel (bin/forge-check:1624) e o `parecer conferido` do Histórico (T-1), e a entrega desta branch agora recusa o forjado. Vira cartão para a versão seguinte, junto do L08/G2 da rodada anterior.

## Tamanho (M14)
bin/forge-check (168) e tests/*.py (467): 635 linhas desde o Base-sha. O PR precisa trazer `teto: excedido, 635 linhas, <motivo>`; o motivo (consertos da mesma conferência em duas voltas, volume nos testes dos ramos negativos) basta.

## Parecer
Aprovado: A4 resolvido e provado pela S2 refeita; o delta não traz defeito provado. A6 é recomendado (custo, sem defeito). A segurança das âncoras e o veredito trocado ficam com o security-engineer; a mutação, com o QA.
