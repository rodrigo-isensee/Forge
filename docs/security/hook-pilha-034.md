---
tipo: revisao-seguranca
contrato: 1
pedido: hook-pilha-034
branch: melhoria/hook-msg-segmento
commit: dde743b95b2424cbdafacc18cfd303dd8193f198
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-05
---
# Review de segurança: hook-pilha-034 (E1.3, confirmação da pilha de hooks)

Revisão estática e defensiva do HEAD `dde743b` de `melhoria/hook-msg-segmento` (igual ao remoto), o topo das 7 branches em cadeia sobre a develop `d9b26bb`. Escopo: o A10 do parecer `264eed0` (E1), o E2 (`32df248`, ROTULO-VARIAVEL), o delta da reaplicação das branches 1 e 4 a 7 (E3) e a junção do changelog (`dde743b`). Execução local só com `gh` falso, pela montagem das fixtures de `tests/test_hooks.py`; o furo conta quando o `gh` falso recebe a ação no bash.

## Gatilhos
Controles do Forge (hooks `conformidade` e `parecer`, rótulo `afrouxa-regra`, mutantes da trilha): R-SEGURANCA. Regras atingidas: R-MAIN, R-VERIFY, R-REVIEW, R-CONFORMIDADE, R-CONTRIB.

## Achados
- A1 (recomendado) hooks/conformidade.py:1803 · mascarado lê a palavra escrita: token do GitHub cortado por barra e quebra de linha (gh, barra, quebra, p_…) sai com 13 caracteres do corpo no trecho da recusa; já igual em 06ec6a7, não vem da reaplicação

## Detalhe dos achados
**A10 do parecer `264eed0` (NUL em `$'…'`): fechado.** Commit `5be062c`, `hooks/_comum.py:428`: `decodificar_ansi_c` corta o resultado no primeiro NUL, por trecho `$'…'`, e `c61cf27` mantém o corte na forma composta até o ponto fixo. Fixtures `tests/hooks/conformidade/continuacao-linha-098` a `-106` (8 recusam, `printf $'a\0b'` libera) e o mutante M43 em `tests/mutantes/hook-conformidade-034-8.json`. Reexecutei os sete repros do A10 e 15 variantes: `\00`, `\000`, `\x0`, `\U00000000`, `$'g\0'h`, `$'g\0zz'$'h'`, NUL no último argumento (`$'delete\0'`), `eval`, crase, `$(`, `bash -c "…"`, heredoc com e sem aspas sob `| bash`, `git push origin $'main\0x'` e `$'g\x69t\0' push origin main`. Todos recusam com rc 2, e o `gh` falso recebe a ação no bash, o que prova que o caso é real. `$'gh\0'$'zz'` vira `ghzz` no bash e não roda o `gh`. Na sessão do Forge, `$'gh\0' pr edit 1 --add-label afrouxa-regra` e mais quatro formas do rótulo (`$'afrouxa-regra\0x'`, `afrouxa$'\x2d\0z'regra`, `bash -c $'gh\0x'…` e NUL com continuação) recusam com a conta `outra-pessoa`. `$'gh\0' pr merge 1` recusa pelo `parecer`. Os legítimos `printf $'a\0b'`, `echo $'a\0b'`, `git status && \⏎git log` e `echo `date`` seguem com rc 0.

**Regressão das voltas anteriores (E1).** O `c61cf27` tira o `com_ansi_c` e compõe as formas até o ponto fixo. Reexecutei 20 repros do A1 ao A6, entre eles:
- heredoc sem aspas com `\\`;
- `$'…'` como texto de `bash -c` e `eval`, também parcial;
- `$'…'` em 2 níveis;
- `$'\x67'$'\x68'` colados;
- composição de `$'…'` com continuação;
- `$'…'` sob `"$(…)"`, que são os casos 40b e 42b do `57d46dc`.

Todos recusam. O pulo do T1 em `57d46dc` vale só para linhas com `$'` e `\\` sob `"$(…)"`, no teste de variantes. Ele não muda o hook, e as fixtures 40b e 42b provam a recusa pela ação. O teto de rodadas (`TETO_DE_FORMAS`) falha fechado pelo `marcado` (`hooks/_comum.py:2517`). `$'…'` codificado em 6 níveis não volta a ser decodificado, porque o conteúdo decodificado sai entre aspas simples. Isso também é o que o bash faz. Leva 0,3 s para 127 kB.

