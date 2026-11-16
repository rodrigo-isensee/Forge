---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-ci-falhas-no-resumo
commit: 8262345394250e8b2f2130950da47af33fac4621
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-16
---
# QA: v047 · ci-falhas-no-resumo (E2.270, parecer E2.289)

Parecer completo (não havia parecer anterior) no head 82623453, base 5e74c70e. Sem especificação de UX nem contrato de API: as obrigações vêm do item E2.270 (o CI escreve no resumo e em anotações o nome e o local dos testes que falharam) e de `R-CUSTO` (sem custo), `R-SEGURANCA` (registro de teste é texto não confiável). Escopo: `scripts/falhas-no-resumo.py`, os 6 passos novos do `ci.yml`, os testes `tests/test_falhas_no_resumo.py`, `tests/test_ci_local.py`, `tests/test_suite_partes.py` e a spec de mutantes. A suíte inteira roda no CI do PR; cito o check-run `bateria` do mesmo sha como prova da suíte, não rodei a suíte inteira local.

## Achados
- A1 (recomendado) scripts/falhas-no-resumo.py:156 · 10 condições Python mudadas sem mutante declarado em `--cobertura` (linhas 156, 160, 162, 171, 178, 179, 180, 189, 199, 209). Não é pedido de controle, não bloqueia; o autor pode declarar ou isentar.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E2.270-a falha e erro com teste, módulo, linha e erro | `Execucao.test_falha_escreve_no_resumo_anota_e_sai_com_zero`, `Leitor` (subteste, setUpClass) | subteste, setUpClass | passou (vermelho na base) |
| E2.270-b verde traz só a contagem | `Execucao.test_verde_so_a_linha_da_contagem` | zero falhas | passou (vermelho na base) |
| E2.270-c tetos de tabela e anotações | `Leitor.test_tetos_da_tabela_e_das_anotacoes` | máximo, logo acima do teto | passou; F4 e F5 morrem |
| E2.270-d registro ausente ou argumento errado não reprova | `Execucao.test_registro_ausente_ou_argumento_errado_nao_reprova` | ausente, uso inválido | passou; F9 e F10 morrem |
| E2.270-e registro não vira comando, tabela nem segredo | `Leitor.test_texto_do_registro_nao_vira_comando_nem_tabela_nem_segredo` | `::`, quebra de linha, `\|`, `<`, segredo | passou; F1, F2, F3, F6, F7 morrem |
| E2.270-f caminho fora do repositório ou com `..` | `Leitor.test_quadro_fora_do_repositorio_ou_com_ponto_ponto_fica_sem_arquivo` | `..`, fora da raiz | passou; F8 morre |
| E2.270-g local é o quadro dos testes, erro é a exceção, bloco repetido conta um | três testes de `Leitor` | quadro posterior do repositório, diff da mensagem | passou; F11, F12, F13 morrem |
| E2.270-h fiação: leitor depois da suíte em cada job, pipefail mantém o rc, permissões iguais | `Fiacao.*`, `test_ci_local`, `test_suite_partes.FiacaoDoCI` | `-I`, `!cancelled()`, `permissions` | passou; F14 morre |

## Cenários e resultado real
- `python3 -m unittest tests.test_falhas_no_resumo tests.test_ci_local tests.test_suite_partes` na raiz do clone: `Ran 119 tests in 104.512s`, `OK`.
- Sonda manual: registro com linha `::stop-commands::x` depois do erro e rótulo simples: sai uma anotação `::error file=tests/test_ci_local.py,line=3::m.C.test_x: AssertionError: a`, a linha injetada não vira comando, resumo em tabela correta, rc=0.
- Fiação conferida no diff: os 4 jobs que rodam a suíte têm `set -o pipefail` e `| tee`, e o passo do leitor com `if: ${{ !cancelled() }}` (partes: também `provada != 'true'`), `python3 -I`, sem mudança em `permissions` e sem rede. Sem custo (`R-CUSTO`). O texto de registro impresso pelo próprio passo da suíte já era assim antes (não é novo).

## Vermelho antes do verde (`forge-testes --vermelho`, restrito aos 3 módulos tocados por `--modulos`; a rodada sem restrição passa dos 550 s)
```
vermelho: base=5e74c70e01fa head=826234539425 módulos=test_falhas_no_resumo,test_ci_local,test_suite_partes (restrito por --modulos)
revertidos à base: .github/workflows/ci.yml, changelog.d/v047-ci-falhas-no-resumo.md, scripts/falhas-no-resumo.py
mantidos no HEAD: tests/mutantes/v047-ci-falhas-no-resumo.json, tests/test_ci_local.py, tests/test_falhas_no_resumo.py, tests/test_suite_partes.py
contagem: não prova (passa na base)=98; prova (API ausente)=13; prova (asserção)=8
rc=0
```
Nenhum teste cai no HEAD (todos `H=ok`). Os testes mudados `test_rapida_e_bateria_rodam_a_suite_pelo_script_dividido` e `test_a_suite_inteira_so_roda_nas_partes_e_na_rapida` provam por asserção.

## Mutação no diff (`bin/forge-mutante tests/mutantes/v047-ci-falhas-no-resumo.json`)
```
forge-mutante: pedido=v047-ci-falhas-no-resumo rev=826234539425 spec=ee3dde3dfc68311ac0f2471490bd10133681af66bd5f3f4613b137e324002658
F1 a F14 · morreu (14 de 14; nenhum sobrevivente, nenhum sem veredito)
```
`--cobertura --base 5e74c70e` lista 10 condições sem mutante (A1, recomendado: o item não é de controle).

## Segurança e abuso
Sem gatilho de segurança declarado no brief. O abuso evidente (injeção de comando de workflow e de Markdown pelo registro) tem teste e mutantes (F1 a F3, F6, F7).

## Achados recorrentes (PA-7)
Conferi AR-5 (python sem `-I` em caminho que decide): o leitor é chamado com `-I` nos 4 passos (F14 guarda o do 3.14). AR-12 (spec de mutante desatualizada): os 14 mutantes aplicam no head. Sem classe nova.
