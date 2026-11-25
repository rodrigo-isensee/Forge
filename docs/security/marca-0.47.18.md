---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/marca-0.47.18
commit: 217e73ed2e9bc41ac0ba09550b76721fbd36359d
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: marca da 0.47.18 (#894, v0481 E12.16; classe C)

Gatilhos: nenhum de código. A marca de release passa pela segurança por exigência do processo (classe C).

Neutro: a marca não muda código, hook, workflow nem regra. Só junta o texto do changelog e sobe a versão. Nada aperta e nada afrouxa.

## Escopo lido
Diff `eeb81062..217e73ed`: 7 arquivos. Três foram modificados (`.claude-plugin/plugin.json`, `dev/.claude-plugin/plugin.json` e `CHANGELOG.md`) e quatro apagados, todos em `changelog.d/`. Nenhum arquivo de código, hook, workflow, teste ou agente foi tocado. A catraca da base (`eeb81062`), rodada como no CI contra o head, não dá violação nem aviso.

## Conferências
- **Release reproduzida:** num clone temporário em `eeb81062`, `bin/forge-changelog release 0.47.18 2026-11-25` gera uma árvore cujo `git diff 217e73ed` é vazio. Os quatro arquivos `changelog.d/` apagados, o `CHANGELOG.md` e os dois `plugin.json` saem idênticos aos da marca. Nada além disso mudou.
- **Fragmentos:** os 4 fragmentos (`v0481-catraca-ajudante`, `v0481-copia-mensagem`, `v0481-corte-completo` e `v0481-g3-testes-uma-vez`) estão linha a linha na seção `## [0.47.18] - 2026-11-25` (`CHANGELOG.md:7-14`), cada um na mesma seção `###` de origem: Adicionado 1, Alterado 1 e Corrigido 2. Em `changelog.d/` sobra só o `README.md`. `bin/forge-changelog conferir-release` dá `ok` e `tests.test_changelog` roda 91 testes, OK.
- **Versão:** `0.47.18` em `.claude-plugin/plugin.json:3` e em `dev/.claude-plugin/plugin.json:3`, igual a `CHANGELOG.md:7`. A seção nova fica logo abaixo de `[Não publicado]` e acima da 0.47.17.
- **Data:** o commit é de 2026-11-25T05:58:49-03:00. O dia local e o dia UTC são os dois 2026-11-25.
- **Corpo do #894:** a linha `teto: excedido, 1349 linhas, marca de versão` está presente. Eu a reproduzi com as funções do próprio `forge-check`, como faz o `medir_a_marca` do `forge-fechar` (`origin/main...217e73ed`, três pontos, com a `origin/main` em `ad55cd9c`): total 1349, acima do teto, classe C. O corpo também lista os três pareceres `release-0.47.18`. O corte com 4 itens, abaixo de 20, segue a autorização do dono só para a noite de 24/11, conforme registrado no corpo. O `teto_versao` e os configs não mudaram, porque o diff não toca `tests/config.json`.
- **Segredos:** nenhum padrão de token, chave ou chave privada nas linhas acrescentadas.
- **CI do head `217e73ed`:** no momento da leitura, 14 checks em `pass`, entre eles `catraca`, `bateria (passos)`, `bateria (pareceres)`, `bateria (verificações longas)`, `instalação` e `árvore já provada na develop`. Duas partes da suíte (3.12 parte 4/5 e 3.14 parte 1/5) estavam em andamento, e os 7 jobs que só rodam em push na develop saíram pulados. O CI da develop em `eeb81062` (push, run 45579103080) está verde. O merge segue cobrando todos os checks.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas ausentes do PATH: `gitleaks`, `osv-scanner`, `semgrep`, `zizmor`, `actionlint`, `shellcheck` e `trivy` (lacuna). O delta não toca workflow nem dependência, e a busca de segredos foi feita por padrões.
