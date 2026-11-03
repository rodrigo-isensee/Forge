---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/lote-fc-seguranca
commit: dd441fa8cf8788b15188b604d0c2877c46da1742
parecer: reprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-03
---
# QA: lote E2+E3 da 0.33 (FC-PEDIDO-FORA-DAS-RAIZES e FC-ENTREGA-GIT-FALHA-ABERTA)

Código testado: `dd441fa` (head da branch `dd8a378`, que só soma os pareceres de review e de segurança). Base `928e61b`. Referência: seções E2 e E3 de `docs/security/ameacas/versao-033.md` (C-n e T-n). O comportamento está correto; o parecer reprova só pela prova de mutação do lote (A1 e A2), que é artefato de teste e não regride nada em produção.

## Achados
- A1 (bloqueante) tests/mutantes/lote-fc-seguranca-2.json:1 · a lista de mutantes do lote não roda no head: M21 e M22 saem "inválido" (trecho 0 vezes, stale depois do A6) e o id M40 repete nas specs 2 e 4; spec 2 sai rc 2 e todas juntas rc 2
- A2 (bloqueante) bin/forge-check:1253 · o mutante `if True` no rótulo "base da entrega" sobrevive, e :504, :518 e :1252 estão sem mutante no `--cobertura` (os meus Q1, Q2 e Q3 morrem; só Q4 sobrevive). Falta teste do rótulo ausente quando só o diff falha (AR-1)

## Correção sugerida
Quem implementou o E3 troca os trechos de M21 e M22 pelos atuais, renumera o M40 da spec 4, acrescenta o teste que mata o Q4 e os mutantes de `:504`, `:518`, `:1252` e `:1253`.

## Evidência da suíte e dos gates (sobre dd8a378)
- Suíte inteira (`.githooks/pre-push --suite`): `Ran 2517 tests in 887.561s (4 processos)`, `OK (skipped=28)`, rc=0. Os 28 skips já existem na base (vermelho: "pulado=28", H e B pulados).
- `scripts/validar-plugin.sh`: `Validation passed`, rc=0.
- `bin/forge-check docs`: rc=0 (antes do parecer).
- Mutantes declarados, spec a spec (em carga baixa): spec 1 rc=0 (M1 a M12 morreram); spec 3 rc=0 (M24 a M36 morreram); spec 4 rc=0 (M37, M39, M40 morreram); spec 2 rc=2 (M13 a M20, M23 e o M40 `:1301` morreram; M21 e M22 inválidos). Na primeira passada, sob carga da suíte, M16, M17, M19 e M20 saíram "controle vermelho"; sem a carga, morreram: foi ruído, não defeito. Todas as specs numa só chamada: `spec inválida; nada foi executado. - id de mutante repetido entre as specs: M40`, rc=2.
- Conferência da lista contra o diff (`forge-mutante --cobertura --base 928e61b`): `sem mutante` em `bin/forge-check:504`, `:518`, `:1252` e `:1253`. Mutantes meus (`$TMPDIR/qa-engineer-lote-fc-seguranca/qa-extra.json`): Q1 (`:504`), Q2 (`:518`) e Q3 (`:1252`) morreram; Q4 (`:1253`, `if True`) sobreviveu, rc=1.
- Vermelho antes do verde (`forge-testes --vermelho 928e61b`, a árvore limpa): `vermelho: base=928e61b66015 head=dd8a37893798`, `contagem: não prova (passa na base)=2421; prova (API ausente)=1; prova (asserção)=20; pulado=28; sem veredito=2`, rc=2. Dos módulos do lote: 16 testes provam por asserção (`test_entrega_git_falha` e `test_pedido_fora`), 19 passam na base por serem de caminho saudável. Os dois "sem veredito" são `test_hooks` (prazo, módulo que o lote não toca) e `test_git_que_falha_exige_todos_os_portoes_sem_excecao`, cuja base eu rodei à mão: `TypeError: 'NoneType' object is not iterable` em `gatilhos` (`bin/forge-check:540` da base), que é a prova do C-4.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E2 C-1/C-2: `--pedido` fora de `docs/pedidos/` das raízes recusa com rc 2 (absoluto, `~/`, `../`, link, `docs/pedidosX`, `./x.md`) | sonda ponta a ponta `entrega` e `brief` (abaixo) e `tests/test_pedido_fora.py` | caminho fora da raiz; prefixo vizinho; link no último componente e em pasta intermediária | passou |
| E2 C-4/C-6: id nu e caminho legítimo dentro das raízes passam | sonda: `p1` (raiz de brief), `p2`, `docs/pedidos/p2.md`, absoluto da raiz, `~/.forge-contrib/docs/pedidos/p1.md` | ordem das raízes | passou |
| E2 T-1/T-2: nenhuma raiz nova; sem aceitar com aviso | leitura do diff e sonda (`/tmp`, cwd) | cwd e `/tmp` fora | passou |
| E3 C-1/C-2: a falha do git em qualquer passo reprova (rc 1) com `escopo: o git falhou (<passo>)` e nunca vira "nada a conferir" | sonda com `git` falso por padrão, etapas `codigo`, `review`, `merge-integracao`, e `tests/test_entrega_git_falha.py` | diff, rev-list, contagens, base | passou |
| E3 C-3: o filtro não tira arquivo na falha | sonda com `--desde` e merge da base (diff `..`, `--first-parent`, `merge-base`) e testes de filtro | filtro com conjunto vazio | passou |
| E3 C-4: `gatilhos` com `None` não levanta exceção | `test_git_que_falha_exige_todos_os_portoes_sem_excecao` (vermelho na base com `TypeError`) | `None` de `arquivos_da_entrega` | passou |
| E3 T-4: git saudável com saída igual à da base | sonda: saída byte a byte, base `928e61b` contra o head, 3 etapas, com e sem `--desde` | caminho de sucesso | passou (6 de 6 iguais) |
| `R-QA`: mutação no diff, um mutante por linha de guarda | `forge-mutante` e `--cobertura` | `:504`, `:518`, `:1252`, `:1253` | reprovou (A1, A2) |

