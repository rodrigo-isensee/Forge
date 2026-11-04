---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/lote-fc-seguranca
commit: 4ccb323dd95762683c8c66e66d7e316498ec2897
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-03
---
# QA: lote E2+E3 da 0.33 (FC-PEDIDO-FORA-DAS-RAIZES e FC-ENTREGA-GIT-FALHA-ABERTA), rodada 2

Código testado: `4ccb323` (head da branch `05ff233`, que só soma os pareceres de review e de segurança da rodada 4). Base `928e61b`. Referência: seções E2 e E3 de `docs/security/ameacas/versao-033.md` (C-n e T-n). A rodada 1 (`95f1b22`, sobre `dd441fa`) reprovou só pela prova de mutação (A1 e A2); os dois bloqueantes estão resolvidos e o comportamento segue correto.

## Achados
- A1 (recomendado) tests/test_volta_por_delta.py:635 · `PqDeMerge.test_etapas_de_merge_trazem_o_pq_por_ancestralidade_da_base` caiu uma vez na suíte (`gerar` rc 1 em vez de 0, etapa `codigo`) e não se repetiu: isolado 7 de 7, módulo 2 de 2, suíte inteira de novo OK. Causa não achada

## Resolução dos bloqueantes da rodada 1
- A1 resolvido: cada spec do lote roda sem "inválido" e as quatro juntas também. Spec 1 rc=0 (M1 a M12), spec 2 rc=0 (M13 a M23, M40, M43 a M45; 15 morreram), spec 3 rc=0 (M24 a M36), spec 4 rc=0 (M37, M39, M46). Todas numa chamada: rc=0, 42 mutantes, todos `morreu`, sem `inválido` nem id repetido. A primeira passada das quatro juntas saiu com M34 "controle vermelho" (a máquina estava sob a suíte de outro agente); repetida em carga normal, rc=0: ruído de carga, como na rodada 1.
- A2 resolvido: `forge-mutante --cobertura --base 928e61b` não lista mais `bin/forge-check:504`, `:518`, `:1252` nem `:1253` como "sem mutante": `:504` coberta por M1 e M44, `:518` por M45, `:1252` por M21, `:1253` por M22 e M43 (todos "declarado, não provado", e a rodada acima os provou). Nenhuma linha "sem mutante" na saída. O rc da checagem é 1 só por três linhas "apagada" da base (`:861`, `:1196`, `:1228`), isto é, condições reescritas cujas novas formas têm mutante (`:1311` por M34; a de `:861` já isentada pela spec em `:857` e `:848`); não há guarda do head sem mutante.

## Evidência da suíte e dos gates (sobre 4ccb323)
- Suíte inteira (`.githooks/pre-push --suite`): primeira passada `Ran 2518 tests in 987.236s (4 processos)`, `FAILED (failures=1, skipped=28)` (o teste do A1, rc=1); repetição `Ran 2518 tests in 847.017s (4 processos)`, `OK (skipped=28)`, rc=0. Os 28 skips já existem na base.
- `scripts/validar-plugin.sh`: `Validation passed`, rc=0.
- `bin/forge-check docs`: rc=0 (antes do parecer).
- Vermelho antes do verde: o delta da rodada 1 (`95f1b22` a `4ccb323`) só mexe nas specs de mutantes e no teste do M44; os testes do lote seguem os que provei vermelhos na rodada 1 (`forge-testes --vermelho 928e61b`: 16 provam por asserção, 19 passam na base por caminho saudável, e o `test_git_que_falha_exige_todos_os_portoes_sem_excecao` dá `TypeError` na base). O M44 (`:504`) morre pelo caminho saudável, a prova de que o teste novo cai sem a guarda.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E2 C-1/C-2: `--pedido` fora de `docs/pedidos/` das raízes recusa (absoluto, `~/`, `../`, link, `docs/pedidosX`, `./x.md`) | sonda ponta a ponta `entrega` e `brief` e `tests/test_pedido_fora.py` | caminho fora da raiz; prefixo vizinho; link no último componente e em pasta intermediária | passou |
| E2 C-4/C-6: id nu e caminho legítimo dentro das raízes passam | sonda: `p1`, `p2`, `docs/pedidos/p2.md`, absoluto da raiz, `~/.forge-contrib/docs/pedidos/p1.md` | ordem das raízes | passou |
| E2 T-1/T-2: nenhuma raiz nova; sem aceitar com aviso | leitura do diff e sonda (`/tmp`, cwd) | cwd e `/tmp` fora | passou |
| E3 C-1/C-2: a falha do git em qualquer passo reprova (rc 1) e nunca vira "nada a conferir" | sonda com `git` falso por padrão, etapas `codigo`, `review`, `merge-integracao`, e `tests/test_entrega_git_falha.py` | diff, rev-list, contagens, base | passou |
| E3 C-3: o filtro não tira arquivo na falha | testes de filtro e sonda com `--desde` | filtro com conjunto vazio | passou |
| E3 C-4: `gatilhos` com `None` não levanta exceção | `test_git_que_falha_exige_todos_os_portoes_sem_excecao` | `None` de `arquivos_da_entrega` | passou |
| E3 T-4: git saudável com saída igual à da base | sonda: saída e rc, base `928e61b` contra o head, 3 etapas, com e sem `--desde` | caminho de sucesso | passou (6 de 6 iguais) |
| `R-QA`: mutação no diff, um mutante por linha de guarda | `forge-mutante` das quatro specs e `--cobertura` | `:504`, `:518`, `:1252`, `:1253` | passou (A1 e A2 da rodada 1 resolvidos) |

