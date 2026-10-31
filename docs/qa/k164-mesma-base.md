---
tipo: qa
contrato: 1
pedido: k164-mesma-base
branch: melhoria/k164-mesma-base
commit: 2ea83f214e1e3ba30aa12c04670b8d279f624cd8
parecer: aprovado
revisor: qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-31
---
# QA: k164-mesma-base

Entrega testada: o hook `parecer` e o `forge-check pr` leem a mesma base do delta (`base_do_delta`, `bin/forge-check:607`); o merge puro da base depois do parecer não o invalida; mudança do autor depois do merge continua invalidando; base fora de develop, homolog e main volta ao modo estrito. Diff de 8c07b44 a 2ea83f2: 35 linhas de código (21+7 em `bin/forge-check`, 3+4 em `hooks/parecer.py`), 3 fixtures e a spec M1 a M4.

## Achados
- A1 (recomendado) bin/forge-check:612 · `base or ""` e o `if aviso:` do pr_da_cli (639) saem "sem mutante" na checagem de cobertura; sem efeito de decisão (base vazia cai em "fora do fluxo"; aviso só imprime). Declarar como `isentas` na spec na próxima mexida.

## Critério → teste → resultado
Pedido sem CA-n em EARS; as obrigações são as do escopo E1.

| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Merge puro da base depois do parecer libera, no hook | fixture `pr-merge-puro-da-base-depois-do-parecer-libera` (`tests.test_hooks.Hooks.test_fixtures`) | merge sem mudança do autor | passou |
| Mudança do autor depois do merge da base bloqueia | fixture `pr-mudanca-do-autor-depois-do-merge-da-base-bloqueia` | um arquivo do autor após o merge | passou |
| Base fora do fluxo segue estrita e bloqueia | fixture `pr-base-fora-do-fluxo-continua-estrita-bloqueia` | nome fora de BASES_DO_FLUXO | passou |
| Hook e `forge-check pr` leem a mesma base | M1 a M4 de `tests/mutantes/k164-mesma-base.json` | guarda por linha mudada | 4 de 4 mortos |

## Cenários e resultado real
Vermelho antes do verde (`bin/forge-testes --vermelho 8c07b44 --modulos test_hooks --prazo 500`), saída real:

```
vermelho: base=8c07b4448aec head=2ea83f214e1e módulos=test_hooks (restrito por --modulos)
revertidos à base: bin/forge-check, changelog.d/k164-mesma-base.md, docs/reviews/k164-mesma-base.md, docs/security/k164-mesma-base.md, hooks/parecer.py
mantidos no HEAD: tests/hooks/parecer/pr-base-fora-do-fluxo-continua-estrita-bloqueia.json, tests/hooks/parecer/pr-merge-puro-da-base-depois-do-parecer-libera.json, tests/hooks/parecer/pr-mudanca-do-autor-depois-do-merge-da-base-bloqueia.json, tests/mutantes/k164-mesma-base.json
tests.test_hooks.Hooks.test_fixtures · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=54; prova (asserção)=1
rc=0
```

A rodada sem `--modulos` (todos os módulos do diff e do plano) também saiu `saida=0` em `.forge/run/testes.log` (modo=vermelho, 3050,7 s), mas a saída em texto se perdeu por corrida de dois redirecionamentos meus; vale a rodada restrita acima.

Mutação (`bin/forge-mutante tests/mutantes/k164-mesma-base.json`):

```
forge-mutante: pedido=k164-mesma-base rev=2ea83f214e1e spec=303d38f1c2510ce4a00b755502fcab648ae9ba87edca11b29d1c597331228c5a
M1 · morreu · hooks/parecer.py:383
M2 · morreu · hooks/parecer.py:374
M3 · morreu · bin/forge-check:622
M4 · morreu · bin/forge-check:613
```

Conferência da lista contra o diff (`--cobertura --base 8c07b44`): `coberta · bin/forge-check:613 · M4`; `sem mutante · bin/forge-check:612 · base or ''` e `:639 · aviso` (A1, sem efeito de decisão); `apagada` em `hooks/parecer.py:440` e `:375` (troca de `base` no `merge` e do `sha_base`, cobertas por M1 e M2 pelo mesmo fluxo). Nenhuma linha de guarda mudada fica sem mutante.

M14 (teto e um comportamento por PR): cumpre. 35 linhas de código contra o teto de 150, um comportamento (a base do delta), uma classe em `hooks/`, fixtures e spec fora da contagem.

Não rodei a suíte completa neste parecer: o pre-push do envio roda os módulos afetados e o CI do PR roda a suíte inteira. O A1 recomendado do parecer de segurança (`hooks/parecer.py:374`) não é achado de QA.
