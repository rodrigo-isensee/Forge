---
tipo: revisao-seguranca
contrato: 1
pedido: conferente-k2
branch: melhoria/conferente-k2
commit: ef3ef4d9bd136d0d1b67c4245aa2b401ca4d94c0
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-16
---
# Review de segurança: conferente-k2

Escopo: `git diff origin/develop...ef3ef4d` (origin/develop = 4922609; implementação até 6d3f41b, Base-sha a7246d4). Foco nos controles do Forge tocados: `bin/forge-check` (subcomando `brief` e `brief gerar`) e `hooks/conformidade.json` (lista `so_leitura` do conferente), mais os textos do conferente, do Jarvis, `R-BRIEF`, `R-PROVA` e os invariantes. Ameaça considerada, a mesma da K1: o Jarvis ou o agente conferido erra ou alucina, e o conferente (haiku, só leitura) aprova o que não devia; além dela, que o comando novo dê ao papel só de leitura escrita, rede ou execução.

## Gatilhos
`R-SEGURANCA`: muda um controle do Forge (`hooks/conformidade.json`, lista branca do papel só de leitura; `bin/forge-check`, que o conferente passa a usar como fonte de forma e corte) e os invariantes que o protegem (`tests/config.json`).

## Resumo
**Veredito: aprovado.** Nenhum achado crítico, alto ou médio.

- **`forge-check brief` na lista `so_leitura`** (`hooks/conformidade.json:77`): acréscimo de um item, nenhuma remoção (o diff tem 1 linha trocada, só com o acréscimo). O hook casa a chave `forge-check <primeiro argumento>` por igualdade (`hooks/conformidade.py:708`, `:720`), então libera `forge-check brief <arquivo>` e `forge-check brief gerar`, e nada além. As barreiras do papel continuam valendo antes da lista: gramática sem expansão, substituição e redirecionamento; programa com caminho recusado; `--output` recusado; valor de opção do `forge-check` que começa com `-` recusado (`:711-716`).
- **O subcomando não abre escrita, rede nem execução arbitrária.** `cmd_brief_conferir` (`bin/forge-check:1815`) só lê dois arquivos (`read_bytes`/`read_text`) e imprime. `cmd_brief_gerar` (`:1838`) lê o pedido, roda no máximo `git rev-parse origin/<base>` (`:1855`) pelo único ponto que roda git (`:275-281`: lista de argumentos, sem shell, sem `GIT_*` herdadas, com tempo-limite) e imprime. `--base` vai prefixado por `origin/`, então não vira opção do git; um valor inválido sai `PREENCHER` (exercitado: `--base '../x'` deu `Base-sha: PREENCHER`). `rev-parse` não roda driver nem hook. Nenhuma chamada de rede. Exercitado em `$TMPDIR` com o fixture `corte-completo.md`: nenhum arquivo criado ou alterado (`git status --porcelain` vazio).
- **Entrada sem injeção.** Os valores vindos de fora que entram em regex passam por `re.escape` (`pedido_id` em `destino_do_brief`, o prefixo esperado em `:1810`); os padrões fixos não têm quantificador aninhado (sem ReDoS realista sobre um brief ou pedido). `--destino` com `../` não escapa: entra só no texto comparado e reprova (`forma: Arquivo fora do padrão docs/briefs/pedido-sintetico-../../x-<n>.md`). A saída de `gerar` é texto para o Jarvis completar; um `--branch 'a;b'` sai literal, sem ser executado. Ler um arquivo qualquer não é capacidade nova: o papel já tem `cat`.
- **Nenhum controle removido ou afrouxado.** `tests/config.json`: só linhas acrescentadas (0 removidas), 20 invariantes novos no conferente, 5 no Jarvis, 2 na `R-PROVA`, 4 na `R-BRIEF`. Nos textos, as mudanças apertam o controle (passada única, `forma: modo ausente`, `Base:` restrita, `Brief-sha256:`, `tests/config.json` nunca é anexo, `--no-renames`, `rc=0 e <espera>`). A `R-PROVA` troca "não roda" por "fora da lista de comandos do conferente", que é mais estrito. `bin/forge-changelog` só extrai `slug_da_branch` sem mudar o comportamento.
- **Determinismo como controle:** forma e corte deixam de ser julgamento do haiku e saem do comando, com `resultado:` e saída 1 quando reprova; o que o comando não reconhece sai `não verificável`, nunca aprovado por omissão, e o conferente mantém a leitura de fidelidade, decisões e etapa.

