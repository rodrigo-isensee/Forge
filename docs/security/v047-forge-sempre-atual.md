---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v047-forge-sempre-atual
commit: 008d66c31e331e3bd150cbb487bec5cdcf521c49
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v0474 (E3.90, revalidação da E1.59 por delta)

Delta lido (`forge-check parecer delta`): `b89aa7ed..008d66c3`, no domínio `bin/forge-check`, `bin/forge-testes`, `docs/adr/README.md`, `hooks/conformidade.py` e `tests/test_hooks.py`. Tudo o que o delta mostra nesses arquivos veio da `develop` pelos merges `28e50dbf` e `008d66c3` (H1 `tamanho_do_pr`, H3/H8 `portao_na_branch`, `autorizacao` da ADR 0018, CF1 `$@`/`$*` e `declare -n` no `conformidade`, `aviso` do `agentes` no `test_hooks`), já revisado nos PRs de origem (#629, #634, #636, #639, #644). Conferido: a mudança própria da branch contra a `develop` nesses cinco arquivos é linha a linha a de `b89aa7ed` contra a base dela; a única diferença é a resolução de merge em `bin/forge-testes` (`RODAM_OS_HOOKS` mantém o `test_estado_ilegivel` da `develop`), que só muda a lista de testes. `bin/forge_sempre_atual.py`, trampolins, `doutor`, `forge-upgrade`, `voltar-versao`, `scripts/` e o oráculo sem mudança desde `b89aa7ed`. Já lido: a rodada de `b89aa7ed` (no git, `701541d9`).

## Gatilhos
Gatilhos: execução de código como o dono fora do sandbox (atalho e postStart), cadeia de suprimentos (troca do plugin pela tag), hook (`conformidade`), escrita fora do projeto.

## Achados
- A4 (recomendado) bin/forge_sempre_atual.py:615 · a origem é conferida pelo nome da tag e o `marketplace add`/`plugin update` buscam a tag de novo: quem move a `v*` entre a conferência e a busca instala commit fora da main. Guardar o sha conferido e exigir o mesmo no catálogo e no `gitCommitSha` instalado.
- A5 (recomendado) hooks/conformidade.py:2589 · o bloqueio de tag não cobre `push.followTags` no `.git/config` com tag por `mktag`/`update-ref`, nem `gh release create/edit/delete`, `gh api .../releases` e `createRelease`; a sessão do Forge fora de projeto não é vigiada (S4-S6 da rodada anterior).
- A6 (recomendado) bin/forge_sempre_atual.py:527 · uma `v*` acima da publicada e fora da main trava a atualização de todas as máquinas (`falhou:origem-da-tag` a cada abertura) até alguém apagá-la; o alvo pode ser a maior tag que está na main.
- A7 (recomendado) docs/adr/0017-forge-sempre-atual.md:50 · "o hook barra todo envio de tag" não confere com o código (A5); ajustar o texto para não prometer o que o hook não cobre.

## Sondas

## Detalhe dos achados
**Estado.** A1 e A2 (bloqueantes da E1.52): corrigidos em `b89aa7ed`, código inalterado no delta. A3: corrigido. A4, A5, A6 e A7: abertos, mesmo texto e mesmo código (`tag_na_main`, `calcular_alvo`, `git_tag` e `git_tags_no_envio` idênticos no head); continuam recomendados, sem critério novo. Detalhe, caminho de ataque e correção mínima: parecer de `b89aa7ed` no git.

**Interação nova no `conformidade` (merge).** A CF1 da `develop` (`SO_VARIAVEL` com `$@`/`$*`, `atribui_como_argumento`) e o bloqueio de tag da branch tocam funções distintas (`valores_da_variavel` × `Guarda.git_tag`/`git_tags_no_envio`); a CF1 só deixa mais palavras opacas (falha fechada). Rodado no head: `tests.test_hooks.Hooks.test_fixtures_do_v0474_tag` OK (as 21 fixtures `tagv-*`).

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Suíte: sem PR e sem CI desta branch (`gh run list` vazio); a suíte inteira fica com o CI do PR. Rodei: fixtures de tag OK; `tests.test_oraculo_sempre_atual` com 39 falhas e 1 erro, o mesmo quadro das rodadas anteriores (`adiado:duvida:proc`: o sandbox roda com `--unshare-pid` e o `/proc` mostra só os processos dele), não conclusivo aqui e sem mudança de código ou de teste no delta. Ferramentas: `gitleaks`, `osv-scanner`, Semgrep, `zizmor`, `actionlint` e `shellcheck` ausentes do PATH (lacuna; nada instalado). Nenhum segredo no delta (revisão manual).
