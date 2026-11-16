---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-ci-falhas-no-resumo
commit: 8262345394250e8b2f2130950da47af33fac4621
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047-ci-falhas-no-resumo

Pedido v047, etapa E2.288: parecer completo (não havia parecer anterior) da entrega E2.270 no head `82623453`, base `5e74c70e`. Escopo lido: `.github/workflows/ci.yml` (4 jobs: `rapida`, `rapida-quatorze`, `partes-doze`, `partes-quatorze`), `scripts/falhas-no-resumo.py`, `tests/test_falhas_no_resumo.py`, `tests/test_ci_local.py`:313-314, `tests/test_suite_partes.py`:336, `tests/mutantes/v047-ci-falhas-no-resumo.json`, `changelog.d/v047-ci-falhas-no-resumo.md`.

## Gatilhos
`R-SEGURANCA`: mudança em `.github/workflows/ci.yml` (o passo que prova a suíte, base do check exigido e da prova da develop lida pela árvore testada) e um leitor de entrada não confiável (o registro da suíte, que o código do PR controla) que escreve comandos de workflow e Markdown no resumo.

## Conclusão
Aprovado. Fronteira: o autor do PR controla o registro (os testes imprimem o que quiserem), mas já controla o código que roda no mesmo runner, com o mesmo `GITHUB_STEP_SUMMARY` e a mesma saída padrão; o leitor não dá a ele capacidade nova. O que importa é que o leitor (1) não abra canal para quem não é autor e (2) não afrouxe o portão. Conferido:
- Gatilho `pull_request` (sem `pull_request_target`), `permissions: contents: read` no topo e nos jobs das partes, `persist-credentials: false`; os passos novos não têm `secrets.`, `GH_TOKEN` nem `continue-on-error` (`tests/test_falhas_no_resumo.py`:233-239).
- O rótulo chega por `env:` (`ROTULO`), não por `${{ }}` no `run:`; `matrix.parte` é estático.
- O portão não afrouxa: o passo da suíte ganhou `set -o pipefail` antes do `| tee` (sem ele o código de saída seria o do `tee`, 0); o leitor sai sempre 0, roda em passo à parte com `!cancelled()` e não tem `continue-on-error`, então quem reprova continua sendo o passo da suíte.
- Anotações: `%`, CR e LF escapados, caracteres não imprimíveis trocados por espaço, `::` desfeito e propriedades com `:` e `,` escapados; o caminho do arquivo só sai se for relativo ao repositório, existir e não ter `..` (sondas abaixo).
- Resumo: `|`, `<`, `>`, `&`, crase, `[` e barra invertida neutralizados; HTML, imagem e link do registro não chegam a renderizar.
- Teto de leitura (64 MiB), de célula (160), de tabela (25) e de anotações (10); a expressão do cabeçalho não explode (linha de 600 KB com 200 mil `a (` em 0,9 s).
- Redação de segredo nas células e anotações é defesa extra (o runner já mascara os segredos do repositório, e o PR de fork não os recebe).

## Achados
- A1 (recomendado) tests/test_falhas_no_resumo.py:225 · a guarda do pipefail só procura o texto no passo; comentar ou mover o `set -o pipefail` para depois do `| tee` nas partes passa nos testes e a suíte vermelha vira passo verde. Executar o `run:` real com python3 falso que sai 1 e exigir rc≠0, como no agregador.

## Sondas

## Detalhe dos achados
**A1.** Evidência: `tests/test_falhas_no_resumo.py`:225 usa `assertIn("set -o pipefail", ...)` no texto do passo; `tests/test_falhas_no_resumo.py`:241-246 prova o pipefail num comando de bash avulso, não no `run:` do `ci.yml`; nenhum mutante do `tests/mutantes/v047-ci-falhas-no-resumo.json` mexe no pipefail. Sonda executada: em `partes-doze` e `partes-quatorze`, troquei `set -o pipefail` + `python3 --version` por `python3 --version` + `# set -o pipefail`; `tests.test_falhas_no_resumo`, `tests.test_suite_partes.FiacaoDoCI` e `tests.test_ci_local.LeituraDosWorkflowsTest` seguiram verdes (arquivo restaurado depois). A `rapida` está presa pela igualdade exata de `tests/test_ci_local.py`:314; `rapida-quatorze`, `partes-doze` e `partes-quatorze` não. Caminho: não há atacante externo; o risco é uma edição futura do workflow (inclusive de agente) que deixe a suíte vermelha passar como verde no check exigido, sem teste que a barre. Severidade: baixa (o código do head está correto). Correção mínima: no teste de fiação, extrair o `run:` do passo da suíte de cada um dos 4 jobs (`rapida`, `rapida-quatorze`, `partes-doze`, `partes-quatorze`) e executá-lo como o Actions (`bash -e`) com `python3` falso no PATH que sai 1 e `RUNNER_TEMP` temporário, exigindo rc≠0; e um mutante que comente o pipefail das partes. Esforço: P. Dono: `devops-engineer` (teste) e `qa-engineer` (mutante).

Sondas de não regressão (não provam bloqueante, ficam em prosa): registro com `FAIL: test_x (tests.mod.C.test_x) (a=%0A::add-mask::y)` e erro com token de forma `ghp_`, `::set-env`, `<img>`, link e `|`: a anotação saiu numa linha só, com `%250A` e `: :`, o token como `[redigido]`; a tabela saiu com `&lt;`, `\[` e `\|`; rc=0. Testes do item no head: `python3 -m unittest tests.test_falhas_no_resumo` (20) e `tests.test_suite_partes.FiacaoDoCI tests.test_ci_local.LeituraDosWorkflowsTest` (22), verdes.

## Riscos aceitos e ferramentas
Nenhum risco aceito. A suíte inteira roda só no CI do PR; não confirmei o estado do CI no head (a CLI do GitHub não responde no sandbox desta sessão): o merge segue preso à bateria verde, com o `tech-lead`. Ferramentas de varredura de segredos e de workflows não estão no PATH desta máquina (lacuna; rodam no CI quando configuradas pelo `devops-engineer`); a revisão foi por leitura e sondas locais.
