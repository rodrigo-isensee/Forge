---
tipo: review
contrato: 1
pedido: agentes-devops-seguranca
branch: melhoria/agentes-devops-seguranca
commit: 1ea1ace
parecer: reprovado
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
