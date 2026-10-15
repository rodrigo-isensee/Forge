---
tipo: qa
contrato: 1
pedido: anti-alucinacao-portao
branch: melhoria/anti-alucinacao-portao
commit: 3c55bce
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-15
---
# Parecer de QA: portão do parecer no Forge (fatia 3 do anti-alucinação)

Escopo: o hook `parecer` no clone do Forge (cópia principal e worktree) e o modo `pareceres` da catraca, conforme a linha "| 3 |" da seção 11 da proposta. Review de autor, review independente e segurança já aprovados (`docs/reviews/anti-alucinacao-portao.md`, `docs/reviews/anti-alucinacao-portao-independente.md`, `docs/security/anti-alucinacao-portao.md`). Sem UI: acessibilidade e E2E de navegador não se aplicam.

## Método
Os hooks vieram de `git archive origin/melhoria/anti-alucinacao-portao` (HEAD 3c55bce) num diretório descartável em `$TMPDIR`. Cada cenário monta do zero, com `HOME` isolado, um repositório git que simula o clone (`~/Forge` com `.claude-plugin/plugin.json`, sem `.forge/versao`), uma worktree em `~/.forge-contrib/wt/` e um projeto comum (`.forge/versao`). O hook real `hooks/parecer.py` recebe o JSON de `PreToolUse` no stdin; o rc é a saída do processo. Para o vermelho antes do verde, a mesma bateria rodou com `git archive origin/melhoria/anti-alucinacao-regras` (o hook anterior).

## PQ-1: ponta a ponta pelo hook real (rc)
| Cenário | Esperado | Clone (cópia principal) | Worktree | Projeto comum | Hook anterior: clone / projeto |
|---|---|---|---|---|---|
| `gh pr create --draft`, sem parecer | 0 (clone) | 0 | 0 | 2 | 0 / 2 |
| `gh pr create` sem `--draft`, parecer reprovado | 2 | 2 | 2 | 2 | 0 / 2 |
| `gh pr ready`, sem parecer | 2 (clone) | 2 | 2 | 0 | 0 / 0 |
| `gh pr ready`, parecer aprovado | 0 | 0 | 0 | 0 | 0 / 0 |
| `gh pr merge`, parecer reprovado | 2 | 2 | 2 | 2 | 0 / 2 |

- **Vermelho:** no hook anterior, o clone dava rc 0 nos cinco cenários, incluindo os três que agora barram. O teste falha sem a implementação.
- **Projeto comum:** a coluna "Projeto comum" é idêntica à do hook anterior nos cinco cenários. Nenhum projeto muda de comportamento. Nota: no projeto, `--draft` não dispensa o parecer (rc 2) e `gh pr ready` não é conferido (rc 0); é o desenho, e já é assim antes da fatia.

## PQ-2: catraca, modo `pareceres`, dois pedidos
Repositório descartável: a branch toca `hooks/novo.py`; dois pareceres de review (`a`, `b`) com `branch: feature/x`; `--base-ref develop`.
| Pedido a | Pedido b | rc (3c55bce) | rc (anterior) |
|---|---|---|---|
| aprovado | reprovado | **1** | 0 |
| reprovado | aprovado | **1** | 0 |
| aprovado | aprovado | **0** | 0 |

A segunda linha cobre a ordem inversa, que o conserto do laço precisava fechar (o `return []` aprovava a branch pelo primeiro pedido limpo).

## PQ-3: as mensagens de recusa dizem o que fazer (clone, saída real do hook)
- `create` sem `--draft`, reprovado: `R-REVIEW: sem parecer aprovado, abra com gh pr create --draft; docs/reviews/p1-1.md: parecer: o último parecer não é aprovado; confira com forge-check pr p1.`
- `ready`, sem parecer: `R-REVIEW: PR sai do rascunho só com parecer: nenhum parecer em docs/reviews/ e docs/qa/ com `branch: feature/x`; faça o code review e o QA (R-QA) antes do PR ou do merge (devops e segurança, quando h…` (cortada em 200 caracteres, o limite do hook; a ação já está inteira antes do corte).
- `merge`, reprovado: `R-REVIEW: docs/reviews/p1-1.md: parecer: o último parecer não é aprovado; confira com forge-check pr p1.` (a mesma mensagem que o projeto já recebe).
- Catraca: `R-REVIEW: PR toca hooks/novo.py (e outros 0) sem parecer aprovado de review (docs/reviews/b-1.md: parecer: o último parecer não é aprovado (R-REVIEW)). Por quê: ... Corrigir: peça o parecer e confira com `bin/forge-check pr <pedido>` (parecer com `branch: feature/x`) (docs/regras/R-REVIEW.md)`.

Todas começam com o ID da regra, têm uma linha só, citam o arquivo ou o comando e indicam a saída (`--draft`, fazer o review e o QA, `forge-check pr`). Observação sem bug: na recusa de `merge`, a mensagem aponta o parecer e o comando de conferência, e não diz explicitamente "peça novo parecer aprovado"; é o texto que os projetos já recebem, fora desta fatia.

## PQ-4: suíte
`python3 -m unittest tests.test_hooks tests.test_catraca -v 2>&1 | tail -3` em 3c55bce: `Ran 140 tests in 88.665s` / `OK`. A fixture do projeto (`pr-draft-em-projeto-sem-parecer-bloqueia`, `pr-ready-em-projeto-libera`) e as 59 anteriores seguem verdes. A suíte completa do repositório e o `validar-plugin.sh` ficam com o pre-push e o CI.

## Tabela obrigação → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Linha 3, PQ-1 (create e merge reprovado barram no clone) | cenários 2 e 5, clone e worktree | worktree fora do `.git` principal | passou (rc 2) |
| PQ-2 (`--draft` sem parecer passa; `ready` sem parecer barra) | cenários 1 e 3 | rascunho vs. pronto | passou (rc 0 / rc 2) |
| `gh pr ready` com parecer aprovado não gera bloqueio falso | cenário 4 | parecer aprovado | passou (rc 0) |
| PQ-3 (catraca acumula pedidos) | `qa_catraca`, 3 combinações | ordem alfabética dos pedidos; reprovado em segundo | passou (rc 1/1/0) |
| PQ-4 (projeto inalterado) | os 5 cenários em projeto, contra o hook anterior | projeto com `.forge/versao` | passou (idêntico) |
| R-QA vermelho antes do verde | mesma bateria contra 354ad7d | n/a | falhava (rc 0 no clone, rc 0 na catraca) |

## Fora do escopo (cartões já registrados)
A1, A2, os textos de `docs/hooks.md` e `agents/tech-lead.md`, C1 a C8 e S8 não foram reabertos. Não verificado: comportamento real do GitHub (sem rede nem PR de teste), como declarou a segurança.

## Bugs
Nenhum aberto. Nada em `docs/qa/bugs/`.
