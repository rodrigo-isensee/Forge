---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0475-copia-pasta
commit: a108ef531a7b40d2bcc05082f23a73ef3888aa37
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v0475-copia-pasta (E3.113, revalidação por delta)

Delta lido: `forge-check parecer delta docs/security/v0475-copia-pasta.md`, intervalo `efe73e17..a108ef53`. No domínio: `docs/propostas/copia-pasta-settings.patch` (o `allowWrite` agora é só `~/.forge-contrib`), `skills/contribuir-com-o-forge/SKILL.md:22-23` e `skills/trabalho-em-paralelo/SKILL.md:10-12` (texto encurtado, a cópia passa a sair do `forge-copia`). Fora do domínio: `tests/test_forge_copia.py`. Já lido na rodada anterior (no git, parecer em `efe73e17`): `bin/forge-copia`, sem mudança neste delta.

## Gatilhos
Gatilhos: configuração do sandbox do modelo de projeto (`allowWrite`, ADR 0009), ferramenta que cria cópia git a partir de entrada do agente (`R-SEGURANCA`).

## Achados
- A1 (recomendado) docs/propostas/copia-pasta-settings.patch:8 · Resolvido em a108ef53: o patch tirou `/workspaces/.forge-contrib`; o `allowWrite` agora bate com a raiz do `bin/forge-copia` e com o README (:52).
- A2 (recomendado) docs/propostas/copia-pasta-settings.patch:8 · Aberto, sem mudança: o `allowWrite` na pasta inteira ainda dá à sessão de projeto escrita em `~/.forge-contrib/wt/*` e nos clones de outros projetos; a skill (:22) só orienta. Estreitar no `forge-init` por projeto.

## Sondas

## Detalhe dos achados
- **A1:** `git diff efe73e17..a108ef53 -- docs/propostas/copia-pasta-settings.patch` troca a lista de duas entradas por `["~/.forge-contrib"]`. Fechado.
- **A2, baixa:** mesma análise da rodada anterior (caminho de ataque por injeção de instrução numa sessão de projeto, mitigado pelos pareceres presos ao SHA). O texto novo da skill `contribuir-com-o-forge` mantém a reserva de `~/.forge-contrib/wt/*` às sessões do Forge, mas tirou a frase de que o `forge-copia` recusa destino fora da pasta (`..`, link); é só documentação, a recusa continua no código (`bin/forge-copia:26-38`, inalterado). O `trabalho-em-paralelo` deixou de dizer "em vez de `git worktree add` ou `git clone` soltos"; a orientação positiva ("Cópia: `forge-copia clone` ou `worktree`") cobre o mesmo, sem efeito na fronteira, que é o sandbox. Dono: `devops-engineer`.

Conferido, sem achado: o comando novo de clone na skill (`forge-copia clone ~/.forge-contrib/<projeto> --origem git@github.com:... --branch melhoria/<projeto>-<tema>`) passa pela mesma validação (destino dentro da raiz, nomes sem `-` inicial, `check-ref-format`); o `--origem` é a URL fixa do repositório do Forge. Sem segredo, dependência, workflow nem rede no delta.

Provas: `python3 -I tests/test_forge_copia.py` no head a108ef53: 13 testes, OK. Suíte: a branch não tem execução de CI nem PR (`gh run list --branch melhoria/v0475-copia-pasta` vazio); a suíte inteira fica para o CI do PR, portão do merge.

## Riscos aceitos e ferramentas
Nenhum risco aceito. `gitleaks`, `semgrep`, `zizmor`: não rodados (o delta não toca segredo, dependência nem workflow). Lacuna mantida: o patch é proposta; os projetos já criados só recebem o `allowWrite` pela migração (ADR 0005).
