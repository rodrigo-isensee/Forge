---
tipo: review
contrato: 1
pedido: agentes-devops-seguranca
branch: melhoria/agentes-devops-seguranca
commit: e413cf2
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-14
---
# Parecer de autor: agentes `devops-engineer` e `security-engineer` (ADR 0010, `R-SEGURANCA`)

Escopo: `origin/develop..1f364c1` (2 commits). Parecer do autor: não substitui a review independente que a catraca e o `R-CONTRIB` exigem para o merge.

Afrouxa, por destaque: a `.github/` passa a aceitar o papel `devops` em `melhoria/*` e `hooks/conformidade.json`, `hooks/parecer.py` e `bin/forge-check` mudam (protegidos). Nenhum invariante saiu de `tests/config.json` (entraram 28 padrões e 6 termos de neutralidade). O PR pede o rótulo `afrouxa-regra`.

## Garantido por hook
- `docs/devops/` só do papel `devops`; `docs/security/` só do `seguranca` (bloqueia `dev`, `tech-lead` e `doc`); autoria dos dois pareceres registrada e conferida pelo `forge-check pr` quando há `.forge/run/autoria.jsonl`.
- `devops` e `seguranca` não mesclam, não abrem PR e não instalam pacote; `devops` escreve em `.github/` só no Forge e em `melhoria/*`; `seguranca` não escreve em `.github/`.
- `parecer` e `forge-check pr` exigem o parecer de devops (`.github/`, `Dockerfile*`, `compose*`, `.dockerignore`, `*.tf`, pastas de IaC) e o de segurança (pipeline, contêiner e IaC, arquivo de travas de dependência, `.env*`, migração, controles do Forge, ou `gatilhos_seguranca` marcado no plano técnico). `riscos-aceitos` exige `aceite_usuario: sim`. 12 fixtures de `parecer`, 21 de `conformidade`, 4 testes de `ForgeCheck`.

## Só orientação
- Gatilhos semânticos (autenticação, LGPD, webhook, consulta com entrada) dependem de o arquiteto marcar `gatilhos_seguranca`; sem a marca e sem arquivo gatilho no diff, nada é exigido.
- O papel `seguranca` "só escreve em `docs/security/`" vale como exclusividade da pasta (o hook protege por caminho) e pela lista de `tools` do agente (sem `Edit`); o hook não proíbe o `Write` dele em outros caminhos.
- Qualidade do parecer, limiar das varreduras, uso de ferramenta gratuita e a regra de não instalar nada.
- O `devops` não envia workflow: o token do bot não tem o escopo `workflow`; o dono executa o comando entregue pelo `tech-lead`.

## Checklist
1. Pedido atendido: dois agentes, skill `ci-cd`, `R-SEGURANCA`, modelos, hook, papéis, fixtures, Jarvis e fronteiras, invariantes, ADR 0010, CHANGELOG: sim.
2. Neutralidade: a detecção de lockfile é por padrão de nome (sem gerenciador); termos por linguagem só em `stacks/node-react/`; seis termos novos em `neutralidade_nucleo`.
3. Custo: só ferramentas gratuitas na skill; nada instalado; nenhum workflow novo.
4. Desvio da proposta: o modelo de ameaças fica em `docs/security/ameacas/<demanda>.md` (e não em `docs/ux/`), porque o papel `seguranca` só tem escrita em `docs/security/`.
5. Risco: o diff como detector é grosso (todo arquivo de travas conta como "dependência nova", inclusive bump do Dependabot); mitigado por o parecer ser curto nesses casos. Reavaliar pelo critério de reversão da ADR.
6. Testes: `python3 -m unittest discover -s tests` verde (315); `scripts/validar-plugin.sh` verde.

## Review independente

Revisor: `forge:tech-lead`, sessão separada da do autor. Escopo: `origin/develop..1ea1ace` (3 commits), com as propostas `agente-devops.md` e `agente-seguranca.md` e as decisões do dono. **Parecer: reprovado** (3 itens que bloqueiam, todos de correção pequena; o resto do PR está correto).

