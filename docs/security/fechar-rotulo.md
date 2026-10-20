---
tipo: revisao-seguranca
contrato: 1
pedido: fechar-rotulo
branch: melhoria/fechar-rotulo
commit: 8b619b3a431685d0f93e54013d3750e903554b69
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-20
---
# Review de segurança: fechar-rotulo

Diff revisado: `50997b72e65d11a7cace0bbc5d4aaf5a55b68d60..8b619b3a431685d0f93e54013d3750e903554b69` (bin/forge-fechar, docs/fechamento-integrador.md, tests/test_fechar.py, changelog.d/fechar-rotulo.md).

## Gatilhos
`R-SEGURANCA`: o passo 5 do `bin/forge-fechar` é uma guarda do fechamento (controles do Forge). Nenhum caminho de `PROTEGIDOS` (tests/catraca.py:37) é tocado; `bin/forge-check` e `.github/` não mudam.

## Achados

## Detalhe dos achados
Veredito: aprovado. A mudança não afrouxa controle: o passo 5 nunca foi o controle do rótulo, só uma cortesia de texto livre (a doc da base já o dizia), e o controle real continua sendo a catraca do CI, cujo resultado o passo 4 exige (bin/forge-fechar:121-143).

**1. O passo 5 mais estreito (bin/forge-fechar:149).** Antes parava com `afrouxa-regra` em qualquer parte do título ou do corpo; agora só com linha de item marcada (`- [x]`/`* [X]`) que cita o rótulo. Casos que antes paravam e agora passam: título com o nome, prosa do corpo, item desmarcado, item marcado em lista `+` ou numerada, citação `>`. Para cada um, a pergunta é se a catraca cobre. Ela barra, sem depender do texto do PR, toda violação de `violacoes_das_regras` (tests/catraca.py:402: invariantes, arquivos de regras, hooks, política, testes enfraquecidos, custo e `PROTEGIDOS`) e só a libera com o rótulo do dono depois do último push; o job roda o script da base (.github/workflows/catraca.yml:32-43) e o passo 4 para em qualquer check que não seja `pass` ou `skipping`. Logo, onde há violação detectável, o PR para no passo 4 com ou sem o texto.
Resta o caso que a catraca não detecta: um afrouxamento que nenhuma regra mecânica vê (por exemplo, texto de regra reescrito sem perder o padrão do invariante) e que o autor honesto sinaliza só no título, como prevê o item de neutralidade do modelo de PR (.github/pull_request_template.md, destaque no título). Antes, se o destaque usasse a palavra `afrouxa-regra`, o passo 5 parava; agora o PR entra na `develop`. Severidade: baixa (recomendação, não vulnerabilidade). Por quê: (a) não há atacante que ganhe algo: quem quer contornar simplesmente não escreve a palavra, o que já passava antes; (b) o destaque de título não exige o rótulo por nenhuma regra (o rótulo é a exceção da catraca, `R-CONFORMIDADE`); (c) a `main` só muda pelo PR do dono (`R-MAIN`), que vê o título; (d) o casamento por título dava falso positivo no próprio tema (o #222 tinha o nome do rótulo no título). Correção mínima, no cartão MODELO-PR-ROTULO (já previsto, mexe em `.github/`): pôr no modelo de PR o item do rótulo, para que o pedido honesto tenha a forma que o passo 5 lê; e, se o dono quiser manter o título como sinal, uma linha de aviso (não parada) quando o título cita o rótulo. Esforço P. Dono: tech-lead (script) e devops-engineer (modelo, enviado pelo dono).
Recomendação menor: o padrão não reconhece item de tarefa em lista `+` nem numerada (`1. [x]`), que o GitHub também desenha como caixa marcada (sonda local: ambos passam). Mesmo raciocínio: não é controle; ampliar para `^[[:space:]]*([-*+]|[0-9]+[.)])[[:space:]]+\[x\]` fecha a lacuna da forma. Esforço P. Dono: tech-lead. A falha de leitura do `gh` continua fechada (bin/forge-fechar:146-147).

**2. `PROTEGIDOS` por importlib (bin/forge-fechar:68, 85-95).** O código executado é o `tests/catraca.py` ao lado do próprio script (`BASH_SOURCE/..`), nunca um arquivo lido da ref revisada por `git show`. Quem roda `bin/forge-fechar` da worktree da branch já executa o script da branch; a catraca ao lado dela não traz confiança nova. Quem roda a cópia do PATH (plugin vigente) ou o checkout da `develop` executa a catraca dessa cópia, não a da branch. Diferente do CI, que roda deliberadamente a catraca da base; aqui é aceitável porque o resultado só decide uma linha de aviso. Na importação, o módulo só define funções e constantes (o `main` fica sob `if __name__ == "__main__"`, tests/catraca.py:688) e importa `neutralidade` da mesma pasta; `python3 -I` ignora `PYTHONPATH` e site do usuário; argumentos vão por argv e o heredoc é citado (`<<'PY'`), sem interpolação; `--ref` já passou por `git check-ref-format` (bin/forge-fechar:36). Severidade: informativa.

**3. O dry-run não esconde caminho de controle.** O aviso cobre só `regra_protegidos`; as outras regras da catraca (invariantes, testes enfraquecidos, política, custo) não entram no aviso, e a ausência da linha não quer dizer que o rótulo não será pedido. A doc limita o aviso ao diff que toca caminho de controle (docs/fechamento-integrador.md:10), então não promete mais do que faz. O diff usa a `origin/develop` local (sem fetch) e a branch local, que podem estar defasadas; erro de execução vira aviso explícito (bin/forge-fechar:97), não silêncio. Nada disso muda o fechamento real, que segue barrado pelo passo 4. Recomendação informativa: acrescentar na doc que a falta do aviso não dispensa a catraca. Esforço P. Dono: tech-lead. Nomes de arquivo da branch vão ao terminal sem filtro (bin/forge-fechar:99); o integrador já vê esses nomes em qualquer `git diff`, então é informativo.

**4. Sem rede (`R-CUSTO`).** O dry-run só roda `git diff --no-renames --name-only` e `git merge-base` locais (tests/catraca.py:54-88, com ambiente sem `GIT_*`); `urllib` é importado mas só usado nas funções da API chamadas pelo `main`, que o dry-run não chama. Sondas: `bin/forge-fechar fechar-rotulo --ref melhoria/fechar-rotulo --dry-run` imprimiu os sete passos e nenhum aviso (a branch não toca `PROTEGIDOS`); `python3 -m unittest tests.test_fechar`: 27 testes OK.

## Riscos aceitos e ferramentas
Sem riscos aceitos. Ferramentas: leitura do diff, `grep`, sonda local do padrão do passo 5, o dry-run e o módulo de teste. `gitleaks`, `semgrep`, `shellcheck`, `actionlint`, `zizmor` e `osv-scanner` não estavam no PATH (lacuna registrada; o CI roda shellcheck e os jobs de workflow). Nenhum segredo no diff (leitura manual).