## Achados da K1: estado
| Achado | Estado | Evidência |
|---|---|---|
| B1 brief editado depois da conferência; `Arquivo:` sem amarração | resolvido (residual informativo, I-K2-1) | `Brief-sha256:` na entrega comparado ao hash completo da linha `arquivo:` (`agents/conferente.md:64`, `:68`); caminho conferido contra `docs/briefs/<pedido>-<destino>-<n>.md` (`bin/forge-check:1807-1811`); invariantes `Brief-sha256: <o hash completo`, `com \`Brief-sha256:\`: diferente`, `forma: Arquivo fora do padrão`. |
| B2 contrapeso do "do autor" | resolvido | `docs/regras/R-PROVA.md:11` ("fora da lista de comandos do conferente", com invariante); `forma: sem PQ que o conferente confira` também sai do comando (`bin/forge-check:1799-1801`). |
| B3 invariantes protegem rótulos | resolvido | `tests/config.json`: `origin/<Base>`, `é corte real`, `só por acréscimo`, `forma: brief diferente do arquivo`, `ao menos um PQ`, `não da cópia do Jarvis`; `etapa do papel do destino que falta` já estava (`:153`). |
| B4 anexo que afrouxa e renome | resolvido | `agents/conferente.md:71` (`tests/config.json` nunca é anexo; `git diff --numstat --no-renames`), com invariantes. |
| B5 `Base:` texto livre | resolvido | `agents/conferente.md:71` (`develop`, `homolog` ou `main`, diferente de `Branch:`; senão `escopo: base fora do fluxo`), `agents/jarvis.md` ("nunca a própria branch"), com invariantes. |
| I1 primeira linha fora dos modos | resolvido | `agents/conferente.md:15` (`forma: modo ausente`, reprovado), com invariante. |
| I2 espera fraca | resolvido | `aviso:` para `contém` < 3 caracteres e `linhas>=1` (`bin/forge-check:1704-1706`); `rc=0 e <espera de saída>` aceito e reprovando rc ≠ 0 (`agents/conferente.md`, `R-PROVA`), com invariantes. O aviso não reprova, por desenho (proporcional). |

## Achados novos

### I-K2-1. O padrão do caminho não está ancorado na raiz do repositório (informativa)
- **Evidência:** `bin/forge-check:1810` usa `re.search(re.escape(esperado) + r"\d+\.md$", norm)`, sem âncora no início.
- **Caminho:** um `Arquivo:` como `/tmp/x/docs/briefs/<pedido>-<destino>-1.md` sai `arquivo-caminho: ok` (exercitado). Não há atacante: exige que o Jarvis grave o brief fora do lugar, e a amarração que importa (o hash em `Brief-sha256:` e a cópia igual ao arquivo) continua valendo. Com o mesmo hash, o conteúdo conferido e o entregue são o mesmo.
- **Sugestão:** aceitar só `docs/briefs/<pedido>-<destino>-<n>.md` relativo à raiz (ou ao `~/.forge-contrib`), por `re.fullmatch` sobre o caminho relativo, sem `..`.
- **Esforço:** P · **Dono:** tech-lead (próxima fatia, sem bloquear).

### I-K2-2. A classificação "conferente/autor" do PQ é mais larga que o hook (informativa)
- **Evidência:** `comando_do_conferente` (`bin/forge-check:1647`) aceita `git diff --output=...`, `git log --show-signature` e `--format=%G...`, que o hook recusa ao papel (`hooks/conformidade.py:710`, `:726` em diante).
- **Caminho:** um PQ com esse comando sai `verificador: conferente` no modo brief; na entrega, o hook recusa e a linha cai em `não verificável`. O hook continua sendo a barreira: nada é executado. O efeito é só um brief aprovado com um PQ que, na prática, ninguém confere de forma automática (o QA ainda roda).
- **Sugestão:** recusar em `comando_do_conferente` as mesmas opções que o hook recusa (`--output`, `--show-signature`, `%G`, `--textconv`, `--ext-diff`), ou importar a regra do hook, para a classificação nunca divergir.
- **Esforço:** P · **Dono:** tech-lead.

### I-K2-3. A checagem "brief com commit" depende da palavra `commit` (informativa)
- **Evidência:** `bin/forge-check:1799` (`(?<!sem )\bcommit` no Entregar e no Pronto quando).
- **Caminho:** um brief que pede "envie a branch" sem a palavra `commit` não dispara `forma: sem PQ que o conferente confira` no comando. O texto do conferente (`agents/conferente.md`, item 4 do modo brief) continua mandando conferir por leitura, então há segunda barreira.
- **Sugestão:** tratar também `push` e `PR` como sinais de entrega com commit.
- **Esforço:** P · **Dono:** tech-lead.

## Riscos aceitos e ferramentas
- Riscos aceitos: nenhum. Os três achados são informativos e viram cartões para o autor, sem aceite do dono.
- Ferramentas: revisão manual e estática do diff; execução local de `forge-check brief` e `forge-check brief gerar` em `$TMPDIR` com entradas incomuns (`--destino` com `../`, `--base '../x'`, `--branch 'a;b'`, caminho fora do repositório). `gitleaks`, `semgrep`, `zizmor`, `actionlint` e `osv-scanner` não estão no PATH (lacuna registrada); o diff não traz workflow, dependência nem segredo. A suíte completa não foi rodada aqui (`R-TETO`; o autor rodou e o QA roda de novo).
