---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-sandbox-controle
commit: 0f55b08af4c05c01bd03e02b0deecbbc4550b3db
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E29.18, revalidação da A3 de SANDBOX-TRAVA-CONTROLE, head 0f55b08a)

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

## Parecer
Aprovado. As correções do CI só ajustam os testes à gravação real (JSON com indentação, pasta `run`, soltura por `null`) e deixam os mutantes P10 e M19 vivos na fonte e mortos pelos testes declarados.