### Bateria local (cota do Actions esgotada; todos os checks do PR estão vermelhos por isso)
- `python3 -m unittest discover -s tests`: 315 testes, OK.
- `scripts/validar-plugin.sh`: "Validation passed".
- `tests/catraca.py` com os argumentos do CI, sobre um merge commit sintético (`HEAD^1` = `origin/develop` b5e5d3d), script da base: `regras` sai com 1, só pelo rótulo `afrouxa-regra` que falta (papéis, `.github/`, `bin/forge-check`, `hooks/conformidade.py`, `hooks/parecer.py`), como previsto; `pareceres` sai com 0; `pr-texto` com o corpo do PR sai com 0.
- Versão e changelog (passo do CI para a `develop`): versão 0.12.0 igual à base, 1 linha nova em `[Não publicado]`: OK.

### Conferido sem achado
- Decisões do dono: devops P1 = (a) parecer próprio exigido pelo hook, P2 = (b) sem proteção de infra nos projetos, P3 = (b) release do Forge segue com o `tech-lead`; segurança P1 = A (portão com gatilho, `R-SEGURANCA`), P2 = A (CI do projeto, local só com ferramenta presente), P3 = A (papel no hook neste PR). Modelos (`sonnet`/`opus`), `tools` e skills como nas propostas.
- Papéis novos: `devops` e `seguranca` fora de merge, `gh pr create`, `gh pr merge` e instalação (inclusive a congelada); sem papel próprio cairiam em `dev` e ganhariam `instalar_pacote`, então o papel explícito estreita. Escrita: `docs/devops/` só `devops`, `docs/security/` só `seguranca`, `.github/` do Forge para `devops` só em `melhoria/*`. Fixtures cobrem cada caso.
- Papéis antigos: nenhum afrouxado. O `doc` perde `docs/security/` (aperta); `CRITICO` ganha `docs/devops` e `docs/security` (falha fechada mais larga); a autoria passa a cobrir as duas pastas. O único afrouxamento é o `devops` em `.github/`, declarado e sob rótulo.
- Invariantes: `tests/config.json` só ganha itens (2 agentes obrigatórios, 6 termos de neutralidade, `R-SEGURANCA` no Jarvis, 4 blocos novos); nenhum teste ou fixture removido.
- Neutralidade e `R-CUSTO`: termos por linguagem só em `stacks/node-react/`; lockfile detectado por padrão de nome; só ferramentas gratuitas, nada instalado, nenhum workflow novo.
- Modelo de ameaças em `docs/security/ameacas/<demanda>.md` em vez de `docs/ux/<demanda>/ameacas.md`: aceitável. A proposta dá ao papel escrita exclusiva em `docs/security/`; `documentos()` não desce em subpasta (`glob("*.md")` e `ls-tree` sem `-r`), então o modelo de ameaças não é lido como parecer.
- Jarvis e fronteiras: tabela, triagem e passos 2, 3 e 5 coerentes com `tech-lead` (cita os pareceres, mantém checks exigidos, SemVer e release), arquiteto (topologia e `gatilhos_seguranca`, sem a seção "Segurança") e QA (não declara "seguro").

