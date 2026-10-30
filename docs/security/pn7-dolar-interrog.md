---
tipo: revisao-seguranca
contrato: 1
pedido: pn7-dolar-interrog
branch: melhoria/pn7-dolar-interrog
commit: 312ecf0d01b9072fa17446c87dd6174c65ac3b6b
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-30
---
# Review de segurança: pn7-dolar-interrog (H1-1 da P-N7, `$?` modelado)

Escopo: `git diff 31257c1...312ecf0` (`hooks/_comum.py`, `hooks/parecer.py`, emenda H1-1 da ADR 0011, `docs/hooks.md`, fixtures, `tests/test_hooks.py`, spec de mutantes e fragmento do changelog). Método: leitura estática e sondas locais. Cada sonda roda o hook do commit revisado (e o da base 31257c1, para comparar) sobre uma cópia das fixtures da branch com o `command` trocado, e o bash 5.3 com um `git` falso no `PATH` que só imprime o argv. Sem rede, sem `git` nem `gh` reais.

## Gatilhos
- Controles do Forge (`R-SEGURANCA`): o diff afrouxa a lista de construções não modeladas dos hooks `conformidade` e `parecer` (gatilho `hooks/`). Rótulo `afrouxa-regra` do dono no PR (`R-CONFORMIDADE`).
- Sem dependência nova, workflow, segredo nem custo (`R-CUSTO`).

## Achados
- A1 (bloqueante) hooks/_comum.py:1456 · a guarda do IFS é textual: `declare I""FS=0`, `printf -v I\FS 0`, `export I''FS=0`, `declare $(printf I)FS=0`, `read I""FS` ou `. arq` põem IFS=0 sem a palavra IFS; `git push origin x$?main` passa (rc 0) e o bash roda `git push origin x main`
- A2 (bloqueante) hooks/_comum.py:1578 · mesma classe do A1 em `simples_da_gramatica` (`"IFS" not in resto`): a guarda textual não prova que o `$?` fora de aspas não divide a palavra na chamada com heredoc e marcador crítico
- A3 (recomendado) hooks/parecer.py:109 · mesma guarda textual em `heredocs_simples`; hoje só aperta (o False segue para `fora_da_gramatica_com_heredoc`), mas deve trocar junto com o A1 para as três funções seguirem uma regra só
- A4 (recomendado) docs/adr/0011-analisador-de-comandos-gramatica-positiva.md:43 · a emenda diz que o `$?` fora de aspas sem IFS no texto não monta programa nem branch; as sondas do A1 atingem o critério de reversão da própria emenda; reescrever junto com a correção

## Detalhe dos achados
**A1 e A2: a guarda do IFS não fecha a divisão de palavras (classe: controle de hook afrouxado além do provado).**

- Evidência: `hooks/_comum.py:1456` aceita o `$?` fora de aspas quando `"IFS" not in linha`, e `hooks/_comum.py:1578` faz o mesmo com `"IFS" not in resto`. O bash aceita o nome da variável com aspas ou escape nos builtins que recebem o nome como argumento, e o nome também pode vir de uma substituição de comando (`$(`, que o analisador modela).
- Sondas no hook `conformidade` (agente `forge:tech-lead`, fixture `pn7-dolar-interrog-push-main-echo-rc-bloqueia` com o `command` trocado). Na base 31257c1 as nove dão rc 2 (`$?` com ação crítica); no 312ecf0 todas dão rc 0, sem stderr:
  - `declare I""FS=0; git push origin x$?main`
  - `printf -v I\FS 0; git push origin x$?main`
  - `export I''FS=0; git push origin x$?main`
  - `read -r I""FS < f; git push origin x$?main`
  - `. ./ifs.sh; git push origin x$?main`
  - `declare I""FS=0; git push origin HEAD:x$?main`
  - `declare I""FS=0; git$?push origin main`
  - `declare I""FS=0; git push --no-verify$?x origin y`
  - `git push origin x$?main` (sem IFS, sozinho; inofensivo, só para referência)
  - No mesmo commit, `declare $(printf I)FS=0; git push origin x$?main` também dá rc 0.
