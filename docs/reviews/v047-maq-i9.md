---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-maq-i9
commit: 029b6456889d801782d65c06adc1ce0423cb2b54
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047 (E2.192, MAQ-I9 fatia 3, lote TE1)

Intervalo `4138445e..029b6456` (Base-sha = merge-base), 1 commit de código, teste, mutantes e changelog, feito por outra instância (E2.178). Classe C (código de controle do Forge). A fatia 1 (conferir-reversao) já está na develop (53a398ad, 8af66e32); a fatia 2 fica com o dono, como manda a E2.178.

## Achados
- A1 (recomendado) bin/forge-testes:925 · a trava vale só sem `-k`; `--completa -k ''` (ou `-k test`) roda a suíte inteira pelo discover, fora da trava e da fila do pre-push. Sonda: `unittest discover -k ''` rodou os 2 de 2 testes. Sugestão: tratar o filtro vazio como sem filtro, em item próprio.

## Sondas

## Parecer
**Aprovado.** O diff faz o que a E2.178 pede para a fatia 3, nem mais nem menos: a suíte completa sem `-k` (pedida ou vinda do plano) vira `execv` de `.githooks/pre-push --suite` da cópia do script; raiz diferente ou pre-push sem `+x` sai 2 sem recuo para o `discover`; a completa do plano só segue com o `--status` em 1. O `--afetados` (o que o pre-push usa) e o `--vermelho` (retorna antes) não mudam, e o pre-push não chama `forge-testes` fora do `--afetados`, então não há laço de `execv`. Ordem das travas sem inversão: `bin/forge-testes --completa` e `pre-push --suite` são ambos pesados no hook `pesado`; a completa do plano (comando leve para o `pesado`) é justamente a que não entra na fila com a suíte rodando.

Checklist (leitura; o Forge não tem `docs/engineering/praticas.md`, vale o da skill):
1. Escopo: confere com a E2.178 (fatia 3). Changelog em fragmento, sem tocar o `CHANGELOG.md`.
2. Regras: `R-TETO` é o objetivo; `R-VERIFY`, `R-CUSTO` e `R-NEUTRO` sem alcance.
3/4. Legível; mensagens de erro em stderr com o motivo e o caminho; `sys.stdout.flush()` antes do `execv`. A1 é limite do recorte "sem `-k`" que a própria spec declara: recomendado.
7. Testes de comportamento de cada ramo (`TravaDoForgeTestes`): `--completa` vira `--suite` com argv fixo e código 7 do falso chegando inteiro (prova o `execv`); `-k` e `--afetados` sem tocar a trava; sem `+x` e ausente saem 2 sem rodar; script de outra cópia sai 2; `--status` 0, 2, 3 e sinal valem ocupado e 1 libera. Subprocesso com `-I`, `PATH` fixo e ambiente limpo (`LIMPO` tira `CI`, `GITHUB_ACTIONS`, `PYTHONPATH`, `FORGE_*`, `GIT_DIR*`, `GIT_INDEX*`; AR-4 conferido). Os três testes antigos ajustados seguem provando o que provavam (log com `-k`, dirigido anotando).
9. Um commit coerente, Conventional Commits em português.
10. Sem mecanismo novo: reaproveita a trava e a fila do pre-push.
11. Achados recorrentes (PA-7) conferidos: AR-1/AR-2 (mutantes e ramo de falha) cobertos; AR-9 (texto antigo): o `--help` e o docstring foram atualizados; nada a gravar em `docs/engineering/achados-recorrentes.md`.

Guardas e mutantes (`R-REVIEW`, 'Mutantes declarados'): 9 mutantes em 2 specs (8 + 1), um por linha de guarda. Rodado aqui no head: `bin/forge-mutante --processos 1` nas duas specs, M1 a M9 morreram; `--cobertura --base 4138445e` rc=0, as 4 linhas de condição `coberta`, nenhuma sem mutante; `--conferir --base 4138445e`: "o trecho de cada spec do diff está no lugar". Testes do item: `python3 -m unittest tests.test_testes_tocados.TravaDoForgeTestes tests.test_testes_tocados.Execucao tests.test_testes_tocados.MedidaDaVagaPesada`, 25 OK (1 pulado pelo sandbox sem `/proc`) em 6,9 s. A suíte inteira fica para o CI do PR (sem PR nesta etapa). Sem shell tocado.

Tamanho (M14): 142 linhas de código e teste (`bin/forge-testes` 31, `tests/test_testes_tocados.py` 111), dentro da orientação, um comportamento.

Segurança tem parecer próprio (E2.193); não o refaço.
