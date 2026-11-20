---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-sandbox-controle
commit: 8d9989d5973bde437b0a13f0252269c77bd15c3c
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E29.18, revalidação da A3 de SANDBOX-TRAVA-CONTROLE, head 0f55b08a; reval. no head 8d9989d5)

Revalidação (H3, R-REVIEW): li só `forge-check parecer delta docs/reviews/v0479-sandbox-controle.md`, intervalo `32c3528e..0f55b08a`, sem o que veio da `develop` (base `cf09782`). O delta tem sete arquivos no domínio. A suíte inteira fica no CI do PR #713 (pendente na leitura; bateria, instalação e árvore verdes). Rodei os testes do item: `python3 -m unittest tests.test_maquina.FilaPesada.test_post_de_outro_uso_mantem_e_dono_morto_sai tests.test_sandbox_controle` deu `Ran 15 tests ... OK (skipped=2)`, os dois do bubblewrap pulados aqui (sem namespace). Rodei também os mutantes mudados: `P10 · morreu · hooks/pesado.py:386` e `M19 · morreu · bin/forge-testes:155`.

Delta lido:
- `tests/test_sandbox_controle.py:113-115`: usa `_comum.Hook` em vez de `doutor.Hook`. É a mesma classe, e o `sys.path` continua limpo no `finally`.
- `tests/test_sandbox_controle.py:276-277`: compara o JSON, não o texto. O comentário explica por quê: o hook grava com `indent=1` e o `forge-init` grava compacto. O teste continua afirmando o conteúdo.
- `tests/test_sandbox_controle.py:301-303`: `lido()` agora percorre a árvore com `rglob`, então a pasta `run` dentro de `.forge/` também entra na comparação antes e depois do ataque. Isso aperta o teste.
- `tests/test_maquina.py:308-309`: afirma que o Post de outro uso não grava `null` na trava do projeto. Esse teste mata o P10, como a execução acima confirmou.
- `tests/mutantes/v0476-mp2-mp4-3.json` (P10) e `tests/mutantes/v0475-ci-custo-2.json` (M19): o texto `de` bate com a fonte (`hooks/pesado.py:386-387`, `bin/forge-testes:155`).
- `skills/fluxo-do-pedido/SKILL.md:44` e `skills/novo-projeto/SKILL.md:27`: os textos foram enxugados para caber no teto (ver A1).
- `docs/hooks-fixtures.md`: são as linhas da tabela gerada para `falha-*` e `permissao-*`, que acompanham a soltura por `null`.

## Achados
- A1 (recomendado) skills/fluxo-do-pedido/SKILL.md:44 · o corte tirou "só o dono muda, fora do sandbox; o agente não grava o .forge/config.json", e a regra 12 de docs/economia-de-tokens.md não diz isso. Assim, o Jarvis pode tentar `forge ritmo` e esbarrar no sandbox. A frase curta de novo-projeto:27 cabe aqui.

## Revalidação (delta 0f55b08a até 8d9989d5, E29.18)
Li `forge-check parecer delta docs/reviews/v0479-sandbox-controle.md` (intervalo `0f55b08a..8d9989d5`). Ele lista quatro arquivos no domínio: `bin/forge-testes`, `docs/hooks.md`, `hooks/agentes.py` e `tests/pesos-d4.json`. Também avisa que o merge `c263d75` não está na `develop`, por isso conta inteiro. Esse merge só junta a própria branch. Os três primeiros arquivos vieram da `develop` (`cf09782`) pelo merge `3acd2ad9`, e o segundo pai desse merge está na `origin/develop`.
- `3acd2ad9`: houve conflito só em `hooks/agentes.py:71-73`, na linha de import. A resolução junta os dois lados: `ler_trava` da branch e `_json_raso` da develop. O patch da branch contra a develop nova é o mesmo de antes: comparei `diff merge-base..0f55b08a` com `diff cf09782..3acd2ad9`, e a única diferença está nos pareceres. `py_compile` ok.
- `8d9989d5` `tests/pesos-d4.json:175`: entra `"test_sandbox_controle": 1.7` em ordem alfabética, e o JSON é válido. Rodei `test_sandbox_controle` no head, com ambiente limpo e `-I`: `Ran 14 tests ... OK (skipped=2)`.
Sem achado novo. A suíte inteira roda no CI do PR #713, ainda pendente na leitura. A catraca falhou só no texto do PR (seções "Projeto de origem" e "Como medir"). Isso é do PR, não do código.

## Parecer
Aprovado. As correções do CI só ajustam os testes à gravação real (JSON com indentação, pasta `run`, soltura por `null`) e deixam os mutantes P10 e M19 vivos na fonte e mortos pelos testes declarados.
