# Índice das fixtures dos hooks

<!-- Gerado por scripts/indice-fixtures.py; não edite à mão. Rode o script depois de mudar o corpus. -->

O corpus de `tests/hooks/<hook>/<caso>.json` (2449 fixtures) roda em `tests/test_hooks.py` (ADR 0003): cada caso dá a entrada de uma chamada ao hook e o código e a saída que ele tem de dar. O índice agrupa por hook e pelo prefixo do nome do caso (até o primeiro `-`); nenhum caso muda de nome nem de lugar. "Recusa" é `esperado.codigo` 2; "libera", 0. As regras são as `R-*` do `stderr` esperado; os cartões, o identificador que abre a `descricao`.

## Por hook

| Hook | Fixtures | Recusa | Libera | Prefixos |
| --- | ---: | ---: | ---: | ---: |
| `agentes` | 79 | 44 | 35 | 27 |
| `conformidade` | 1799 | 1327 | 472 | 89 |
| `doutor` | 3 | 0 | 3 | 3 |
| `meta` | 25 | 10 | 15 | 12 |
| `parecer` | 463 | 357 | 106 | 24 |
| `pesado` | 24 | 9 | 15 | 19 |
| `quadro` | 7 | 2 | 5 | 7 |
| `vigia` | 49 | 0 | 49 | 25 |

## `agentes`

| Prefixo | Fixtures | Recusa | Libera | Regras | Cartões | O que prova (exemplo) |
| --- | ---: | ---: | ---: | --- | --- | --- |
| `errointerno-*` | 8 | 6 | 2 | `R-BRIEF` | `HOOK-ERRO-LIBERA` | HOOK-ERRO-LIBERA (C7): erro ao fixar a pasta do estado não leva o R-BRIEF junto: o especialista sem brief segue recusado. |
| `carga-*` | 7 | 5 | 2 | `R-TETO` | — | Load 5 está abaixo de 80% de 8 núcleos (6,4): um ativo libera. |
| `pid-*` | 7 | 7 | 0 | — | `C1-1` | C1-1/C1-2: pid acima do pid_max mantém o registro (falha para o lado seguro) e o hook segue barrando no teto. |
| `nproc-*` | 6 | 3 | 3 | — | — | 16 núcleos, load 3: teto 16; quinze ativos liberam (o teto segue o hardware). |
| `inicio-*` | 5 | 0 | 5 | — | `C1-5` | C1-5: o SubagentStart da mesma sessão confirma a reserva e ela mantém o pid. |
| `piso-*` | 5 | 3 | 2 | — | — | `piso_memoria_gb` 3 em .forge/config.json: 2,5 GB livres bloqueia. |
| `sem-*` | 5 | 3 | 2 | — | `C1-3` | Projeto sem .forge/versao: o hook não age nem cria estado. |
| `teto-*` | 5 | 4 | 1 | — | — | teto_agentes 1 no .forge/config.json, um ativo: bloqueia. |
| `load-*` | 3 | 0 | 3 | — | — | 8 núcleos, load 5 (< 6,4) e 8 GB livres: dispara. |
| `memoria-*` | 3 | 2 | 1 | `R-TETO` | — | 16 GB no total (piso padrão 2 GB), 1,5 GB livres: bloqueia. |
| `reserva-*` | 3 | 0 | 3 | — | `C1-5` | C1: a reserva grava pid da sessão, namespace e session_id. |
| `ritmo-*` | 3 | 2 | 1 | — | — | ritmo acelerado com teto_maximo 1 e um ativo: bloqueia (o acelerado não passa do teto de sempre). |
| `bloqueia-*` | 2 | 2 | 0 | — | — | Mesmo tipo e mesma descrição de um agente ativo: relançamento duplicado. |
| `duplicado-*` | 2 | 1 | 1 | — | — | C1: o relançamento com a mesma descrição passa quando o registro é de sessão morta. |
| `fim-*` | 2 | 0 | 2 | — | — | C1: o SubagentStop remove só o agent_id; o outro, de sessão viva, fica. |
| `sessao-*` | 2 | 1 | 1 | — | — | C1: registro cujo pid de sessão não existe mais (mesmo namespace) sai na hora; o lançamento passa no teto. |
| `desligado-*` | 1 | 0 | 1 | — | — | hooks_desligados na config desliga só este hook. |
| `erro-*` | 1 | 0 | 1 | — | — | Estado corrompido: libera (saída 0) e registra em erros.log. |
| `expirado-*` | 1 | 0 | 1 | — | — | Registros com mais de 2 h expiram (SubagentStop perdido não trava o teto). |
| `ferramenta-*` | 1 | 1 | 0 | — | — | Nome antigo da ferramenta de agentes (Task) também conta. |
| `lanca-*` | 1 | 0 | 1 | — | — | Dois agentes ativos, teto 3: libera e reserva a vaga. |
| `mesmo-*` | 1 | 0 | 1 | — | — | Mesmo tipo com outra descrição não é duplicado. |
| `namespace-*` | 1 | 1 | 0 | — | `C1-3` | C1-3: namespace gravado de tipo errado: mantém. |
| `outra-*` | 1 | 0 | 1 | — | — | PreToolUse de outra ferramenta: nada a fazer. |
| `outro-*` | 1 | 1 | 0 | — | `C1-3` | C1-3: pid morto, mas o registro é de outro namespace de PID: mantém. |
| `registro-*` | 1 | 1 | 0 | — | — | C1: registro antigo, sem pid, segue só a regra do prazo. |
| `worktree-*` | 1 | 1 | 0 | — | — | Chamada numa worktree lê o estado da cópia principal. |

