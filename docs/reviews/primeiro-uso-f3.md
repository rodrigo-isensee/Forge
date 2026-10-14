---
tipo: review
contrato: 1
pedido: primeiro-uso-f3
branch: melhoria/primeiro-uso-f3
commit: a851fda
parecer: aprovado
revisor: forge:tech-lead (autor)
data: 2026-10-13
---
# Parecer de autor: primeiro uso F3 (forge doutor)

- **Mudança:** `bin/forge-doutor` (Python, biblioteca padrão; também `forge doutor` pelo despachante); hook `hooks/doutor.py` (SessionStart e Stop); `forge_doutor()` em `hooks/_comum.py`; chamadas do atalho `jarvis`, do `forge-upgrade` e do `tech-lead` (antes de abrir PR).
- **Conferências:** plugin instalado e versão; `.forge/versao` x plugin; proteção do git (`core.hooksPath`, pasta e permissão de `.githooks`); `gh auth status` (só no modo completo; erro de rede não vira "sem login"); identidade do git; `.claude/settings.json` com `agent: forge:jarvis`; sandbox ligado; `develop` e `homolog`. Tudo bem = silêncio e saída 0; senão, cabeçalho e lista em linguagem simples, saída 1.
- **Conserto:** só o restaurável a partir do modelo do Forge (religar `core.hooksPath` e permissão, recriar `.githooks`, `agent` no settings com cópia em `~/.local/state/forge/backup/`, branch local que existe no GitHub). Exige terminal (teste com pty) e "s"; Enter, "n" e `--rapido` não mexem em nada. Settings ilegível, `gh` e identidade só viram instrução. Teste estático: sem `--force`, `--no-verify`, `reset --hard`, `clean -f` nem `push`.
- **Frequência:** atalho `jarvis` roda o doutor rápido antes do `claude` (custo zero de tokens, pausa com Enter se listou algo); SessionStart examina e grava `.forge/run/doutor` sem escrever no stdout; Stop reexamina só se a data mudou e avisa uma vez por problema com `systemMessage` de uma linha (até 200 caracteres). Cache da data decide; `FORGE_HOJE` só nos testes.
- **Desvio da arquitetura (decisão do review):** o desenho previa a chamada dentro do `vigia`. Foi para um hook separado (`doutor.py`) porque o `vigia` tem fixtures que exigem stdout vazio em SessionStart e a mensagem fixa de violações; mexer nelas alteraria resultados de fixture existente. Mesma política: só avisa, nunca `additionalContext`, e não usa `UserPromptSubmit` (o stdout viraria contexto, ADR 0003).
- **Vermelho antes:** `tests/test_doutor.py` escrito antes do código; sem a mudança falharam 35 testes e 6 deram erro (script e hook inexistentes). **Verde depois:** 398 testes (`python3 -m unittest discover -s tests`), `shellcheck scripts/jarvis bin/forge` e `scripts/validar-plugin.sh` passam; o shellcheck não se aplica a `forge-doutor` (Python). Fixtures com HOME, git e `gh` falsos, sem rede (`R-CUSTO`), sem termo de projeto (`R-NEUTRO`).
- **Atenção ao dono:** toca `hooks/` e `tests/hooks/`, protegidos: o PR precisa do rótulo `afrouxa-regra`. Duas asserções de `tests/test_hooks.py` passaram a aceitar o `doutor` ao lado do `vigia`; nenhuma fixture existente foi alterada. Sem mudança de versão (sobe na release, ADR 0006). Depende do #102 (F2).

Parecer de autor, feito pelo mesmo agente que escreveu a mudança; o review independente fica a cargo do `tech-lead` no PR.
