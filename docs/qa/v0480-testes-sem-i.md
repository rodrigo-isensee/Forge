---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-testes-sem-i
commit: 870f0b9157ad1953d2aa343be767e85b48ab0c34
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0478 (E161.3, TESTES-SEM-I-NA-RAIZ, PR #845)

Base 789fc141, head 870f0b91 (um commit de código). Diff: `skills/qa-testing/comandos.md` (forma única), os três apontadores em `skills/*/SKILL.md`, o fragmento do changelog e a classe `RodarUmModuloComIsolamento` em `tests/test_forge.py`. Sem UX nem API: a obrigação é E161.1 (forma única na raiz, sem `-I`, dita uma vez). Suíte inteira não rodada (CI do PR, `R-QA`); só os arquivos tocados.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A forma `python3 -m unittest tests.test_x` aparece uma só vez em `comandos.md` | `test_a_forma_e_dita_uma_vez_e_as_skills_apontam_para_ela` | exatamente 1 ocorrência; mínimo de 40 arquivos lidos em skills+agents (guarda de suíte vazia); nenhum `-I -m unittest discover` restante | passou; cai na base |
| As três skills apontam para `comandos.md`; a contribuição fica em `nice` e um arquivo por vez | mesmo teste (`subTest` por skill, seção 5) | ponteiro ausente; texto da seção 5 | passou; cai na base |
| A forma roda de fato na raiz, sem `-I`, num projeto mínimo com módulo vizinho | `test_a_forma_roda_na_raiz_sem_menos_i` | `tests/` sem `__init__`; ambiente limpo; "Ran 1 test" | passou; erro na base (a forma não existia) |
| `-I` com `tests.<mod>` não importa (o aviso de `comandos.md` segue verdadeiro) | `test_tests_ponto_modulo_com_menos_i_nao_importa` | rc diferente de 0 sob `-I` | passou; inalterado (passa na base, é regressão da afirmação, não correção) |

## Cenários e resultado real
- Clone `/root/.forge-contrib/wt/v0480-testes-sem-i-qa` no head 870f0b91. Forma nova de `comandos.md` executada: `nice -n 19 python3 -m unittest tests.test_forge.RodarUmModuloComIsolamento` → `Ran 3 tests ... OK`; uma classe de módulo real `tests.test_forge.DocsPareceresPedidoECaminho` → `Ran 11 tests ... OK`; um teste (`...RodarUmModuloComIsolamento.test_a_forma_roda_na_raiz_sem_menos_i`) → `Ran 1 test ... OK`. As três granularidades da forma (módulo, classe, teste) funcionam.
- Vermelho antes do verde, à mão: `git archive origin/develop` numa pasta em `$TMPDIR` com o `tests/test_forge.py` do head por cima → `ERROR: test_a_forma_roda_na_raiz_sem_menos_i`, `FAIL: test_a_forma_e_dita_uma_vez_e_as_skills_apontam_para_ela`, `Ran 3 tests, FAILED (failures=1, errors=1)`; o terceiro teste passa nos dois lados, como esperado.
- `bin/forge-testes --vermelho origin/develop --modulos test_forge` (1012 s): abriu com `vermelho: base=789fc14160fd head=870f0b9157ad módulos=test_forge (restrito por --modulos)` e listou como revertidos à base `changelog.d/v0480-testes-sem-i.md`, as três `SKILL.md` e `comandos.md`; mantido `tests/test_forge.py`. Eu cortei a saída em 20 linhas (`head -20`), então o veredito e as linhas da classe `RodarUmModuloComIsolamento` não foram capturados; o vermelho por teste acima vem da execução manual. Não repeti a rodada de 17 min.
- Resíduo do `-I` antigo: `grep` em `skills/` e `agents/` só acha a frase negativa de `comandos.md:11` (a ressalva correta). Os demais acertos são pareceres arquivados e o teste.
- Oráculo: pedido sem guarda nem controle, sem `tests/test_oraculo_*` próprio; não aplicável. Mutação: o diff não muda regra de código em `bin/`, `hooks/`, `.githooks/` nem `tests/catraca.py`; não aplicável.

Bugs: nenhum.
