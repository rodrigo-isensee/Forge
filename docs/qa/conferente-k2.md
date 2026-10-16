---
tipo: qa
contrato: 1
pedido: conferente-k2
branch: melhoria/conferente-k2
commit: ef3ef4d9bd136d0d1b67c4245aa2b401ca4d94c0
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-16
---
# QA - conferente confiável, fatia K2 (`forge-check brief`, `brief gerar`, passada única)

Sem UX nem API. Código testado em ef3ef4d (merge da develop 4922609 sobre a implementação 6d3f41b); o HEAD da branch (5cd602e) só acrescenta os pareceres de review e de segurança (`git diff --stat ef3ef4d..HEAD`: só `docs/reviews/` e `docs/security/`). Obrigações: PQ-1 a PQ-13 de `docs/briefs/k2-tech-lead-3.md`, decisão técnica do time (acréscimo `forge-check brief` em `hooks/conformidade.json`), `R-QA`, `R-BRIEF`, `R-PROVA`, `R-TETO` (load 0.64 e 6,9 GB livres antes da suíte; uma suíte por vez).

## Critério -> teste -> resultado
| ID | Obrigação | Teste (comando real) | Fronteira protegida | Resultado |
|---|---|---|---|---|
| PQ-1 | Classe `ConferirBrief` verde | `python3 -m unittest -v tests.test_forge.ConferirBrief` | n/a | `Ran 25 tests` / `OK` |
| PQ-2 | Etapa de outro papel não é corte | `bin/forge-check brief tests/fixtures/brief/etapa-outro-papel.md --pedido tests/fixtures/brief/pedido.md` | E3 retirado por E3.1-E3.3 | `corte: etapa (ok) "E3" por E3.1, E3.2, E3.3`; `resultado: aprovado`; rc=0 |
| PQ-3 | Corte sem marca reprova | idem com `corte-sem-marca.md` | item retirado sem a marca | `corte: sem marca "E2" (item de ## Escopo retirado sem a marca)`; `resultado: reprovado`; rc=1 |
| PQ-4 | Saída determinística | `for i in 1 2 3; do ... \| md5sum; done \| sort -u \| wc -l` | 3 execuções | `1` |
| PQ-5 | Suíte completa | `python3 -m unittest discover -s tests -q` | n/a | `Ran 685 tests in 237.388s` / `OK` |
| PQ-6 | Plugin válido | `scripts/validar-plugin.sh` | n/a | `Validation passed` |
| PQ-7 | "todos os achados" nos 3 textos | `grep -q ... agents/conferente.md && ... docs/regras/R-BRIEF.md && ... agents/jarvis.md` | os 3 arquivos | rc=0 |
| PQ-8 | `gerar` copia as decisões | `bin/forge-check brief gerar --pedido ... \| grep -q 'DECISÃO DO DONO'` | n/a | rc=0 |
| PQ-11 | `gerar` traz a marca de corte | `... \| grep -q 'Retira do escopo original'` | n/a | rc=0 |
| PQ-12 | Acréscimo único no hook | `grep -c '"forge-check brief"' hooks/conformidade.json` | exatamente 1 | `1` (na develop: 0) |
| PQ-13 | Só `conformidade.json` mudou em hooks/ | `git diff --name-only origin/develop -- hooks/` | nenhum outro arquivo | `hooks/conformidade.json` |
| PQ-9 | Nada removido em `tests/config.json` | `git diff origin/develop...HEAD -- tests/config.json \| grep '^-[^-]'` | só acréscimo | saída vazia |
| PQ-10 | Push da branch | `git ls-remote origin refs/heads/melhoria/conferente-k2` vs `git rev-parse HEAD` | n/a | ambos `5cd602e65a22d30706998483726751aed7bc10e0` |
| V-1 | Pareceres e frontmatter contra a base | `bin/forge-check pr conferente-k2 --ref HEAD --base origin/develop` | n/a | antes deste commit só faltava `docs/qa` (este arquivo): "sem parecer para o pedido `conferente-k2` (R-QA)"; refeito depois do commit pelo integrador |

## Exploratório (cópia em `$TMPDIR`, briefs reais intocados)
| Caso | Entrada | Resultado |
|---|---|---|
| a | `etapa-outro-papel.md` | `corte: etapa (ok) "E3" por E3.1, E3.2, E3.3`; `E1`, `E2` ok no Entregar; aprovado |
| b | `corte-sem-marca.md` | `corte: sem marca "E2"`; `resultado: reprovado`; rc=1 |
| c | `pq-cmd-sem-espera.md` e variante (brief aprovado com ` · espera:` removido por `sed`) | `forma: PQ-2 sem espera`, `espera ausente`; reprovado nos dois |
| d | `brief gerar` sobre o pedido sintético | as 2 linhas `DECISÃO DO DONO` do pedido aparecem literais (com o prefixo `- `); modelo de corte traz `PREENCHER` (a ser preenchido pelo Jarvis, esperado) |
| e | `brief` e `brief gerar` 3 vezes cada | 2 hashes distintos, 3 ocorrências cada: mesma entrada, mesma saída |
| f | hook `conformidade` com `agent_type: forge:conferente`, projeto git temporário com `.forge/versao` (mesmo método de `tests/test_hooks.py`) | liberados (rc=0): `forge-check brief <arq> --pedido ...`, `forge-check brief gerar ...`, `forge-check pr p1`. Recusados (rc=2, R-CONFORMIDADE): `forge-check merge`, `rm -rf docs`, `forge-check brief x.md; rm a`, `forge-check brief x.md > saida`, `gh pr merge 1`, `git push origin x` |
| g | clone temporário, fragmento renomeado para `changelog.d/outro-nome.md` | `FragmentoTemONomeDaBranch` falha: `fragmento de changelog.d/ sem o nome da branch 'melhoria/conferente-k2' (esperado <branch-sem-prefixo>.md)`; com o nome certo: `OK` |

## Vermelho antes do verde
Os casos b, c e g são o vermelho observado: a mesma ferramenta e o mesmo teste, com a entrada errada, falham pelo motivo exato (marca, espera, nome do fragmento); com a entrada certa (a, PQ-2, fragmento original) passam. Não rodei os testes novos contra o commit anterior (develop): sem `forge-check brief`, eles não têm o que executar (o subcomando não existe lá; PQ-12 mostra 0 ocorrências no hook).

## Mutação
Sem ferramenta gratuita de mutação em `stacks/` para o código do Forge (Python da biblioteca padrão); não executada. Os casos b, c e g fazem o papel de mutantes manuais da entrada.

## Observações (não reprovam)
- `brief gerar` deixa o modelo de corte com `PREENCHER`; a conferência do brief final reprova se sobrar, por desenho (o Jarvis completa).
- A saída do conferente sobre um brief real, a colar no PR (informativo do review da K1), é da abertura do PR (E3.4), fora deste QA.

## Bugs
Nenhum aberto (`docs/qa/bugs/` sem entrada nova).

## Resultado
Aprovado. Suíte completa verde (685 testes), plugin válido, PQ-1 a PQ-13 cumpridos, exploratório a-g sem divergência. Riscos: o `forge-check pr` só fecha depois deste commit (V-1).
