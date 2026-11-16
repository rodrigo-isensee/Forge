---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-ambiente-sobrevive
commit: 8050cf500fdfb14247d993f3198ea84a9f11a1fe
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047-ambiente-sobrevive

Code review da classe C (E2.135) no head 584b2239, AMBIENTE-SOBREVIVE-RECRIACAO (E2.54), por delta das voltas E2.108 e E2.128. O revisor não participou da entrega. Revalidado no head e3dfc4cb (E2.205), com o `pedido:` trocado para `v047` (a integração não enxergava o nome da branch). Revalidado de novo no head 8050cf50 (E2.427), depois do merge da origin/develop.

Delta lido: `forge-check parecer delta docs/reviews/v047-ambiente-sobrevive.md`, intervalo 68072575..584b2239, 12 arquivos no domínio: `.devcontainer/devcontainer.json`, `changelog.d/v047-ambiente-sobrevive.md`, `docs/adr/0003-hooks-deterministicos-e-silenciosos.md`, `hooks/ambiente.py`, `hooks/hooks.json`, `scripts/preparar-estacao.sh`, `templates/projeto/.devcontainer/devcontainer.json`, `templates/projeto/.devcontainer/preparar-ambiente.sh`, `tests/mutantes/v047-ambiente-sobrevive-1.json`, `tests/mutantes/v047-ambiente-sobrevive-2.json`, `tests/test_ambiente_hook.py`, `tests/test_forge.py`.

Delta da revalidação (E2.205): `forge-check parecer delta docs/reviews/v047-ambiente-sobrevive.md`, intervalo 584b2239..e3dfc4cb, "delta: nenhum arquivo do domínio mudou" (só pareceres e merges da própria branch); achados, linhas e ferramentas abaixo seguem válidos.

Delta da revalidação (E2.427): `forge-check parecer delta docs/reviews/v047-ambiente-sobrevive.md`, intervalo e3dfc4cb..8050cf50, sem o que veio da base; 3 arquivos no domínio: `docs/engineering/achados-recorrentes.md` (contagens do parecer anterior e AR-12/AR-14 da develop), `scripts/preparar-estacao.sh` (resolução do conflito: o `garantir_gh` da develop, gh >= 2.47, com os `FORGE_APT_*` e o `chave_confere` desta branch; o `gh` sai da lista do apt e ganha passo próprio) e `tests/test_forge.py` (o gh falso responde `--version` com 2.104.0; a asserção do `TesteEParecerSeparados` acompanha a mensagem com a base, E2.201). Lido sem achado novo: a chave sem a digital segue falhando fechada antes do apt; o `feitos=(); faltas=()` depois do passo do gh não perde resumo (o modo completo não os lê depois).

## Achados
- A4 (recomendado) tests/test_forge.py:1960 · M14: agora são 531 linhas de código e teste contadas (hooks 67, scripts 94, tests 370). O corpo do PR precisa de `teto: excedido, 531 linhas, <motivo>` (a ordem do dono juntou o preparo, a segurança do postStart e o hook de abertura).
- A5 (recomendado) hooks/ambiente.py:40 · AR-1: guardas sem mutante, apontadas pela --cobertura: o filtro `startswith('falta: ')` e o `returncode == 1` (decidem o que entra no contexto, item 3 da emenda da ADR 0003), e o `not comando.is_file()` em :33. Declare um mutante por linha na próxima mudança do hook.
- A6 (recomendado) tests/test_ambiente_hook.py:58 · AR-4: o hook roda com `{**os.environ, ...}` e herda o ambiente de quem chama (CI, sessão); use `ambiente_limpo()`, como em `tests/test_forge.py`. O `-s -E` sem `-I` está certo: espelha o hooks.json, e o `-I` tiraria do caminho a pasta do `_comum`.
- A7 (recomendado) docs/adr/0003-hooks-deterministicos-e-silenciosos.md:55 · R-DECISAO: a emenda do SessionStart do ambiente não traz critério de reversão, e a emenda anterior (:53) traz. Sugestão: reverter se o hook passar do prazo ou falar com o ambiente em ordem numa sessão real.