### Achados
1. `bin/forge-check:54` · **bloqueia** · `[^/]*\.tfvars?` casa `.tfvar`/`.tfvars`, não `.tf`. `infra/main.tf` e `main.tf` na raiz (o layout mais comum de Terraform) não exigem nem devops nem segurança; o parecer de autor, a `R-REVIEW` e o modelo de devops dizem que `*.tf` e "pasta de IaC" estão cobertos. Correção: `[^/]*\.tf(vars)?(\.json)?`, mais fixture `infra/main.tf` em `test_pr_com_pipeline_exige_devops_e_seguranca` (ou num `subTest`).
2. `bin/forge-check:288` · **bloqueia** · `git diff --name-only` detecta renomeação por padrão e lista só o nome novo. Testado: `git mv pnpm-lock.yaml vendor-deps.yaml` com uma linha nova dá `gatilhos() == (False, [])`. O mesmo vale para `Dockerfile` ou pasta de IaC renomeados. Correção: `--no-renames` (o nome antigo aparece como removido e dispara), mais fixture de renomeação.
3. `docs/regras/R-SEGURANCA.md:13`, `bin/forge-check:360` · **bloqueia** · `aceite_usuario: sim` não prova o aceite do usuário. Só o papel `seguranca` escreve em `docs/security/`, e a autoria exige que a versão atual tenha sido gravada por ele. Se o usuário acrescentar a linha, o hash muda e o `forge-check pr` reprova. Na prática, só o próprio agente consegue gravar o aceite, ou seja, o agente aceita o próprio risco. Isso contradiz "gravado pelo usuário" e a ADR 0010, que lista `riscos-aceitos` como verificado. Correção sugerida: o aceite fica num arquivo que nenhum papel grava (como `.forge/config.json`, `quem: []`), por exemplo `.forge/aceites/<pedido>`, com o `commit` aceito, e o `forge-check pr` só aceita `riscos-aceitos` com esse arquivo. Alternativa mínima: até haver aceite verificável, tratar `riscos-aceitos` como não aprovado no `pr` e mover o aceite para "Só orientação" na ADR. Se a escolha for estrutural, decide o arquiteto.
4. Falso positivo do Dependabot · **recomendado** · todo diff de lockfile exige o parecer de segurança (`opus`), inclusive bump de patch, embora a regra fale em "dependência nova ou versão maior". O fluxo não trava, porque a falha é fechada e o parecer pode ser curto, mas cada PR do Dependabot ganha mais um parecer. Proposta: na branch `dependabot/*`, com diff só em lockfile e manifesto, basta o parecer de devops (a triagem já é dele), que marca `bump_maior: sim` quando a versão maior sobe; aí o `forge-check` exige o de segurança. Somado ao agrupamento semanal da skill `ci-cd`, fica um parecer por semana.
5. Manifestos sem lockfile · **recomendado** · `requirements*.txt`, `pyproject.toml`, `package.json` sozinho, `pom.xml`, `*.gradle*`, `gradle.lockfile` e `npm-shrinkwrap.json` não disparam. `requirements.txt` é a forma comum de declarar dependência em Python sem lockfile. Acrescentar esses nomes à lista neutra ou registrar o caso em "Só orientação".
6. Pastas de IaC com outro nome · **recomendado** · `infra/`, `deploy/`, `charts/`, `kubernetes/`, `Containerfile` e `.gitlab-ci.yml` não disparam. O `*.tf` (achado 1) resolve o Terraform; para o resto, acrescentar os nomes comuns ou deixar o projeto declarar a pasta de IaC num arquivo do usuário.
7. Efeito no próprio Forge · **recomendado** · depois do merge, o job `pareceres` (que roda o `forge-check` da base) passa a exigir parecer de segurança em todo PR do Forge que toca `docs/regras/`, `tests/config.json`, `hooks/conformidade.json` ou `tests/catraca.py`, e o de devops em `.github/`. É o efeito pretendido, mas deve constar do `CHANGELOG` e do PR. Até a release chegar à instalação, o hook em uso não protege `docs/security/` e o CI não tem `autoria.jsonl`; registrar essa janela no PR.
8. `bin/forge-check:33` (`LIVRES`) · informativo · um commit posterior que só toca `docs/devops/` ou `docs/security/` não invalida os pareceres, como já acontece com `docs/reviews/`. Aceitável.

Para aprovar: corrigir 1, 2 e 3 com fixture e reenviar. O 4 a 7 podem virar cartão, desde que registrados no PR.

## Re-review independente

Revisor: `forge:tech-lead`, sessão separada da do autor. Escopo: `de4820d..fea66c7` (1 commit), sobre os achados da review independente. **Parecer: reprovado** (2 itens que bloqueiam; os 3 bloqueios anteriores estão corrigidos).

