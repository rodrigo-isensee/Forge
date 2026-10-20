---
tipo: revisao-seguranca
contrato: 1
pedido: fc-aq-hook
branch: melhoria/fc-aq-hook
commit: f058327f0dbed7dcc9e7eec11140eac02e6b358d
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-20
---
# Review de segurança: fc-aq-hook

Escopo: `git diff 50997b72e65d11a7cace0bbc5d4aaf5a55b68d60 f058327f0dbed7dcc9e7eec11140eac02e6b358d` (hooks/conformidade.json, tests/test_hooks.py, tests/test_forge.py, ADR 0009 seção 6, changelog.d/fc-aq-hook.md) e, só leitura, `caminho_barrado` e `fora_da_lista_de_escrita` em hooks/conformidade.py.

## Gatilhos
`R-SEGURANCA`: controles do Forge (hooks/) e ampliação de onde um papel grava. A mudança é só de política (dado): `escrita_permitida.aq` ganha `~/.forge-contrib/docs/propostas/` e `~/.forge-contrib/docs/arquitetura/` (hooks/conformidade.json:15). Nenhuma linha de código do hook mudou.

## Achados

## Detalhe dos achados
Sem achado bloqueante. O que foi conferido, com evidência:

- **Alcance da liberação.** A entrada `~/...` casa só com a forma `home` do caminho, montada a partir de `os.path.realpath` do alvo e do home (hooks/conformidade.py:514-520, 556-571; `resolver` em 576-578). Logo `..`, caminho relativo, caminho absoluto e link simbólico são resolvidos antes da comparação, que é por prefixo com a barra final (`casa`, hooks/conformidade.py:210-212): `docs/propostasX/` não casa. Sondas locais (fixtures do próprio test_hooks, HOME temporário, 16 casos, todos com o resultado esperado): `propostas/../arquitetura/y.md` passa; `propostas/../../../.bashrc`, `propostas/../pedidos/x.md`, `docs/Propostas/`, `.Forge-Contrib/`, link de arquivo e link pendente dentro de `propostas/` apontando para fora, e `~/.forge-contrib` como link para fora do home são recusados (o realpath sai do home e a forma `home` some: falha fechado). Worktree em `~/.forge-contrib/wt/<x>/`: a forma `home` é `~/.forge-contrib/wt/...` e não casa com as entradas novas; `wt/<x>/docs/pedidos/` e `wt/<x>/hooks/` continuam recusados ao aq. Maiúsculas: a comparação é sensível a caixa, então numa FS insensível a caixa a grafia diferente é recusada (só disponibilidade, nunca ampliação).
- **`caminhos` protegidos antes da lista.** Em `caminho_barrado` o laço de `caminhos` roda antes de `fora_da_lista_de_escrita` (hooks/conformidade.py:521-547), sem mudança. Sondas: `propostas/e/.git/config`, `propostas/e/.claude/settings.json` e `propostas/.githooks/pre-push` são barrados por `caminhos` (entradas sem dono valem em qualquer lugar), o que fecha o caminho de plantar um repositório falso com `core.fsmonitor` ou configuração do Claude Code dentro da pasta liberada. `~/.forge-contrib/docs/pedidos/` e `docs/briefs/` seguem do `jarvis`.
- **Nenhum outro papel ganhou escrita.** Só a chave `aq` de `escrita_permitida` mudou; `papeis.aq` segue `forge-dev:aq` (hooks/conformidade.json:12). A lista é restritiva: os demais papéis não têm lista e não foram afetados (sondas com `forge:tech-lead` e `forge:security-engineer` em `~/.forge-contrib/docs/pedidos/` seguem barradas). O aq continua sem Bash nem WebFetch (dev/agents/aq.md:4; conferido por tests/test_forge.py), então não cria link nem corre corrida de TOCTOU por conta própria.
- **Origem do home.** `Path.home()` vem do `HOME` do processo do hook, que o Claude Code define; o aq não tem Bash para alterá-lo.
- **Rede e custo (`R-CUSTO`).** Nenhum arquivo do diff importa ou chama rede; sem dependência nova.
- **Testes.** tests/test_hooks.py:831 cobre as duas pastas, outra pasta do clone, fora do clone, travessia e link de pasta para fora.

Recomendação (informativa, não bloqueante; esforço P; dono `tech-lead`): os casos de maiúsculas, `~/.forge-contrib` como link para fora do home e `.git/` aninhado em `propostas/` não estão no teste novo; acrescentá-los fixa como regressão o que hoje só as sondas desta revisão mostraram.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão estática e sondas locais com o próprio harness de testes (sem rede). gitleaks, osv-scanner, semgrep, zizmor, actionlint e trivy não estão no PATH (lacuna registrada; o diff não toca dependência, workflow nem segredo).
