---
tipo: review
contrato: 1
pedido: release-0.25.0
branch: melhoria/release-0.25.0
commit: 630d200aff68570aa1a184be41b645ecb8d60ab8
parecer: aprovado
revisor: forge:tech-lead (outra instância)
data: 2026-10-20
---
# Review da release 0.25.0 e revisão a posteriori da DV-4

Escopo: o fechamento da versão (`git diff 71ac7fc..630d200`) e a DV-4 (implementação 37212eb, mesclada pelo dono no #229 sem pareceres; decisão do dono "B").

## DV-4 (37212eb)
Li o patch do commit (`git show 37212eb`: ci.yml, scripts/conferir-release.py, changelog.d/dv-4.md e quatro arquivos de teste). O `git diff aa81f6b..37212eb` citado no brief traz também reversões de seis commits que não são da DV-4, porque a DV-4 nasceu de 8833e1c, antes da 0.24.0; não as revisei como parte dela.

- **Uma função só, chamada nos dois PRs (pedido dv-4, E1):** o passo inline com a comparação de versão e o heredoc virou `scripts/conferir-release.py`, chamado por um único passo do job `bateria` cujo `if` exige `pull_request` com `base_ref` `main` ou `homolog`. A develop e o push não chamam o passo.
- **Homolog só quando a versão difere:** com `BASE_REF = homolog` o script recebe `--so-se-versao-mudou` e sai 0 sem conferir quando a versão do PR é igual à da base. Versão diferente, inclusive menor, roda a checagem inteira e reprova a menor. A base ilegível vira 0.0.0, então a checagem roda (falha fechada).
- **A main continua igual:** mesmas três checagens na mesma ordem (versão maior que a base, entrada `## [<versão>]`, `[Não publicado]` vazia) e depois `bin/forge-changelog conferir-release`; a base ilegível segue valendo 0.0.0, e as mensagens de erro são as mesmas.
- **Entradas não confiáveis:** `BASE` e `BASE_REF` chegam por `env`, sem `${{ }}` no `run` (há teste para isso). A análise de CI/CD é da devops (E2.2) e da segurança (E2.3), não refeita aqui.
- **Testes (pedido dv-4, E2):** `tests/test_conferir_release.py` prova as duas chamadas (dois `--base` no passo, as duas `base_ref` no `if`, um passo só, a regra fora do yml) e a condição (a flag só no ramo da homolog). Os testes de comportamento cobrem a homolog sem versão nova, que passa mesmo com fragmento esquecido; com versão nova, que pega o fragmento esquecido, passa com o changelog fechado e reprova sem entrada; e a main, que reprova sem versão nova, passa com a release fechada e reprova com `[Não publicado]` preenchida. As três asserções antigas (test_changelog, test_ci_local, test_forge) foram trocadas por outras equivalentes, que apontam para o script, sem afrouxar nada: o trecho `a <= b` continua exigido, agora no script.
- **No HEAD revisado:** `git diff 37212eb 630d200 -- .github/workflows/ci.yml scripts/conferir-release.py tests/test_conferir_release.py` sai vazio, então a DV-4 revisada é a que vai para a main.

## Fechamento da versão (630d200)
- Os 9 arquivos do diff são os esperados: os dois plugin.json, o CHANGELOG.md e os seis fragmentos apagados. Nenhum outro arquivo mudou.
- `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` passam de 0.24.0 para 0.25.0.
- A seção `[0.25.0] - 2026-10-20` traz as seis entregas (DV-4, DV-5, FC-AQ-HOOK, FC-PEDIDO-FORA, FECHAR-ROTULO, SUITE-CONCORRENTE) em 7 linhas, cada uma igual ao fragmento apagado (a SUITE-CONCORRENTE tinha duas), sem perda nem duplicação. `### Adicionado`, `### Alterado` e `### Corrigido` seguem o tipo de cada fragmento, e `## [Não publicado]` fica vazia.
- SemVer minor correto: melhorias e correções compatíveis, nenhuma quebra para os projetos. As entradas não trazem custo (R-CUSTO) nem termo de projeto (R-NEUTRO).
- O `changelog.d/` some do tree (pasta vazia), como na 0.24.0. Testei num `git archive` de 630d200: `bin/forge-changelog conferir-release` dá `ok` com a pasta ausente, e o `novo` cria a pasta (`mkdir`).

## Saída das ferramentas (sem refazer)
- `python3 scripts/conferir-release.py --base 71ac7fc` → `versão base: 0.24.0 | versão da release: 0.25.0`, rc 0 (o PR para a main).
- `python3 scripts/conferir-release.py --base origin/homolog --so-se-versao-mudou` (homolog em 0.24.0) → a checagem roda, rc 0 (o PR de promoção desta release).
- `python3 scripts/conferir-release.py --base 630d200 --so-se-versao-mudou` → `promoção sem versão nova: não é release`, rc 0.
- `python3 -m unittest tests.test_conferir_release` → `Ran 10 tests`, `OK`. Quem roda a suíte inteira é o pre-push deste push.
- actionlint e shellcheck não rodaram na entrega da DV-4 (ausentes na máquina); quem cobre isso é o CI do PR e o parecer da devops (E2.2), por isso não fica como pendência deste review.

## Achados

## Detalhe dos achados
- Recomendado (não bloqueia) · scripts/conferir-release.py:33 · `tuple(map(int, ...))` estoura com traceback quando a versão não é numérica (por exemplo `0.26.0-rc1`). O comportamento é o mesmo do passo inline antigo, então não é regressão; numa próxima mudança do script, vale uma mensagem clara.
- Recomendado (não bloqueia) · tests/test_conferir_release.py · nenhum teste cobre a base sem `plugin.json` legível (que vira 0.0.0, roda a checagem e passa). Um caso a mais deixaria a falha fechada documentada.
- Recomendado (processo) · o brief mandou ler `git diff aa81f6b..37212eb`, que mistura a DV-4 com reversões alheias porque a base da DV-4 é 8833e1c. Para revisar um commit isolado, o certo é `git show <sha>` ou o diff contra a base real (`git merge-base`).
