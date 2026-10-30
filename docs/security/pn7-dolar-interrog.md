---
tipo: revisao-seguranca
contrato: 1
pedido: pn7-dolar-interrog
branch: melhoria/pn7-dolar-interrog
commit: 3b412fa65d473b33ddd8bc61504db97046cdf510
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-30
---
# Review de segurança: pn7-dolar-interrog (H1-1 da P-N7, `$?` modelado, volta 2)

Escopo: revalidação por delta do parecer anterior (`d6f478c`, sobre `312ecf0`), com `forge-check delta --parecer` e `git diff c6eb028..3b412fa` (`hooks/_comum.py`, `hooks/parecer.py`, emenda H1-1 da ADR 0011, `docs/hooks.md`, fixtures novas, `tests/test_hooks.py`, spec de mutantes e fragmento do changelog). Como o delta toca um controle do Forge, reli inteiras as duas funções novas e os pontos de `construcao_nao_modelada` e de `simples_da_gramatica` em que elas entram. Método: leitura estática e sondas locais. Cada sonda roda o hook do commit revisado e o da base 31257c1, sobre uma cópia das fixtures da branch com o `command` trocado. Para ver o que o bash executa, usei o bash 5.3 com um `git` falso no `PATH`, que só imprime o argv. Sem rede, sem `git` nem `gh` reais.

## Gatilhos
- Controles do Forge (`R-SEGURANCA`): o diff afrouxa a lista de construções não modeladas dos hooks `conformidade` e `parecer` (gatilho `hooks/`). O PR precisa do rótulo `afrouxa-regra`, que só o dono aplica (`R-CONFORMIDADE`).
- Sem dependência nova, workflow, segredo nem custo (`R-CUSTO`).

## Achados
- A5 (recomendado) hooks/_comum.py:1441 · a recusa do pipe olha só o caractere depois do comando simples: `(echo git push origin x$?main) | sh` passa (rc 0). O consumo por `<(…)` e por `$(…)` também passa. Na base, o mesmo texto sem `$?` já passava, então não há caminho novo
- A6 (recomendado) docs/adr/0011-analisador-de-comandos-gramatica-positiva.md:43 · o texto diz que o `$?` dividido só muda o que se imprime, e o critério de reversão é atingido ao pé da letra por `bash <(echo git push origin x$?main)`; escrever o critério contra o mesmo texto sem `$?`

## Detalhe dos achados
**Revalidação de A1 a A4 (`d6f478c`): resolvidos.**

- **A1 e A2** (guarda textual do IFS): a guarda saiu. Agora `codigo_de_saida_vale` (`hooks/_comum.py:1428`) e `codigo_de_saida_solto` (`hooks/_comum.py:1437`) decidem pela posição do `$?`, e `simples_da_gramatica` (`hooks/_comum.py:1597`) usa a mesma regra. Sondas no `conformidade` (agente `forge:tech-lead`), todas com rc 2 no 3b412fa e a mensagem `$? fora de echo ou printf`: `export I"FS"=0`, `declare I""FS=0`, `export I''FS=0`, `printf -v I\FS 0`, `read -r I""FS < f`, `. ./ifs.sh` e `declare $(printf I)FS=0`, cada uma seguida de `git push origin x$?main`. Também dão rc 2 `git push origin x$?main` sozinho, `git$?push origin main` e `git push --no-verify$?x origin y`. Na chamada com heredoc, `<<'E'`…`E` seguido de `declare I""FS=0; git push origin x$?main` dá rc 2.
- **A equivalência da decisão técnica de 2026-10-30 01:45 se confirma.** A regra não lê o `IFS`, então a grafia do nome não muda o veredito: as sete grafias acima dão o mesmo rc 2. Fora de aspas, o `$?` só vale como argumento de `echo` ou de `printf` depois do formato e sem opção. Nessa posição a divisão de palavras muda só os argumentos do `echo`; o resultado só chega a outro programa pelos canais do A5. `IFS=0 echo x$?` (atribuição antes do programa), `echo$?x` (o `$?` na palavra do programa) e `printf -v`/`printf --` caem fora de `codigo_de_saida_vale`.
- `echo git push origin x$?main | sh` dá rc 2, com ou sem `declare I""FS=0`. O mesmo vale para `|& sh` e para `> s.sh; sh s.sh`.
- **A3:** `heredocs_simples` (`hooks/parecer.py:97`) é idêntica à da base 31257c1 (diff vazio da função). `hooks/parecer.py` não difere da base.
- **A4:** a emenda H1-1 (`docs/adr/0011-…:43`) e `docs/hooks.md:97` agora descrevem uma regra de posição, com a marca de critério mudado e o critério de reversão. Ressalva no A6.
- **Item 1 da ADR 0011 inalterado:** `hooks/conformidade.py` e `hooks/conformidade.json` não diferem da base. `echo $?` do conferente segue com rc 2 (`$` fora da gramática do papel só de leitura).
- Legítimos: `git push origin x; echo rc=$?`, `git push origin x; printf 'rc=%s\n' $?` e `<<'E'`…`E` seguido de `echo rc=$?` dão rc 0. Na base 31257c1, os dois primeiros davam rc 2. `git push origin main; echo rc=$?` segue com rc 2 (`R-MAIN`). `python3 -m unittest tests.test_hooks.CodigoDeSaida` roda 2 testes, OK.

