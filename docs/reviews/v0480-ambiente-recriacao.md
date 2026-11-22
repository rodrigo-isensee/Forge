---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-ambiente-recriacao
commit: 09457540dde8f8b4d47c47d32cc6d57e9b883b10
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0478 (E119.3, AMBIENTE-SOBREVIVE-RECRIACAO: Claude Code atual no preparo do container)

Base 38c37de9, head 09457540 (E119.1, 2 commits). Revisão completa única, sem PR aberto (sem CI ainda).

## O que foi conferido
- Escopo (E119.1): o preparo do Forge (`scripts/preparar-estacao.sh --container`) e o do modelo (`templates/projeto/.devcontainer/preparar-ambiente.sh`) instalam o Claude Code em `~/.local/bin` pelo instalador oficial, baixado para arquivo e só então rodado, com `timeout 300` e stdin fechado; idempotente (`claude_ok`); `--verificar` diz a falta sem alterar nada; falha vira `falta:` e não barra o container. Nem mais, nem menos.
- Tamanho (H1): cerca de 60 linhas de código nos dois scripts, um comportamento.
- Testes: `tests/test_ambiente_recriacao.py` exercita os dois scripts por subprocesso com ambiente limpo (sem `GIT_`, `GH_`, `XDG_`, `FORGE_`), curl falso, sem rede; ramos de falha (download falho, `--verificar` sem binário, segunda rodada sem novo download) cobertos por comportamento. Ajustes de fixture em `tests/test_forge.py` e `tests/test_ambiente_hook.py` coerentes com a falta nova.
- Rodados aqui: `python3 -m unittest tests.test_ambiente_recriacao` (7 OK, 1,1 s); `tests.test_ambiente_hook tests.test_forge.PrepararEstacao` (36 OK, 8,6 s). `shellcheck` não existe neste container: fica com o CI do PR. Mutantes declarados (9, `tests/mutantes/v0480-ambiente-recriacao.json`) e a rodada deles são do QA (não é pedido de controle: `scripts/` e `templates/`).
- Segurança (instalador de claude.ai sem sha256 fixo, rodado como root no postStart): decisão do `security-engineer` (E119.2, `R-SEGURANCA`), não refeita aqui.
- Neutralidade (`R-NEUTRO`) e custo (`R-CUSTO`): nada de projeto; instalador gratuito; testes sem rede. Changelog em fragmento; peso do módulo novo em `tests/pesos-d4.json`.
- Commits: Conventional Commits em português, mensagens claras.

## Achados
- A1 (recomendado) scripts/preparar-estacao.sh:194 · guarda do --simular sem teste: o mutante `true || return 0` sobrevive a test_ambiente_recriacao e a test_container_simular_nao_altera_nada (o --simular passaria a escrever ~/.bashrc); falta assert de .bashrc ausente no --simular e o mutante na spec.
- A2 (recomendado) scripts/preparar-estacao.sh:195 · grep '.local/bin' aceita qualquer menção (comentário, PATH no fim): .bashrc só com `# ver ~/.local/bin/README` deixa o export fora (reproduzido no modelo, linha 107). Sugestão: grep -qF da linha exata gravada.
- A3 (recomendado) scripts/preparar-estacao.sh:192 · claude_ok só aceita ~/.local/bin/claude: um Claude Code atual instalado por outro caminho (npm global) vira falta permanente no --verificar e no SessionStart e ganha segunda instalação; mesmo em templates/projeto/.devcontainer/preparar-ambiente.sh:38. Documentar a escolha.
- A4 (recomendado) tests/test_ambiente_recriacao.py:71 · f-string sem campo (`f"-o "`) e o assert aceita `-o ` em qualquer chamada registrada; conferir `-o` na mesma linha do INSTALADOR.

## Sondas

## Parecer
Aprovado. O item faz o que o E119.1 pede, nos dois scripts, com testes de comportamento dos ramos de falha. Os quatro achados são recomendados (nenhum defeito do caminho normal provado): viram cartão depois do merge (`R-REVIEW`). O merge depende ainda da segurança (E119.2), do QA (E119.4) e do CI do PR verde, incluindo o `shellcheck`.