### Bateria local (cota do Actions esgotada)
Checkout do PR em `fea66c7`; merge commit sintético com `HEAD^1` = `origin/develop` (b5e5d3d); script da base.
- `python3 -m unittest discover -s tests`: 328 testes, OK.
- `scripts/validar-plugin.sh`: "Validation passed".
- `catraca.py` modo `regras`: sai com 1, só pelo rótulo `afrouxa-regra` que falta (`hooks/conformidade.json` com papéis e `.github/`, `bin/forge-check`, `hooks/conformidade.py`, `hooks/parecer.py`), como previsto. Modo `pareceres`: sai com 1, só porque este parecer de review está reprovado. Modo `pr-texto` com o corpo do PR: sai com 0.
- Versão e changelog: versão 0.12.0 igual à base, 1 linha nova em `[Não publicado]`: OK.

### Bloqueios anteriores
1. `*.tf`: corrigido. `main.tf`, `infra/main.tf`, `*.tfvars` e `*.tf.json` casam; pastas `infra/` e `deploy/` também; fixtures em `tests/test_forge.py`.
2. Renomeação: corrigido. `--no-renames` em `arquivos_da_entrega`, `commit_vale` e `hooks/parecer.py`; fixtures de lockfile e `Dockerfile` renomeados.
3. Aceite gravado pelo agente: corrigido no mecanismo. `docs/security/aceites/` com `quem: []` antes de `docs/security/`; o `forge-check pr` só aceita `riscos-aceitos` com `docs/security/aceites/<pedido>.md` (`pedido` igual, `aceite: sim`); `aceite_usuario` no parecer deixou de valer. A pasta não é lida como parecer (`documentos()` não desce em subpasta) e um commit que só a toca não invalida o parecer (`LIVRES`). Falta amarrar o aceite ao risco aceito (achado R2 abaixo).

### Conferido
- **Arquivo de aceite, escrita pelos agentes.** Testado com o hook `conformidade` deste commit, papéis `seguranca`, `tech-lead`, `devops` e sessão principal (`jarvis`): barrados (saída 2) Write, Edit, MultiEdit, `>`, `>>`, `tee`, heredoc, `cd docs/security && ... > aceites/x`, `cp`, `mv`, `install -D`, `sed -i`, `python3 -c "open(...,'w')"`, `bash -c '...'` e caminho com `..`. Escapam (saída 0) o caminho por variável (`d=docs/security/aceites; echo x > $d/p1.md`), `git checkout <ref> -- <aceite>` e `git restore --source` (estes dois exigem um commit que já tenha o arquivo) e o encanamento do git (`hash-object` + `update-index --cacheinfo`). É o nível [B] da ADR 0009 para caminhos versionados (o mesmo de `.forge/config.json` no Bash e de `docs/regras/`), e contornar é violar `R-CONFORMIDADE`; Write e Edit são [I]. Diferente dos pareceres, o aceite não tem a segunda linha [D] da autoria. Ver R3.
- **Invariante de `R-SEGURANCA`:** aperta. O texto trocado exigia um campo que o próprio agente grava; o novo exige um arquivo que nenhum papel grava. Em relação à base, o invariante é novo (a regra nasce neste PR) e a catraca não acusa remoção. Não precisa de destaque adicional no título, que já pede o `afrouxa-regra` pelos outros motivos.
- Recomendados anteriores: 5 (manifestos) e 6 (pastas de IaC) atendidos em parte; 7 (efeito no Forge) registrado no `CHANGELOG`.

