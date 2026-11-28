---
tipo: review
contrato: 1
pedido: v048
branch: melhoria/v0481-ambiente-claude-path
commit: 75f2e456414d0cb3e8e6e32c3afd1752798db61d
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-28
---
# Review: v048 (E13.22, PR #965, volta 1, delta df4b2bf9..75f2e456)

Revalidação. Li só `forge-check parecer delta docs/reviews/v0481-ambiente-claude-path.md`: intervalo df4b2bf9..75f2e456, no domínio só `scripts/preparar-estacao.sh` (+1 linha, `# shellcheck disable=SC2016` com motivo acima da 197).

## Achados
- A1 (bloqueante) scripts/preparar-estacao.sh:198 · o CI do head segue vermelho pelo diff: a regex nova desta linha deixou M7, M12 e M16 de tests/mutantes/v0480-ambiente-recriacao.json (linhas 66, 116, 156) com o `de` fora da fonte, e a suíte parte 4/5 cai em test_forge_mutante.py:1564. Alinhe as três trocas.
- A2 (recomendado) tests/test_guia_varios_projetos.py:31 · o teste novo é a 2.ª linha que cita README.md, e a lista em tests/test_reval_delta.py:147 diz 1. A suíte parte 1/5 do 4ac2698e cai em test_reval_delta.py:195. Suba a contagem para 2; sem isso o CI segue vermelho.

## Sondas
- S1 · `python3 -m unittest tests.test_forge_mutante.ConferirTodas` · espera: OK (na base a1971853 dá OK) · obtido: FAILED no 75f2e456 e no df4b2bf9, M7, M12 e M16 de v0480-ambiente-recriacao.json
- S2 · `python3 -m unittest tests.test_reval_delta.Guarda.test_caminho_de_texto_so_e_citado_como_a_lista_conhece` · espera: OK (na base dá OK) · obtido: FAILED no 4ac2698e, `README.md: 2 linhas, a lista diz 1`

## Delta lido
- A1 da 1.ª rodada resolvido: `shellcheck scripts/preparar-estacao.sh` no 75f2e456 sai 0. A diretiva tem motivo e segue o padrão da linha de baixo.
- O descendente 4ac2698e só muda docs/qa/ e docs/security/ (2 arquivos, +21/-30) e tira o caminho pessoal: `scripts/verificar-contribuicao.sh` dá ok, e a bateria (passos) do run 46167394478 passou.
- A1 repete o bloqueante da 1.ª rodada: a mesma linha da regex ainda deixa o CI vermelho, agora na suíte. No df4b2bf9 a suíte não rodou, porque a bateria (verificações longas) caiu antes no SC2016. O A2 é novo e fora do delta, então fica recomendado (G1.2), mas derruba o CI que o merge exige.

## Verificação
- CI do 4ac2698e (run 46167394478, descendente só com pareceres): suíte partes 1/5 e 4/5 vermelhas (A2, A1), o resto verde fora bateria (pareceres), bateria e catraca. Sem CI verde, sem linha `ci:`.

## Parecer
Reprovado. O delta está correto, mas o CI do head que a segurança deixou está vermelho por dois defeitos do próprio diff, os dois provados (S1, S2), e sem CI verde não há aprovação (PARECER-LE-O-CI). Volta ao autor: alinhar M7, M12 e M16 da spec v0480 e subir para 2 a contagem do README.md em tests/test_reval_delta.py:147. Antes do envio, ele roda local os dois testes das sondas. A2 e A3 da 1.ª rodada continuam recomendados e viram cartão.