## Cenários e resultado real
Repositório descartável em `$TMPDIR/qa-engineer-lote-fc-seguranca/e2e` (`develop` e `melhoria/x`, HOME falso com `~/.forge-contrib/docs/pedidos`), `forge-check` do head contra o da base `928e61b`.

**E2, `entrega --pedido`.** Head: recusa com rc 2 e `--pedido fora de docs/pedidos/ das raízes` para `/tmp/...`, absoluto solto, `~/notas.md`, `$HOME/notas.md`, `docs/pedidos/../propostas/x.md`, link `docs/pedidos/link.md` e `docs/pedidos/dirlink/alvo.md` para fora, `docs/pedidosX/x.md`, `./x.md`, `x.md`, o link de `~/.forge-contrib/docs/pedidos/link2.md`, os ids `link` e `link2` e `../x`. Passam (rc 0): `p1`, `p2`, `docs/pedidos/p2.md`, o absoluto da raiz e `~/.forge-contrib/docs/pedidos/p1.md`. Na base, o absoluto solto, `~/notas.md`, o link e o `$HOME/notas.md` passavam com rc 0: o abuso era real e o head o fecha.

**E2, `brief --pedido`.** Mesmo contraste: o head recusa `solto2.md` absoluto, `~/notas.md`, `../x`, o link e `lk` (rc 2); passam o id nu, `docs/pedidos/...` e o caminho da raiz de brief (rc 0). A base aceitava o absoluto solto e o link.

**E3, git falho.** O `git` falso sai 128 só no padrão pedido. Head: `*--name-only*...*`, `*rev-list --parents -n 1*`, `*--numstat*`, o `rev-parse` só do Base-sha (`--verify --quiet <sha>`), o `rev-list --first-parent` e o diff `..` do filtro dão rc 1 e `escopo: o git falhou (...)` nas etapas `codigo`, `review` e `merge-integracao`, com e sem `--desde`; nenhuma sai "nada a conferir". Na base, o diff falho na etapa `review` virava `escopo: sem commit (nada a conferir)` com rc 0, o rev-parse do Base-sha que falha dava `confira "a.txt"` com rc 0, e o filtro do primeiro pai com o git falho seguia sem aviso (rc 1 só pela falta de `Conferida` do meu pedido). O `rev-parse --verify` geral sem o Base-sha legível sai rc 2 (recusa da ref, igual à base), o que não é falha aberta. `merge-base` falho sai "Base-sha fora da branch", rc 1, como na base.

**Acessibilidade e E2E de interface:** não se aplicam (CLI, sem tela).

## Já registrados nos pareceres (não repetidos)
Review A1 e A6; segurança A5 (`bin/forge-check:6118`) e A7 (docstring de `arquivos_da_entrega`).

## Riscos
- O comportamento do lote passou em tudo que provei; o risco é só a prova de mutação, que fica sem rodar inteira até a spec ser corrigida.
- AR-1 (lista de mutantes incompleta) volta pela sétima vez; a linha de `docs/engineering/achados-recorrentes.md` fica com o tech-lead, porque o pedido manda commitar só este parecer.
- Nada dos pareceres anteriores avisa que a lista do lote ficou inválida depois do A6: eles rodaram mutantes soltos; a rodada completa das specs é o que acusa (A1).
