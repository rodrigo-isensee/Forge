---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0475-copia-pasta
commit: efe73e1755211bf8d2db0dbbf1fb4e1fc2f808af
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v0475-copia-pasta (E3.56, cobre E3.44)

Escopo: `git diff 2fa505d7..efe73e17` (`bin/forge-copia`, `docs/propostas/copia-pasta-settings.patch`, `tests/test_forge_copia.py`, `tests/mutantes/v0475-copia-pasta.json`, duas linhas de skill, fragmento de changelog). Análise estática, mais sondas locais em diretório temporário com `HOME` próprio. Origem: num projeto, os agentes rodaram fora da proteção do terminal; o patch libera `~/.forge-contrib` no sandbox de escrita do modelo de projeto, para a cópia de trabalho nascer dentro dele.

## Gatilhos
Gatilhos: configuração do sandbox do modelo de projeto (`allowWrite`, ADR 0009), ferramenta que cria cópia git a partir de entrada do agente (`R-SEGURANCA`).

## Achados
- A1 (recomendado) docs/propostas/copia-pasta-settings.patch:9 · O patch libera também `/workspaces/.forge-contrib` em todo projeto, mas `bin/forge-copia:14` só aceita `~/.forge-contrib` e o README (:52) só cita esta: área de escrita sem uso. Tirar do patch ou documentar o motivo.
- A2 (recomendado) docs/propostas/copia-pasta-settings.patch:9 · `allowWrite` na pasta inteira dá à sessão de um projeto escrita nos clones de outros projetos e em `~/.forge-contrib/wt/*` (exclusivo do Forge, `R-CONTRIB`). Estreitar para `~/.forge-contrib/<projeto>` e `<projeto>-wt` no `forge-init`.

## Sondas

## Detalhe dos achados
- **A1, baixa.** Evidência: `docs/propostas/copia-pasta-settings.patch:9`; `bin/forge-copia:14-18` (raiz só `~/.forge-contrib`). O `settings.json` do próprio Forge já traz as duas entradas, então o patch só repete no modelo. Caminho de ataque: nenhum direto; é privilégio a mais (uma sessão com injeção de instrução ganha um lugar gravável fora do projeto que nenhuma ferramenta do Forge usa). Correção mínima: remover `/workspaces/.forge-contrib` do patch, ou, se ele cobre ambiente com `HOME` diferente, fazer o `forge-copia` aceitar a mesma lista e dizer isso no README. Esforço: P. Dono: `devops-engineer` (o patch é aplicado pelo dono, `.claude/settings*.json` é protegido).
- **A2, baixa.** Evidência: o mesmo `allowWrite`; `skills/contribuir-com-o-forge/SKILL.md:22` reserva `~/.forge-contrib/wt/*` às sessões do Forge, mas nada no sandbox nem no `forge-copia` impõe isso (a sonda S8 abaixo cria em qualquer subpasta). Caminho de ataque: agente de um projeto, sob injeção de instrução vinda de conteúdo do projeto, altera arquivos não commitados numa worktree do Forge ou no clone de outro projeto; o autor dessa cópia pode commitar sem perceber. Mitigado em parte: os pareceres são presos ao SHA e o diff passa por review. Mesmo assim, o patch melhora a postura frente à origem (antes, a escrita fora do projeto levava o agente a sair do sandbox; agora fica dentro dele). Correção mínima: o `forge-init` grava `~/.forge-contrib/<projeto>` e `~/.forge-contrib/<projeto>-wt` no `allowWrite` do projeto, e o `forge-copia` aceita uma raiz por `--raiz` limitada a essas. Esforço: M. Dono: `devops-engineer`.

Conferido, sem achado:
- `..` (`bin/forge-copia:28`) é recusado como componente antes de qualquer resolução, mesmo voltando para dentro; `realpath` (`:31`) resolve links nos pais e no último componente, inclusive link pendente (S1); `commonpath` (`:34`) barra o prefixo parecido (`.forge-contrib-outro`, teste próprio); a própria pasta e o destino ocupado são recusados (`:32`, `:36`).
- Nome que começa com `-`: `branch`, `base` e `origem` recusados (`:53-55`); o destino com `-` cai no erro do analisador de argumentos (saída 2) e, relativo (`./-x`), vai depois de `--` (`:62`, `:65`), então nunca vira opção do git. `check-ref-format --branch` (`:56`) barra `a..b` e `@{-1}`. A base no `switch` (`:65`) não tem `--`, mas já passou pela recusa de `-`.
- `--origem` aceita qualquer URL: o transporte `ext::` fica barrado pela política padrão do git (git 2.43 no ambiente, `protocol.ext.allow` sem valor); clone local não copia ganchos nem configuração do repositório de origem. Informativo.
- O `forge-copia` confia no `HOME` e no próprio processo; é guia de uso, não fronteira: a fronteira é o sandbox (`allowWrite`). Corrida entre a conferência (`:26-38`) e o `git` só serve a quem já escreve na pasta. Informativo; vale uma frase no docstring dizendo que o limite real é o sandbox.
- Sem segredo, dependência nova, workflow nem rede no diff. A rotina usa só a biblioteca padrão e `git` com lista de argumentos (sem shell).

Provas: `python3 -I tests/test_forge_copia.py` no head efe73e17: 13 testes, OK. Sondas passivas (HOME temporário): S1 link pendente para fora → saída 2 "fora de"; destino `-x` → 2; `./-x` relativo → criado dentro; `~` literal → criado dentro; `--origem=-uabc` → 2; `--branch '@{-1}'` → 2; base `x y` → 1; S8 `~/.forge-contrib` como link para outra pasta → aceito dentro do alvo real (esperado). Suíte: a branch não tem execução de CI nem PR (`gh run list --branch melhoria/v0475-copia-pasta` vazio); a suíte inteira fica para o CI do PR, portão do merge.

## Riscos aceitos e ferramentas
Nenhum risco aceito. `gitleaks`, `semgrep`, `zizmor`: não rodados (o diff não toca segredo, dependência nem workflow; o CI os executa). Lacuna: o patch é só proposta; os projetos já criados só recebem o `allowWrite` pela migração (ADR 0005), então a origem do incidente segue aberta neles até o dono aplicar e migrar.
