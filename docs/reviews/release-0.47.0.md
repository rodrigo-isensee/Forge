---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/release-0.47.0
commit: 51c51139b04881506718924895678cecb0a55453
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-13
---
# Review: release 0.47.0 (v047, E2.6)

Head revisado 51c51139 (classe C: plugin.json, CHANGELOG, placar), instância que não fez a entrega.

## Achados
- A1 (bloqueante) docs/engineering/placar-mutacao.md:18 · a linha gravada (mortos=49, invalido=0) não reproduz no head: `placar-mutacao.py --desde v0.46.0` deu mortos=62 invalido=1 specs=9; a spec escopo-ponto-2 M10 ficou inválida pelo #536; grave essa linha

## Sondas

## Parecer
Reprovado só pelo placar; o resto confere.

- Versão: `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` em 0.47.0 (eram 0.46.0); o marketplace.json não leva versão. `tests.test_changelog` OK (74 testes) e `forge-check docs` sem saída de erro.
- CHANGELOG: os 22 fragmentos apagados somam 23 linhas e as 23 aparecem, sem perda, em `## [0.47.0] - 2026-11-13` (5 Adicionado, 8 Alterado, 10 Corrigido); `changelog.d/` fica só com o README.
- Placar (medida, não portão): `envio-leve.json` não entra na amostra, pois não foi adicionada desde a v0.46.0 (a amostra é placar.json mais as 8 primeiras novas: mp1311-conferencia-janela, trava-agente-morto e -2 a -5, v0457-escopo-ponto-2 e -3). Ele roda sozinho com rc=0 e 5 mortos, então o rc=2 do relato não vem dele.
- Reprodução no head 51c51139: todas as specs rc=0 e sem sobrevivente, exceto v0457-escopo-ponto-2.json (rc=2: M10 inválido, "o trecho aparece 0 vezes", guarda movida pelo #536 afba389e, que o merge ce9a0c03 trouxe). O script trata isso como dado do placar, não como falha, e não pode sumir da linha. Linha correta no head: `placar: 0.47.0 mortos=62 sobreviveu=0 equivalente=0 invalido=1 sem-veredito=0 specs=9`.
- Recomendado, fora dos achados: a spec escopo-ponto-2 precisa de M10 atualizado (guarda movida), para a próxima release não repetir o inválido; é a mesma classe de envelhecimento que o placar mede.
