---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-parecer-mesclado
commit: 8cff35a0a8a65134b83fbd3841c4f3bb290269bc
parecer: reprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0478 E50.10 (ENTREGA-PARECER-MESCLADO-ANTES-DO-AUTOR), E50.6 (A4) e E50.7 (A3)

Head testado: `8cff35a0`. Delta lido por `forge-check parecer delta` (de `cdf62e0a`): `bin/forge-check` (A4), `hooks/conformidade.py` (barreira de papel), 21 fixtures, specs de mutante 3 e 4, `tests/test_hooks.py`, `tests/test_selo_e_entrega.py`. Sem suíte local: a suíte inteira fica com o CI do PR.

## Achados
- A1 (bloqueante) tests/mutantes/v0479-entrega-parecer-mesclado.json:M1 · o mutante M1 (tirar `and valido` da guarda da volta, `bin/forge-check:3245`) sobrevive; a spec o declara morto por `test_sem_conferida_a_regra_nao_vale`. Sobrevive também no `cdf62e0a` (`:3234`): falha do meu parecer anterior, que cortou a linha no `tail`. Sem teste, a regra vale na 1ª entrega com `commit:` = Base-sha. Teste novo ou equivalente justificado.
- A2 (bloqueante) tests/hooks/conformidade/pp-sessao-forge-outro-repo-dev-write-reviews-libera.json:15 · `scripts/verificar-contribuicao.sh` reprova o delta contra a base por `caminho pessoal`; o pre-push recusa o envio do head (o CI reprova igual). Troque o caminho ou marque `forge:exemplo`.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E50.1/E50.5: parecer mesclado na volta preso ao Desde e à pasta (regressão) | `ParecerMescladoNaVolta` | `commit:` = Desde; pasta do tipo | passou (junto com a classe do A4: 19 de 19) |
| E50.6 A4: parecer do papel do autor da volta só vale com `parecer conferido` do Jarvis, no blob do head | `ParecerDoMesmoPapelDoAutor` (sem linha, com linha, outra versão, sem autor conhecido, brief de outro pedido) | autor vazio (falha fechada); mesmo papel; outro pedido | passou |
| E50.7 A3: pastas de parecer só do papel dono na sessão do Forge (clone, `wt/*`, outro repositório, vizinho `reviewsx`, MultiEdit, Notebook, redirecionamento, `cp`, `git show`) | `test_hooks.test_fixtures_do_parecer_pelo_papel` (21 fixtures: bloqueios e liberações) | papel × pasta × forma; vizinho de nome; fora do Forge | passou |
| E50.1: guarda da volta só com conferida (`and valido`) | `test_sem_conferida_a_regra_nao_vale` | 1ª entrega | M1 sobrevive (A1) |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_selo_e_entrega.py -k ParecerDoMesmoPapelDoAutor -k ParecerMescladoNaVolta` → `Ran 19 tests ... OK`.
- `python3 -I -m unittest discover -s tests -p test_hooks.py -k fixtures_do_parecer_pelo_papel` → `Ran 1 test ... OK`.
- `forge-mutante --cobertura --base 8a503799…`: toda condição mudada em `bin/forge-check` e `hooks/conformidade.py` tem mutante declarado (só `declarado, não provado` e `coberta`; nenhuma linha sem mutante); `spec editada · tests/mutantes/v0457-escopo-ponto-2.json` (trecho do M12 reescrito).
- Mutantes, saída colada: spec 3 e 4 (`--processos 2`): `M17 · morreu · bin/forge-check:3035`, `M18 · :3245`, `M19 · hooks/conformidade.py:3748`, `M20 · :3755`, `M21 · :3757`, `M22 · :3758`, `M23 · :3778`, `M24 · :3779`, rc 0. Spec 2: `M9` a `M16 · morreu` (`:3028`, `:3001`, `:3014`, `:3002` ×2, `:3026`, `:3022` ×2), rc 0. Spec 1: `M2` a `M8 · morreu`, e `M1 · sobreviveu · bin/forge-check:3245`. Spec `v0457-escopo-ponto-2.json`: `M14`, `M15`, `M16 · morreu` no fim da saída; `M12` morreu no parecer anterior e a linha não foi relida.
- Vermelho: cada mutante morto nos itens do delta (M15 a M24) prova teste que cai sem a guarda; `forge-testes --vermelho` não rodado (estourou o prazo no head anterior; não vale como vermelho).
- Barreira A3 (E50.7): bloqueio para todo papel fora do dono, inclusive pela forma relativa ao topo da cópia (`wt/*`); o papel dono segue livre. A confirmação escrita da barreira é da segurança (E50.9), não minha.
