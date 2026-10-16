---
tipo: qa
contrato: 1
pedido: ta-6-pa-3-pa-9
branch: melhoria/ta-6-sobreposicao-fila-quadro
commit: f257b67d7c0405f133980382fff7b5f06bb8591b
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 1
aceite_usuario: sim
data: 2026-10-16
---
# QA - TA-6 + PA-3 + PA-9 (sobreposição, fila de integração, registro do quadro)

Sem UX nem API. Código testado: f257b67 (implementação c7a2b6a + volta do autor) sobre a base 1fd122f (origin/develop). O HEAD da branch (d4c08f1) só acrescenta as revalidações de review e segurança sobre f257b67 (2 arquivos em `docs/reviews/` e `docs/security/`; ambos `parecer: aprovado`, `commit: f257b67`), então não há código diferente do testado. Teste novo de regra: `tests/test_sobreposicao_quadro.py` (15 testes), escrito pelo autor; não rodei vermelho-antes-do-verde nem mutação sobre ele (fora do brief, e `stacks/` não define mutação para o Python da fábrica); o exploratório abaixo exercita o código real nas mesmas fronteiras.

## Obrigação -> teste -> resultado
| ID | Obrigação | Teste (comando real) | Fronteira protegida | Resultado |
|---|---|---|---|---|
| PQ-1 | Suíte verde | `python3 -m unittest discover -s tests -q` | n/a | 700 testes, OK (188 s) |
| PQ-2 | Plugin válido | `scripts/validar-plugin.sh` | n/a | "Validation passed" |
| PQ-3 | Pareceres de review e segurança antes do QA | `grep ^parecer` nos dois arquivos | portão R-REVIEW/R-SEGURANCA | ambos `aprovado`, em f257b67 |
| PQ-4 | `forge-check pr` (R-QA) | `forge-check pr ta-6-pa-3-pa-9 --ref HEAD --base origin/develop` | parecer de QA ausente | antes deste parecer: único achado "sem parecer de QA (R-QA)", rc=1, esperado; reconferir com este arquivo commitado |
| EX-a | E1: só pares com sobreposição, ordenados, rc=0 | repo temporário, 3 branches `melhoria/*` (a e b com `shared.txt` em comum, c isolada) | par sem arquivo comum | saída: `melhoria/a <-> melhoria/b: shared.txt` + resumo "1 par(es) ... entre 3 branch(es)"; c não aparece; rc=0 |
| EX-b | Base inexistente: aviso e rc=0 | repo sem develop/main, com e sem `--base zzz` | base ausente | "sobreposicao: base não encontrada (...); nada comparado", rc=0 nos dois casos. Ver B-1 para `--base` errado com develop presente |
| EX-c | E3: uma linha, hora ISO 8601 com fuso, colunas de espera | `movimento CARD-1 --de "Em andamento" --para "Aguardando o dono"` e `--de "Aguardando o dono" --para "Sem credencial"` | colunas com espaço | cabeçalho criado uma vez, 2 linhas, `2026-10-16T10:22:32-03:00`, rc=0; motivo omitido vira "—" |
| EX-d | Campo vazio: rc=1 e nada gravado | cartão `""`; `--de "  "` (só espaço) | vazio e só espaço | "movimento: cartão, --de e --para não podem ser vazios", rc=1; `cmp` com cópia do arquivo: intacto |
| EX-e | `\|` e quebra de linha sanitizados | cartão `C\|2`, de `A<LF>B`, para `D\|E`, motivo `m\|1<LF>linha2` | separador de tabela, newline | uma única linha `\| ... \| C/2 \| A B \| D/E \| m/1 linha2 \|`; arquivo cresceu 1 linha |
| EX-f | Determinismo | `sobreposicao` 3 vezes, `md5sum` | n/a | 3 hashes idênticos |
| CA-E2 | Fila de integração na regra e no tech-lead | `test_fila_de_integracao_na_regra_e_no_tech_lead` + invariantes novos (`Fila de integração`, `ordem de chegada`) na suíte | texto sumir | verde na suíte (PQ-1) |
| CA-E1/E3 | Jarvis e skill usam os subcomandos | `test_jarvis_serializa...`, `test_skill_do_quadro...` + invariantes | texto sumir | verde na suíte (PQ-1) |
| CI | Fragmento do changelog | `changelog.d/ta-6-sobreposicao-fila-quadro.md` presente com o nome da branch | n/a | presente; `forge-check pr` não acusou |

## Bugs
- B-1 (baixa, `forge:tech-lead` como autor): `forge-check sobreposicao --base <ref inexistente>` não avisa quando existe `develop`; `base_da_entrega` cai para a lista padrão `BASES` e compara contra `develop` em silêncio. Passos: repo com `develop` e 2 branches `melhoria/*`; `forge-check sobreposicao --base nao-existe`. Esperado: aviso de base não encontrada, como no caso sem nenhuma base (EX-b). Obtido: resultado normal contra `develop`, sem aviso. Impacto: comando é informativo e o erro é do lado seguro (compara contra a base padrão); só engana quem digitou a base errada. Comportamento herdado do helper compartilhado com `forge-check pr`; mudá-lo afetaria o `pr`, então não bloqueia. Sem arquivo em `docs/qa/bugs/` por restrição do brief (só este arquivo); fica aqui para o autor ou o dono decidir.

## Pendências já aceitas
- Branch já mesclada por squash e não apagada gera falso par em `sobreposicao` (ajuste 3 do review; decisão do Jarvis 2026-10-16 09:58, cartão TA6-REC3). Não é bug novo; erro do lado seguro.

## Resultado
Aprovado: nenhum bug crítico, alto ou médio; 1 baixo aberto (B-1), com `aceite_usuario: sim` a registrar pelo dono. Segurança segue sendo parecer do `security-engineer` (aprovado em f257b67).
