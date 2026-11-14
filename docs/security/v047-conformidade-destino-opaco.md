---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-conformidade-destino-opaco
commit: e8c459de79e98bd22a65892b4605c97a7583de58
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: v047 (lote B, destino opaco sem resto, A9 e A10)

Intervalo `origin/develop..e8c459de` (13 commits; a develop entrou pelo merge `e8c459de`): `hooks/conformidade.py` (+190: U1, U2, U3, teto de 64, `palavra_juntada` do D2b, A10 por `rev_parse_de_varios_comandos`), 88 fixtures `opaco-*`, oito arquivos de mutantes, `tests/test_hook_destino_opaco.py`, `tests/test_conformidade_opaco.py`, o mapa de `bin/forge-testes`, `docs/hooks.md`, o índice de fixtures e o fragmento do changelog. Etapa E1.206, instância que não fez a entrega. Primeira rodada de segurança do analisador: varri a família inteira contra o corpus de legítimos, e os achados vão juntos.

## Gatilhos
`R-SEGURANCA`: hook de guarda (`conformidade`) que analisa entrada livre (linha de Bash) para proteger o `.git` (`config`, `hooks/`, marca da sessão). Bloqueio por `R-CONFORMIDADE`.

## Achados
- A1 (bloqueante) hooks/conformidade.py:1141 · Destino opaco sem resto cujo corpo calcula o .git sem citá-lo (printf %s%s .g it, tr, sed, rev, base64 -d, cat de arquivo) libera com rc 0 e grava .git/config ou .git/hooks/pre-push: U1 é lista negativa de citação, e A9 segue aberta (R-CONFORMIDADE)
- A2 (bloqueante) hooks/conformidade.py:1104 · Resto colado sem barra ("$(echo .g)it/config", "${X:-.g}it/config", "$(echo .gi)"t/hooks/pre-push) não conta como opaco nem cai no resto_no_git: grava .git/config com rc 0. Dimensão D3 nova: resto colado (R-CONFORMIDADE)
- A3 (recomendado) hooks/conformidade.py:415 · CORPO_POSITIVO aceita mktemp -p e --tmpdir com qualquer literal, inclusive .git; hoje o U1 recusa antes, mas a lista positiva do plano diz literal fora do .git (AR-3): excluir o .git na própria lista

## Sondas
- S1 · echo a > "$(printf %s%s .g it/config)" (projeto, tech-lead) · espera: 2 · obtido: 0
- S2 · cp x "$(printf %s%s .g it/config)" · espera: 2 · obtido: 0
- S3 · install -m 755 x "$(printf %s%s .g it/hooks/pre-push)" · espera: 2 · obtido: 0
- S4 · echo a | tee "$(printf %s%s .g it/config)" · espera: 2 · obtido: 0
- S5 · dd of="$(printf %s%s .g it/config)" if=x · espera: 2 · obtido: 0
- S6 · echo a > "$(echo .hit/config | tr h g)" · espera: 2 · obtido: 0
- S7 · echo a > "$(echo .hit/config | sed s/h/g/)" · espera: 2 · obtido: 0
- S8 · echo a > "$(rev <<< gifnoc/tig.)" · espera: 2 · obtido: 0
- S9 · echo a > "$(echo LmdpdC9jb25maWc= | base64 -d)" · espera: 2 · obtido: 0
- S10 · echo a > "$(cat lugar2.txt)" com lugar2.txt = .git/config · espera: 2 · obtido: 0
- S11 · echo a > "$(printf %s%s .g it/config)" (worktree do projeto) · espera: 2 · obtido: 0
- S12 · echo a > "$(echo .g)it/config" · espera: 2 · obtido: 0
- S13 · echo a > "$(echo .gi)"t/hooks/pre-push · espera: 2 · obtido: 0
- S14 · echo a > "${X:-.g}it/config" · espera: 2 · obtido: 0
- S15 · cp x "${X:-.gi}t"/config · espera: 2 · obtido: 0

## Detalhe dos achados
Como as sondas rodaram: o próprio `tests/test_oraculo_v047.py` como biblioteca (`montar`, `rodar_hook`, `esperado_pelo_bash`), sem editá-lo, num script no meu rascunho. O "espera" é o do bash: no repositório temporário, `printf %s <destino>` resolve o caminho e o caso espera 2 se ele cai no `.git`. O "obtido" é o rc do hook no head `e8c459de`, papel `forge:tech-lead`, projeto em `melhoria/x`. Na develop (`f4b0c2ae`), S1, S2, S6 e S14 também dão 0: o furo é anterior, mas é exatamente o que a A9 promete fechar.

