---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-ae3-1-controle
commit: 59ad2edc89d3ae5d030c994c1c2b0bd67fae90c0
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0478 (E108.7, revalidação da volta única do AE3.1 bin/forge_controle.py)

Revalidação por delta (H3, `R-REVIEW`): li só `forge-check parecer delta docs/reviews/v0480-ae3-1-controle.md`, intervalo 98882c49..59ad2edc, sem o que veio da `develop`. No domínio: `bin/forge_controle.py`, `tests/test_forge_controle.py`, `tests/mutantes/v0478-ae3-controle-5.json` e `-6.json`, o fragmento do changelog e `tests/pesos-d4.json` (este só do merge da base b97343ca; o commit de correção 59ad2edc não o toca). Código do delta: 41 linhas em `bin/forge_controle.py`, dentro do teto H1, um comportamento (o `salvar` recusa o que rodaria código de fora ou escaparia da pasta).

O delta fecha o A1 da rodada anterior (fsmonitor, filtros, assinatura): `_comando_na_config` lê a config efetiva (`config -z --list`, com includes) e sai `nao-verificavel` sem mexer nela (`R-VERIFY`). Também traz o que o parecer de segurança pediu: `SEGREDO` sem diferença de caixa e com `.netrc`, `credentials*`, `secrets*`, `.p8`, `.kdbx`, `.jks` e `.keystore`, e a trava aberta com `O_NOFOLLOW` pelo caminho não resolvido. Os recomendados A2 a A4 da rodada anterior viraram cartão (`R-REVIEW`) e saem deste parecer.

## Sondas
- S1 · `[core] fsmonitor` sem valor (booleano implícito) e `KANBAN.md` mudado · espera: `nao-verificavel` · obtido: `('nao-verificavel', 'comando na config core.fsmonitor')`
- S2 · `salvar` numa worktree ligada (`--git-path` devolve caminho absoluto) · espera: `salvo` com a trava em `.git/worktrees/<w>/` · obtido: `('salvo', '13e05295...')`, trava em `r/.git/worktrees/w/forge-controle.lock`

## Parecer
Aprovado. Cada guarda nova tem mutante declarado (CTL26 a CTL35, um por linha) e teste do ramo de falha por comportamento (o script de fsmonitor, filtro ou gpg não roda; o alvo do link da trava não é criado); o ramo de sucesso com `false`/`off` também é provado. Valor vazio (`key =`) também barra: lado seguro, não é defeito.

Provas lidas e rodadas:
- `python3 -I -m unittest discover -s tests -p test_forge_controle.py` (ambiente limpo): `Ran 41 tests ... OK`.
- `bin/forge-mutante --processos 1 --rev 59ad2edc` nas specs `v0478-ae3-controle-5.json` e `-6.json`: 10 de 10 mortos (CTL26 a CTL35), rc=0.
- `bin/forge-mutante --cobertura --base 98882c49 --rev 59ad2edc`: as guardas de `bin/forge_controle.py` (linhas 47, 63, 68, 70) cobertas; os "não coberto" listados são da base (`bin/forge-fechar`, `tests/pesos-d4.json`), fora do domínio.
- Suíte inteira: fica no CI do PR (não rerrodada aqui).
