---
tipo: qa
contrato: 1
pedido: CI-PY314
branch: melhoria/ci-py314
commit: e01e13d4ea1712c726a3346ce27ca33a176e3445
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-23
---
# QA: CI-PY314

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 (job em Python 3.14, sem renomear checks, ações por sha) | CT-01 leitura do diff de `.github/workflows/ci.yml` | nomes `bateria`, `checagem rápida (push na develop)`, `catraca` intactos; shas iguais aos do job atual | passou |
| PQ-1 (job roda na branch enviada) | CT-02 log do run 39979644068 | versão do Python impressa e número de testes | passou |
| Falha só no 3.14 deixa o job vermelho | CT-03 leitura do passo | `run` multilinha em `bash -e`: `scripts/suite-paralela.py` sai com `sys.exit(main())`, rc diferente de zero derruba o passo; setup-node, CLI e e2e usam `!cancelled()` e rodam mesmo assim, o job fecha vermelho | passou (por leitura, sem quebrar nada) |
| Teste `Workflows` | CT-04 `python3 -m unittest tests.test_catraca` | trava de passos únicos e nomes dos workflows | passou |

## Cenários e resultado real
- CT-02: no run 39979644068 (conclusão success), `bateria (python 3.14)` imprimiu `Python 3.14.8`, depois `suite-paralela: 1594 testes em 44 módulos, 4 processos` e `Ran 1594 tests in 240.021s (4 processos)` / `OK`; o passo `bash tests/e2e-instalacao.sh` terminou com `e2e-instalacao: ok (plugin instalado, 8 agentes, 9 skills, projeto inicializado)`. Todos os passos do job em success; `bateria` (3.12) também success; `checagem rápida` skipped, como esperado em PR.
- CT-04: na worktree do commit, com Python 3.14.4 local, `python3 -m unittest tests.test_catraca` deu `Ran 222 tests ... OK` (as mensagens "API do GitHub não respondeu" são ruído esperado da rede bloqueada pelo sandbox, tratadas como sem rótulo).
- Não rodei a suíte completa local (o run do CI no 3.14 já a cobre sobre este conteúdo; os commits seguintes só adicionam pareceres em `docs/`). Nenhum novo run do CI foi disparado.
- Observação (não bloqueia, já no review como A1): o job 3.14 roda tudo também em commit só de parecer, pois não usa o gate da `bateria`; custo de minutos de CI em repositório público, sem cobrança.
- Vermelho antes do verde e mutação: não se aplicam (mudança de workflow, sem código de produção nem teste novo).
- Pendência do dono, fora do escopo: tornar `bateria (python 3.14)` obrigatório na proteção de branch.