### Achados
R1. `bin/forge-check:303-315` (`bump_do_dependabot`) · **bloqueia** · a isenção do Dependabot se decide pelo nome da branch e pelas mensagens dos commits, e os dois são do agente. Testado: branch `dependabot/npm/a-1.0.1`, `package.json` com o bump `a` 1.0.0 → 1.0.1 **e um pacote novo** `malicioso`, mensagem "Bump a from 1.0.0 to 1.0.1": `gatilhos() == (True, [])`, sem parecer de segurança; a mesma mudança em `feature/x` exige. "Dependência nova" é gatilho da própria `R-SEGURANCA`. Além disso, com a cabeça solta (CI) a branch é `HEAD` e a isenção nunca vale, ou seja, ela só serve no hook local, onde o Dependabot de verdade não passa, e só beneficia quem forja. Exigir o autor `dependabot[bot]` em todos os commits não resolve sozinho: `git commit --author=...` não é barrado pelo hook. Correção: remover a isenção (o falso positivo era só recomendado; o parecer de segurança curto resolve). Se o dono quiser manter, só com identidade que o agente não forja (o `PR_AUTOR` do evento do GitHub, como já faz o `pr-texto`), nunca por branch, mensagem ou autor do commit; e a `R-SEGURANCA` volta ao texto sem a exceção até lá.
R2. `bin/forge-check:340-351` (`aceite_do_usuario`) · **bloqueia** · o aceite não diz o que foi aceito: vale para qualquer `riscos-aceitos` do pedido, em qualquer commit. Caminho: o usuário aceita o risco A no commit X; o dev muda o código, o `seguranca` grava um parecer novo no commit Y com `riscos-aceitos` para A e B; o `forge-check pr` aprova com o aceite antigo, e o agente volta a aceitar risco que o usuário não viu, que era o bloqueio 3. Correção mínima: o aceite leva `commit:` e só vale se for igual ao `commit` do parecer de segurança (parecer novo pede aceite novo); fixture com aceite de commit antigo reprovando. Atualizar `R-SEGURANCA`, os dois `_modelo.md` e o `security-engineer`.
R3. `templates/projeto/.claude/settings.json` · recomendado · pôr `docs/security/aceites/` no `denyWrite` do sandbox e em `deny Edit(...)` do modelo de projeto: o caminho por variável e o `cp` ofuscado passam a [I] no Bash (o usuário escreve no editor, fora do sandbox). Registrar na ADR 0010 o nível do controle (Write/Edit [I], Bash [B], encanamento do git sem detecção, o diff do PR mostra o arquivo).
R4. `bin/forge-check:53-57` · recomendado · ainda não disparam `charts/`, `kubernetes/`, `Containerfile`, `.gitlab-ci.yml`, `pom.xml`, `*.gradle*`, `gradle.lockfile` e `npm-shrinkwrap.json`. Acrescentar ou registrar em "Só orientação" da `R-SEGURANCA`.
R5. `hooks/conformidade.py:89` (`casa`) · informativo · a comparação diferencia maiúsculas. Em sistema de arquivos que não diferencia (macOS, com `core.ignorecase`), o `seguranca` grava em `docs/security/ACEITES/p1.md` (só `docs/security/` casa), o arquivo cai na pasta `aceites/` que já existe e o `forge-check` o lê como aceite. Baixo; o R3 cobre.

Para aprovar: corrigir R1 e R2 com fixture e reenviar. R3 a R5 podem virar cartão, registrados no PR.

## Terceira review independente

Revisor: `forge:tech-lead`, sessão separada da do autor. Escopo: `f6ee155..e413cf2` (1 commit), sobre R1 e R2 da re-review. **Parecer: aprovado.** Os dois bloqueios foram corrigidos e não há desvio novo que bloqueie. Fica um ajuste de texto recomendado (T1).

### Bateria local (cota do Actions esgotada)
Checkout do PR em `e413cf2`; merge commit sintético com `HEAD^1` = `origin/develop` (b5e5d3d, igual à base do PR); script da base.
- `python3 -m unittest discover -s tests`: 327 testes, OK. Saíram 4 testes da isenção e entraram 3: Dependabot ainda exige o parecer, aceite de commit antigo e aceite sem commit.
- `scripts/validar-plugin.sh`: "Validation passed".
- `catraca.py`:
  - modo `regras`: sai com 1, só pelo rótulo `afrouxa-regra` que falta (`hooks/conformidade.json` com papéis e `.github/`, `bin/forge-check`, `hooks/conformidade.py`, `hooks/parecer.py`), como previsto;
  - modo `pareceres`: rodado depois deste commit; o resultado está no comentário do PR;
  - modo `pr-texto` com o corpo do PR: sai com 0.
