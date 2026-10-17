---
tipo: qa
contrato: 1
pedido: ta-3
branch: melhoria/ta-3-testes-tocados
commit: 604b2a90c509915c39becadbd5f56cb47cbd195e
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-16
---
# QA - TA-3 (teste dirigido `bin/forge-testes`)

Sem UX nem API. Código testado: 604b2a9 (implementação 98bd38a + volta do autor) sobre a base 6ebd201. O HEAD da branch (e9016ab) só acrescenta as revalidações de review e segurança sobre 604b2a9 (2 arquivos em `docs/reviews/` e `docs/security/`, ambos `parecer: aprovado`, `commit: 604b2a9`); não há código diferente do testado. Não rodei vermelho-antes-do-verde nem mutação sobre `tests/test_testes_tocados.py` (fora do brief; `stacks/` não define mutação para o Python da fábrica); o exploratório exercita o código real nas mesmas fronteiras.

## Obrigação -> teste -> resultado
| ID | Obrigação | Teste (comando real) | Fronteira protegida | Resultado |
|---|---|---|---|---|
| PQ-1 | Suíte verde | `python3 -m unittest discover -s tests -q` | n/a | 728 testes, OK (191 s) |
| PQ-2 | Plugin válido | `scripts/validar-plugin.sh` | n/a | "Validation passed" |
| PQ-3 | Pareceres de review e segurança antes do QA | `forge-check pr ta-3 --ref HEAD --base origin/develop` | portão R-REVIEW/R-SEGURANCA | ambos `aprovado` em 604b2a9; único achado: "sem parecer de QA (R-QA)", esperado antes deste arquivo |
| EX-a | Só um teste alterado roda só o módulo dele | clone temporário, `echo >> tests/test_changelog.py`, `--listar` | um módulo | `dirigido (test_changelog)` |
| EX-b | Agente ou doc alterado roda os módulos do mapa | `agents/jarvis.md`; `docs/economia-de-tokens.md` | regra de conteúdo; regra específica | `test_changelog, test_doutor, test_forge, test_novo_projeto, test_sobreposicao_quadro`; a economia acrescenta `test_testes_tocados` |
| EX-c | Sem mapa, `tests/config.json` e o script caem na completa | `.github/workflows/ci.yml`, `LICENSE`, `tests/catraca.py`, arquivo novo em pasta nova, `tests/config.json`, `bin/forge-testes` | falha fechada | todos `suíte completa (... sem mapa / altera o mapa ou a configuração)` |
| EX-d | Diff vazio não roda nada e diz isso | `--base HEAD` (com e sem `--listar`) | vazio | "nada alterado; nada a rodar.", rc=0, `.forge` não criado |
| EX-e | Log: uma linha por execução, fora do git | 2 dirigidas + 1 `--completa`; `git status`; `git check-ignore -v` | log ignorado | 3 linhas (`modo=dirigido ... duracao=1.2s saida=0`; `modo=completo ... 192.4s saida=0`); `git status` só mostra o arquivo editado; ignorado por `.gitignore:20 /.forge` |
| EX-f | Nenhum portão chama o script | `grep -rn forge-testes .githooks .github hooks bin/forge-check` | portão | vazio (rc=1) |
| EX-g | B-TA3-1: `tests/config.json` renomeado para docs/ cai na completa | `git mv tests/config.json docs/cfg.json`, sem commitar e depois commitado | caminho antigo de renomeio | `suíte completa (tests/config.json altera o mapa ou a configuração)` nos dois casos |
| EX-h | `migrations/`, `templates/`, `.claude-plugin/`, `bin/forge-doutor`, `bin/forge`, `hooks/doutor.py` rodam `test_atualizar`; `stacks/` roda `test_hooks` | `--listar` após alterar cada um | achado bloqueante do review | todos incluem `test_atualizar`; `stacks/node-react/pronto.md` inclui `test_hooks`; `.claude-plugin/` também |

## Bugs
Nenhum aberto.

## Observações (não são bugs)
- `--base HEAD` com a árvore limpa é a forma de simular "nada alterado" fora de uma branch; o padrão `origin/develop` depende de a referência existir, e a ausência dela cai na completa (falha fechada, coberto por teste do autor e pelo código).
- `test_changelog` roda com 1 teste ignorado (`skipped=1`); é anterior a esta branch, não foi introduzido por ela.

## Resultado
Aprovado: nenhum bug aberto de qualquer severidade. Segurança segue sendo parecer do `security-engineer` (aprovado em 604b2a9).
