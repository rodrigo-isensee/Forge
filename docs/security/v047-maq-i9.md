---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-maq-i9
commit: 029b6456889d801782d65c06adc1ce0423cb2b54
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047-maq-i9 (MAQ-I9, fatia 3)

Etapa E2.193 do pedido v047. Escopo: `4138445e..029b6456` (`bin/forge-testes`, `tests/test_testes_tocados.py`, `tests/mutantes/v047-maq-i9*.json`, `changelog.d/v047-maq-i9.md`). Parecer completo (não havia parecer anterior nesta branch).

## Gatilhos
Controle da fábrica que guarda a `R-TETO` (a suíte inteira uma por vez): o `bin/forge-testes` passa a entregar a suíte completa sem `-k` ao `.githooks/pre-push --suite` (trava e fila) por `execv`, sem recuo para o `discover`. Sensível da catraca (`R-SEGURANCA`).

## Achados
- A1 (recomendado) bin/forge-testes:925 · Com qualquer `-k` a completa segue fora da trava; `--completa -k test` casa todo teste e roda a suíte inteira sem pre-push (sonda no detalhe). Desenho declarado no changelog; vale contar os casados contra o total ou levar `-k` largo à trava.
- A2 (recomendado) tests/test_testes_tocados.py:1586 · `LIMPO` é lista negativa de ambiente (AR-3): tira CI, FORGE_*, GIT_DIR e GIT_INDEX mas herda GIT_WORK_TREE, GIT_CONFIG_* e GIT_CEILING_*; prefira lista positiva (HOME, LANG, TMPDIR) como o PATH já fixado.

## Sondas

## Detalhe dos achados
**Conferido sem achado.**
- `bin/forge-testes:77`: `PRE_PUSH` vem de `Path(__file__).resolve()`, não do cwd; `bin/forge-testes:799` recusa (sai 2) quando a raiz da cópia do script difere de `git rev-parse --show-toplevel` do cwd. Um repositório alheio não consegue fazer o script executar o pre-push dele, e um script de outra cópia (ou um link simbólico para o cache do plugin) falha fechado, sem recuo ao `discover` (AR-7 coberto).
- `bin/forge-testes:803`: pre-push ausente ou sem `+x` sai 2. A janela entre `os.access` e `execv` não dá ganho: o arquivo é do mesmo usuário e da mesma árvore que o próprio script.
- `bin/forge-testes:807`: só a saída 1 do `--status` vale "livre"; 0, 2, outro código e morte por sinal valem ocupado (teste `test_completo_por_plano_so_roda_com_o_status_livre`). O `--status` do pre-push usa `flock -n`, não bloqueia, e roda com `stdin` nulo.
- `bin/forge-testes:813`: `argv` fixo (`--suite`), sem entrada do usuário; o `execv` não passa por shell. O modo `--suite` do pre-push só é aceito com exatamente esse argumento e herda a trava.
- `--afetados` (o plano do pre-push) nunca chama a trava, o que evita recursão do pre-push em si mesmo (teste `test_afetados_nao_passa_pela_trava`).
- Os testes novos rodam o script com `-I` (AR-5) e `PATH` fixo.

**A1.** Evidência: `bin/forge-testes:925` desvia para a trava só quando `not args.filtros`. Sonda executada num repositório temporário com o pre-push falso registrando chamadas: `python3 -I bin/forge-testes --completa -k test` · espera (pela `R-TETO`): passar pela trava · obtido: rc=0, `Ran 1 test`, arquivo `rodou` criado, nenhuma chamada ao pre-push. Caminho: um agente que quer a suíte local sem esperar a fila usa `-k test` (todo nome de teste contém `test`) e roda em paralelo com outra suíte, o efeito que a `R-TETO` quer evitar (carga e FLAKY). Não há atacante externo nem ganho de privilégio: severidade baixa, recomendado. O changelog declara que `-k` "segue como antes", então não promovo. Correção mínima: antes de rodar com `-k`, contar os testes casados (`unittest` carrega e filtra sem rodar) e, se forem todos ou passarem de uma fração, seguir pela trava; ou passar os `-k` ao `--suite`. Esforço P. Dono: autor da branch (tech-lead da fatia).

**A2.** Evidência: `tests/test_testes_tocados.py:1586`. Caminho: o teste rodado de dentro de um hook do git (pre-push com a suíte afetada) herda variáveis `GIT_*` não listadas, e o `git init`/`commit` do fixture pode agir fora da pasta temporária ou com configuração alheia. É confiabilidade do teste, não exposição: recomendado, classe AR-3. Correção mínima: montar o ambiente por lista positiva (`HOME`, `LANG`, `LC_ALL`, `TMPDIR`, `PATH` fixo) mais as variáveis do pre-push falso. Esforço P. Dono: autor da branch.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes do item: `python3 -m unittest tests.test_testes_tocados` na raiz do clone, 157 testes, OK (1 skip pré-existente do sandbox sem `/proc`). A suíte inteira roda no CI do PR (ainda não aberto, por desenho do brief); é condição do merge, não deste parecer. Ferramentas: `shellcheck` presente; `gitleaks`, `semgrep`, `zizmor` e `actionlint` ausentes no ambiente (lacuna; a entrega não toca workflow nem traz segredo, conferido por leitura do diff).
