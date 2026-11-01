---
tipo: qa
contrato: 1
pedido: heredoc-rapido
branch: melhoria/heredoc-rapido
commit: c1eaaec72bbb54a878baee575a7ec4ca8713190e
parecer: aprovado
escopo: completo
revisor: forge:qa-engineer
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-01
---
# QA: heredoc-rapido

Etapa E1.4 (revalidada em c1eaaec). Diff do código lido na 1ª rodada: `c454ccb..c51715f` (`hooks/conformidade.py` +8/-2, `tests/test_hooks.py` +21, fragmento de changelog). Entrega o item E1 do pedido, passo 1 do desenho: `Guarda._regras` e `Guarda._raiz_home` guardam por decisão o manifesto e o par realpath(raiz)/realpath(home). Passo 2 fora do diff. Cumpre a M14 (agents/tech-lead.md:19): 31 linhas contáveis (limite 150), um comportamento, uma classe em `hooks/`. O limite de 5,0 s do teste não mudou.

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: a recusa de R-MAIN com 3000 heredocs não muda | `Hooks.test_muitos_heredocs_recusam_dentro_do_orcamento` (duas formas) | 3000 heredocs, limite 5,0 s de parede e de CPU | passou |
| E1: decisão igual em todo o corpo de fixtures | `Hooks.test_fixtures` (corpo de fixtures dos hooks) | `so_forge`, home, projeto, papéis | passou |
| C-1/C-5 (e): uma leitura do manifesto e um home por decisão, sem cache entre decisões | `Hooks.test_regras_e_raiz_sao_calculadas_uma_vez_por_decisao` | 4 instâncias × 50 destinos | passou |
| C-5 (a),(b): 2 destinos protegidos, com e sem manifesto | `test_fixtures`: `protegido-claude-plugin-*`, `protegido-github-*`, `politica-de-conformidade-so-em-melhoria` | `so_forge` vale só com manifesto | passou (H1, H3, H4 mortos) |
| C-5 (c): sessão de projeto com manifesto forjado, `so_forge` não vale | `test_fixtures`: `so-forge-sessao-de-projeto-com-manifesto-forjado-libera` | `externo` não nulo | passou (H5 morto; era A1) |
| C-5 (d): home e raiz resolvidos (ordem e realpath) | `test_fixtures`: `vigor-claude-md-*`, `home-claude-*` | ordem `raiz, home` | passou (H8 e H9 mortos); `home-por-link-simbolico-bloqueia` (realpath do home, era A2) e `home-trocado-na-linha-bloqueia` (HOME trocado na linha, C-5 d, era A3) |

## Execução anterior (head c51715f, 2026-11-01, já lida)
Vermelho, cobertura, 9 de 11 mutantes mortos e tempo 1,4 a 1,5 s: ver o histórico da branch (303f5ee); superada pela revalidação abaixo.

## Revalidação no head c1eaaec (volta 1 do autor)
- `forge-check delta --parecer docs/qa/heredoc-rapido.md`: intervalo `c51715f..c1eaaec`; lido só o que listou: as três fixtures novas em `tests/hooks/conformidade/` (`home-por-link-simbolico-bloqueia`, `home-trocado-na-linha-bloqueia`, `so-forge-sessao-de-projeto-com-manifesto-forjado-libera`, 77 linhas, só dados) e a spec `tests/mutantes/heredoc-rapido.json`. `hooks/` e `tests/test_hooks.py` não mudaram desde c51715f: o resto (diff do código, M14, execução anterior) é "já lido" no parecer anterior. A fixture de C-5 (c) é a descrita no A1 anterior; as de A2 e A3 usam link simbólico de HOME e `HOME=/tmp/x cd /` na linha.
- Diff da branch contra a base (`c454ccb..c1eaaec`) lido: `hooks/conformidade.py` +8/-2, `tests/test_hooks.py` +21, 3 fixtures, spec, fragmento e pareceres. Entrega o item E1 (passo 1 do desenho). M14 (agents/tech-lead.md:19): 31 linhas contáveis (limite 150), um comportamento, uma classe em `hooks/`: cumpre. O limite de 5,0 s do teste não mudou.
- Mutantes: `bin/forge-mutante --cobertura --base c454ccb...` rc=0 (linhas 440 e 492 cobertas, "declarado, não provado"; conferido contra o diff: 440, 441, 492, 493 e 494 têm mutante). `bin/forge-mutante tests/mutantes/heredoc-rapido.json`, rc=0, todos mortos:
```
H1 H2 H3 H4 H5 H6 H7 H8 H9 H10 H11 · morreu (440,440,441,441,441,492,492,494,493,440,492)
```
  H5 e H9, sobreviventes do parecer anterior, agora morrem. A primeira rodada deste QA não terminou (processo sumiu, log sem saída de mutante); repeti com o `run_in_background` da ferramenta e a saída acima é dessa repetição.
- Teste: `python3 -m unittest tests.test_hooks.Hooks.test_fixtures ...test_muitos_heredocs_recusam_dentro_do_orcamento ...test_regras_e_raiz_sao_calculadas_uma_vez_por_decisao`: `Ran 3 tests in 137.638s` `OK` (corpo de fixtures inteiro, com as 3 novas).
- Vermelho antes do verde: `bin/forge-testes --vermelho c454ccb...`, rc=0, `contagem: não prova (passa na base)=1358; prova (asserção)=1; pulado=26` (o que prova é o teste de contagem; as fixtures novas provam por mutante, H5 e H9, que cai só com elas).
- Medida de tempo do hook (3000 heredocs, parede em s, WSL, load 3 a 5, 5 medidas por forma, mesmo roteiro do teste de orçamento; a primeira de cada série inclui aquecimento):

| Forma | Base c454ccb | Head c1eaaec |
|---|---|---|
| um por linha | 2,82 1,91 1,90 1,90 1,92 | 1,73 1,43 1,45 1,44 1,43 |
| `&&` | 2,00 1,99 1,97 1,96 1,97 | 1,49 1,48 1,47 1,49 1,52 |

  Redução de cerca de 25 a 27%. Com a razão CI/local do pedido (2,6 a 3,1) o pior caso (1,52) dá 4,0 a 4,7 s no runner, abaixo de 5,0 s mas acima dos 4,5 s em que o Jarvis abriu o passo 2. A medida no runner do CI sai do CI do PR (E1.5), não daqui; acima de 4,5 s lá, o passo 2 vira PR próprio.

## Achados
- A1 (recomendado) pedido heredoc-rapido:1 · a medida no runner do CI (limite 5,0 s; alerta se acima de 4,5 s) só existe no CI do PR (E1.5); local, o pior caso estimado é 4,7 s. Conferir o run antes do merge.

## Parecer
Aprovado. O código revisado cumpre o item E1 e a M14, o hook recusa igual, o tempo cai cerca de 27% e os 11 mutantes das linhas mudadas morrem (H5 e H9 só sobreviviam por falta de fixture; as três fixtures da volta 1 fecham A1, A2 e A3 do parecer anterior). Bugs de produção: 0. Pendência fora do meu alcance: a medida no runner do CI (A1).
