---
tipo: qa
contrato: 1
pedido: impl-n-agt-a
branch: melhoria/impl-n-agt-a
commit: 5b1ff24c62d8b88490c8e59cf48cb0c0c00aa335
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-23
---
# QA: impl-n-agt-a

Sem especificação de UX nem contrato de API (melhoria da fábrica, pedido de origem perdido; RET-AGT-A). As obrigações vêm de `changelog.d/impl-n-agt-a.md`, de `docs/hooks.md` e das regras `R-TETO` e `R-BRIEF`. Sem stack de E2E: a ferramenta é `unittest` mais execução real do hook.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| AGT-1: `agentes` registra no clone e nas worktrees, em `<comum>/forge/run/` (`R-TETO`) | `tests/test_agentes_clone.py` (11) | teto somado entre clone e worktree; pasta 0700; `FORGE_GUARDA_ABERTA` não abre o teto; sem diretório comum | passou |
| AGT-1: `forge-check fila` lê o mesmo arquivo | `test_agentes_clone.py` (caso da fila) | caminho antigo com lista vazia | passou |
| AGT-2: hash do arquivo do brief confere (`R-BRIEF`) | `tests/test_agentes_hash_brief.py` (19) | brief editado, hash errado; 256 KiB e 256 KiB + 1; FIFO e dispositivo; atalho e `..` para fora de `docs/briefs/`; cabeçalho duplicado; segundo bloco | passou |
| Forma da mensagem preservada | `tests/test_guarda_conferente.py` | só a forma | passou |
| Nada mais regride | suíte completa | n/a | só as 4 falhas conhecidas |

## Cenários e resultado real
- Vermelho antes do verde: com `hooks/agentes.py` da base (`af79bef`) sobre a branch, `python3 -m unittest tests.test_agentes_clone tests.test_agentes_hash_brief tests.test_guarda_conferente` deu 46 testes, `FAILED (failures=20, errors=7)`; com o código da branch, `OK` (46). Árvore restaurada e limpa.
- Suíte completa (`python3 -m unittest discover -s tests`): 1624 testes, 379 s, `failures=4, skipped=1`. As 4 são as conhecidas do ambiente (PR #288): `test_shellcheck_no_hook`, `test_erro_interno_com_lista_de_permissao_falha_fechado`, fixtures `conformidade/contrib-falha-fechada-pela-raiz-cwd-home-bloqueia` e `-cwd-wt-bloqueia`. Nenhuma outra. O `skipped=1` já existe na suíte e não foi adicionado por esta entrega.
- `scripts/validar-plugin.sh`: `Validation passed`, rc 0.
- Execução real do hook no clone (stdin JSON, evento `PreToolUse` do `Agent`, `forge:conferente`): hash correto, rc 0 (`agentes.json` criado em `<git-common-dir>/forge/run/`); hash zerado, rc 2 com `R-BRIEF: o hash do brief não bate com o arquivo`.
- Mutação: sem ferramenta gratuita na stack do Forge; o vermelho acima (27 de 46) faz as vezes, e o review lista as fronteiras.
- Observação, não é bug da entrega: a raiz de brief fora do clone é `~/.forge-contrib/docs/briefs/`; briefs em `~/.forge-contrib/forge/docs/briefs/` serão bloqueados por `R-BRIEF` depois da release (R1 do review, já com o Jarvis).
- Fora do que testei: o CI do PR e a promoção. Depois do PR #288, revalidar só o delta.

## Bugs abertos
Nenhum (crítico 0, alto 0, médio 0, baixo 0).
