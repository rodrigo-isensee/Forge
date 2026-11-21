---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-hook-propria-copia
commit: 4ee59dfcdf2b82cb10a3c49f8ed6fefdc92113dd
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478 E88.4, hook `copia` (HOOK-AGENTE-FORA-DA-PROPRIA-COPIA)

Escopo: diff `ad3b3b6f..4ee59dfc` (`hooks/copia.py`, `hooks/hooks.json`, `docs/hooks.md`, fixtures, `tests/test_copia.py`, mapas do `bin/forge-testes`). Suíte inteira não rodada aqui (só no CI, conforme o brief); sondas no processo, contra as funções do hook, com repositório e worktree reais em pasta temporária.

## Gatilhos
Gatilhos: hook de controle (R-CONFORMIDADE), guarda de escrita do time, leitura do registro do R-TETO.

## Achados
- A1 (bloqueante) hooks/copia.py:148 · Agente com reserva se solta com um comando que o hook libera: `git switch -c <outra>` (ou `checkout --detach`) na própria cópia zera `proprias` e tudo passa a liberar só com aviso; `git -C <raiz> symbolic-ref HEAD refs/heads/<sua>` faz da raiz cópia própria.
- A2 (recomendado) hooks/copia.py:58 · Só o segmento que começa pela palavra `git` é lido: `timeout 60 git push`, `env git`, `command git`, `/usr/bin/git`, `GIT_DIR=.git git commit` e `--git-dir=/--work-tree=` (o alvo fica a pasta atual) passam fora da lista de limites declarados.
- A3 (recomendado) hooks/copia.py:23 · `GIT_DE_ESCRITA` sem `symbolic-ref`, `update-ref`, `branch`, `worktree`, `read-tree`, `checkout-index`, `init`, `clone` e sem resolver alias (`-c alias.ci=commit ci`): esses comandos na raiz ou noutra cópia passam.
- A4 (recomendado) hooks/copia.py:33 · O corte no primeiro `<<` joga fora o resto da linha, não só o corpo do heredoc: `echo '<<'; cd <raiz> && git commit` e `cat <<< a; git -C <raiz> commit` liberam; o docs/hooks.md diz corpo do heredoc.

## Sondas
- S1 · hook com Write em `<raiz>/x`, registro `escrita: melhoria/x`, worktree `wt` em `melhoria/x` · espera: recusa (2) · obtido: recusa (2)
- S2 · depois de `git switch -c outra` em `wt` (alvo lido: a própria `wt`, liberado), Write em `<raiz>/x` · espera: recusa (2) · obtido: libera, só a linha `copia: agente a1 sem cópia no registro` no erros.log
- S3 · `git -C <raiz> symbolic-ref HEAD refs/heads/melhoria/x` (alvos lidos: nenhum), depois Write em `<raiz>/x` · espera: recusa (2) · obtido: libera, sem aviso (a raiz virou cópia própria)

## Detalhe dos achados
**A1.** Evidência: `hooks/copia.py:146-150` (`proprias` vazio libera) e `copia.py:106-120` (a cópia própria é qualquer worktree ou clone cujo HEAD está na branch da reserva, lido do disco a cada chamada). Caminho: o agente de escrita, na própria cópia, troca de branch (fluxo comum e sem malícia: branch auxiliar, `checkout` de um sha para conferir) e a guarda se desliga em silêncio pelo resto da vida dele; o agente que quer se liberar faz o mesmo de propósito, ou aponta o HEAD da raiz para a sua branch com `symbolic-ref`, que o hook não lê (S3) e que a deixa inteira liberada, `.git` incluso. Severidade: alta para o objetivo do controle (a guarda some sem mexer no registro). Correção mínima: (1) com `refs` não vazio e `proprias` vazio, não liberar: recusar o alvo que cai em `outras` (a raiz e as outras cópias) e anotar no erros.log; (2) a raiz da sessão nunca vale como cópia própria (tirar `realpath(raiz)` de `proprias`), e (3) `symbolic-ref` e `update-ref` em `GIT_DE_ESCRITA` (A3). Fixtures novas: as três sondas acima como recusa. Esforço P. Dono: autor do E88.1.

**A2.** Evidência: `hooks/copia.py:55-58` (`nome = segmento[0]`; só `cd` e `git` são lidos) e `copia.py:60-64` (`--git-dir`, `--work-tree` e `GIT_DIR=` não mudam `pasta_git`). Caminho: forma comum (`timeout`) ou deliberada de rodar git de escrita na raiz; sem o prefixo o hook recusaria. Severidade: média. Correção mínima: antes de ler o nome, pular atribuições `NOME=valor`, os prefixos `env` (com as opções dele), `command`, `timeout <n>`, `nice`, `nohup`, `exec`, `time`, e aceitar `git` por nome de arquivo do caminho (`/usr/bin/git`); `--git-dir=<p>`, `--work-tree=<p>`, `GIT_DIR=<p>` e `GIT_WORK_TREE=<p>` viram a pasta do alvo; pasta que sobra incerta (`$`) com git de escrita recusa em vez de sair da conta. Ou, se não corrigir, listar cada forma em `docs/hooks.md`, junto dos limites. Esforço P. Dono: autor do E88.1.