- No bash 5.3, com um `git` falso no `PATH`, `declare I""FS=0; git push origin x$?main` roda `git push origin x main`. A forma com `git$?push origin main` roda `git push origin main`, e a forma com `--no-verify$?x` roda `git push --no-verify x origin y`. Ficam provados o push direto para a `main` (`R-MAIN`) e o envio com `--no-verify` (`R-VERIFY`), ambos sem recusa do hook.
- Caminho de ataque: um agente desviado por injeção de prompt (texto de issue, PR ou arquivo lido) ou por erro próprio escreve a chamada acima. O hook deixa passar; o pre-push e a proteção do servidor seguem como última linha, mas o `--no-verify` montado desse jeito pula o pre-push. Antes deste diff, o hook recusava.
- Severidade: alta. É uma regressão de um controle do Forge com caminho concreto para ações que os hooks existem para barrar, e o brief exige que nenhum merge, pull, `gh pr` ou `gh api` real passe a ser aceito.
- Correção mínima, a mesma nas duas funções: trocar a guarda textual por uma guarda de posição. Fora de aspas, o `$?` vale só como argumento de `echo` ou de `printf` sem `-v`, nunca na palavra do programa nem num comando simples que carregue o marcador crítico. Entre aspas duplas, segue valendo sempre. Os nove casos legítimos das transcrições (`echo rc=$?` depois da ação) continuam passando. As sondas acima entram como fixtures de recusa e como dimensão nova (o nome do IFS montado por aspas, escape, substituição ou `source`) no teste de propriedade `CodigoDeSaida` e na spec de mutantes. Esforço P. Dono: tech-lead.
- O `. ./ifs.sh` sozinho é da classe [B] já documentada em `docs/hooks.md` (o script lido faz o que quiser). Ele entra aqui porque a correção por posição também o fecha.

**A3 (recomendado).** A decisão técnica de 2026-10-30 00:36 está conferida. Quando `heredocs_simples` (`hooks/parecer.py:109`) dá False, a chamada segue para `fora_da_gramatica_com_heredoc` (`hooks/parecer.py:612`), então a guarda mais estrita só aperta o caminho rápido. Com a guarda do A1 trocada, esta deve seguir a mesma regra.

**A4 (recomendado).** O texto da emenda (`docs/adr/0011-...:43`) e o de `docs/hooks.md:97` afirmam que só o `IFS` no texto da chamada divide o `$?`. As sondas do A1 são exatamente o critério de reversão escrito na emenda. A frase volta a valer depois da correção, com a regra de posição no lugar do teste textual. A linha de revisão de 2026-11-30 (`:104`) pode ficar.

**Itens do brief conferidos sem achado:**
- O IFS do ambiente não entra: `env -i IFS=0 bash -c 'git push origin x$?main'` roda `git push origin x0main`, e o `IFS` dentro do bash fica no valor padrão (espaço, tab e quebra de linha).
- Todo outro `$`, crase, chaves e `\` com quebra de linha seguem recusados. O teste `CodigoDeSaida` (2 testes, OK) cobre `${?}`, `$#`, `$@`, `$1`, `$x`, `$'r'`, `$"r"`, `$$?` e `$?$x` por posição e aspas. A sonda com `eval I""FS=0` segue recusada (`eval` com ação crítica).
- `<<` com `$?` no delimitador: o bash lê o delimitador literal (`E$?`), o hook também, e o `git push origin main` depois do corpo segue recusado (rc 2, `R-MAIN`).
- Item 1 da ADR 0011 (papel só de leitura): `hooks/conformidade.py` e `hooks/conformidade.json` não mudaram, e `echo $?` do conferente segue recusado (rc 2, fixture `conferente-gramatica-status-saida-bloqueia`).
- Fora do diff, informativo: no `parecer`, `IFS=0; gh$?pr merge feature/x` já passava na base 31257c1 (o marcador crítico montado por expansão não aparece no texto). É a classe [B] documentada (variável ou função), não foi introduzido aqui e não bloqueia. A correção por posição do A1 também não o fecha: ele depende do `CRITICO` textual.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `shellcheck` está no PATH, sem uso (o diff não toca shell). `gitleaks`, `semgrep`, `zizmor`, `actionlint`, `osv-scanner` e `trivy` não estão no PATH deste ambiente (lacuna registrada). O diff não tem segredo, dependência nem workflow.