**A1 · corpo que calcula o valor (dimensão D2c nova).**
- Evidência: `hooks/conformidade.py:1136-1141`. O destino opaco sem resto só recusa se algum texto do valor cita a família do `.git` (U1, `cita_o_dir_do_git`, também depois de `palavra_juntada`) ou se é ilegível (U2: `eval`, `sh`, `$'`, barra invertida, aninhado). Fora isso, `else: return` libera. O U3 (`:1146`) só olha `cp`, `mv`, `install` e `ln` com origem de nome do git, e o destino como arquivo (origem `x`, valor `.git/config`) não passa por ele. Redireção, `tee` e `dd` nunca passam.
- Caminho de ataque: um agente com o papel de qualquer projeto, levado por injeção num arquivo ou numa saída de ferramenta, roda `echo '[core] hooksPath = /tmp/h' > "$(printf %s%s .g it/config)"` ou `install -m 755 x "$(printf %s%s .g it/hooks/pre-push)"`. O primeiro cala o pre-push (`R-VERIFY`); o segundo roda código na próxima operação do git, e `core.fsmonitor` roda código em todo `git status`. É o mesmo ativo e o mesmo ganho do A4 do plano (`v047-serie-hooks-pos-550.md`, seção 2), que foi bloqueante.
- Por que é bloqueante: requisito do plano provado como não cumprido (`R-REVIEW`). O texto de "O que fecha" da A9 é a escrita em `.git/config` e `.git/hooks/<hook>` por destino opaco sem resto. A regra U1 do plano cobre só o corpo que **cita** o `.git`. Fica a lista negativa que a AR-3 proíbe: cada forma de calcular (`printf` com formato, `tr`, `sed`, `rev`, `base64`, `cut`, `awk`, `cat` de arquivo que o Write gravou antes) é mais uma porta. O furo é do plano, que eu escrevi; registro aqui como dimensão nova da matriz, sem correção pontual.
- Correção mínima (inverte a decisão do U1/U2 para lista positiva, como o U3 já faz): o destino opaco sem resto (e o de resto colado, A2) **libera só** quando o hook sabe o valor. Isso vale em dois casos.
  - (a) O corpo está em `CORPO_POSITIVO`, ampliado com `git rev-parse --short [<ref>]` e `git rev-parse --abbrev-ref <ref>`, para manter os legítimos `leg-short-head` e `leg-short-head-sufixo`.
  - (b) O corpo é só `echo` ou `printf %s` de palavras literais (sem `%` além do `%s` único, sem `-e`), ou uma função ou variável da linha que se reduz a isso, e o valor juntado (`palavra_juntada`) não cai no `.git` pelo U1.
  Todo o resto recusa com a mensagem do U2 ("escreva o caminho literal"). O corpus de legítimos do oráculo segue passando: `echo docs`, função `echo docs`, `date`, `mktemp`, `pwd`, `--show-toplevel`, `--short HEAD`, `${OUT:-docs}` e variável de `mktemp -d`. O falso positivo novo é `> "$(cat nome.txt)"`, que já recusa com origem do git pelo U3. Fixtures que bloqueiam: S1 a S11. Mutantes: (a) sem o `--short` e (b) aceitando `printf` com formato. Esforço: M. Dono: tech-lead (autor do lote B).

