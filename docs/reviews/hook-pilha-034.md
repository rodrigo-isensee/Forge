---
tipo: review
contrato: 1
pedido: hook-pilha-034
branch: melhoria/hook-msg-segmento
commit: ed9c22a7ef1e43d0142183afcdada364b9df339e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-06
---
# Review: hook-pilha-034 (E1.2, confirmação do E1 e do E2 e delta da reaplicação)

Base: develop d9b26bb. Head: dde743b, o topo da pilha de 7 branches em cadeia, igual a `origin/melhoria/hook-msg-segmento`. Revisor: outra instância do `tech-lead`, que não implementou as voltas (E1.1).

## Revalidação em ed9c22a (2026-11-06)
Delta lido: `git diff dde743b ed9c22a`. Fora os pareceres de review, segurança e QA (5edf63c, ee0f291 e dae76f8), muda só uma linha da fixture `tests/hooks/conformidade/hook-msg-segmento-atribuicao-mascarada-bloqueia.json:20`. O token falso passa a `ghp_FAKE_FAKE_…`, fora do padrão `ghp_[A-Za-z0-9]{20,}` de `scripts/verificar-contribuicao.sh:16` (grep sem casamento), e o hook ainda o mascara. O `TOKEN_DO_GITHUB` (`hooks/conformidade.py:42`) aceita `_` no corpo. O esperado não mudou: código 2, o trecho `GH_TOKEN=***` e `ghp_` e `FAKE` fora do stderr. Rodada só essa fixture pelo `executar_em_lote` do `tests.test_hooks.Hooks`: 1 caso, OK. O resto ficou como já lido. O veredito não muda.

## Achados
- A1 (recomendado) hooks/conformidade.py:1037 · `bash -c "g\$'\\x68' repo delete dono/proj --yes"` (e o mesmo com `eval`) passa com rc 0, e o bash roda `gh repo delete`. Já passava na develop e no 6598bb7: o leitor deixa o `\$` dentro de aspas duplas. Vai como cartão à segurança
- A2 (recomendado) changelog.d/hook-msg-segmento.md:9 · a entrada diz que todo `$'…'` se lê decodificado em todo nível, mas o caso do A1 (`\$'…'` dentro de `bash -c "…"`) fica de fora. Sugestão: ressalvar o caso ou citar o cartão do A1
- A3 (recomendado) changelog.d/hook-msg-segmento.md:1 · a mensagem do dde743b diz que a pilha vai à develop num PR só a partir do topo, mas o E1.5 do pedido manda um PR por branch. Um PR só com as 7 passaria do teto da M14, e em `hooks/` não há exceção. A junção dos fragmentos serve aos dois caminhos

## Confirmação dos achados anteriores
- A3 do f352820 (`g$'\x68' repo de\⏎lete …` passava no `conformidade`): fechado no c61cf27. Em `hooks/_comum.py:366-381`, `formas_que_o_shell_le` compõe os passos (expandida, juntada e `$'…'` decodificado) até o ponto fixo. Acima de `TETO_DE_FORMAS` (`_comum.py:363`), levanta `RuntimeError`, e o `marcado` (`_comum.py:2514-2518`) marca e falha fechado. As fixtures `continuacao-linha-107` a `-111` (`tests/hooks/conformidade/`) provam a recusa. As sondas do parecer anterior, rodadas no head, saem todas com rc 2: `g$'\x68' repo de\⏎lete`, `g$'\x69't pu\⏎sh origin main` e `$'\x67'it push origin ma\⏎in`.
- A4 do f352820 (`g$'\x68' pr mer\⏎ge docs/x` passava no `parecer`): fechado no c61cf27, pela mesma função, que o `parecer` usa no prefiltro (`hooks/parecer.py:647`) e no `conferir_linha` (`hooks/parecer.py:660`). A fixture `tests/hooks/parecer/continuacao-linha-112-…-bloqueia.json` prova a recusa, e a sonda sai com rc 2.
- M4 (A1 do parecer cd76d07 da rotulo-variavel, o M4 declarado equivalente): fechado no 32df248. Em `tests/mutantes/hook-conformidade-034-2.json:19-24` saiu o campo `equivalente`, e o `tests.test_hook_ansi_c` entrou nos testes do M4. O commit 165eb6c, que declarava a equivalência, não está na cadeia reaplicada. `bin/forge-mutante` (rev dde743b95b24): o M4 morreu.

