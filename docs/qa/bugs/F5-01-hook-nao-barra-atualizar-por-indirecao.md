# F5-01 - o hook não barra `forge atualizar` escondido atrás de indireção do shell, e a trava de terminal se contorna com pty
- Severidade: média
- Responsável sugerido: forge:tech-lead (hooks `conformidade`) ou o agente que mantém `bin/forge_versoes.py`
- Ambiente: melhoria/primeiro-uso-f5 @ e532702; `claude` falso, HOME e git temporários

## Passos para reproduzir
1. Num projeto com `forge-init` e um Forge publicado com tag mais nova, monte o evento PreToolUse do `hooks/conformidade.py` com `tool_input.command` igual a cada um destes e veja a saída 0 (liberado):
   - `$(which forge) atualizar`
   - `f=forge; $f atualizar`
   - `` `which forge` voltar-versao ``
   - `bash <<< "forge atualizar"`
   - `python3 -c "import pty;pty.spawn(['forge','atualizar'])"`
2. Rode, no projeto: `printf 's\n' | python3 -c "import pty;pty.spawn(['python3','bin/forge-atualizar'])"`.

## Resultado esperado
Um agente não consegue rodar `forge atualizar` nem `forge voltar-versao` (`R-CONFORMIDADE`; a trava `tem_terminal()` deveria ser a segunda camada).

## Resultado obtido
O hook libera as cinco formas do passo 1. O passo 2 passa na trava de terminal (o pty dá um tty ao filho), a resposta `s` vem do pipe, e a atualização completa roda: o plugin é trocado (`marketplace remove/add/update` no `claude` falso) e a branch `forge/upgrade-9.9.0` é criada, sem pessoa alguma no terminal. Formas diretas (`forge atualizar`, `bash -c`, `env`, `sh -c`, `cd x && forge atualizar`, caminho absoluto, `script -qc`, `python3 bin/forge-atualizar`) são barradas.

## Evidência
Saída 0 do hook nos cinco casos; no passo 2, chamadas registradas pelo `claude` falso: `marketplace remove forge --scope user`, `marketplace add <repo>#v9.9.0 --scope user`, `plugin update forge@forge --scope user`, e branch `forge/upgrade-9.9.0` criada. Nada se perde (é recuperável por `forge voltar-versao`), por isso média e não alta.

## Sugestão
Segunda camada nos dois scripts: recusar quando o ambiente indicar sessão de agente (por exemplo a variável que o Claude Code define nos processos do Bash) em vez de confiar só em `isatty`; e/ou o hook barrar expansões (`$(`, crases, `$var` antes de `atualizar`) quando a palavra seguinte for `atualizar`/`voltar-versao`.
