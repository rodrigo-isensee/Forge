---
tipo: qa
contrato: 1
pedido: textos-a1
branch: melhoria/textos-a1
commit: b9a8d7548e429dc7abebd4c61c5c16895484a001
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-20
---
# QA: textos-a1

Entrega: texto (R-FLUXO, seção nas skills qa-testing e ci-cd), 4 casos de teste do hook do papel aq e fragmento de changelog. O HEAD da branch é 62a4803 (só o parecer do review sobre b9a8d75); o código testado é b9a8d75.

## Achados

## Critério → teste → resultado
O pedido não traz `CA-n`; as obrigações são os itens E1 a E4.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 (R-FLUXO com leitura da develop do remoto após `git fetch`) | testes de duplicação, neutralidade, invariantes e changelog da suíte | acréscimo não remove item protegido | passou |
| E2 (4 casos do hook aq) | `test_aq_grava_so_nas_duas_pastas_do_clone_de_contribuicao` (4 casos novos, todos rc 2) | maiúsculas, clone como link para fora do home, `.git/` aninhado | passou (mutação feita no review: os 4 falham sem o controle) |
| E3 (roteiro de simulação de merge) | execução manual do roteiro, abaixo | base remota ausente | passou |
| E4 (fragmento) | teste de changelog da suíte | n/a | passou |

## Cenários e resultado real
- Suíte: `python3 -m unittest discover -s tests -q`, sem outra suíte rodando (`.githooks/pre-push --status` rc=1 antes; esperei uma que rodava): 1082 testes, OK, 261 s. Nenhuma falha, logo nenhum teste instável observado (cartão FLAKY-CARGA sem novidade).
- `scripts/validar-plugin.sh`: Validation passed (avisos de ícone ausente; o validador tentou rede e foi negado pelo sandbox, sem efeito no resultado).
- Roteiro de merge, em cópia em `$TMPDIR` (clone da worktree): `git fetch origin develop` ok; `git rev-parse refs/remotes/origin/develop` = 0f480c8; `git merge --no-ff refs/remotes/origin/develop` rc 0 ("Already up to date", a develop não andou); diff contra essa base mostra as 6 mudanças da entrega; `tests.test_hooks` na cópia: 34 OK. Contra-prova: clone `--no-tags --single-branch` da branch não tem `refs/remotes/origin/develop` e `git rev-parse` falha, como a skill avisa. O roteiro funciona como está escrito.
- Vermelho antes do verde: não refeito aqui; a mutação do hook feita no review (62a4803) mostra os 4 casos novos falhando.
- Observação (não bloqueia): o roteiro não diz como montar a cópia (clone de onde); funcionou com clone da worktree porque ela tem a `develop` local.
