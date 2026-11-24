---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-d1-integrador-laco
commit: 5f6c5db00109b919c31c383193e59e9fe34b1be9
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478

## Achados
- A2 (recomendado) bin/forge-fechar:1303 · mergeable UNKNOWN (o GitHub calcula sob demanda) nunca recebe o aviso de conflito: o PR em conflito não lido fica fora do aviso de 2 h. Sugestão: reler o mergeable pelo pr view do PR em UNKNOWN. Agora descrito como limite conhecido no manual (docs/fechamento-integrador.md:103).
- A3 (recomendado) bin/forge-fechar:1277 · O check bateria (pareceres) reprovado conta como vermelho (hoje o #865 tem 1 ruim só por ele): PR à espera dos portões há mais de 2 h recebe o aviso de parado. Sugestão: separar esse check na contagem. Agora descrito como limite conhecido no manual.
- A4 (recomendado) docs/fechamento-integrador.md:103 · "os de fora saem com uma linha do motivo" não vale para o PR fora de melhoria/* ou com nome inválido: o código (bin/forge-fechar:1312-1313) o pula calado. Sugestão: dizer no manual que esses saem sem linha, ou imprimir o motivo no script.

## Parecer
Aprovado. Revalidação por delta (`forge-check parecer delta`), intervalo 8b056d4d..5f6c5db0: só o docs/fechamento-integrador.md mudou (3 linhas), nada de código.

A1 resolvido: o manual traz a forma de uso do --laco (linha 11), a seção do laço ao lado da do lote (linha 103) e a reversão com a medida e o critério de 7 dias para o aviso de 2 h (linha 121, R-DECISAO).

Conferi o texto contra o código no head:
- Opções aceitas (só --base, --espera, --espera-ci, --dry-run): bin/forge-fechar:170-173.
- C1: gh pr list --state open --limit 100, ordem por número, sem fork (JQ_LACO, 1277; 1299); aviso de parado com conflito ou check ruim e último commit há mais de 7200 s ou data ilegível, em stderr, e o PR sai da volta (1302-1310); fetch, pedido_da_branch e forge-check pr --ref refs/remotes/origin/<branch> (1311-1316).
- C2: grupos de até 3 sem arquivo em comum, um item pelo fechamento de um item e mais pelo --lote (1318-1330); códigos 0, 3, 5 e 1 como descritos (1333-1343); --dry-run imprime o comando sem fechar (1328).
- FORGE_FECHAR_AGORA só com FORGE_FECHAR_TESTE=1 (225-231).
- Nomes da reversão (fechar_laco, JQ_LACO, segundos_de, pedido_da_branch, --laco) existem no script.
- O nome do check `bateria (pareceres)` é o do .github/workflows/ci.yml:740.

Teste que lê o arquivo tocado: tests.test_forge.GuiaDaPromocao, OK. Suíte inteira: fica com o CI do #865 (no head 5f6c5db0 ainda em andamento; a bateria (pareceres) vermelha é a deste parecer pendente).

A2, A3 e A4 são recomendados e viram cartão depois do merge.
- delta: 8b056d4d81fc3c68596c10afb7ba41f8003efe19..5f6c5db00109b919c31c383193e59e9fe34b1be9 docs/fechamento-integrador.md
