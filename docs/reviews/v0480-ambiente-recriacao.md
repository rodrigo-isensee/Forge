---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-ambiente-recriacao
commit: 93a2123cdbef523aaa7da20aaaf2a7455895d475
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

## Revalidação (E119.7, head 93a2123c)
- Delta lido: `forge-check parecer delta` de 09457540..93a2123c, sem o que veio da develop; no domínio: os dois scripts de preparo, `tests/test_ambiente_recriacao.py`, a spec de mutantes e o fragmento do changelog.
- A1 resolvido: `test_simular_nao_grava_o_bashrc_e_nao_roda_o_instalador` e o mutante M16 (guarda do `--simular`, preparar-estacao.sh:194) morre.
- A2 resolvido: o grep passa a exigir `^[[:space:]]*export PATH=.*\.local/bin` nos dois scripts; comentário não conta (teste novo, M12 e M15 morrem). Resta o export com `.local/bin` no fim do PATH contar como presente: A5.
- A4 resolvido: `assertRegex` confere `--proto =https ... -o .../instalar.sh <INSTALADOR>` na mesma linha registrada.
- Além do pedido no review, vindo da segurança (E119.5): `--proto '=https' --proto-redir '=https'`, limites de tempo e a falta em dois passos em vez de `curl | bash`, com teste do ramo sem curl e mutantes M10, M11, M13 e M14.
- A3 virou cartão (decisão do Jarvis); fica abaixo só como registro.
- Rodados aqui: `python3 -m unittest tests.test_ambiente_recriacao` (10 OK, 3,4 s); `bin/forge-mutante tests/mutantes/v0480-ambiente-recriacao.json` (rev 93a2123cdbef, 16 de 16 morreram). Suíte inteira e `shellcheck`: CI do PR.

## Achados
- A1 (recomendado) scripts/preparar-estacao.sh:194 · guarda do --simular sem teste: o mutante `true || return 0` sobrevive a test_ambiente_recriacao e a test_container_simular_nao_altera_nada (o --simular passaria a escrever ~/.bashrc); falta assert de .bashrc ausente no --simular e o mutante na spec.
- A2 (recomendado) scripts/preparar-estacao.sh:195 · grep '.local/bin' aceita qualquer menção (comentário, PATH no fim): .bashrc só com `# ver ~/.local/bin/README` deixa o export fora (reproduzido no modelo, linha 107). Sugestão: grep -qF da linha exata gravada.
- A3 (recomendado) scripts/preparar-estacao.sh:192 · claude_ok só aceita ~/.local/bin/claude: um Claude Code atual instalado por outro caminho (npm global) vira falta permanente no --verificar e no SessionStart e ganha segunda instalação; mesmo em templates/projeto/.devcontainer/preparar-ambiente.sh:38. Documentar a escolha.
- A4 (recomendado) tests/test_ambiente_recriacao.py:71 · f-string sem campo (`f"-o "`) e o assert aceita `-o ` em qualquer chamada registrada; conferir `-o` na mesma linha do INSTALADOR.
- A5 (recomendado) scripts/preparar-estacao.sh:195 · o grep aceita `export PATH="$PATH:$HOME/.local/bin"` (no fim) como presente; com um claude antigo mais cedo no PATH, o atual não vence. Mesmo em templates/projeto/.devcontainer/preparar-ambiente.sh:107. Vira cartão.

## Parecer
Revalidação no 93a2123c: aprovado. A1, A2 e A4 resolvidos com teste de comportamento e mutante que morre; A3 e A5 são recomendados e viram cartão (`R-REVIEW`).

Parecer anterior (09457540): aprovado. O item faz o que o E119.1 pede, nos dois scripts, com testes de comportamento dos ramos de falha. Os quatro achados são recomendados (nenhum defeito do caminho normal provado): viram cartão depois do merge (`R-REVIEW`). O merge depende ainda da segurança (E119.2), do QA (E119.4) e do CI do PR verde, incluindo o `shellcheck`.