## `conformidade`

| Prefixo | Fixtures | Recusa | Libera | Regras | Cartões | O que prova (exemplo) |
| --- | ---: | ---: | ---: | --- | --- | --- |
| `trava-*` | 189 | 119 | 70 | `R-CONFORMIDADE`, `R-VERIFY`, `R-MAIN` | `TMPDIR` | git branch -D develop. (perfil iniciante: com a consequência em linguagem simples) |
| `contrib-*` | 144 | 102 | 42 | `R-CONTRIB`, `R-CONFORMIDADE`, `R-MAIN` | `PR`, `FILA-22`, `PATCH`, `GET` e mais 1 | Comando aninhado que não dá para analisar (aspas abertas) e aponta para o Forge: falha fechado. |
| `conferente-*` | 111 | 90 | 21 | — | `ADR`, `VV-2`, `AA2-01` | Citação ANSI-C $'...': o bash entrega --upload-pack ao git e o hook não vê a opção. |
| `gh-*` | 99 | 84 | 15 | `R-MAIN`, `R-CONFORMIDADE` | `GH-MERGE-ADMIN` | GH-MERGE-ADMIN: gh pr merge melhoria/x --admin --squash |
| `continuacao-*` | 98 | 85 | 13 | `R-CONFORMIDADE`, `R-CONTRIB`, `R-MAIN`, `R-VERIFY` | `HOOK-CONTINUACAO-LINHA` | HOOK-CONTINUACAO-LINHA: o bash junta \ + quebra de linha; a forma juntada recusa como a escrita direta. |
| `gitcomum-*` | 84 | 61 | 23 | `R-CONFORMIDADE` | `E20.6` | Volta 1 da E20.6 (v046, segurança E20.8 A5, sem falso positivo): `--target-directory=docs` segue livre. |
| `v0453-*` | 81 | 57 | 24 | `R-FLUXO`, `R-CONFORMIDADE` | `V0453-GH-ALIAS`, `V0453-AQ-LEITURA`, `V0453-PARECER-BASH`, `V0453-PUSH-TODAS` | V0453-AQ-LEITURA: aq não prepara commit |
| `heredoc-*` | 68 | 59 | 9 | `R-CONFORMIDADE`, `R-MAIN`, `R-REVIEW`, `R-VERIFY` | `HEREDOC-FURO-HOOK`, `C-8`, `HEREDOC-COMENTARIO`, `HEREDOC-DONOS` e mais 1 | A1 do review (volta 3): o mkdir e o cd antes do && não leem o corpo: o dono é o cat > n.md, que só o grava. |
| `merge-*` | 47 | 40 | 7 | `R-CONFORMIDADE`, `R-REVIEW`, `R-MAIN`, `R-DECISAO` | `FURO-HOOK-A`, `FILA-22`, `QA` | git merge main numa branch de trabalho (atualização): qualquer papel. |
| `lancador-*` | 40 | 36 | 4 | `R-CONFORMIDADE`, `R-VERIFY` | — | Prefixo desembrulhado antes de classificar: command git commit --no-verify -m x |
| `rotulo-*` | 40 | 31 | 9 | `R-CONTRIB` | `FURO-HOOK-A`, `ROTULO-VARIAVEL`, `HOOK-COMENTARIO-SHLEX` | Sessão do Forge: gh api em issues/N/labels, conta do dono. |
| `git-*` | 37 | 32 | 5 | `R-CONFORMIDADE` | — | `git checkout -- <arquivo comum>` e `git rm` de arquivo comum seguem livres: só o caminho protegido barra. |
| `oraculo-*` | 36 | 19 | 17 | — | `EXT-1` | EXT-1 (C-7): `cat > tests/test_oraculo_x.py <<'F'` do tech-lead no oráculo bloqueia. |
| `n5r-*` | 35 | 25 | 10 | `R-REVIEW`, `R-VERIFY`, `R-CONFORMIDADE` | — | N5 (review da 0.43.5): alias na linha troca o subcomando (commit na develop) |
| `n5-*` | 34 | 21 | 13 | `R-REVIEW` | — | N5 (L22, IMPL-FURO-HOOK-N): am na develop |
| `nao-*` | 34 | 21 | 13 | `R-MAIN` | `ADR`, `AA2-01` | ADR 0011 (item 2): $' que o shlex lê como aspas abertas. |
| `pn7-*` | 32 | 24 | 8 | `R-MAIN` | `PN7-DOLAR-INTERROG` | PN7-DOLAR-INTERROG (H1-1, ADR 0011): continua barrado. |
| `rverify-*` | 29 | 22 | 7 | `R-VERIFY` | `HOOK-RVERIFY-FALSO-POSITIVO` | HOOK-RVERIFY-FALSO-POSITIVO: cat > $TMPDIR/x.py <<'EOF' com `*` e .githooks/pre-push só no corpo (dado, não destino); sessão do Forge, pasta… |
| `n2-*` | 28 | 22 | 6 | `R-REVIEW` | — | N2 (L20b, IMPL-FURO-HOOK-N): GIT_OBJECT_DIRECTORY por declare -x |
| `shell-*` | 28 | 20 | 8 | `R-CONFORMIDADE` | — | Contorno pelo shell: echo 9.9.9 >> .forge/versao |
| `comentario-*` | 26 | 23 | 3 | `R-VERIFY`, `R-CONFORMIDADE`, `R-MAIN` | `HOOK-COMENTARIO-SHLEX` | Na regex do `=~` o bash não abre comentário depois de `\|`: o push seguinte é lido. |
| `fc-*` | 26 | 17 | 9 | `R-CONFORMIDADE` | `FURO-HOOK-A` | FURO-HOOK-A, A4: contraprova: saída fora de pasta protegida. |
| `vigor-*` | 25 | 24 | 1 | `R-CONFORMIDADE` | `CLAUDE` | {raiz}/.claude/agents/x.md é do usuário: bloqueia até o jarvis. |
| `hook-*` | 21 | 13 | 8 | `R-VERIFY` | `HOOK-N4`, `HOOK-MSG-SEGMENTO` | hooks_desligados com conformidade (escolha do usuário): libera. |
| `leitura-*` | 21 | 17 | 4 | — | `K2-REC` | bash -c com forge sugerir segue recusada (F6, só leitura) |
| `n1-*` | 21 | 16 | 5 | `R-MAIN`, `R-VERIFY` | — | N1 (IMPL-FURO-HOOK-N, C-N1-2): o alias com ponto no nome também é lido |
| `pacote-*` | 21 | 9 | 12 | `R-CONFORMIDADE` | `QA` | Dev instala dependência nova. |
| `pr-*` | 21 | 17 | 4 | `R-CONFORMIDADE`, `R-MAIN` | `FILA-22`, `QA` | Dev criando PR: bloqueia. |
| `aq-*` | 18 | 13 | 5 | — | `AQ` | AQ barrado em agents/ de uma worktree fora da raiz. |
| `autoria-*` | 17 | 0 | 17 | — | — | Redirecionamento para docs/qa/ pelo Bash também registra. |
| `errointerno-*` | 17 | 11 | 6 | — | `HOOK-ERRO-LIBERA` | HOOK-ERRO-LIBERA (E5, C3): erro interno com alvo opaco (`$(...)`) numa linha que escreve recusa, sem depender do nome do caminho. |
| `desenho-*` | 16 | 7 | 9 | — | `E5-0` | E5-0 (Q-B, PAR-P2): sonda: docs/architecture/ de projeto fica sem dono até DESENHO-PROJETO-DONO; o devops grava a seção CI/CD do plano. |
| `parecer-*` | 16 | 12 | 4 | `R-CONFORMIDADE` | `QA` | dev escrevendo parecer em docs/devops/: bloqueia. |
| `subst-*` | 16 | 14 | 2 | `R-VERIFY`, `R-MAIN` | `HEAD` | Caminho colado a $(...): o resto é conferido também a partir da raiz (na dúvida, recusa). |
| `flag-*` | 15 | 13 | 2 | `R-VERIFY` | — | Flag proibida: git -c core.hooksPath=/dev/null push origin feature/x |
| `protegido-*` | 15 | 11 | 4 | `R-CONTRIB` | — | .claude-plugin/plugin.json: Dev em melhoria/*: bloqueia. |
| `profundidade-*` | 14 | 10 | 4 | `R-CONFORMIDADE`, `R-VERIFY` | `PROFUNDIDADE-BASH-C` | PROFUNDIDADE-BASH-C (v0457 E17.1): 3 níveis legítimos de bash -c no projeto seguem liberados. |
| `ar-*` | 13 | 11 | 2 | `R-VERIFY`, `R-MAIN`, `R-REVIEW` | `AR-TRAVA-UMA-SINTAXE` | AR-TRAVA-UMA-SINTAXE: o programa pelo caminho é o mesmo |
| `n3-*` | 12 | 9 | 3 | — | — | N3 (IMPL-FURO-HOOK-N, S1b): cp -l faz o mesmo link físico |
| `fila22-*` | 11 | 7 | 4 | `R-CONFORMIDADE` | `FILA-22` | FILA-22 (review da 0.43.2): abrir PR pelo `gh api` segue a política `pr_criar`; o jarvis (sessão principal) não abre. |
| `home-*` | 11 | 10 | 1 | — | `HOME` | ~/.claude.json é do usuário. |
| `m1-*` | 10 | 7 | 3 | — | — | M1 (review da 0.43.2): a linha de selo ou de conferência é da ferramenta; `cd docs/pedidos && cat >> p1.md <<'FIM'` com a conferência no cor… |
| `crase-*` | 9 | 7 | 2 | `R-CONFORMIDADE` | `CRASE-ASPA-HOOK`, `CRASE-SESSAO-PROJETO` | Orçamento: 60 cd e 60 crases aninhadas terminando em push com --no-verify: o hook recusa sem estourar o timeout (a base recusava em 0,34 s). |
| `erro-*` | 7 | 5 | 2 | — | — | Config corrompida e comando sem marcador: libera e registra. |
| `pedido-*` | 6 | 4 | 2 | — | `VV-2` | VV-2, A1: o dev não grava no pedido. |
| `push-*` | 6 | 4 | 2 | `R-CONFORMIDADE`, `R-MAIN`, `R-VERIFY` | `AGENTE-NAO-EMENDA-ENVIADO` | git push -u origin <branch de trabalho>: livre. |
| `api-*` | 5 | 3 | 2 | — | — | Comentário em PR por gh api: não é crítico. |
| `i-*` | 5 | 5 | 0 | `R-CONFORMIDADE` | — | Busca de classe: `awk -i inplace` sobre arquivo em vigor dá bloqueio. |
| `ativar-*` | 4 | 2 | 2 | `R-VERIFY` | — | -c core.hooksPath= junto da ativação continua barrado. |
| `d-*` | 4 | 4 | 0 | `R-CONFORMIDADE` | — | Achado D, cadeia 3: sem `.forge/versao`, `mv .git .g` (para depois usar `GIT_DIR=.g`) cai na conferência inteira: o `.git` da raiz é protegi… |
| `f-*` | 4 | 4 | 0 | `R-CONFORMIDADE` | — | Achado F: com o `commondir` escrito fora dos hooks no clone principal (a marca não se consulta) e sem `.forge/versao`, o push falha fechado. |
| `pasta-*` | 4 | 2 | 2 | — | `HOOK-RAIZ-CONTRIB` | HOOK-RAIZ-CONTRIB: o jarvis grava em ~/.forge-contrib/forge/docs/briefs/ (a sessão do Forge grava ali). |
| `regra-*` | 4 | 2 | 2 | — | — | Dev editando regra do Forge, mesmo em melhoria/*: bloqueia. |
| `segmento-*` | 4 | 3 | 1 | `R-CONFORMIDADE` | `SEGMENTO-CRASE-HOOK` | SEGMENTO-CRASE-HOOK: crase em dois níveis com comando comum segue liberada. |
| `amend-*` | 3 | 2 | 1 | `R-VERIFY` | `AGENTE-NAO-EMENDA-ENVIADO` | AGENTE-NAO-EMENDA-ENVIADO: o git aceita `--amen` (prefixo único de `--amend`); a recusa também. |
| `atribuicao-*` | 3 | 2 | 1 | `R-CONFORMIDADE`, `R-MAIN` | — | N1, excesso: a atribuição com substituição que só lê continua liberando. |
| `b8-*` | 3 | 3 | 0 | `R-CONFORMIDADE` | — | B8 do review: `gawk -E inplace.awk` carrega a extensão `inplace`, confere os arquivos-alvo e dá bloqueio. |
| `brief-*` | 3 | 2 | 1 | — | `VV-2` | VV-2, A1: o autor não grava em ~/.forge-contrib/docs/briefs/. |
| `env-*` | 3 | 2 | 1 | — | — | cat .env expõe segredo. |
| `n-*` | 3 | 3 | 0 | `R-CONFORMIDADE` | — | N da segurança (B9 do review): interpretador dono do heredoc entre aspas (`"perl" <<'X'`, `'python3' <<'X'`) tem o texto conferido e dá bloq… |
| `projeto-*` | 3 | 0 | 3 | — | — | Projeto comum com tests/hooks/ próprio: não é o Forge, nada protegido. |
| `aceite-*` | 2 | 2 | 0 | — | — | Seguranca nao grava o aceite de risco (docs/security/aceites/): so o usuario. |
| `aritmetica-*` | 2 | 2 | 0 | `R-CONFORMIDADE` | `HOOK-COMENTARIO-SHLEX` | HOOK-COMENTARIO-SHLEX volta 3, A3: aspa no comentário de `((…))` deixava a leitura falhar e a linha crítica passava; agora é recusada. |
| `b5-*` | 2 | 2 | 0 | `R-CONFORMIDADE` | — | B5 do review: `-i` com sufixo fora de letras, dígitos e ponto (`-pi~`) em perl passa pelas duas conferências e a escrita em arquivo em vigor… |
| `b6-*` | 2 | 2 | 0 | `R-CONFORMIDADE` | — | B6 do review: `gawk --include` com `inplace` em qualquer forma do nome (`inplace.awk`) confere os arquivos-alvo e dá bloqueio. |
| `b7-*` | 2 | 2 | 0 | `R-CONFORMIDADE` | — | B7 do review: heredoc para interpretador com versão no nome (`perl5.34.0`) tem o texto conferido e dá bloqueio. |
| `guarda-*` | 2 | 0 | 2 | — | — | FORGE_GUARDA_ABERTA=1 com erro interno e marcador: libera. |
| `j-*` | 2 | 2 | 0 | `R-CONFORMIDADE` | — | Achado J: `perl -0777pi` (opção numérica junto do `-i`) sobre arquivo em vigor dá bloqueio. |
| `k-*` | 2 | 2 | 0 | `R-CONFORMIDADE` | — | K da segurança: `w arquivo` do sed depois de delimitador escolhido pelo usuário (`s\|a\|b\|w arq`, `\%a%w arq`) conta como escrita e dá bloq… |
| `o-*` | 2 | 2 | 0 | `R-CONFORMIDADE` | — | O da segurança: segundo w no mesmo script do sed (s/saw/x/;w arquivo) ainda é achado. |
| `sem-*` | 2 | 0 | 2 | — | — | Projeto sem .forge/versao: escrita em .claude/ liberada. |
| `versao-*` | 2 | 1 | 1 | — | — | A marca de projeto do SessionStart (`.git/forge/projeto-<hash da raiz>`) existe e o `.forge/versao` sumiu: a ação crítica falha fechado (R-C… |
| `b10-*` | 1 | 1 | 0 | `R-CONFORMIDADE` | — | B10 do review: aspas no meio do nome do dono do heredoc (p''erl) não o esconde da conferência de texto. |
| `b4-*` | 1 | 0 | 1 | — | — | B4: worktree sem Forge aberta por link simbólico (`CLAUDE_PROJECT_DIR` e cwd passam pelo link): o `.git` se resolve (caminho real dos dois l… |
| `codigo-*` | 1 | 0 | 1 | — | — | Código do projeto: libera para qualquer papel. |
| `commit-*` | 1 | 0 | 1 | — | `AGENTE-NAO-EMENDA-ENVIADO` | AGENTE-NAO-EMENDA-ENVIADO: depois do `--` é caminho, não opção; o commit comum de commit enviado passa. |
| `e-*` | 1 | 1 | 0 | — | — | Achado E: a marca é uma por raiz (`projeto-<hash do caminho real>`, no common dir do clone). A sessão está na worktree `wt`, que perdeu o `.… |
| `expandir-*` | 1 | 1 | 0 | — | — | Custo (0.44.0): `$CLAUDE_PROJECT_DIR` no caminho gravado ainda se expande (o atalho de `expandir` só pula o caminho sem `$`): o dev gravando… |
| `extglob-*` | 1 | 1 | 0 | `R-VERIFY` | `HOOK-COMENTARIO-SHLEX` | HOOK-COMENTARIO-SHLEX volta 3, A5: no extglob o # não abre comentário; o push depois é lido. |
| `ferramenta-*` | 1 | 0 | 1 | — | — | Read não é decidido por este hook. |
| `g-*` | 1 | 1 | 0 | — | — | Achado G: a raiz da sessão (`{tmp}/wt`) foi movida (`git worktree move`); a sessão segue na pasta nova, sem `.forge/versao`, e o push falha… |
| `kanban-*` | 1 | 0 | 1 | — | `KANBAN` | KANBAN.md é do quadro, não é protegido. |
| `mit-*` | 1 | 1 | 0 | `R-CONFORMIDADE` | — | Mitigação da segurança (L): com `.forge/versao` presente, a linha que cita a marca da sessão (`.git/forge`) é recusada, seja qual for o prog… |
| `politica-*` | 1 | 1 | 0 | — | — | A política do hook é protegida como as regras. |
| `r10-*` | 1 | 0 | 1 | — | — | R10 do review: `perl -Mstrict` só lê o arquivo protegido; o `i` de `-Mstrict` não liga a edição no lugar e a linha passa (sem falso positivo… |
| `r7-*` | 1 | 1 | 0 | — | — | R7: pasta sem Forge cujo `.git` não se resolve (`commondir` num clone principal): a falha fechada da raiz da sessão fica, e a mensagem diz o… |
| `rm-*` | 1 | 1 | 0 | `R-CONFORMIDADE` | — | A marca da sessão (`.git/forge/projeto-<hash da raiz>`) é protegida contra escrita e remoção pelos agentes. |
| `so-*` | 1 | 0 | 1 | — | — | Sessão de projeto (externo) com plugin.json forjado na raiz: os caminhos so_forge não valem (C-5 c). |
| `sparse-*` | 1 | 1 | 0 | — | — | A marca da sessão fica dentro do `.git/`: `git sparse-checkout set src` apaga o `.forge/versao` da árvore de trabalho e não a marca, então a… |

## `doutor`

| Prefixo | Fixtures | Recusa | Libera | Regras | Cartões | O que prova (exemplo) |
| --- | ---: | ---: | ---: | --- | --- | --- |
| `abrir-*` | 1 | 0 | 1 | — | — | Projeto com problemas (sem settings, sem sandbox): ao abrir, o SessionStart é silencioso e só grava o cache (ADR 0003). |
| `erro-*` | 1 | 0 | 1 | — | — | Config corrompida: o doutor sai 0, não avisa e registra em erros.log. |
| `sem-*` | 1 | 0 | 1 | — | — | Projeto sem .forge/versao: o doutor não age (nem cria .forge/run). |

## `meta`

| Prefixo | Fixtures | Recusa | Libera | Regras | Cartões | O que prova (exemplo) |
| --- | ---: | ---: | ---: | --- | --- | --- |
| `v0454-*` | 12 | 8 | 4 | — | `V0454-CAMINHOS-EXTRA` | V0454-CAMINHOS-EXTRA: a pasta de `caminhos_extra` entra no fim do PATH da checagem |
| `mensagem-*` | 2 | 0 | 2 | — | — | S6: a última mensagem ao dono é medida (caracteres e jargão do modo iniciante) e o Stop passa. |
| `sem-*` | 2 | 0 | 2 | — | — | Projeto sem .forge/versao: o hook não age. |
| `ainda-*` | 1 | 1 | 0 | — | — | S4: checagem que falha bloqueia o Stop dizendo qual. |
| `desarmado-*` | 1 | 0 | 1 | — | — | S4: objetivo desarmado não bloqueia o Stop. |
| `entregue-*` | 1 | 0 | 1 | — | — | S4: todas as checagens com rc 0: entregue e provado, desarma. |
| `erro-*` | 1 | 0 | 1 | — | — | meta.json corrompido: libera e registra em erros.log. |
| `espera-*` | 1 | 0 | 1 | — | — | S4: pedido em Aguardando o dono: o Stop passa e o objetivo fica armado. |
| `falha-*` | 1 | 1 | 0 | — | — | S4: "ainda não" com outra falha recomeça a conta e bloqueia. |
| `pausado-*` | 1 | 0 | 1 | — | — | S4: objetivo pausado não bloqueia o Stop. |
| `pergunta-*` | 1 | 0 | 1 | — | — | S4: última linha do dono no pedido é PERGUNTA AO DONO: espera o dono. |
| `quarta-*` | 1 | 0 | 1 | — | — | S4: o quarto "ainda não" igual seguido pausa sozinho e o Stop passa. |

## `parecer`

| Prefixo | Fixtures | Recusa | Libera | Regras | Cartões | O que prova (exemplo) |
| --- | ---: | ---: | ---: | --- | --- | --- |
| `pasta-*` | 140 | 123 | 17 | `R-REVIEW` | `HK3-PARECER` | HK3-PARECER, PR A, volta 1: a pasta do git é a do bash e a do git; a partir de a integração, barra. |
| `texto-*` | 73 | 58 | 15 | `R-REVIEW` | `HK3-PARECER`, `PARECER-HOOK-DICA-EDIT` | HK3-PARECER, PR B (E2): o eval continua recusado, até com texto inofensivo. |
| `forge-*` | 61 | 50 | 11 | `R-REVIEW`, `R-CONTRIB` | `FURO-HOOK-A`, `HOOK-COMENTARIO-SHLEX`, `CRASE-ASPA-HOOK`, `FD1` e mais 1 | A1 do review: git commit -m com heredoc que cita merge e tem apóstrofo no corpo. |
| `pr-*` | 45 | 31 | 14 | `R-REVIEW`, `R-CONTRIB`, `R-SEGURANCA`, `R-QA` e mais 1 | `K-164`, `PR` | K-164: base escolhida pelo autor fora de develop, homolog e main (aqui uma branch copiada da develop): não afrouxa; fica o modo estrito e o… |
| `v0454-*` | 30 | 26 | 4 | `R-REVIEW` | `V0454-GH-ALIAS-PARECER` | V0454-GH-ALIAS-PARECER: alias `gh m` = api de merge com `$1` |
| `fila27-*` | 22 | 14 | 8 | `R-REVIEW` | `FILA-27` | FILA-27 A1 (S7b): no clone do Forge com .forge/versao, o manifesto vence o hooks_desligados; gh pr merge sem parecer barra. |
| `heredoc-*` | 17 | 10 | 7 | `R-REVIEW` | `HOOK-PARECER-HEREDOC-FALSO-POSITIVO` | HOOK-PARECER-HEREDOC-FALSO-POSITIVO (0.43.2): echo literal depois do corpo. |
| `continuacao-*` | 16 | 15 | 1 | `R-REVIEW` | `HOOK-CONTINUACAO-LINHA` | HOOK-CONTINUACAO-LINHA (A4 do review, volta 4): $'…' e \ + quebra de linha na mesma linha; as formas compostas até o ponto fixo recusam. |
| `pn7-*` | 13 | 3 | 10 | `R-REVIEW` | `PN7-DOLAR-INTERROG` | PN7-DOLAR-INTERROG (H1-1, ADR 0011): continua barrado. |
| `atualiza-*` | 6 | 3 | 3 | `R-REVIEW` | `PARECER-BARRA-FETCH` | PARECER-BARRA-FETCH, o que segue barrado: na develop, fetch e merge --ff-only da branch com review reprovado é a entrada na integração. |
| `merge-*` | 6 | 3 | 3 | — | `FURO-HOOK-A` | git merge --abort não mescla nada. |
| `api-*` | 5 | 3 | 2 | `R-CONTRIB` | — | gh api só lendo o PR: libera. |
| `checkout-*` | 5 | 2 | 3 | — | — | `git checkout develop --` sem caminho é troca de branch; o merge na develop sem parecer bloqueia. |
| `v0456-*` | 5 | 3 | 2 | `R-REVIEW` | — | gh pr merge depois de `env VAR=1` (as palavras gh pr merge fora do início do comando) com o git lento de 4 s: segue com o prazo longo de 8 s… |
| `v0455-*` | 4 | 3 | 1 | `R-REVIEW` | — | gh pr create (sem gh pr merge na linha) com o mesmo git lento de 4 s: segue o prazo de 3 s e recusa por prazo. |
| `gh-*` | 3 | 3 | 0 | `R-CONTRIB`, `R-REVIEW` | `GH-MERGE-ADMIN` | GH-MERGE-ADMIN: o -R do Forge entre pr e o subcomando também é o repositório do Forge |
| `hook-*` | 3 | 3 | 0 | `R-REVIEW` | `HOOK-N4` | HOOK-N4: o merge escondido em "$(true ")"; L)" na integração, sem parecer, rodava sem leitura |
| `pull-*` | 2 | 1 | 1 | — | — | git pull origin feature/x na develop (ref remota conhecida): bloqueia como merge. |
| `switch-*` | 2 | 1 | 1 | — | — | cd, switch para a develop e merge com -C: a branch atual acompanha a linha; bloqueia. |
| `comando-*` | 1 | 0 | 1 | — | — | Comando comum: sai sem chamar git. |
| `erro-*` | 1 | 1 | 0 | — | — | Config corrompida e gh pr create (marcador crítico): falha fechado e registra em erros.log (ADR 0009, seção 7). |
| `guarda-*` | 1 | 0 | 1 | — | — | FORGE_GUARDA_ABERTA=1 abre a guarda do parecer em erro interno. |
| `sem-*` | 1 | 0 | 1 | — | — | Projeto sem .forge/versao: o hook não age. |
| `subst-*` | 1 | 1 | 0 | — | — | git merge sem parecer dentro de substituição de processo <(...): também bloqueia. |

## `pesado`

| Prefixo | Fixtures | Recusa | Libera | Regras | Cartões | O que prova (exemplo) |
| --- | ---: | ---: | ---: | --- | --- | --- |
| `sem-*` | 3 | 0 | 3 | — | — | Projeto sem .forge/versao: o hook não age. |
| `mutacao-*` | 2 | 1 | 1 | `R-TETO` | `TM-25` | TM-25: Stryker de outra sessão ativo; o teste de banco da lista da stack espera (um por vez). |
| `outra-*` | 2 | 2 | 0 | — | `HOOK-COMENTARIO-SHLEX` | HOOK-COMENTARIO-SHLEX (ADR 0013): a linha que a leitura fiel não lê é lida pela antiga: o pesado continua visto. |
| `pos-*` | 2 | 0 | 2 | — | — | PostToolUse de outra chamada não solta a trava alheia. |
| `aguardando-*` | 1 | 1 | 0 | — | — | Orkastery 5: cartão da branch em "Aguardando o dono" recusa na hora, sem esperar na fila. |
| `citar-*` | 1 | 0 | 1 | — | — | Comando que só cita a ferramenta (argumento, pacote) não é pesado nem disputa a trava. |
| `comando-*` | 1 | 0 | 1 | — | — | Comando fora da lista de pesados: não lê nem grava estado. |
| `erro-*` | 1 | 0 | 1 | — | — | Trava corrompida: libera e registra em erros.log. |
| `expirado-*` | 1 | 0 | 1 | — | — | Trava com mais de 2 h (expiracao_horas) expira. |
| `falha-*` | 1 | 0 | 1 | — | — | PostToolUseFailure do mesmo comando também solta a trava. |
| `lancador-*` | 1 | 1 | 0 | `R-TETO` | — | — |
| `lista-*` | 1 | 1 | 0 | `R-TETO` | — | pesados do .forge/config.json substituem os padrões. |
| `livre-*` | 1 | 0 | 1 | — | — | Nenhuma tarefa pesada ativa: libera e grava a trava. |
| `mesma-*` | 1 | 0 | 1 | — | — | Trava da própria sessão (permissão negada, Post que não chegou): não bloqueia e é renovada. |
| `outro-*` | 1 | 1 | 0 | — | — | Mesma sessão, mas a trava é de um subagente (agent_id): bloqueia. |
| `permissao-*` | 1 | 0 | 1 | — | — | PermissionDenied (modo auto) do mesmo comando solta a trava. |
| `pid-*` | 1 | 0 | 1 | — | — | Trava de sessão encerrada (PID morto) não vale. |
| `teste-*` | 1 | 1 | 0 | `R-TETO` | `TM-25` | TM-25: teste de banco de outra sessão ativo; o Stryker da lista da stack espera (um por vez). |
| `teto-*` | 1 | 1 | 0 | — | — | Orkastery 5: ocupado, espera na fila até o teto e recusa dizendo a posição. |

## `quadro`

| Prefixo | Fixtures | Recusa | Libera | Regras | Cartões | O que prova (exemplo) |
| --- | ---: | ---: | ---: | --- | --- | --- |
| `caminho-*` | 1 | 1 | 0 | — | — | file_path relativo ao cwd também é conferido. |
| `erro-*` | 1 | 0 | 1 | — | — | Config corrompida: libera e registra em erros.log. |
| `kanban-*` | 1 | 0 | 1 | — | `KANBAN` | KANBAN.md em subpasta não é o quadro do projeto. |
| `outro-*` | 1 | 0 | 1 | — | — | Edição de outro arquivo: nada a fazer. |
| `quadro-*` | 1 | 0 | 1 | — | — | Quadro no formato e dentro do WIP. |
| `sem-*` | 1 | 0 | 1 | — | — | Projeto sem .forge/versao: o hook não age. |
| `wip-*` | 1 | 1 | 0 | `R-WIP` | — | Coluna QA com 3 cartões e WIP 2: avisa o agente (saída 2). |

## `vigia`

| Prefixo | Fixtures | Recusa | Libera | Regras | Cartões | O que prova (exemplo) |
| --- | ---: | ---: | ---: | --- | --- | --- |
| `entrada-*` | 12 | 0 | 12 | — | — | Só 2 itens de lista: silêncio. |
| `d-*` | 4 | 0 | 4 | — | — | Achado D, cadeia 3: o `mv .git .g` é barrado pelo conformidade (o `.git` fica); sem o `.forge/versao`, o vigia avisa no Stop. |
| `bloqueio-*` | 3 | 0 | 3 | — | — | Bloqueio de outra sessão não vale nesta. |
| `contorno-*` | 3 | 0 | 3 | — | — | O bloqueio fica no estado: a nova tentativa em outro turno (outro Stop) também é contorno. |
| `medida-*` | 3 | 0 | 3 | — | `AV3` | AV3 etapa 1: o SubagentStop grava em comandos.jsonl a forma de cada comando crítico com o papel (do agent_type no subagente; da sessão sem a… |
| `em-*` | 2 | 0 | 2 | — | — | Arquivo em vigor muda depois do SessionStart: aviso ao usuário e registro. |
| `f-*` | 2 | 0 | 2 | — | — | Achado F: o `commondir` escrito fora dos hooks no clone principal, com o `.forge/versao` fora: a marca não se consulta, falha fechado e o vi… |
| `leitura-*` | 2 | 0 | 2 | — | — | Push em main barrado (R-MAIN) e depois `git log main`: leitura, não contorno. |
| `sem-*` | 2 | 0 | 2 | — | — | Projeto sem .forge/versao: o hook não age (nem cria .forge/run). |
| `compactacao-*` | 1 | 0 | 1 | — | — | Compactação (SessionStart `compact`) no meio da tarefa não zera a base: a mudança de antes dela ainda é avisada. |
| `corrigir-*` | 1 | 0 | 1 | — | — | `git push --no-verify` barrado (R-VERIFY) e depois `git push` sem a flag: é a correção, não contorno. |
| `erro-*` | 1 | 0 | 1 | — | — | Config corrompida: o vigia sai 0, não avisa e registra em erros.log. |
| `erros-*` | 1 | 0 | 1 | — | — | Linha nova em erros.log (hook com erro interno) vira violação; linha anterior ao SessionStart e do próprio vigia não. |
| `g-*` | 1 | 0 | 1 | — | — | Achado G: a raiz da sessão movida (`git worktree move`): o vigia avisa no Stop, no estado da pasta nova, e não recria a raiz antiga. |
| `git-*` | 1 | 0 | 1 | — | — | Arquivo em vigor já sujo no git antes do SessionStart (o hash não vê): o git status avisa. |
| `inicio-*` | 1 | 0 | 1 | — | — | SessionStart é a entrada principal: grava o ponto de partida e não escreve nada (o stdout dele vira contexto do modelo). |
| `merge-*` | 1 | 0 | 1 | — | — | `git merge x` barrado na main (R-MAIN) e depois `git merge main`: trazer a main para a branch de trabalho não é contorno. |
| `nova-*` | 1 | 0 | 1 | — | — | A nova tentativa também foi barrada: o controle funcionou, não há contorno. |
| `r9-*` | 1 | 0 | 1 | — | — | R9: a raiz da sessão sumiu e a pasta corrente não é cópia de trabalho: o vigia avisa no Stop e não cria `.forge/run/` nessa pasta. |
| `repete-*` | 1 | 0 | 1 | — | — | A mesma violação já avisada não reaparece no turno seguinte (sem saída). |
| `repetir-*` | 1 | 0 | 1 | — | — | Write barrado em docs/reviews e outro Write no mesmo caminho aceito (agora liberado): mesma ferramenta, não é contorno. |
| `settings-*` | 1 | 0 | 1 | — | — | .claude/settings.local.json é do próprio Claude Code (aprovações do usuário): não é violação. |
| `sparse-*` | 1 | 0 | 1 | — | — | Depois de `git sparse-checkout set src` o `.forge/versao` some da árvore e a marca (no `.git/`) fica: o vigia avisa no Stop. |
| `subagente-*` | 1 | 0 | 1 | — | — | SubagentStop lê a transcrição do subagente (agent_transcript_path) desde o início. |
| `versao-*` | 1 | 0 | 1 | — | — | Depois de um `git rm .forge/versao` o vigia não fica mudo: o SessionStart marcou a sessão e o Stop avisa o usuário. |