**A5 e A6 (recomendados; classe: texto isento executado por outro caminho, AR-10).**

- Evidência: o `$?` no argumento do `echo` é aceito, mas a saída do `echo` pode virar código por canais que a regra nova não vê. Esses canais são o subshell fechado por `)` antes do `|` ou da redireção (o limite do comando simples é o `)`, então `hooks/_comum.py:1441` não vê o que vem depois), o `exec >` num comando anterior, a substituição de processo e a substituição de comando. Estas sondas dão rc 0 no 3b412fa e rc 2 na base 31257c1:
  - `declare I""FS=0; bash <(echo git push origin x$?main)`
  - `declare I""FS=0; . <(echo git push origin x$?main)`
  - `declare I""FS=0; (echo git push origin x$?main) | sh`
  - `declare I""FS=0; (echo git push origin x$?main) > s.sh; sh s.sh`
  - `declare I""FS=0; exec > s.sh; echo git push origin x$?main; sh s.sh`
  - `declare I""FS=" 0"; $(echo git push origin x$?main)`
  - `declare I""FS=" 0"; git push origin $(echo x$?main)`
  - `declare I""FS=0; bash <(echo git push --no-verify x$?y origin main)`

  No bash 5.3, as sete primeiras rodam `git push origin x main` (no caso do `exec >`, o `s.sh` gravado contém essa linha), e a última roda `git push --no-verify x y origin main`.
- Por que não bloqueia: em cada caso, o mesmo texto sem `$?` já passa na base 31257c1 e no 3b412fa (rc 0). Exemplos: `echo git push origin main | sh`, `bash <(echo git push origin main)`, `(echo git push origin main) | sh`, `(echo git push origin main) > s.sh; sh s.sh`, `exec > s.sh; echo git push origin main; sh s.sh`, `$(echo git push origin main)`, `git push origin HEAD:$(echo main)` e `git push $(echo --no-verify) origin y`. O `$?` não dá ao agente nenhuma capacidade nova. O critério de parada da ADR 0011 (item 3, ii) exige uma brecha ligada à construção que a emenda aceita, e esta é anterior a ela: é a classe [B] de `docs/hooks.md:93` (o comando montado em tempo de execução). Os efeitos sobre a `main` seguem barrados pelo pre-push e pela proteção do servidor.
- Severidade: baixa para o diff (sem caminho novo); informativa quanto à classe [B], que é anterior e está documentada.
- Correção mínima do A5 (dono: tech-lead, esforço P), opcional: a regra de pipe e de redireção de `codigo_de_saida_solto` deve olhar o primeiro caractere fora de espaço depois do `)` que fecha o subshell ou o `$(`/`<(` que contém o comando. Outra opção é recusar o `$?` fora de aspas dentro de `<(…)` e de `$(…)` e depois de `exec >` quando há marcador crítico. A dimensão nova da matriz `CodigoDeSaida` é o consumidor da saída do `echo`: `|` ou `>` depois de `)`, `<(`, `$(` na posição de programa ou de argumento, e `exec >`.
- Correção mínima do A6 (dono: tech-lead, esforço P): na emenda e em `docs/hooks.md:97`, trocar "só muda o que se imprime" por "só muda o que se imprime; a saída que vira código segue a classe [B]". O critério de reversão passa a ser "uma sonda em que o `$?` faz passar uma ação crítica que o mesmo texto sem `$?` não faz passar".
- Fora do diff: `echo git push origin main | sh` e `git push origin HEAD:$(echo main)` passam no `conformidade` desde a base, e `(echo gh pr merge feature/x) | sh` passa no `parecer`. O `--no-verify` montado assim pula o pre-push num envio que não é para a `main`. Sugiro um cartão próprio para a classe [B] "saída de comando que vira código" (`| sh`, `<(…)`, `$(…)` na posição de programa ou de argumento crítico). Não bloqueia este PR.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `shellcheck` está no PATH, mas não foi usado (o diff não toca shell). `gitleaks`, `semgrep`, `zizmor`, `actionlint`, `osv-scanner` e `trivy` não estão no PATH deste ambiente (lacuna registrada). O diff não tem segredo, dependência nem workflow.
