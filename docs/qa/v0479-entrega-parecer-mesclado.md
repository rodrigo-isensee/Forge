---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-parecer-mesclado
commit: aebace7125b5873038e1c4ffefbb512cd7e111b2
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0478 E50.14 (ENTREGA-PARECER-MESCLADO-ANTES-DO-AUTOR), revalidação no head `aebace71`

Head testado: `aebace71` (revalidação do reprovado em `8cff35a0`; A1 e A2 anteriores). Delta lido por `forge-check parecer delta` (de `8cff35a0`): `hooks/conformidade.py` (A5 da segurança, `PARECER_NO_TEXTO`), 14 fixtures `pp-sessao-forge-*`, specs de mutante 5 e 6, `tests/test_hooks.py`, `tests/test_selo_e_entrega.py`, `docs/hooks.md`, fragmento do changelog. Sem suíte local: a suíte inteira fica com o CI do PR.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A1 anterior: guarda da volta só com conferida (`and valido`) | `test_sem_conferida_a_regra_nao_vale` (agora na 1ª entrega) | 1ª entrega, `commit:` = Base-sha | M1 morreu |
| A2 anterior: fixture sem caminho pessoal | `scripts/verificar-contribuicao.sh` | caminho pessoal no diff | ok |
| E50.11 A5: variável no alvo e linha ilegível/acima do teto que citam pasta de parecer alheia recusam na sessão do Forge; dono livre; vizinho `reviewsx` e linha sem parecer livres | `test_hooks.test_fixtures_do_parecer_pelo_papel` | variável no alvo; teto; ilegível; vizinho de nome; dono | passou |
| E50.1/E50.5/E50.6 (regressão) | `ParecerMescladoNaVolta`, `ParecerDoMesmoPapelDoAutor` | `commit:` = Desde; papel do autor | 20 de 20 |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_selo_e_entrega.py -k ParecerDoMesmoPapelDoAutor -k ParecerMescladoNaVolta` → `Ran 20 tests ... OK`.
- `python3 -I -m unittest discover -s tests -p test_hooks.py -k fixtures_do_parecer_pelo_papel` → `Ran 1 test ... OK`.
- `bash scripts/verificar-contribuicao.sh` → `ok: nenhum segredo nem caminho pessoal no diff contra origin/develop.`
- `forge-mutante --cobertura --base 8a503799…`: toda condição mudada tem mutante (`coberta · … · declarado, não provado`); nenhuma linha sem mutante; `spec editada` em `v0457-escopo-ponto-2.json` e `v0478-guardas-conformidade.json` (o `de` de M4 e M5 reescrito para a nova condição, conferido no diff).
- Mutantes, rc 0 em todas: spec 1 `M1` a `M8 · morreu` (M1 `bin/forge-check:3245` agora morre); spec 5 `M25` a `M32 · morreu`; spec 6 `M33 · morreu` (`hooks/conformidade.py:3822`); spec editada `v0478-guardas-conformidade.json` `M1` a `M7` e `M12 · morreu`. Specs 2, 3 e 4 sem mudança no delta, não rerrodadas.
- Vermelho: cada mutante morto prova teste que cai sem a guarda; `forge-testes --vermelho` não rodado (estourou o prazo antes; não vale como vermelho).
- Pre-push: roda no envio (barato, sem suíte); resultado no relatório.