**E2 (`32df248`, ROTULO-VARIAVEL): sem achado.** O commit só tira a declaração de equivalente do M4 (guarda `aspa_escapada`, `hooks/_comum.py:1894`) e põe `tests.test_hook_ansi_c` entre os testes dele. Apliquei o M4 numa cópia de `dde743b`: `tests.test_hook_ansi_c` falha em 9 subcasos (3 testes), e sem o mutante passa (9 testes OK). O mutante morre, e a ressalva do parecer `rotulo-variavel` (`165eb6c`) fica resolvida. Na sessão do Forge, as 7 fixtures do R7 e do R8 (`5e807a7`) reproduzem o esperado. Testei também 9 variantes delas, todas com rc 2 e o `gh` falso rodando no bash:
- crase com continuação e com NUL depois de `${x:-a #}`;
- `$(` no lugar da crase;
- rótulo com `$'\x2d'`;
- `${#x}` e `${x//#/a}`;
- `$'\x27'` e `$'\047'` antes da crase;
- o R8 dentro de `bash -c "…"`.

Os dois controles com outro rótulo seguem com rc 0.

**E3, reaplicação das branches 1 e 4 a 7: sem mudança de segurança.** `git range-diff 6598bb7..06ec6a7 c61cf27..123512a` dá os commits de tema idênticos aos aprovados: `b3e4de7`/`f11906b`, `4c38c0d`/`8faf45e`, `ed5690d`/`84a89d6`, `acdf626`/`8b53cec` e `123512a`/`06ec6a7`. A única diferença é a linha de import de `hooks/conformidade.py`, sem o `com_ansi_c`. A segmento-crase-hook (`66fa688`, aprovada) é ancestral sem mudança. `git show --remerge-diff` dos 14 merges da volta 5 sai vazio: nenhuma resolução de conflito nem conteúdo a mais. A develop trazida (`b45e40a..d9b26bb`) não toca `hooks/`; ela muda só `bin/forge-check` e `bin/forge-testes`, e o `parecer` desta pilha não chama esses dois. O diff da pilha contra `d9b26bb` toca só `hooks/_comum.py`, `hooks/conformidade.py`, `hooks/parecer.py`, testes, mutantes e o changelog. A develop atual (`30b4453`) também não toca `hooks/` e faz merge limpo com `dde743b`. Na mensagem da HOOK-MSG-SEGMENTO, o mascaramento continua valendo sobre as formas novas: `GH_TOKEN=$'…\x44…'`, `GH_TOKEN=…\0`, `GH_TOKEN` com continuação, `$'ghp_…'` e `$'\x67hp_…'` saem com `***`, e `\e` e `‮` decodificados não aparecem no trecho.

**Junção do changelog (`dde743b`): só documentação.** Sete fragmentos viram um (`changelog.d/hook-msg-segmento.md`) com o texto igual, agrupado por seção. Não há código, segredo nem instrução nova. Nota de processo, fora da segurança: a mensagem do commit fala em PR único a partir do topo, e o E1.5 do pedido fala em um PR por branch. Quem decide isso é o E1.5 e o Jarvis.

**A1 (recomendado), mascaramento na forma escrita.**
- Evidência: `mascarado` (`hooks/conformidade.py:1803`) aplica `TOKEN_DO_GITHUB` à palavra escrita. Com `gh` + `\` + quebra + `p_<corpo>`, o bash junta e passa o token inteiro ao `gh`. O trecho da recusa sai como `gh p_AAAAAAAAAAAAA…`, com 13 caracteres do corpo. O mesmo acontece em `06ec6a7`.
- Caminho de ataque: nenhum realista. O token já está no comando que o próprio agente escreveu e no transcript. O mascaramento é defesa em profundidade.
- Severidade: baixa.
- Correção mínima: mascarar também sobre `juntar_continuacoes(palavra)`.
- Esforço: P. Dono: o autor da trilha, em cartão próprio. Não devolve a pilha.

**Fora da classe, sem mudança:** o A7, o A8 e o A9 do parecer `264eed0` (`bash -c --`, programa por variável, `bash -c "$(printf …)"`) seguem nos cartões urgentes. Esta pilha não os toca.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes rodados (D-5), numa cópia de `dde743b`:
- `tests.test_hook_ansi_c`: 9 testes, OK;
- `tests.test_hooks.Hooks.test_fixtures`, `test_fixtures_da_trilha_034`, `test_ansi_c_decodifica_como_o_bash` e `test_ansi_c_decodificado_no_texto`: 4 testes, OK em 262 s.

Também rodei 84 casos ad hoc pelos dois hooks e pelo bash com o `gh` falso. `gitleaks`, `semgrep`, `osv-scanner`, `zizmor`, `actionlint` e `trivy` estão fora do PATH: é lacuna, e não os instalei (R-CUSTO). A pilha não muda dependência nem workflow.
