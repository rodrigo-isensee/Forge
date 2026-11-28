---
tipo: review
contrato: 1
pedido: release-0.47.10
branch: melhoria/v0479-release-04710
commit: e4f6238dfde392141c656171913a4358aea65002
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-19
---
# Review: release-0.47.10

Code review da versão 0.47.10 inteira no head e4f6238d (marca da release na branch melhoria/v0479-release-04710, base develop 5ae868eb), para integrar na develop e promover à homolog (v0478 E40.2). Os dois pareceres, `docs/reviews/v0479-release-04710.md` e `docs/reviews/release-0.47.10.md`, têm o mesmo veredito e o mesmo conteúdo.

## Parecer
Aprovado.

- Ponto de partida: a marca da 0.47.9 na develop, 9e88262f (#691), até e4f6238d. `git log --first-parent 9e88262f..e4f6238d` traz 9 itens mais a marca: catraca-movidas #687 (c720891e), mp8-maquina #696 (74cf0318), mutante-lote #692 (eca1d21b), meta85-recomendado #699 (b23124f8), placar-fases #700 (8fe02a42), selecao-testes #695 (29e8c6fd), guardas-conformidade #697 (153c0152), placar-varredura #702 (aa16e1a7) e guardas-parecer #698 (5ae868eb).
- Pareceres dos itens (não refeitos, `R-REVIEW`): cada item entrou na develop com os próprios pareceres.
- Marca (e4f6238d, 12 arquivos, 28+/34-): `git diff --stat 5ae868eb e4f6238d` mostra só os dois `plugin.json`, o `CHANGELOG.md` e os fragmentos apagados.
- Versão: `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` em `"version": "0.47.10"` (antes 0.47.9); `CHANGELOG.md` com `[Não publicado]` vazio (linha 5) e `[0.47.10] - 2026-11-19` (linha 7) acima de `[0.47.9]` (linha 33), em português, com Adicionado, Alterado e Corrigido.
- Fragmentos: 9 fragmentos apagados na marca (lidos em 5ae868eb, um por item); as 21 linhas de conteúdo deles aparecem no `CHANGELOG.md` (conferência por trecho de 80 caracteres: 21 ok, 0 faltando); `changelog.d/` só traz o `README.md`.
- Ferramentas no head: `bin/forge-changelog conferir-release`: "ok: changelog.d/ sem fragmentos pendentes" (rc 0); `scripts/validar-plugin.sh`: "Validation passed" nos dois manifestos (rc 0; o sandbox nega só api.anthropic.com, sem efeito na validação).
- SemVer: há Adicionado (ferramentas e opções novas, compatíveis) e nada quebra os projetos; a marca sobe o patch (0.47.9 para 0.47.10), como as versões 0.47.x anteriores da série, sem bloqueio.
- Suíte: a suíte local falha por ambiente (sandbox: /proc e gh) e não foi rerrodada; a prova da marca é o CI do PR para a develop, obrigatório para o integrar.