- Versão e changelog: versão 0.12.0 igual à base, 28 arquivos da fábrica alterados e 1 linha nova em `[Não publicado]`: OK.

### Bloqueios anteriores
R1. Isenção do Dependabot: **corrigido**. `bump_do_dependabot` e `VERSAO_ATUALIZADA` foram removidos; `gatilhos()` não olha mais branch nem mensagem. Reproduzi o ataque da re-review com a branch `dependabot/npm/a-1.0.1`, o `package.json` com o bump `a` 1.0.0 → 1.0.1 mais o pacote novo `malicioso`, a mensagem "Bump a from 1.0.0 to 1.0.1" e o autor `dependabot[bot]` no commit. O resultado foi `revisao-seguranca: sem parecer (dependência (travas ou manifesto): package.json)`, saída 1, tanto no disco quanto em cabeça solta com `--ref HEAD --base develop` (modo do CI). `R-SEGURANCA` diz "sem isenção". Efeito colateral aceitável: um bump só de dependência deixa de exigir o parecer de devops; a triagem do Dependabot continua com ele, como orientação. A isenção da catraca para `dependabot[bot]` (só troca de SHA de `uses:`, ADR 0008) é outra coisa, vem do evento do GitHub e não mudou.

R2. Aceite preso ao commit: **corrigido**. `aceite_do_usuario` só vale com `pedido` igual, `aceite: sim` e `commit` igual ao `commit` do parecer de segurança, que não pode ser vazio. Testado em repositório descartável, com `riscos-aceitos` no commit X:

| Caso | Resultado |
|---|---|
| aceite `commit: X` | saída 0 |
| aceite de outro commit | saída 1, mensagem `R-SEGURANCA` |
| aceite sem `commit` | saída 1 |
| aceite com `commit:` vazio | saída 1 |
| aceite com `commit` abreviado e parecer com o SHA completo | saída 1 (falha fechada; o usuário copia o valor do parecer) |
| código muda, `seguranca` troca o parecer para o commit Y e mantém o aceite de X | saída 1 (aceite) |
| parecer mantido em X depois de o código mudar | saída 1 (`desatualizado`) |
| aceite novo do usuário com `commit: Y` | a parte de segurança passa |

Ou seja, trocar o `commit:` do parecer depois do aceite invalida o aceite, e não trocar invalida o parecer. O caminho da re-review (aceite antigo cobrindo o parecer novo) fechou. A fixture do hook `parecer` usa `commit: {HEAD}`, e `R-SEGURANCA`, os dois `_modelo.md` e o `security-engineer` dizem o mesmo.

### Achados
T1. `CHANGELOG.md:7` · **recomendado** (texto; corrigir antes do merge, sem nova review de código) · a linha diz "sem isenção para o Dependabot (pasta sem escrita para agentes)" e, adiante, "em `dependabot/*` basta o devops, salvo versão maior". A segunda frase sobrou da versão anterior e contradiz a regra, e o parêntese ficou no lugar errado: ele se refere à pasta de aceites. É o texto que os projetos leem na release. Correção: apagar "em `dependabot/*` basta o devops, salvo versão maior" e mover "(pasta sem escrita para agentes)" para depois de "escrito pelo usuário".

T2. `bin/forge-check:324` · informativo · o aceite prende o commit, não o texto do parecer. Com o código parado em X, o `seguranca` ainda pode reescrever o corpo do parecer (acrescentar um risco B) sem invalidar o aceite. O dano é estreito: o código é o mesmo que o usuário viu, a autoria registra a nova gravação e o diff do PR mostra a mudança. Se quiser fechar, o aceite pode levar o `sha256` do parecer. Vale um cartão, não bloqueia.

Pendências registradas no PR: R3 a R5 da re-review (cartão) e o rótulo `afrouxa-regra`, que só o dono aplica, depois do último push.
