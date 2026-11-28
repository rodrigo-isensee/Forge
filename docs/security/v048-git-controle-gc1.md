---
tipo: revisao-seguranca
contrato: 1
pedido: v048
branch: melhoria/v048-git-controle-gc1
commit: 841c557ea6eb82bddf4eec7bf48c816683b533b0
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-28
---
# Review de segurança: v048 (E3.8, PR #957, GC1, delta das voltas 1 e 2)

Volta por delta no head `841c557e`, desde o parecer da 1ª rodada no `29bdda15` (fica no git). Delta lido por `forge-check parecer delta`: no domínio só `bin/forge_git.py`; `tests/test_forge_git.py`, os `tests/mutantes/*.json` e o fragmento do changelog estão fora, e o teste foi lido só para casar com as sondas e as mutações.

## Gatilhos
Gatilhos: execução fora do sandbox (hooks), config e arquivos de `.git` graváveis pelo time, controle que analisa entrada (lista positiva de subcomandos e de opções).

## Achados
- A5 (recomendado) bin/forge_git.py:93 · Opção curta aglutinada fura o -O do grep: o teste só vê o argumento que começa com -O, e grep -nO<programa> (grep é LEITURA sem conferência) roda o programa (sonda local). Recusar todo agrupamento curto que contenha O, mais um teste.

## Sondas

## Detalhe dos achados

**Estado dos achados anteriores.**
- A1 (bloqueante, gitlink): **fechado.** `sem_gitlink` (`bin/forge_git.py:75-78`) entra na condição do INDICE (`:100`). Refiz a S1 e a S2 com a mesma montagem (gitlink `sub` no índice, `filter.mal.clean` e `* filter=mal` no `.git` do submódulo, `.gitmodules` com `ignore = none`): `status --porcelain`, `diff`, `checkout HEAD`, `switch --detach HEAD` e `commit --dry-run --allow-empty` dão `Recusado` e o marcador não aparece; `ls-files`, `add`, `reset`, `restore`, `rm` e `mv` também recusam. A cópia limpa passa (`status` rc=0). Tentei contornar com o gitlink fora do índice e não consegui: gitlink só no HEAD com `rm --cached` (`status`, `diff HEAD`, `checkout HEAD`, `switch --detach HEAD`, `reset --hard`), `checkout` de uma ref cujo commit traz o gitlink, com `sub/` aninhado já presente, e repositório aninhado fora do índice (`status -uall`, `diff`, `add .`, `add sub`). Em nenhum desses o marcador apareceu; quando o gitlink chega ao índice, o comando seguinte recusa. Teste: `test_gitlink_no_indice_recusa`.
- A2 (recomendado, opção abreviada e `--output`): **fechado** (`:38`, `:92-93`). `cat-file --textc`, `--filt`, `--text` e `--filter`, `grep --open-files`, `log --out=` e `--o=` dão `Recusado`. `core.pager=cat` está no `NEUTRO` (`:25`). Testes: `test_opcao_abreviada_reabre_programa` e `test_neutro_fecha_o_pager_da_copia`. Resta a aglutinação de opção curta, que virou o A5 (dimensão nova da matriz: grafia curta agrupada).
- A3 (recomendado, ação fora da posição): **fechado** (`:81-86`). `worktree add list`, `remote add` e `remote -v add` dão `Recusado`; `remote`, `remote -v`, `worktree list`, `branch --show-current` e `branch --list --contains HEAD` passam; `branch novo` recusa; `branch -r novo` o próprio git recusa (rc=128). Teste: `test_leitura_pela_posicao_da_acao`.
- A4 (recomendado, corpus do clone principal): **fechado** (`:42`). As duas chaves entram por nome, e nenhuma aponta programa. Teste: `test_chaves_do_clone_principal_passam`.

**Mutação, refeita por mim** (os logs carimbados do autor não valem; R-PROVA). Cada mutante foi aplicado sobre o `841c557e` e rodei `tests/test_forge_git.py` (24 testes, OK sem mutante). Os nove morreram: tirar `sem_gitlink` da condição; trocar o modo `160000`; comparar a opção inteira em vez do prefixo; tirar `--output` da REATIVA; tirar `core.pager=cat`; aceitar a ação em qualquer posição; `branch` sem o limite de opções; tirar as chaves do VS Code da PERMITIDAS; tratar `--` como opção.

**A5 (média, depende de quem chama, como o A2 era).** Evidência: `bin/forge_git.py:93`, `any(a.startswith("-O") for a in resto)`. O analisador de opções do git aceita opção curta agrupada, e o `-O` do grep aceita valor colado. Sonda local: `forge_git.git(copia, "grep", "-nOtouch MARCX", "a")` dá rc=0 e grava `copia/MARCX`; `git grep -nO"touch <caminho>" a` grava o arquivo. `grep -nO a` sem valor usa o `core.pager=cat` e não roda nada. Caminho de ataque: só existe com um chamador do GC2 ao GC6 que repasse opção vinda do agente para o `grep`. Hoje não há chamador, por isso o achado é recomendado. Correção mínima: em `montar`, recusar todo argumento que comece com um só `-` e traga `O` antes do primeiro `=` (regra: `re.match(r"-[^-=]*O", a)`). A recusa falsa de padrão `-e` com `O` é falha fechada. Acrescentar um teste com `grep -nO<programa>` e `-iO<programa>`. Esforço P. Dono: tech-lead (autor da E3.2). Volta ao autor e é corrigido antes do merge (R-REVIEW).

Resíduo: a janela entre `sem_gitlink` e o git é a mesma corrida já registrada para a config (anexo, seção 4). O docstring (`:8`) cita só a config; uma palavra sobre o índice basta, sem achado.

**Catraca e teste de custo** (ordem do dono 28/11 07:41, o diff toca `bin/`): `tests/catraca.py` rc=0 local; jobs `catraca` e `catraca (conferência)` verdes no run 46145488828. `tests/test_hooks_volta_corpus.py` dá OK local, e o diff contra a develop não toca `hooks/`. CI do head `841c557e`: as cinco partes da suíte (a 5/5 rodada de novo), passos, verificações longas, instalação e python 3.14 estão verdes. Ficam vermelhos só `bateria (pareceres)` e o agregador `bateria`, porque esperam os pareceres aprovados (R-REVIEW cita este parecer e o do review). Não há falha de código.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: sondas locais em repositórios descartáveis no `$TMPDIR` (git 2.43, sem rede e sem hook real) e mutação manual da suíte do módulo. Não estão no PATH: `gitleaks`, Semgrep CE, `osv-scanner`, `zizmor` e `actionlint`. Fica como lacuna; o delta não traz dependência nem workflow.
