---
tipo: revisao-seguranca
contrato: 1
pedido: fechar-rotulo
branch: melhoria/fechar-rotulo
commit: 32fb00871dc99c096d76469c54ff558eb3123def
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-20
---
# Review de segurança: fechar-rotulo (revalidação por delta da volta E1.1v)

Delta revisado: `ce3221797902030b831a71e4e1d649559d8666ba..32fb00871dc99c096d76469c54ff558eb3123def` (bin/forge-fechar, docs/fechamento-integrador.md, tests/test_fechar.py, changelog.d/fechar-rotulo.md). `forge-check delta --parecer` sobre o parecer anterior (commit 8b619b3) listou só esses quatro arquivos fora dos pareceres; o restante do parecer anterior (importlib, falha fechada do `gh`, ausência de rede) foi relido onde o delta toca.

## Gatilhos
`R-SEGURANCA`: o passo 5 do `bin/forge-fechar` é uma guarda do fechamento (controles do Forge). Nenhum caminho de `PROTEGIDOS` (tests/catraca.py) é tocado; `bin/forge-check` e `.github/` não mudam.

## Achados

## Detalhe dos achados
Veredito: aprovado. A volta fecha o caso residual do parecer anterior e não abre caminho novo.

**1. O caso residual voltou a parar (bin/forge-fechar:155-160).** Sem o rótulo aplicado, a primeira linha do texto lido do `gh` (o título; o GitHub não admite quebra de linha no título) que cita `afrouxa-regra`, sem diferença de caixa, para o passo 5; o corpo para com item marcado em `-`, `*`, `+`, `1.` ou `1)`, com `[x]`/`[X]`. Sonda local do mesmo par de `grep`: título `feat: X (AFROUXA-REGRA)` para; item indentado `  * [X]` para; prosa no corpo e item desmarcado seguem. Em relação ao parecer anterior (8b619b3), o conjunto que para só cresce; em relação à base (50997b7), seguem livres só a prosa do corpo, o item desmarcado e a citação `> - [x]`, aceitos pela segunda DECISÃO TÉCNICA do pedido e cobertos pela catraca no passo 4 (o mesmo raciocínio do parecer anterior: quem quer contornar não escreve a palavra, e a catraca não lê o texto). A leitura do `gh` continua em falha fechada (bin/forge-fechar:151-152). O título padrão é o nome da branch: uma branch que cite o rótulo para, o que é falha para o lado seguro.

**2. O item desmarcado do corpo gerado não libera nada (bin/forge-fechar:66-69).** O item `- [ ] Rótulo afrouxa-regra pedido ao dono` não casa o padrão do corpo (exige `[x]`; sonda local: segue) e não tem efeito sobre o rótulo: o script nunca aplica rótulo, o passo 5 só decide parar, e a exceção da catraca é o rótulo aplicado pelo dono depois do último push (`R-CONFORMIDADE`). Marcado, ele só faz parar. O teste `test_corpo_gerado_traz_o_item_do_rotulo_desmarcado` prende a forma.

**3. O `git diff` do dry-run (bin/forge-fechar:95-98).** Continua rodando o `tests/catraca.py` ao lado do próprio script, nunca conteúdo lido da branch; o heredoc é citado (`<<'PY'`), os valores vão por argv e o Python roda com `-I`. A chamada `c.git` executa `subprocess.run` com lista (sem shell), ambiente sem `GIT_*` e `timeout`. `--name-only` não roda driver de diff, `textconv` nem diff externo, e `git diff` não dispara hook; nada da branch é executado. Injeção pelo `--ref`: o valor passa por `git check-ref-format --branch` (bin/forge-fechar:36) e chega como `refs/heads/<ref>`, então nunca começa com `-`; a base é fixa em `origin/develop`. Sondas: `--ref '--output=/tmp/x'` e `--ref x..y` foram recusados na validação; `--ref 'a;id'`, `--ref '$(id)'` e `--ref melhoria/inexistente` deram só o aviso de que não deu para conferir, sem executar nada. O erro do diff agora vira aviso explícito em vez de lista vazia (a R1 do review), o que remove o silêncio apontado no parecer anterior. Severidade: informativa.

**4. Sem rede (`R-CUSTO`).** O delta não acrescenta chamada de rede: o dry-run roda só `git merge-base` e `git diff` locais; `grep` por `urllib`, `http` e `curl` em bin/forge-fechar não acha nada. `python3 -m unittest tests.test_fechar`: 32 testes OK.

**R1 (recomendado, informativa) docs/fechamento-integrador.md:17.** O passo 5 atribui a `R-CONFORMIDADE` o título como lugar oficial do sinal; o destaque no título vem da regra das invariantes no `CLAUDE.md` do Forge (seção "Regras invioláveis"), e `R-CONFORMIDADE` trata de não contornar controle. Sem efeito de segurança; corrigir a referência evita que o leitor procure o requisito no lugar errado. Esforço P. Dono: tech-lead.

**R2 (recomendado, baixa) bin/forge-fechar:157.** O item marcado dentro de citação (`> - [x] ... afrouxa-regra`) segue, como no parecer anterior. Sem caminho de ataque (a catraca não depende do texto); entra no cartão MODELO-PR-ROTULO se o dono quiser a forma fechada. Esforço P. Dono: tech-lead.

## Riscos aceitos e ferramentas
Sem riscos aceitos. Ferramentas: leitura do delta, `forge-check delta`, sondas locais do padrão do passo 5 e do `--ref` no dry-run, e o módulo de teste. `gitleaks`, `semgrep`, `shellcheck`, `actionlint`, `zizmor` e `osv-scanner` não estavam no PATH (lacuna registrada; o CI roda shellcheck e os jobs de workflow). Nenhum segredo no delta (leitura manual).
