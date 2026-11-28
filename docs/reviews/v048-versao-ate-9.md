---
tipo: review
contrato: 1
pedido: v048
branch: melhoria/v048-versao-ate-9
commit: c727c89722a5a68b336f7e7e296d02ffa5272cc9
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-27
---
# Review: v048 (VERSAO-PATCH-ATE-9, #951)

1ª rodada completa (E2.2) do commit c727c89 sobre a Base-sha b414714.

## CI
- ci: c727c89722a5a68b336f7e7e296d02ffa5272cc9 verde
- Run 46084959115, headSha conferido: suíte 1/5 a 5/5, instalação, passos, verificações longas, python 3.14, teto de pulados e árvore provada verdes; `bateria` e `bateria (pareceres)` esperam os pareceres.

## Verificações
- Testes afetados (`tests.test_forge_contador`, `tests.test_changelog`): 119 testes, OK.
- Mutantes declarados (`tests/mutantes/v048-versao-ate-9.json`, 1 processo): M1, M2 (`bin/forge-contador:49`), M3, M4 (`bin/forge-changelog:191`) morreram.
- `forge-mutante --cobertura --base b414714`: as duas guardas mudadas cobertas, rc=0.
- Tamanho (H1): 9 linhas de código, um comportamento.

## Achados
- A1 (recomendado) .claude/CLAUDE.md:17 · a regra de versão (SemVer, correção → patch) não diz que o patch para no .9 e que depois vem X.(Y+1).0; quem lê só o CLAUDE.md não sabe do corte que as ferramentas já aplicam

## Sondas

## Parecer
Aprovado. Limites conferidos: `versao_seguinte` com 0.47.9 e 0.47.19 dá 0.48.0, 0.48.0 dá 0.48.1, 0.48.8 dá 0.48.9, 0.48.9 dá 0.49.0 (testados); o 0.47.20 da develop cai no mesmo `>= 9` e dá 0.48.0. A release recusa 0.47.10 e 0.47.20 com saída 1, sem gravar CHANGELOG, manifesto nem apagar fragmento, e aceita 0.1.9 (limite); a mensagem cita a versão certa. O `--anexar` sai antes da guarda, sem mudança.

Ferramentas que calculam versão: o `bin/forge-fechar` V4 lê a versão do `forge-contador` e a V5 passa essa mesma versão ao `forge-changelog release`, então o corte vale nos dois passos; o `bin/forge-voltar-versao` não calcula versão (volta para a tag anterior guardada), e nenhum outro script de `bin/`, `scripts/` ou `hooks/` soma patch. Os dois testes antigos de 1.4.9 agora esperam 1.5.0, coerentes com a regra. Commit em Conventional Commits, fragmento em `changelog.d/`.

A1 é recomendado (documentação), vira cartão depois do merge.
