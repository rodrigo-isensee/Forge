#!/usr/bin/env bash
# Teste de ponta a ponta (sem custo de IA): instala o Forge num projeto vazio como os projetos reais fazem
# (marketplace + plugin em escopo de projeto), confere o time e as skills carregados e roda o inicializador.
# Uso: tests/e2e-instalacao.sh   (na raiz do Forge; exige o Claude Code CLI no PATH)
set -euo pipefail
raiz="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# Um hook do git (ex.: pre-push numa worktree) exporta GIT_DIR e afins; sem limpar, o git abaixo
# escreveria no repositório real em vez do temporário.
while IFS= read -r var; do unset "$var"; done < <(compgen -e | grep '^GIT_' || true)
export GIT_CONFIG_NOSYSTEM=1
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
export HOME="$tmp/home"; mkdir -p "$HOME"   # isola a configuração do Claude Code deste teste
projeto="$tmp/projeto"; mkdir -p "$projeto"; cd "$projeto"
git init -q -b trabalho

falha() { echo "e2e-instalacao: FALHOU - $*" >&2; exit 1; }

claude plugin marketplace add "$raiz" --scope project >/dev/null || falha "marketplace add"
claude plugin install forge@forge --scope project >/dev/null || falha "plugin install"
claude plugin list 2>&1 | grep -q 'forge@forge' || falha "forge@forge não aparece em 'claude plugin list'"

detalhes="$(claude plugin details forge@forge 2>&1)" || falha "plugin details"
for agente in jarvis tech-lead software-architect ux-designer node-backend react-frontend qa-engineer agile-coach; do
  grep -q "$agente" <<<"$detalhes" || falha "agente $agente não carregado"
done
for skill in engineering-practices software-architecture ux-design node-backend react-frontend qa-testing kanban-scrum cyber-security iniciar-projeto; do
  grep -q "$skill" <<<"$detalhes" || falha "skill $skill não carregada"
done

bash "$raiz/bin/forge-init" --nome E2E --pronto "make pronto" . >/dev/null || falha "forge-init"
for f in CLAUDE.md KANBAN.md .claude/settings.json .githooks/pre-push docs/kanban/historico.md docs/pedidos/README.md; do
  [ -f "$f" ] || falha "forge-init não criou $f"
done
grep -q '"agent": "forge:jarvis"' .claude/settings.json || falha "agente principal não é forge:jarvis"
[ "$(git config core.hooksPath)" = ".githooks" ] || falha "hook não ativado"
echo "e2e-instalacao: ok (plugin instalado, 8 agentes, 9 skills, projeto inicializado)"
