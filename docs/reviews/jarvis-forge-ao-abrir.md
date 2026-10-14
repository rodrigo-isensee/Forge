---
tipo: review
contrato: 1
pedido: jarvis-forge-ao-abrir
branch: melhoria/jarvis-forge-ao-abrir
commit: a5b3e3f
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Parecer de autor: `jarvis-forge` atualiza a cópia vigente e consulta a fonte de harness ao abrir

Escopo: `origin/develop..55f8be6` (1 commit): `scripts/jarvis-forge`, `bin/forge-check` (subcomando `fontes`), `tests/test_forge.py`, ADR 0009 (ajuste), README, `docs/fontes-de-praticas.md` e `CHANGELOG.md`. O autor é o próprio `tech-lead`: parecer de autoria; `bin/forge-check` é protegido, então o PR exige o rótulo `afrouxa-regra` do dono, que é o portão independente.

## O que muda
- Atualização automática só por `fetch` + `merge --ff-only` na cópia vigente, nunca `reset`. Recusa com aviso de uma linha (e abre com a cópia atual) se houver mudança local, commit local, branch diferente da `develop` ou falta de rede. Não atualiza sob sessão tmux já aberta (`FORGE_ABERTURA_FEITA` evita repetir dentro do tmux). `--dev` não atualiza.
- `forge-check fontes` lê `~/.forge-contrib/fontes/fontes.json`, usa `git ls-remote -- <url> HEAD`, compara por prefixo com `commit_revisado`; sem registro, silêncio; sem resposta, saída 3 (o `jarvis-forge` não grava o cache e tenta na abertura seguinte). URL começando com `-` é ignorada. Nome e URL da fonte não entram no repositório (`R-NEUTRO`).

## Verificação
- Testes novos escritos antes e falhando sem a mudança: fast-forward, mudança local, commit local, sem rede, cache diário, `fontes` com versão nova, sem novidade, sem registro e fonte inalcançável. Repositórios bare locais e HOME temporário, sem rede.
- Um teste existente foi ajustado: a segunda abertura agora toca a cópia vigente (só fetch e merge), mas continua sem clone nem reset.
- Suíte completa, `shellcheck scripts/jarvis-forge` e `scripts/validar-plugin.sh` passam.

## Riscos e limites
- `R-CUSTO`: só `git ls-remote` e `git fetch`, sem API paga.
- O cache é por data local; arquivos `fontes-<data>` se acumulam (vazios, um por dia); o script não apaga nada.
- `ls-remote` consulta `HEAD` da fonte, não uma branch fixa: acompanha a branch padrão dela.

## Review independente

Revisor: `forge:tech-lead` (sessão independente da autoria). Escopo: `origin/develop..a5b3e3f` (2 commits), revisado como código de segurança (ADR 0009, seção 4, e `bin/forge-check`, protegido). Parecer: **reprovado** (2 itens bloqueiam).

### Bateria local (checkout `a5b3e3f`)
- `python3 -m unittest discover -s tests`: 319 testes, OK.
- `scripts/validar-plugin.sh`: passou. `shellcheck scripts/jarvis-forge`: sem achados.
- `tests/catraca.py --base <merge-base>` (regras): falha só por `bin/forge-check` (pede o rótulo `afrouxa-regra`, esperado). `--modo pareceres`: OK. `--modo pr-texto` com o corpo do PR: OK.
- Versão e changelog: `plugin.json` sem mudança; linha nova em `## [Não publicado]`: OK.