**A2 · resto colado sem barra (dimensão D3 nova).**
- Evidência: `hooks/conformidade.py:1101-1104`. `opaco_sem_resto` só vale se o que vem depois da última parte opaca é vazio ou `/`. Com resto colado (`it/config`), não é "sem resto", e o `resto_no_git` (regra antiga) só vê resto que começa em `/`. O plano afirmou "com resto, `resto_no_git` já recusa (S7)", e isso só vale para o resto com barra.
- Caminho de ataque: o do A1, com `> "$(echo .g)it/config"` ou `> "${X:-.g}it/config"`. O segundo nem tem substituição: é o S6 do plano com o sufixo colado.
- Correção mínima: em `opaco_sem_resto` (ou num irmão chamado pelo `destino_opaco`), o resto que não começa em `/` entra na mesma decisão do sem resto. Para o U0, o valor padrão de `${x:-v}` e os corpos são juntados ao resto antes do U1. `palavra_juntada` já faz isso: `${X:-.g}it/config` vira `*it/config`, que o curinga casa com `.git`. Os legítimos `"$(date +%F)".log`, `"$(git rev-parse --short HEAD).txt"` e `"$(echo docs)"x.md` seguem livres pela lista positiva do A1. Fixtures que bloqueiam: S12 a S15. Mutante: o resto colado tratado como resto com barra. Esforço: P. Dono: tech-lead.

**A3 · lista positiva do `mktemp` aberta ao `.git` (recomendado).**
- Evidência: `hooks/conformidade.py:415-416`. `-p\s+[\w./-]+` e `--tmpdir(?:=[\w./-]+)?` aceitam `-p .git` e `--tmpdir=.git/hooks`.
- Por que não bloqueia: o U1 do `destino_opaco` roda antes do U3 (`checar_escrita` vem antes de `origem_do_git_no_opaco`) e recusa pela citação. Sem caminho de ataque hoje, mas a lista positiva do plano diz "literal fora de `.git`". Com a correção do A1, ela passa a ser a única porta e não deve depender da ordem.
- Correção mínima: no `corpo_positivo`, recusar o valor de `-p` ou de `--tmpdir` que cite o `.git` (`cita_o_dir_do_git`). Esforço: P. Dono: tech-lead.

### O que foi conferido e está correto
- **Oráculo (EXT-1):** `tests/test_oraculo_v047.py` só tem o commit `730843a9` (`git log -- tests/test_oraculo_v047.py`), sem edição pelo autor. Local: `python3 -m unittest tests.test_oraculo_v047 tests.test_hook_destino_opaco tests.test_conformidade_opaco` deu 8 testes OK em 373 s. Os 9 casos D2b recusam, e os legítimos e as leituras liberam.
- **D2b além do oráculo:** `cp x "$(echo .g""it)"`, `d=.g; echo a > "$(echo "$d"it/config)"`, `printf '\056git/config'`, `printf '%b' '\x2egit/config'` e `printf -v d %s .git` recusam. `${HOME:+.git/config}` recusa por `${` com ação crítica.
- **A10:** `rev_parse_de_varios_comandos` olha a linha inteira no nível 0, e `origens_livres` (`:1261`) zera a liberação do #512 com qualquer corpo misto na linha. Isso só restringe. A liberação de `ln -s "$(git rev-parse --git-dir)"/HEAD h` segue intacta (`leg-link-512`).
- **Orçamento e negação de serviço:** linhas de 140 mil caracteres, 64 funções opacas com 20 mil palavras e 20 mil palavras com curinga estouram o prazo e recusam (rc 2, falha fechada). Na develop, as mesmas três também recusam por prazo, em tempo da mesma ordem (develop 12,9 s, 7,4 s e 6,5 s; head 7,0 s, 8,3 s e 6,8 s). Não há regressão nem caminho que libere por lentidão. `glob_casa` monta o padrão a partir de palavra da linha, mas casa só com `.git` (4 caracteres) e fica barata.
- **Falsos positivos vistos (do lado seguro, anteriores à entrega):** `"$(echo .gi{t,})/config"` e `"$(ls -d .gi*)/config"` recusam pela regra antiga "lido como `.git`".
- **Sem afrouxar:** o diff não remove recusa. `origens_livres` ganhou só a condição que zera, e os fixtures `gitcomum*` seguem na suíte do autor.

## Riscos aceitos e ferramentas
Nenhum risco aceito.

Suíte inteira: **sem CI no head**. `gh api .../actions/runs?head_sha=e8c459de…` e `.../check-runs` devolvem `total_count` 0, porque a branch não tem PR (o brief diz "sem PR"). Rodei só os módulos da entrega e o oráculo, citados acima. Quando houver PR, o portão pede o CI verde no head da revalidação.

Faltaram no ambiente: gitleaks, Semgrep, osv-scanner, zizmor e actionlint (`R-CUSTO`, não instalo). A entrega não traz segredo, dependência nem workflow, e a análise foi manual e por sonda.