## Parecer
Aprovado no head 8050cf50: o merge da develop não muda o comportamento revisado e mantém o da develop (gh >= 2.47). A4 a A7 seguem recomendados; o M14 continua em 531 linhas contra a develop c6a5932c.

Achados anteriores: **A1 resolvido.** O novo hook SessionStart `hooks/ambiente.py` (registrado em `hooks/hooks.json`) roda o `--verificar` da cópia do plugin, nunca do work tree, e põe no contexto as linhas `falta:` com o recado ao Jarvis para a 1ª mensagem; o núcleo do Jarvis fica intacto. Há testes de comportamento para o Forge, o projeto, o ambiente em ordem (silêncio), fora do container, o evento errado, o projeto sem devcontainer e o script forjado no work tree. O adendo da ADR 0003 declara a exceção ao item 1. **A2 resolvido.** O postStart deixou de ler `refs/remotes/origin/main`: faz um clone raso novo da main com a URL do `.git/config` (sonda S1 abaixo: não gravável pelo agente) e, no Forge, só roda o script que traz a guarda `FORGE_PREPARO_ESSENCIAL`. O `test_poststart_roda_so_a_main_do_remoto_nunca_o_ref_local_forjado` forja o ref e a main local e prova que só o script do remoto roda. Sai também o `remoteEnv` com o GH_TOKEN (A2 da segurança). **A3 resolvido.** As specs `-1` (M1–M13) e `-2` (M14–M25) têm até 13 mutantes por arquivo, cada um com teste de comportamento do ramo de falha; o que sobrou está no A5. **A4 mantido** como recomendado, com a contagem nova.

Conferido sem achado: nos dois scripts, a impressão digital da chave do apt do gh falha fechada e não instala nada (teste com digital errada); `FORGE_APT_*` só redirecionam caminhos nos testes; o `; true` mantém o container de pé, inclusive sem o script na main (teste); o prazo de 7 s fica abaixo do timeout de 10 s; as mensagens `falta:` estão atualizadas nos dois scripts e nos testes; o changelog bate com o código. PA-7 (achados-recorrentes): AR-1 e AR-4 voltam aqui (A5 e A6); as contagens de AR-1 e AR-4 sobem no `achados-recorrentes.md` neste commit (E2.205). AR-12 conferido: as 25 specs batem com o head (todas se aplicaram). AR-5: o hook segue o padrão `-s -E` dos demais hooks.

Ferramentas, citadas e não refeitas (rodadas neste clone no head db1c3166, que só soma o parecer de devops a 584b2239): `bin/forge-mutante tests/mutantes/v047-ambiente-sobrevive-1.json` rc=0, M1–M13 morreram; `-2.json` rc=0, M14–M25 morreram (o M23 por erro do teste sob o mutante); `bin/forge-mutante --cobertura --base cb45a962` com `sem mutante` em hooks/ambiente.py:21, 22, 33, 40 e 55, e os arquivos shell e JSON `não coberto`; `shellcheck` nos dois scripts rc=0; `tests.test_ambiente_hook` e `tests.test_forge.PrepararEstacao`, 30 testes OK. A suíte completa fica com o CI do PR.


Rodado no head 8050cf50 (E2.427): `bin/forge-mutante` em `v047-sessao-automatica.json` (S1–S3, G1–G3, F1–F4, W1–W4), `v047-ambiente-sobrevive-1.json` (M1–M13) e `-2.json` (M14–M25), rc=0, os 39 morreram (M23 por erro do teste sob o mutante), então as specs batem com a resolução do conflito (AR-12); `shellcheck scripts/preparar-estacao.sh` rc=0; `python3 -m unittest tests.test_sessao_automatica tests.test_ambiente_hook tests.test_forge.PrepararEstacao tests.test_forge.TesteEParecerSeparados`, 46 testes OK. PA-7: nenhum AR volta neste delta; `achados-recorrentes.md` sem mudança.

## Sondas
- S1 · test -w /workspaces/Forge/.git/config (Bash do agente, sandbox ativo) · espera: não gravável · obtido: não gravável