### Achados
1. **`scripts/jarvis-forge` (`atualizar_ao_abrir`, `rev-list`/`merge --ff-only origin/develop`) · bloqueia.** O nome curto `origin/develop` é ambíguo: o git resolve `refs/tags/origin/develop` antes de `refs/remotes/origin/develop`. Uma tag `origin/develop` publicada na origin apontando para um commit de `melhoria/*` é trazida pelo `fetch` (auto-follow, porque o commit vem com a branch) e o `merge --ff-only` avança a cópia vigente para código não revisado. Reproduzido em repositório local: a cópia vigente passou a ter o conteúdo da branch `melhoria/x`; o aviso `refname 'origin/develop' is ambiguous` some no `2>/dev/null`. O envio de tag não é barrado (`hooks/conformidade.py` libera `git push --tags`; o `pre-push` só barra mover tag existente). Isso quebra a garantia da ADR 0009, seção 4 ("nenhuma branch `melhoria/*` entra em uso"), e agora sem ação do dono, a cada abertura. O mesmo vetor existe, antes deste PR, no `--atualizar-vigente` (`reset --hard origin/develop`). Sugestão: `git -C "$vigente" fetch --quiet --no-tags origin +refs/heads/develop:refs/remotes/origin/develop`; usar `refs/remotes/origin/develop` por extenso no `rev-list`, no `merge --ff-only` e no `reset --hard` do `--atualizar-vigente`; depois do merge, conferir `HEAD == $(git rev-parse refs/remotes/origin/develop)`. Teste novo: tag `origin/develop` na origin apontando para fora da `develop`, e a cópia vigente não pode sair da `develop`.
2. **`bin/forge-check` (`cmd_fontes`, `git ls-remote -- url HEAD`) · bloqueia.** Qualquer URL do registro é aceita. O registro fica em `~/.forge-contrib/fontes/`, que o sandbox dos agentes pode gravar, e o `jarvis-forge` roda o `fontes` fora do sandbox. O `ext::` só está bloqueado pelo padrão do git: com `protocol.ext.allow=always` na configuração do usuário, `git ls-remote -- 'ext::sh -c touch% /caminho' HEAD` executou o comando (reproduzido com `-c protocol.ext.allow=always`). Caminho local, `file://` e `ssh` também passam. Sugestão: aceitar só `https://` com regex estrita (sem espaço nem caracteres de controle) e reforçar no próprio comando: `git -c protocol.allow=never -c protocol.https.allow=always ls-remote -- <url> HEAD`. Os testes passam a cobrir a recusa (`ext::`, `file://`, caminho local, URL com `;`, sem chamar o git) e o caminho feliz com um `git` falso no `PATH`, em vez de repositório bare local.
3. **`bin/forge-check` (`cmd_fontes`, linhas impressas) · recomendado.** `codigo` vem do registro gravável pelos agentes e `topo`, da rede; os dois vão para o terminal do dono sem filtro. Validar `topo` como 40 hexadecimais e `codigo` como `[A-Za-z0-9_-]+` (ou descartar caracteres de controle).
4. **`tests/test_forge.py` · recomendado.** Faltam testes para branch diferente da `develop`, sessão tmux já aberta (não atualiza) e `--dev` (não atualiza), comportamentos prometidos na ADR.
5. **`scripts/jarvis-forge` (`consultar_fontes`) · recomendado.** `XDG_STATE_HOME` relativo não é recusado, ao contrário do `XDG_DATA_HOME`.

### Conferido sem achado
- Só fast-forward na abertura; recusa com mudança local, commit local e fora da `develop`; sem `reset --hard` no caminho novo.
- Não atualiza com a sessão `jarvis-Forge` aberta; `FORGE_ABERTURA_FEITA` evita repetir dentro do tmux.
- Sem rede: `timeout 30` no `fetch`, uma linha de aviso, e a sessão abre.
- `fontes` não grava URL no repositório (`R-NEUTRO`) e usa só `git ls-remote` (`R-CUSTO`); registro malformado (JSON inválido, não-objeto, campos ausentes, URL começando com `-`) é tratado.
- Cache diário: fica em `~/.local/state`, fora da escrita do sandbox. Forjá-lo só esconde o aviso de versão nova da fonte, que não é controle de segurança.
- Teste antigo ajustado (`test_cria_a_copia_vigente_uma_vez_e_nao_toca_depois`): a mudança acompanha o comportamento novo (`fetch` e `merge` passam a ser esperados) e o teste continua barrando `clone`, `reset` e `checkout`. Não perdeu força no que protege.
