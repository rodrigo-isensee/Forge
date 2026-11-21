---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-vigia-resumo-compactado
commit: 06a0220a908ce4a467361b9935e500b3c0d62af5
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0479-vigia-resumo-compactado

Etapa E93.2, cartão FALA-DO-DONO-RESUMO-COMPACTADO, diff `fb3b670b..06a0220a` (9 arquivos; código: `hooks/vigia.py`, +23 −4, dentro do teto H1).

## Achados
- A1 (recomendado) hooks/vigia.py:308 · `chave.startswith("is")` pega qualquer campo que comece por "is" com valor verdadeiro, não só marcas: sonda com `issueRef: "x"` num registro digitado devolveu None. Trocar por `re.match(r"is[A-Z]", chave)`; sem campo assim nas transcrições de hoje, não bloqueia.

## Parecer
Aprovado.

- **Escopo:** o classificador positivo `digitado_pelo_dono` troca o filtro negativo; `texto_do_dono` mantém assinatura e contrato (str ou None) e só delega a forma do registro. `hooks/meta.py:31,156` (`fala_do_dono`) segue certo: chama `texto_do_dono` como antes e só fica mais estrito (resumo de compactação e aviso de tarefa deixam de virar "fala do dono" na medida de jargão), que é o que o cartão pede. As 32 fixtures de `meta` passam no head.
- **Registro sem `origin` contando (forma antiga do cliente):** escolha certa. O vigia só avisa (F10, nunca bloqueia) e o meta só mede; recusar a forma antiga calaria o aviso em toda transcrição de cliente anterior ao campo, falso negativo sem ganho. O risco do lado aberto está coberto pelas outras guardas: o resumo de compactação real vem sem `origin`, mas com `isCompactSummary`, e cai na guarda `is*` (teste `test_resumo_de_compactacao_nao_conta` monta exatamente essa forma). `origin` presente e malformado (`None`, string, dict sem `kind`) falha fechado (sonda: `origin: None` dá None).
- **Guardas e mutantes:** 5 linhas de guarda mudadas, 6 mutantes declarados (inclui o default de `origin` e a delegação), todos mortos, cada um com teste de comportamento do ramo de falha; nenhum teste lê a fonte.
- **Documentação:** `docs/hooks.md` e o índice `docs/hooks-fixtures.md` (3377, vigia 54) atualizados; fragmento em `changelog.d/`.
- **Commit:** um só, Conventional Commits em português, com a etapa.
- **Suíte:** inteira só no CI do PR; aqui rodei só o recorte do brief.

Provas (rodadas no head 06a0220a, ambiente limpo com `env -i` e TMPDIR de `mktemp -d`):
- `python3 -m unittest tests.test_vigia`: `Ran 10 tests ... OK`.
- fixtures `vigia` e `meta` pelo `executar_em_lote` do `test_hooks` (runner equivalente ao `so_vigia.py`, com as duas pastas): `fixtures vigia+meta: 86`, `OK`.
- `bin/forge-mutante --processos 1 tests/mutantes/v0479-vigia-resumo-compactado.json`: M1 a M6 `morreu` (vigia.py:306, 308, 310, 313, 312, 319).
