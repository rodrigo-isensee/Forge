---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-sandbox-controle
commit: 0f55b08af4c05c01bd03e02b0deecbbc4550b3db
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-sandbox-controle

Revalidação (E29.19) no head 0f55b08a, por delta: `forge-check parecer delta` de 32c3528e..0f55b08a, sem o que veio da develop (base cf09782). Já lido e aprovado em 32c3528e (rodada anterior no git): o patch de `.claude/settings.json`, o merge 004ce869 e a lista `PODEM_PULAR` 18 -> 20 com o OK do dono (19/11).

## Gatilhos
Gatilhos: configuração do sandbox do Bash (controle de escrita), estado dos hooks de R-TETO, lista fechada de testes que podem pular (afrouxa-regra).

## Resumo
- **Delta lido (no domínio):** `skills/fluxo-do-pedido/SKILL.md:44` e `skills/novo-projeto/SKILL.md:27` enxugam o texto do ritmo; os dois continuam mandando o dono rodar `forge ritmo` (o segundo, "fora do sandbox"). É orientação, não controle: a negação de escrita de `.forge/config.json` vem do `denyWrite`, que não mudou. Sem achado.
- **Fora do domínio (conferido só o que toca controle):** `tests/test_sandbox_controle.py` passa a usar `_comum.Hook`, compara o conteúdo por JSON (o hook grava com `indent=1`, o `forge-init` compacto) e lê `.forge/` em árvore (`rglob`), o que cobre a pasta `run`: a prova de recusa fica igual ou mais larga. `test_maquina.py`, mutantes e `docs/hooks-fixtures.md` não tocam controle.
- **Continua só apertando: sim.** `.claude/settings.json` não mudou no delta (blob 161117cc em 32c3528e e em 0f55b08a), nem `templates/projeto/.claude/settings.json` (blob 6429ee3c nos dois). `hooks/`, `bin/`, `scripts/`, `.githooks/` e `.github/` não aparecem no delta. Nenhuma negação sai, nenhuma regra perde força no CI; o afrouxamento formal da lista fechada segue o já aprovado.
- Teste rodado no head: `tests.test_sandbox_controle` (14, OK, 2 pulados fora do CI por bubblewrap aninhado negado). A prova da recusa dentro do bubblewrap vem do CI verde do PR #713, obrigatório para o merge.
- **A2 fechado; resíduo do A5** (S2, corrida entre `unlink` e `open`) segue no cartão da identidade da pasta.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Suíte inteira: não rodada (brief); CI do PR no head 0f55b08a. Ferramentas: varredor de segredos e linters de workflow fora do PATH (lacuna; o delta não toca workflow nem segredo); bubblewrap aninhado negado aqui (lacuna para sondar dentro do sandbox).
