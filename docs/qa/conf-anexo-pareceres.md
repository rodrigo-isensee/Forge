---
tipo: qa
contrato: 1
pedido: conf-anexo-pareceres
branch: melhoria/conf-anexo-pareceres
commit: 135ee4ed8018078c88d059d18bd9a4aaf3d529d9
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-17
---
# QA - conf-anexo-pareceres (lista de anexos implícitos do conferente)

Sem UX nem API. Diff testado: `f636d27...135ee4e` (`agents/conferente.md`, `tests/test_forge.py`, `changelog.d/conf-anexo-pareceres.md`). Não escrevi o diff. Review e segurança aprovados sobre `135ee4e`; os commits seguintes (`ed9c4e7`, `d099535`) só trazem esses pareceres. Rodado na raiz da worktree, árvore limpa, sem outra suíte em curso (`pgrep`).

## Obrigação -> teste -> resultado
| ID | Obrigação | Teste / comando | Fronteira protegida | Resultado |
|---|---|---|---|---|
| E1 | `docs/security/` e `docs/devops/` entram na lista, só por acréscimo | `test_conferente_lista_de_anexos_implicitos` (lista exata, 8 itens) | lista exata (item a menos ou a mais falha) | verde |
| Decisão 2026-10-17 | `docs/security/aceites/` fora da lista (aceite é do dono; R-SEGURANCA:13) | mesmo teste: `assertNotIn` na lista + frase "fica fora dela" | aceite na entrega continua `escopo: fora` | verde; mutação 1 e 4 derrubam |
| C5 | lista vale a partir da raiz (`templates/projeto/docs/...` não é anexo) | mesmo teste: frase "a lista vale a partir da raiz do repositório" | caminho aninhado | verde; mutação 3 derruba |
| Regra existente | `tests/config.json` nunca é anexo | mesmo teste: `assertIn` | n/a | verde |
| E2/PQ | suíte e plugin verdes | suíte inteira; `scripts/validar-plugin.sh` | n/a | 786 OK; plugin OK |

## Execução
- `python3 -m unittest discover -s tests` na raiz da worktree: `Ran 786 tests in 135.134s` / `OK`.
- `scripts/validar-plugin.sh`: `Validation passed` (manifesto e plugin). O sandbox negou `api.anthropic.com` e datadog durante o validar (rede bloqueada, esperado; não afetou o resultado).
- Árvore da worktree sem alteração (`git status --short` vazio) antes de escrever este parecer.

## Vermelho antes do verde (mutação dirigida, cópia em `$TMPDIR`)
Cópia por `git archive HEAD | tar -x -C $(mktemp -d)`; worktree intocada. Comando: `python3 -m unittest tests.test_forge.Agentes.test_conferente_lista_de_anexos_implicitos`. Original: `OK`.
| Mutação em `agents/conferente.md` | Resultado |
|---|---|
| 1. `docs/security/aceites/` acrescentado à lista | `FAILED (failures=1)` |
| 2. `docs/devops/` removido da lista | `FAILED (failures=1)` |
| 3. frase "a lista vale a partir da raiz do repositório" removida | `FAILED (failures=1)` |
| 4. frase "`docs/security/aceites/` fica fora dela" removida | `FAILED (failures=1)` |
Nota: na mutação 1 quem falha primeiro é a igualdade da lista; o `assertNotIn` ficaria como segunda guarda (redundante, mas não reprova). A recomendação N1 da segurança (o `assertIn` olha o arquivo inteiro, não o item 2) segue válida: a frase poderia estar em outro trecho do arquivo e o teste passaria; risco baixo, o `re.search` da lista é ancorado no item 2.

## Casos de borda
A regra é texto para o conferente (agente), não código; não há função para executar. Repositório descartável em `$TMPDIR` com os cinco casos, `git diff --name-only <base>...HEAD` e `git diff --numstat --no-renames <base>...HEAD` (os comandos que o item 2 manda rodar), classificados por um script meu que aplica a lista literal do item 2. Prova que os comandos dão a entrada esperada e que a lista, aplicada à letra, separa os casos; não prova o julgamento do conferente.
| Caso | Saída | Esperado |
|---|---|---|
| parecer novo `docs/security/novo.md` | `1 0` , anexo | anexo |
| parecer novo `docs/devops/novo.md` | `1 0`, anexo | anexo |
| aceite `docs/security/aceites/r.md` | `1 0`, fora | `escopo: fora` |
| `templates/projeto/docs/security/t.md` | `1 0`, fora | fora (não é da raiz) |
| parecer existente com linha removida `docs/security/velho.md` | `0 1`, anexo | anexo com remoção (reprova se fora do "Entregar") |

## Achados por classe (VV-1)
- Classe "lista sem guarda de caminho aninhado/aceite": 0 achados; reproduz com as mutações 1, 3 e 4 acima (todas falham).
- Classe "teste lê o arquivo inteiro, não o item 2" (N1, informativo): 1 ocorrência, as duas frases `assertIn`. Reproduz: `grep -n 'a lista vale a partir da raiz' agents/conferente.md` retorna só a linha 71 hoje; mover a frase para outro item não derrubaria o teste. Não abro bug (baixa, já recomendada pela segurança como P); sem bug aberto.
- Fora do escopo, já no cartão do pedido: ADR 0004:20 sem `docs/devops/` e `docs/security/` nos caminhos livres.

## Resultado
Aprovado. Nenhum bug crítico, alto, médio ou baixo aberto.
