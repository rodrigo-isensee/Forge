---
tipo: qa
contrato: 1
pedido: conferente-k1
branch: melhoria/conferente-k1
commit: 0368e72c056e87f4a6e1e09ef4a3f43dd0fbe77b
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 1
aceite_usuario: sim
data: 2026-10-15
---
# QA - conferente confiável, fatia K1 (texto e forma)

Sem UX nem API. Código testado em 0368e72 sobre a base bad3edd; o HEAD da branch (1e774bc) só acrescenta o parecer de review (`git diff --stat 0368e72..HEAD`: só `docs/reviews/conferente-k1.md`). Obrigações: os PQ da §6 linha K1 da proposta, `R-QA`, `R-PROVA`, `R-BRIEF`, `R-DECISAO`.

## Critério -> teste -> resultado
| ID | Obrigação | Teste (comando real) | Fronteira protegida | Resultado |
|---|---|---|---|---|
| PQ-1 | Suíte completa verde (`R-TETO`: load 0.24 antes) | `python3 -m unittest discover -s tests -q` | n/a | `Ran 653 tests in 173.672s` / `OK` |
| PQ-2 | R-PROVA com `espera:` | `grep -c 'espera:' docs/regras/R-PROVA.md` | mínimo 1 linha | `1` |
| PQ-3 | `## Etapas` no modelo de pedido | `grep -n '^## Etapas' templates/projeto/docs/pedidos/_modelo.md` | exatamente 1 linha | `12:## Etapas` |
| PQ-4 | Base-sha no conferente e no jarvis | `grep -n 'Base-sha' agents/conferente.md agents/jarvis.md` | uma linha em cada | conferente.md:58 e :65; jarvis.md:63 |
| PQ-5 | numstat no conferente | `grep -n 'numstat' agents/conferente.md` | mínimo 1 linha | conferente.md:65 |
| PQ-6 | Brief real em disco, conferido | ver "Brief real" abaixo | arquivo existe; corte pareado por ID | ok |
| V-1 | Plugin válido | `scripts/validar-plugin.sh` | n/a | `Validation passed` |
| V-2 | Pareceres e frontmatter contra a base | `bin/forge-check pr conferente-k1 --ref HEAD --base bad3edd` | n/a | antes deste commit: só faltavam QA (este) e o parecer de segurança sem commit; refeito depois do commit (ver relatório) |

## Brief real (PQ-6)
Conferido à mão, passo a passo, pelo texto de `agents/conferente.md` da worktree (não rodou o agente haiku; limitação abaixo). Brief: `~/.forge-contrib/docs/briefs/conferente-k1-tech-lead-5.md`; pedido: `~/.forge-contrib/docs/pedidos/conferente-k1.md`; destino `forge:tech-lead`.
- `test -e` no arquivo: existe.
- Pareamento por ID: `## Escopo` do pedido tem E1, E2, E3 (`grep -nE '^- E[0-9]\. '`). E1 está no "Entregar" (itens 1 e 2, citação `(E1)`); E2/E3 aparecem no "Fora do escopo" com a marca. Quatro linhas com `Retira do escopo original` (`grep -n`: 16, 17, 18, 19).
- Etapa não é corte: os trechos citados das linhas 16 e 17 existem literais no pedido (`grep -n -F` linhas 20 e 21 do pedido); `E1.1 (tech-lead)` é do destino e é coberta pela referência do Objetivo e pelos itens de "Entregar" (E1). Resultado: `corte: etapa (ok)` nas linhas de E2.x e E3.x, sem reprovação.
- Forma: 7 PQ `cmd`/`push`, todos com `espera:` (`grep -vc 'espera:'` = 0); há PQ `push` (brief com commit). Comandos fora da lista do conferente (suíte, validar-plugin) viram `PQ-n do autor`.
- Veredito resultante: `corte: ok | forma: ok`; `veredito-brief: aprovado`.
- Observação (não reprova): E2 e E3 do `## Escopo` não são citados por ID, só por E2.x/E3.x das etapas; um conferente rigoroso pode pedir a citação do ID. Texto da regra: "cada `E<n>` ... está no Entregar ... ou no Fora do escopo". Aqui o Fora do escopo traz a marca e o trecho, então fica ok.

