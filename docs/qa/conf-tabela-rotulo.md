---
tipo: qa
contrato: 1
pedido: conf-tabela-rotulo
branch: melhoria/conf-tabela-rotulo
commit: 51500c2f60488d9b8729cd58b19a0afb9f474f28
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 1
aceite_usuario: sim
data: 2026-10-17
---
# QA - conf-tabela-rotulo (tabela do conferente alinhada à Catraca)

Sem UX nem API. Diff `0095d29...51500c2`: uma linha alterada em `agents/conferente.md` (`merge-integracao`, e a remissão em `pedido-de-merge-ao-dono`), dois invariantes novos em `tests/config.json` (nada removido) e o fragmento de changelog. Os commits depois de 51500c2 só trazem pareceres. Não escrevi o diff. Review e segurança com `parecer: aprovado` e `commit: 51500c2f...`; `forge-check pr conf-tabela-rotulo --ref HEAD --base origin/develop` só apontava a falta deste parecer.

## Obrigação -> teste -> resultado
| ID | Obrigação (pedido E1) | Teste (comando real) | Fronteira protegida | Resultado |
|---|---|---|---|---|
| O-1 | Rótulo só quando a Catraca pede | #186 (catraca `pass` em 23:38, sem rótulo, diff em `docs/regras/R-DECISAO.md` e `tests/config.json`): `gh pr checks 186`, `gh pr view 186 --json labels,files,statusCheckRollup` | permissão: arquivo protegido tocado sem rótulo | passou: pela linha nova, em ordem (labels `[]`, catraca `SUCCESS`, bateria `SUCCESS`, rápida `SKIPPED`) |
| O-2 | `fail` antigo substituído por `pass` mais novo, mesmo check e mesmo head, não reprova | #182: `gh pr checks 182`; `gh run view` dos dois runs da catraca | mesmo head, ordem no tempo | passou: run 38969773946 `failure` (21:29:56) e run 38981236093 `success` (23:24:05), ambos com `headSha` 484acac; rótulo `afrouxa-regra` presente; linha nova aprova |
| O-3 | Catraca mais recente em `fail` por falta de rótulo não passa | leitura da linha nova: o rótulo é exigido quando o check do head pede, e a execução mais recente com `fail` reprova | último estado manda | passou por leitura. Sem PR real nessa situação agora; o estado intermediário do #182 (só o run `failure`, sem rótulo) é o caso, e a linha o reprovaria |
| O-4 | `pass` de outro head ou de outro check não substitui a `fail` | leitura da linha ("mesmo check no mesmo head"); `gh pr view --json statusCheckRollup` traz só os checks do head atual | head diferente; check diferente | passou por leitura; no #186 o run da catraca (head 4b4bb09) é de outro head que o do #182 (484acac) e não se mistura |
| O-5 | `pedido-de-merge-ao-dono` com a mesma regra | leitura da linha: "O mesmo de `merge-integracao` (inclusive o rótulo só quando a `catraca` pede)" | n/a | passou |
| O-6 | Invariante da frase nova, nunca só remover | `git show 0095d29:agents/conferente.md \| grep -cF` e `grep -cF` no HEAD, para as duas frases novas | frase ausente na base | passou (vermelho antes do verde): base 0 e 0, HEAD 1 e 1; `git diff` de `tests/config.json` sem linha removida. Não havia invariante para a frase antiga |
| O-7 | Suíte e validação do plugin | `python3 -m unittest discover -s tests -q`; `scripts/validar-plugin.sh` | n/a | passou: 774 testes, OK (142 s); "Validation passed" |

Mutação: não se aplica (diff só de texto e dados de invariantes; sem código de produção).

## Bugs
- B-1 (baixa, aberto): o comando da linha, `gh pr checks <b>`, não mostra hora nem head de cada run (esta versão do `gh` não aceita `--json` em `pr checks`). A ordem das linhas coincidiu com a cronológica no #182, mas nada garante. Para provar "execução mais recente" e "mesmo head", o conferente precisa de `gh pr view <b> --json statusCheckRollup` (campos `startedAt`, `completedAt`) e `gh run view <id> --json headSha`, que a coluna de comando não cita.
  - Passos: `gh pr checks 182` (duas linhas `catraca`, `fail` e `pass`, sem hora) e comparar com `gh pr view 182 --json statusCheckRollup`.
  - Esperado: comando que mostra a hora de cada execução. Obtido: lista sem hora.
  - Responsável sugerido: tech-lead (autor da linha), em pedido à parte (CONF-CMDS está fora deste pedido). Não bloqueia: contorno simples e o texto da regra está correto.

## Resultado da execução
Aprovado, com um baixo aberto (aceite do usuário). Nenhum crítico, alto ou médio.