**A3.** Evidência: `hooks/copia.py:23-24`. Caminho: `git -C <raiz> branch -f develop <sha>`, `read-tree -u --reset`, `worktree add`, alias por `-c`, todos com alvo lido igual a nenhum (sondas de leitura). Severidade: média (`symbolic-ref` é a peça do A1, por isso alta lá). Correção mínima: somar à lista `symbolic-ref`, `update-ref`, `branch`, `worktree`, `read-tree`, `checkout-index`, `update-index`, `init`, `clone`, `notes`, `replace`, `filter-branch`, `gc`, `prune`, `fetch`, `submodule`, `sparse-checkout`, `bisect`; subcomando vindo de `-c alias.<x>=` resolve para o valor; leitura (`log`, `show`, `status`, `diff`, `rev-parse`, `ls-remote`, `branch` sem opção de escrita) segue fora. Esforço P. Dono: autor do E88.1.

**A4.** Evidência: `hooks/copia.py:33` (`texto.split("<<", 1)[0]`) contra o `docs/hooks.md` (limites, "o corpo do heredoc"). Caminho: `<<` entre aspas, here-string `<<<` ou comando depois do terminador do heredoc (o `git push` que vem depois do `EOF`) somem da leitura. Severidade: média. Correção mínima: cortar só o corpo: achar o delimitador do `<<` fora de aspas, pular até a linha que é igual a ele e seguir lendo; `<<<` não é heredoc; aspa ou delimitador não resolvido recusa o git de escrita da linha. Esforço P–M. Dono: autor do E88.1.

## Respostas ao brief
- **Contornar o hook / limites declarados.** `cp`, `mv`, `sed -i`, `tee`, script, destino em variável e corpo de heredoc estão no `docs/hooks.md` e exigem forma deliberada ou pouco comum de gravar fora: viram cartão (ler `cp`/`mv`/`tee`/`sed -i`/`install`/`rsync`/`ln` pelo último argumento ou `-t`), não bloqueiam. O que bloqueia é o A1; A2 a A4 são formas fora da lista declarada e voltam antes do merge.
- **De onde vem a cópia e se dá para forjar.** A reserva sai do `agentes.json` gravado pelo hook `agentes` no lançamento (`escritas_do_registro`, `copia.py:123-129`). Forjar a entrada direto: o Write/Edit no estado cai na `conformidade` (pasta `.forge` protegida e `ESTADO_NO_TEXTO`, `hooks/conformidade.py:334` e `:3796`), e no Bash a A3 do sandbox nega a escrita nos projetos; no clone do Forge a A3 ainda depende do arquivo de correção que o dono aplica (`docs/engineering/v0479-sandbox-controle.md`). Registro ilegível libera (fixture `erro-interno`), o mesmo da HOOK-ESTADO-ILEGIVEL-LIBERA. A peça que não tem proteção é a outra metade do par, o HEAD das cópias, lido do disco: é o A1.
- **Sem registro libera e avisa.** Aceitável para o agente sem reserva (parecer, brief sem `Branch:`), coerente com a ADR 0003 e com o aviso no erros.log. Não é aceitável quando há reserva e a cópia sumiu por troca de HEAD: é o A1, que separa os dois casos.
- **Só aperta?** Sim: o hook só acrescenta saída 2; erro interno sai 0 (`_comum.executar`); a sessão principal fica de fora; não grava nada além do erros.log. Custo: `copias()` lê o HEAD de cada clone de `~/.forge-contrib/wt/` a cada escrita de agente; nesta máquina, 2014 cópias em 1,15 s, dentro do prazo de 10 s, mas cresce com os clones velhos.

## Plano em cartões
- A1, A2, A3, A4: autor do E88.1, nesta branch, antes do merge.
- Cartão (limites declarados): ler o destino de `cp`, `mv`, `tee`, `sed -i`, `install`, `rsync`, `ln`. Dono: autor do E88.1, item futuro.
- Cartão: raiz vem de `hook.cwd()` (`copia.py:143`); com o cwd fora de projeto e de clone do Forge, o hook não age. Hoje o cwd do agente volta à raiz da sessão a cada chamada; registrar no `docs/hooks.md`.
- Cartão (custo): limpar clones velhos de `~/.forge-contrib/wt/` ou ler só os clones cujo nome casa com a branch da reserva.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff e sondas no processo contra as funções do hook; varredura de segredos e de dependências não se aplica ao achado (diff sem segredo nem dependência nova).