## Teste exploratório do texto novo
Fixtures sintéticas em `$TMPDIR/ex` (pedido com E1, E2 em `## Escopo` e E1.1 tech-lead, E1.2 qa-engineer, E2.1 dono em `## Etapas`; destino tech-lead). Aplicado o texto do conferente com os comandos permitidos.
| Caso | Entrada | Comandos e saída | Resultado esperado | Resultado |
|---|---|---|---|---|
| 1 etapa de outro papel | Fora do escopo cita `E1.2 (qa-engineer): QA.` e `E2.1 (dono): merge.` sem a marca; E1 e E2 no Entregar | `grep -c -F 'E1.2 (qa-engineer): QA.' pedido.md` → 1; `grep -c -F 'E2.1 (dono): merge.' pedido.md` → 1; `grep -c 'Retira do escopo original' brief1.md` → 0 | `corte: etapa (ok)`, não reprova | ok |
| 2 corte real sem marca | E2 fora do Entregar (`grep -c '(E2)'` → 0); Fora do escopo diz só "Documentação de X fica para depois." | `grep -c -F 'Documentação de X' pedido.md` → 0 (não está em Etapas); marca → 0 | `corte: sem marca "E2"`, reprova | ok (reprova) |
| 3 Base-sha não ancestral | Base-sha `4976304a1f1e0de7e3ed93de4eb225d5bab795e2` (ponta de `backup/estado-ciclo-2026-10`) | `git merge-base --is-ancestor 4976304a... HEAD && echo contém \|\| echo não contém` → `não contém`; com a base real `bad3edd...` → `contém` | `escopo: Base-sha fora da branch`, reprova | ok (acusa) |

Extra do mesmo texto: o anexo `escopo: ok (anexo)` só por acréscimo: `git diff --numstat bad3edd...HEAD -- docs/reviews changelog.d` → `3 0 changelog.d/conferente-k1.md`, `54 0 docs/reviews/conferente-k1.md` (nenhuma remoção).

## Vermelho antes do verde (mutação nos trechos novos)
Cópia limpa de HEAD em `$TMPDIR/mut`; cada trecho trocado por `X` e rodado `python3 -m unittest -q tests.test_forge.RegrasInviolaveis` (controle sem mutação: rc 0).
| Trecho apagado | Resultado |
|---|---|
| `corte: etapa (ok)` na regra do veredito | falha (rc 1) |
| "o Base-sha precisa ser ancestral das duas" | falha (rc 1) |
| "etapa do papel do destino que falta no Entregar é corte" | falha (rc 1) |
| `escopo: anexo com remoção` | falha (rc 1) |
| "`pendente:` existe só na entrega" (separação de vocabulário, C10) | **passou: mutante vivo** (BUG-K1-1) |

## Defeitos
### BUG-K1-1 (baixa): a frase de separação de vocabulário entre os modos não tem invariante
- Responsável sugerido: `tech-lead` (autor da fatia; `tests/config.json`).
- Passos: 1. copiar HEAD para uma pasta limpa. 2. em `agents/conferente.md`, trocar "`pendente:` existe só na entrega" (ou a frase inteira "Cada modo tem vocabulário próprio e não se mistura: ...") por `X`. 3. `python3 -m unittest -q tests.test_forge.RegrasInviolaveis`.
- Esperado: falha, pois a separação `corte:` só no brief e `pendente:` só na entrega é o núcleo do C10. Obtido: rc 0 (os invariantes `use só a seção Modo brief/entrega` e `pendente:` seguem satisfeitos por outros trechos).
- Impacto: a regra pode sumir sem o teste acusar; não afeta o comportamento atual. Sugestão: invariante `existe só na entrega`.
- Não bloqueia (baixa); exige aceite do usuário (`aceite_usuario: sim`).

## Lacunas
- O conferente real (haiku) não foi invocado: o sandbox nega `api.anthropic.com` (telemetria do `claude`; `scripts/validar-plugin.sh` passou mesmo assim) e o agente não é executável por script. Os casos acima aplicam o texto da regra com os mesmos comandos permitidos; o comportamento do modelo diante do texto fica para o uso real (K2 trará o `forge-check brief`, determinístico).
- Sem UX, E2E ou acessibilidade: não se aplicam (fábrica, só texto e testes estruturais).

## Resultado
Nenhum defeito crítico, alto ou médio. Um baixo aberto (BUG-K1-1). Aprovado, com aceite do usuário para o baixo.
