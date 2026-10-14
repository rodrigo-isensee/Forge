---
tipo: review
contrato: 1
pedido: agentes-devops-seguranca
branch: melhoria/agentes-devops-seguranca
commit: 1f364c1
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
