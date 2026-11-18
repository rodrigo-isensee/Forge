---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-parecer
commit: 9b075525eaa2a3cadf408e77bafbe5e1817884ab
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478 (guardas do hook `parecer`, E3.22, revalidação)

Volta por delta, volta 3 de 3 do A5. Rodada anterior: `commit b989773a` (E3.17), no git. Delta lido (`forge-check parecer delta`, conteúdo de `014f3e53..9b075525`): no domínio, `hooks/parecer.py` (D1 em `mexidas_na_linha`, `nome_incerto`, `mexe_no_config_do_git`, `linha_mantem_os_remotos`, `remotos_incertos`, a recusa em `pasta_do_gh` e o `gh_na` em `conferir`), `tests/test_hooks_parecer_matriz.py` (o gerador da matriz D1 a D7), `bin/forge-testes` (mapa) e a matriz em `docs/hooks.md`. Fora do domínio, não relido: changelog, `tests/mutantes/*`, `tests/pesos-d4.json`, `tests/test_testes_tocados.py`.

Gatilhos: hook de controle (`hooks/parecer.py`) que guarda o portão de parecer de todos os projetos e do Forge.

## Achados
- A8 (recomendado) hooks/parecer.py:126 · D7, decisão do dono: `PATH` mexido na linha troca o programa que roda com nome de `SO_LEEM_A_COPIA` (`ls`, `cat`) e o `git` do gh; `export PATH="$PWD/b:$PATH"; ls; gh pr ready` dá 0 (S27). Recusar quebra o legítimo do corpus.

## Sondas
- S14 · `command -p . ./env.sh; gh pr ready feature/x` · espera: 2 · obtido: 2 (fechado)
- S15 · `command -- source ./env.sh; gh pr ready feature/x` · espera: 2 · obtido: 2 (fechado)
- S16 · `builtin -- source ./env.sh; gh pr ready feature/x` · espera: 2 · obtido: 2 (fechado)
- S17 · `c=source; $c env.sh; gh pr ready feature/x` · espera: 2 · obtido: 2 (fechado)
- S18 · `env $(cat vars) gh pr ready feature/x` e `... gh pr merge feature/x` · espera: 2 · obtido: 2 (fechado)
- S19 · `GIT_CONFIG_GLOBAL=g.cfg gh pr ready feature/x` e `export GIT_CONFIG_GLOBAL=g.cfg;` · espera: 2 · obtido: 2 (fechado)
- S20 · `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=remote.origin.gh-resolved GIT_CONFIG_VALUE_0=dono/forge gh pr ready feature/x` · espera: 2 · obtido: 2 (fechado)
- S21 · `export GIT_CONFIG_PARAMETERS="'remote.origin.gh-resolved'='dono/forge'"; gh pr ready feature/x` · espera: 2 · obtido: 2 (fechado)
- S22 · `HOME=$PWD/h gh pr ready feature/x` e `export XDG_CONFIG_HOME=$PWD/x;` · espera: 2 · obtido: 2 (fechado)
- S23 · `git remote add upstream git@github.com:dono/forge.git && gh pr ready feature/x` · espera: 2 · obtido: 2 (fechado)
- S24 · `git remote set-url origin git@github.com:dono/forge.git; gh pr ready feature/x` · espera: 2 · obtido: 2 (fechado)
- S25 · `git config remote.origin.gh-resolved dono/forge;` e `git config url.<forge>.insteadOf <outro>;` antes de `gh pr ready feature/x` · espera: 2 · obtido: 2 (fechado)
- S27 · `export PATH="$PWD/b:$PATH"; ls; gh pr ready feature/x` (b/ls roda `git remote add`) · espera: decisão do dono · obtido: 0

## Estado dos achados anteriores
- **A5:** fechado. S14 a S18 dão 2, e as vizinhas fora do gerador também: `command -pv ls;`, `s\ource`, `"sou"rce`, `set -a; for GH_REPO in …; do :; done;`, `set -a; read -r GH_REPO < vars;`.
- **A6:** fechado (D4). S19 a S22 dão 2, e as vizinhas `env GIT_CONFIG_GLOBAL=g.cfg gh`, `set -a; for GIT_CONFIG_GLOBAL in g.cfg; …`.
- **A7:** fechado (D5, lista positiva). S23 a S25 dão 2, e as vizinhas `./ls;`, `$PWD/ls;`, `"$PWD"/ls;`, `{ echo x; } >> .git/config;`, `echo x >&f;`. O `git -c … status;` do corpus da rodada anterior agora recusa, como a matriz declara (D5); aceito: o `-c` não muda os remotos, mas o `git` numa cópia alheia roda o `core.fsmonitor` e os ganchos dela.
- **A1 a A4:** fechados antes; sem delta que os toque.
- Corpus de legítimos, todos 0: `gh pr ready feature/x`, `cd .;`, `export PATH="$HOME/bin:$PATH";` e os oito do gerador com `ready` e `merge`.

## Detalhe dos achados
**A8 (média, recomendado; decisão do dono).** Evidência: `hooks/parecer.py:126` (`SO_LEEM_A_COPIA`) e `hooks/parecer.py:660` (`linha_mantem_os_remotos`) confiam no nome do programa, e o nome é resolvido pelo `PATH` que a própria linha pode mudar. A D7 da matriz cita o `git` que o gh roda; a classe é maior: qualquer programa da lista (`ls`, `cat`, `grep`…) sai do `PATH` e pode ser um script que roda `git remote add` antes do gh (S27). Caminho de ataque: na cópia alheia recusada, o agente grava `b/ls` e prefixa o `PATH`; é evasão deliberada, a mesma classe do limite aceito A2 da 0.45.4 (o hook protege contra engano; o CI e o merge do dono são o portão). As duas saídas, para o dono decidir (`R-DECISAO`): (1) recusar, na cópia alheia sem `-R`, a linha que mexe em `PATH` (prefixo, `export`, `declare`, `read`, `printf -v`, nome por expansão), o que recusa o legítimo `export PATH="$HOME/bin:$PATH"; gh pr ready` do corpus; o contorno é `-R <dono/repo>` ou o gh noutra chamada; (2) limite declarado em `docs/hooks.md` (D7 "limite aceito", com S27 como fixture de 0 documentada) e aceite do usuário em `docs/security/aceites/` com `commit:` igual ao deste parecer, que leva este parecer a `riscos-aceitos`. Com a saída (1), esforço P, dono tech-lead. O resto da matriz (D1 a D6) fecha sem depender desta decisão.

## Riscos aceitos e ferramentas
Nenhum risco aceito gravado; a D7 aguarda o dono. Cenário das sondas: o do gerador (`tests/test_hooks_parecer_matriz.py`, base `incidente-r-copia-alheia-source-gh-repo-ready-bloqueia.json`, mais `vars`, `g.cfg`, `h/.gitconfig`, `x/git/config`, `muda.sh` e a cópia `alheio2`), com o lançador da suíte (`Fixture.montar`, `montar_proc`, `rodar`), por um script local fora do repositório. Testes rodados: `python3 -m unittest tests.test_hooks_parecer_matriz tests.test_hooks_parecer_repo` (OK, 10 testes, 27 s). A suíte inteira roda no CI; este head não tem CI citado no brief ("sem suíte local"). Lacuna: `gitleaks` e `semgrep` não estão no PATH. O delta não traz segredo nem dependência.