## Cenários e resultado real
Repositório descartável em `$TMPDIR/qa-engineer-lote-fc-seguranca/e2e` (`develop` e `melhoria/x`, HOME falso com `~/.forge-contrib/docs/pedidos`), `forge-check` do head.

**E2, `entrega --pedido`.** Recusa com rc 2 e `--pedido fora de docs/pedidos/ das raízes` para `/tmp/...`, absoluto solto, `~/notas.md`, `$HOME/notas.md`, `docs/pedidos/../propostas/x.md`, link `docs/pedidos/link.md`, `docs/pedidos/dirlink/alvo.md` (link em pasta intermediária), `docs/pedidosX/x.md`, `./x.md`, `x.md`, o link da raiz de brief, os ids `link` e `link2` e `../x`. Passam (rc 0): `p1`, `p2`, `docs/pedidos/p2.md`, o absoluto da raiz do repositório, o absoluto da raiz de brief e `~/.forge-contrib/docs/pedidos/p1.md`.

**E2, `brief --pedido`.** Recusa rc 2 para o absoluto solto, `~/notas.md`, `../x`, `docs/pedidos/link.md`, `link` e `dirlink/alvo.md`. Id nu, `docs/pedidos/p2.md`, `~/.forge-contrib/...` e o absoluto da raiz são resolvidos (a linha sai `conferencia-brief-regra: p1 → b.txt`); o rc 1 desses casos é o veredito do conteúdo do arquivo de brief fictício `b.txt`, não recusa do `--pedido`.

**E3, git falho.** O `git` falso sai 128 só no padrão pedido. Nas etapas `codigo` e `review`: diff `--name-only ...`, `rev-list --parents -n 1`, `--numstat` e `rev-list` dão rc 1 e `escopo: o git falhou (<passo>); o escopo não foi lido`, nunca "nada a conferir" (0 ocorrências nas 21 combinações). Na `merge-integracao` o rc é 1 em todas (a saída é a dos pareceres ausentes no repositório de teste, igual à saudável). O `rev-parse --verify --quiet` sem o Base-sha legível sai rc 2 (recusa da ref, igual à base); `merge-base` falho sai "Base-sha fora da branch", rc 1, como na base. Git saudável: saída e rc idênticos aos da base `928e61b` em 6 de 6 combinações (3 etapas, com e sem `--desde`).

**Acessibilidade e E2E de interface:** não se aplicam (CLI, sem tela).

## Já registrados nos pareceres (não repetidos)
Review A1 e A6; segurança A5 e A7.

## Riscos
- O A1 (teste que caiu uma vez) pode ser interferência entre processos da suíte paralela; não é defeito provado do lote e não bloqueia, mas quem o vir cair de novo deve reportar com a saída de `gerar` (o teste só imprime o stderr).
- AR-1 (lista de mutantes incompleta) voltou na rodada 1 e está resolvido; a linha de `docs/engineering/achados-recorrentes.md` fica com o tech-lead, porque o pedido manda commitar só este parecer.
