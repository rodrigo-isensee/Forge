---
tipo: revisao-seguranca
contrato: 1
pedido: conf-so-leitura-fix
branch: melhoria/conf-so-leitura-fix
commit: f3d68cb9933219014b82279d730c2dd525393eed
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-20
---
# Review de segurança: conf-so-leitura-fix

## Gatilhos
Controles do Forge (`R-SEGURANCA`): `hooks/conformidade.json` e `tests/hooks/` (fixtures). A mudança endurece, não afrouxa.

## Achados

## Detalhe dos achados
Sem bloqueantes. Conferido sobre `f3d68cb` (diff contra `0f480c8`: política, 3 fixtures, `tests/test_forge.py` +2 -1, fragmento):

1. Causa e correção. Em `hooks/conformidade.py:1654` e `:1670`, papel fora de `escrita_permitida` sai do hook na sessão do Forge antes de `Guarda.bash`. Com `"conferente": ["/dev/null"]` em `hooks/conformidade.json:15-16`, `com_lista` fica verdadeiro e a lista de só leitura passa a valer. A lista tem de ser não vazia (`conformidade.py:1528`); `/dev/null` já consta em `so_leitura.saidas`.
2. Sonda direta do hook (cópia em `$TMPDIR`, `agent_type: forge:conferente`, sessão do Forge, pasta corrente fora de projeto). Recusados (saída 2): `python3 -m unittest`, `sh`, `bash -c`, `env python3`, `cat x > y`. Liberados (0): `git log -1`, `git status`, `git diff`, `cat`, `grep -rn`, `ls | wc -l`, `forge-check delta`, `gh pr view`, `test -f`, `cd <dir> && git diff`. Nada do que o conferente precisa ler deixou de passar.
3. Outros papéis não mudam. `com_lista` depende só do papel (`conformidade.py:1654`); tech-lead, qa, segurança, devops, jarvis e `developer` seguem saindo com 0 na mesma sonda (comportamento da base). `aq` mantém a lista. O conferente só tem `Read, Grep, Glob, Bash` (`agents/conferente.md:4`), sem ferramenta de arquivo que a lista `/dev/null` pudesse afetar.
4. Mutação (cópia em `$TMPDIR`, só as 3 fixtures `conferente-sessao-forge-*` pelo harness `test_fixtures`): com a correção as 3 passam; removida a linha do conferente, `python3-bloqueia` e `redirecionamento-bloqueia` falham (`0 != 2`) e `git-log-libera` segue passando (guarda de regressão). `PluginDeDesenvolvimento` (`tests/test_forge.py`, que compara `escrita_permitida` exato) passa.
5. Efeito colateral aceito: o papel com lista falha fechado em erro interno do hook (`conformidade.py:1679`), certo para papel só de leitura.

Recomendações não bloqueantes, já fora do escopo do pedido: R1 do estudo (`grep` com `--filter`, `--pager`, `--config`, cartão GREP-OPCOES-EXEC); a alternativa estrutural (aplicar `so_leitura` em `principal` mesmo fora de `escrita_permitida`) para um papel futuro em `so_leitura.papeis`, em pedido próprio.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Análise estática e hook com entrada simulada; suíte completa não rodada (`R-TETO`, só as classes tocadas). Ferramentas `gitleaks`, `osv-scanner`, `semgrep`, `zizmor` e `actionlint` ausentes do PATH: lacuna registrada, sem relevância para este diff (sem segredo, dependência nem workflow).
