---
tipo: review
contrato: 1
pedido: melhorias-de-projeto-1311
branch: melhoria/mp1311-pre-envio-modelo
commit: 2b5fbd83fb4776c16dd6668448b0accb9d0a9657
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-14
---
# Review: melhorias-de-projeto-1311 (pré-envio no modelo de projeto, E1.33; revalidação E1.56)

## Achados
- A1 (recomendado) bin/forge-upgrade:1 · o diff passa de 150 linhas de código e teste (cerca de 420, pelo numstat contra a base); o corpo do PR deve trazer `teto: excedido, <n> linhas, <motivo>` (M14).
- A3 (recomendado) templates/projeto/.githooks/pre-push:80 · `dev` não está no `local` de `so_docs` e vaza para o escopo global do hook; hoje sem colisão (nenhum outro `dev` no arquivo); acrescente-o à linha `local`.
- A4 (recomendado) templates/projeto/.githooks/pre-push:78 · `changelog.d/*` aceita qualquer arquivo da pasta (um `.sh` ou `.py` posto ali pula o pronto rápido); se a pasta for só de fragmentos, basta `changelog.d/*.md`, que o `*.md` já cobre, mais o `.gitkeep`.

## Sondas

## Parecer
Aprovado. Lido no head 27c40107 (E1.33) e revalidado por delta no 2b5fbd83 (E1.56).

## Delta
Delta lido: `forge-check parecer delta docs/reviews/mp1311-pre-envio-modelo.md` (rc=0), intervalo `27c40107..2b5fbd83` sem o que veio da develop: `migrations/0.47.1/LEIA-pre-envio.md`, `stacks/node-react/pronto.md`, `stacks/python/pronto.md`, `templates/projeto/.githooks/pre-push`, `templates/projeto/.githooks/pre-push.local`, `tests/mutantes/mp1311-pre-envio-modelo-4.json`, `tests/test_forge.py`, `tests/test_prepush_so_docs.py`. A seção do vermelho em TypeScript e o teste do home do runner vêm da develop (#533, #532), com pareceres próprios.

- Requisito: `so_docs` segue a DECISÃO DO DONO de 13/11 17:31 (só texto, parecer ou junção com a develop pulam o pronto rápido). Arquivo fora do texto pula só se o blob no ref enviado é igual ao da `origin/develop`; arquivo apagado, ausente na develop ou sem `origin/develop` roda tudo (conservador). `.github/*` segue recusado antes do texto.
- A2 do parecer anterior resolvido: `${arquivos[@]+"${arquivos[@]}"}` no `pre-push.local` não quebra com `set -u` em bash antigo.
- Guardas do diff (linhas 78, 80 e 81) com mutante declarado em `-4.json` (M30 a M32) e teste de comportamento de cada ramo de falha. `bin/forge-mutante --processos 1 tests/mutantes/mp1311-pre-envio-modelo-4.json`: M30, M31 e M32 morreram. `shellcheck` nos dois hooks: rc=0. `PreEnvioDoModelo`: 18 testes passam. Textos do `LEIA`, das stacks e do comentário batem com o comportamento.
- Suíte completa fica no CI do PR 555; não rerrodada aqui.
