---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-d2-resto
commit: f1d048fb8051ee5c7a6d152ccc767e6794ea37a6
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0481 (E11.16, #881, D2 `forge-check pronto`, revalidação por delta)

Gatilhos: controle do Forge (`bin/forge-check`, `bin/forge_pronto.py`).

Rodada anterior: aprovado no `ec5c704` (o git guarda o texto dela). Esta é a revalidação do delta `ec5c704..f1d048f`, a volta E11.13. Pelo `forge-check parecer delta`, o domínio só tem `bin/forge-check` (`cmd_pronto`, `:1224-1245`) e `bin/forge_pronto.py` (docstring e `conferir`, `:52-76`). Li os dois inteiros. Fora do domínio, e lidos também: `tests/test_forge_pronto.py` (5 testes novos), as quatro specs de mutante (renumeradas de M1 a M27, mais a spec `-4` nova) e o fragmento de changelog. Achados anteriores: não havia nenhum. As duas observações da rodada anterior seguem iguais: a catraca da branch no `pronto` e o `--base` sem `--`, sem fronteira de confiança.

## Veredito do delta: só aperta ou neutro
- **O rc 0 continua exigindo tudo ok.** `conferir` devolve `1 if reprovadas else 2 if nao_verificaveis else 0` (`bin/forge_pronto.py:76`). Cada passo com rc diferente de 0 entra numa das duas listas (`:63`). O corpo `None` vai a `tamanho_e_corpo`, que reprova (`:40`), ou a não verificável (`:64-66`). Nenhum dos caminhos novos cai no 0.
- **Agora 1 vira 2 em só três casos, e nenhum deles passa:** passo que sai 2, comando que não abre (`rodar` devolve 2, `:34`) e `gh` em erro sem `--corpo`. Reprovado vence o não verificável (`:76`). Passo morto por sinal (rc negativo) e saídas 1, 3 e 255 seguem reprovando.
- **Sem PR ou com PR fechado, continua reprovando (1), não vira 2.** `pr_da_branch` devolve `({}, None)` para "no pull requests found" (`bin/forge-check:9448`), e o `motivo` fica `None`. Só "sem gh", timeout, erro de rede ou JSON ilegível trazem motivo e levam ao 2 (`:9443-9454`). Branch destacada (`branch` vazio) cai em `(None, None)` e reprova (`bin/forge-check:1242`).
- **Nada consome o rc do `pronto` como prova.** O único chamador é o parser (`bin/forge-check:11087`). O `pr`, a catraca e o CI seguem como portão, e o diff não toca em nenhum deles.
- Observação, sem caminho de ataque: com `gh` em erro e sem `--corpo`, o teto H1 não é avaliado (`bin/forge_pronto.py:63`, o mock `teto.assert_not_called` confirma). Um diff de 151 linhas sai 2 em vez de 1. Continua não passando, e a mensagem manda passar `--corpo`.

## Mutantes e sondas
`bin/forge-mutante` com as quatro specs numa chamada, no `f1d048f`: rc 0, 27 de 27 morreram (M1 a M27, ids únicos, rodada única).

Sonda local (`sonda_pronto2.py` no rascunho da sessão, contra o Revisar-sha): `conferir` com o produto de 7 passos (ok, rc 1, 2, 3 e 255, SIGKILL, comando que não abre), falhas do teto (nenhuma ou uma), corpo (`None`, vazio, texto) e `sem_corpo` (`None` ou motivo). São 84 combinações, e todas deram o rc esperado (0 só com passo ok, sem falha e com o corpo verificável). O teto nunca é chamado com `corpo None` mais motivo. O `tamanho_e_corpo` real com `corpo None` reprova. Nenhuma combinação divergiu.

## Suíte e CI
Rodado aqui: `python3 -m unittest -q tests.test_forge_pronto`, 19 testes OK no Revisar-sha. CI do #881 no momento deste parecer: instalação, bateria (passos) e árvore já provada passaram. A suíte (10 partes) e as verificações longas estavam pendentes. A bateria (pareceres) e a catraca falharam pelos mesmos motivos da rodada anterior: faltam pareceres no head, e o rótulo `afrouxa-regra` do dono (R-CONFORMIDADE, ADR 0008) é decisão dele (R-DECISAO). Este parecer serve de insumo para essa decisão: o delta só aperta ou é neutro. O merge continua preso à suíte verde no CI.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Leitura estática, mais os mutantes e a sonda acima. O delta não traz segredo nem dependência nova, então `gitleaks` e `osv-scanner` não se aplicam.
