---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-tempo-fixture
commit: 57150d5ee607032f8e302e5319882ed3eeb0edac
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0480-tempo-fixture (PR #850, E164.3)

Diff contra a base 8f37daf8: `hooks/conformidade.py` (regex `CRITICO` linear), `tests/mutantes/v0480-tempo-fixture.json` (TF1) e o fragmento do changelog. Nenhum teste novo: a obrigação é o tempo do caso existente e a decisão igual (E164.1).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E164.1: a busca do marcador CRITICO fica linear | `test_fixtures_do_repo_publico`, caso `trava-gh-marcador-linear-libera` (limite PRAZO/2) | 8 KB de `gh repo ` repetido | passou: CPU 0,72-0,80 s na base, 0,16 s no head (3 rodadas cada) |
| E164.1: a decisão não muda | 2658 fixtures de `tests/hooks/conformidade` e demais hooks, via `test_hooks.py` | todas as fixtures, os dois lados (0 e 2) | passou (ver abaixo) |
| E164.1: a ação após outras palavras do programa segue marcada (`git -C x push`) | `test_marcador_critico_tambem_na_forma_juntada` + mutante TF1 | ação não colada ao programa | passou; TF1 morreu |

## Cenários e resultado real
- Tempo do caso `trava-gh-marcador-linear-libera` (custo de CPU do hook, `medir_o_hook`, o mesmo código de teste nas duas árvores; 3 rodadas): base 8f37daf8 = 0,720 / 0,795 / 0,722 s; head 57150d5e = 0,161 / 0,161 / 0,164 s. O caso vizinho `trava-graphql-string-aberta-prazo-bloqueia`: 0,23-0,25 s (base) e 0,23-0,28 s (head), sem mudança. Limite do teste: PRAZO_DA_DECISAO_S/2.
- Mesma saída em todas as fixtures: `python3 -I -m unittest discover -s tests -p test_hooks.py` no head (2658 arquivos em `tests/hooks/conformidade`); resultado abaixo. As fixtures não foram tocadas pelo diff, então as saídas esperadas são as da base.
- Diferencial direto base × head da regex `CRITICO` (extraída de cada `hooks/conformidade.py`, `search`): 29254 textos (todas as strings de todas as fixtures JSON + 30000 combinações aleatórias de git/gh/ações/maiúsculas/quebras de linha), 0 divergências.
- Mutação: `bin/forge-mutante tests/mutantes/v0480-tempo-fixture.json`
```
forge-mutante: pedido=v0480-tempo-fixture rev=57150d5ee607 spec=331098f7a7f3f16f1d26c1a17df7eca75d44d4e03935c77b3ceddf5ea59b5480
TF1 · morreu · hooks/conformidade.py:65
```
  rc=0. `--cobertura --base 8f37daf8`: sem condição Python mudada fora da spec; a linha de guarda mudada (a única, `CRITICO`) tem o TF1.
- Vermelho antes do verde: sem teste novo ou mudado no diff (perf, mesma decisão); o teste de tempo já existia e o diferencial acima prova o ganho, então `forge-testes --vermelho` não se aplica.
- `test_hooks.py` inteiro no clone (172 testes, 11 pulados por ambiente, 946 s): 170 passaram; 2 falhas, ambas na fixture `pesado/mesma-sessao-libera` (hook `pesado`, que o diff não toca; `PrazoEstourado: prazo de 120 s`) em `test_fixtures_do_v0442` e `test_fixtures_fatia_3`. As fixtures de conformidade e `test_fixtures_do_repo_publico` passaram. A falha repete no clone, mas `test_fixtures_do_v0442` passa (OK, 10,6 s) numa cópia limpa do mesmo commit (extraída com git archive) e na cópia da base: é ambiental (clone em worktree), não efeito do diff; o CI do PR decide.
- Suíte inteira: no CI do PR (check-run `bateria` do mesmo sha), não rerrodada aqui.