## E1, delta lido (6598bb7..57d46dc)
Li só o delta das voltas 4 e 5. O resto ficou como já lido no f352820.
- 5be062c: `decodificar_ansi_c` corta no primeiro NUL (`_comum.py:428`, o A10 da segurança). Vêm com ele 9 fixtures `continuacao-linha-98` a `-106`, inclusive a `106-printf-a-0b-libera`. O corte só encurta a forma a mais, e a escrita segue conferida, então nenhum caminho de liberação é novo.
- c61cf27: o ponto fixo descrito acima, e o `$"…"`, que agora se lê como aspas duplas (`_comum.py:401`). O `com_ansi_c` saiu de `bash -c` e de `eval` (`conformidade.py:1037`, `:1039` e `:1574` a `:1576`), porque o `aninhado` já passa por `formas_que_o_shell_le` em todo nível. Sondas no head: `bash -c $'\x67h repo delete …'`, `eval $'\x67h …'`, `sh -c $'g\x69t push origin main'`, `bash -c $'…\x00x'` e `bash -c $'gh repo de\\⏎lete …'` saem com rc 2. No `parecer`, `bash -c` e `eval` com `gh pr m\x65rge` também saem com rc 2. Os controles (`gh repo view`, `echo $'a\x00b' && git status`, `printf '%s' $"gh" repo view` e `gh pr view`) saem com 0.
- 57d46dc (volta 5): o T1 deixa de reler a variante `"$(…)"` só nas linhas com `$'` e `\\`. A limitação do `shlex` é a mesma já pulada para a aspa dupla e o `case`. As fixtures `continuacao-linha-40b` e `-42b` provam pela ação que o hook recusa essa variante. O teste não ficou mais frouxo que o hook.
- O furo do A1 deste parecer é anterior à pilha e de outra classe, a leitura do `\$` dentro de aspas duplas pelo leitor. Conferi com o mesmo script de sonda sobre o `git archive` da `origin/develop` e do 6598bb7: as três variantes saem com rc 0 nos dois. Por isso não é regressão, e não devolve.

## E2 (rotulo-variavel, 32df248)
O commit só mexe na spec `-2.json` (+2/-1). O M14 do PR segue com 2 linhas de `tests/test_hooks.py`. O PR não toca `hooks/`.

## E3, delta da reaplicação (branches 1 e 4 a 7)
- `git cherry -v 06ec6a7 HEAD`: os commits das branches 3 a 7 são equivalentes por patch aos heads já aprovados (2a81f63, 4eecf5e, 7598e40 e 06ec6a7, todos com `parecer: aprovado`). A exceção é o acdf626, e o `git range-diff 8b53cec^! acdf626^!` mostra que só muda a linha de contexto do import (sai o `com_ansi_c`). A branch 1 mantém os mesmos SHAs aprovados (40ca781 e 66fa688).
- Os 14 merges de `origin/develop..HEAD`, que trazem a develop e o T1 por toda a cadeia, saem limpos: `git show --remerge-diff` vem vazio em todos, e nenhum muda o patch das entregas. Atualizar antes da hora do merge foge do padrão do R-FLUXO. O motivo foi o T1 vermelho vindo da develop no pre-push, e o `forge-check pr` do E1.5 confere o `commit_vale`.
- dde743b: as entradas dos 7 fragmentos são as mesmas (`diff` das linhas `- ` ordenadas, antes e depois: iguais). Ficam só `hook-msg-segmento.md` e os fragmentos que vieram da develop. Sobre o modo do PR, ver o A3.

## O que foi rodado
- `bin/forge-mutante tests/mutantes/hook-conformidade-034-2.json …-6.json …-8.json --processos 1` (rev dde743b95b24): os 26 mutantes morreram, M3, M4, M18 a M22, M25, M27 a M31, M34 a M46.
- `python3 -m unittest tests.test_hook_ansi_c` e mais 4 testes de `tests.test_hooks.Hooks` (`test_ansi_c_decodificado_no_texto`, `test_formas_compostas_ate_o_ponto_fixo_e_teto_fecha`, `test_ansi_c_decodifica_como_o_bash` e `test_marcador_critico_tambem_na_forma_juntada`): 13 testes, OK. O T1 (`test_t1_variantes_que_o_bash_ignora_nao_tiram_comando_da_leitura`) também rodou: 1 teste, OK, em 523 s.
- Script de sonda do review no scratchpad (`rev034sonda.py`): monta a fixture 40b ou 112 com outro comando e roda o hook.

## M14
- E1 (hook-continuacao-linha): código e teste somam 144 linhas. São `_comum.py` 91, `conformidade.py` 12, `parecer.py` 7 e `tests/test_hooks.py` 29 mais 5 da volta 5. Ficam dentro do teto, com um comportamento só, como no f352820.
- E2: 2 linhas.
- E3: o patch das branches não mudou.

## Regras de ferramenta
O `shellcheck` não se aplica. A suíte inteira fica com o QA e o CI (D-5). O gatilho de segurança (`hooks/`) pede o parecer do `security-engineer` (E1.3), que é dele.

## Parecer
Aprovado. O A3 e o A4 do f352820 e o M4 do cd76d07 estão fechados, com fixtures e mutantes que os provam. O E2 está correto. A reaplicação não mudou o patch de nenhuma branch já aprovada, e a junção do changelog preserva as entradas. O A1 é um furo anterior, de outra classe, e vai como cartão à segurança. O A2 e o A3 não devolvem.
