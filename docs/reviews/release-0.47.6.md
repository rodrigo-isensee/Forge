---
tipo: review
contrato: 1
pedido: release-0.47.6
branch: melhoria/v0476-release-0476
commit: 00fa5c76561332e52eed0dca9c077f4db8adc15c
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: release-0.47.6

Code review da versão 0.47.6 inteira no head 00fa5c76 (marca da release na branch melhoria/v0476-release-0476, base develop 9ae3e442), para integrar na develop e promover à homolog (v0474 E4.41). Os dois pareceres, `docs/reviews/v0476-release-0476.md` e `docs/reviews/release-0.47.6.md`, têm o mesmo veredito e o mesmo conteúdo.

## Sondas

## Parecer
Aprovado.

- Leva: `git log --first-parent v0.47.5..00fa5c76` traz 6 entradas: MP6 #659 (71f280f2), diretriz 36 #661 (d48993e6, com o rótulo de regra protegida apertada no título), MP3 #662 (038249c5), núcleo do Jarvis #666 (8f9c0c52), dependências da stack #660 (9ae3e442) e a marca (00fa5c76). `v0.47.5` (ebda96d3) é ancestral do head.
- Pareceres dos itens: review, QA e segurança `parecer: aprovado` em `docs/{reviews,qa,security}/` para v0476-mp6 (93d21712), v0475-dir36 (42af552e), v0476-mp3 (2be06289), v0476-nucleo-teto (8a91fe3b) e v0476-stack-deps (8727471d); não refeitos aqui (`R-REVIEW`).
- Escopo: `git diff --name-only v0.47.5 00fa5c76` dá 194 arquivos; a união dos arquivos das cinco junções cobre todos, menos os 3 da marca (`.claude-plugin/plugin.json`, `dev/.claude-plugin/plugin.json`, `CHANGELOG.md`). Nada fora dos itens.
- Junção: arquivos tocados por mais de um item: `agents/jarvis.md` (diretriz 36, MP3, núcleo), `bin/forge-copia` e `tests/test_forge_copia.py` (MP6 e dependências da stack). Em 00fa5c76, `bin/forge-copia` traz as duas mudanças (`forge_disco` na linha 20, `--instalar` na linha 104) e o Jarvis manda ler `skills/trabalho-em-paralelo/ritmo-e-corte.md` (linha 37), o conserto do teto do #666. Testes no head (discover, `-I`, ambiente limpo): `test_forge_copia` 36 OK, `test_jarvis_nucleo` 43 OK, `test_changelog` 89 OK.
- Marca: `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` em `"version": "0.47.6"`; `CHANGELOG.md` com `[Não publicado]` vazio (linha 5) e `[0.47.6] - 2026-11-18` (linha 7) acima de `[0.47.5]` (linha 19), em português, com Adicionado, Alterado e Corrigido.
- Fragmentos: cada linha `- ` dos 5 fragmentos apagados na marca (lidos em 00fa5c76^) aparece uma vez no `CHANGELOG.md` (`grep -cxF`: 1 nas 7); `changelog.d/` só traz o `README.md`; `bin/forge-changelog conferir-release`: "ok: changelog.d/ sem fragmentos pendentes".
- CI: o head ainda não tem execução (`gh run list --commit 00fa5c76`: vazio) nem PR; a suíte inteira fica no CI do PR da marca para a develop, obrigatório para a integração (`R-REVIEW`), não rerrodada aqui; a local falha por ambiente (sandbox: /proc e gh).
