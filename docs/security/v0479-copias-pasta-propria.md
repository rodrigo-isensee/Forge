---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-copias-pasta-propria
commit: 48a6e19b88bac450f1b749c1351d6396db35632e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478 (E78.3, cópias do projeto em pasta própria)

Lido `git diff 5e3ca873..48a6e19b`: `bin/forge-copia` (detecção do projeto, `raiz()`, `.gitignore` da pasta), `tests/test_forge_copia.py` (classe `Projeto`), `skills/trabalho-em-paralelo/ritmo-e-corte.md:43`, o fragmento do changelog e o índice. Sem mudança em `templates/projeto/.claude/settings.json`, `.claude/`, `hooks/` nem `.githooks/`.

## Gatilhos
Gatilhos: remoção de arquivos (limpeza de cópias), limite de escrita do sandbox, detecção de contexto Forge/projeto.

## Conferências
- **A limpeza não apaga fora da pasta certa.** `bin/forge-copia:177-183` segue exigindo destino resolvido estritamente dentro de `raiz()` e igual à raiz git da cópia. No projeto, `raiz()` sempre termina em `<projeto>/.forge/wt` (`bin/forge-copia:45-47`), com o projeto vindo de `realpath` do `--show-toplevel` (`:37`); o projeto e a própria `.forge/wt` são recusados (S4), e uma cópia em `~/.forge-contrib` é recusada de dentro do projeto (S3).
- **Trabalho fora da origem.** `sujeira` e `fim_do_item` (`bin/forge-copia:140-172`) sem mudança: mudança, stash, commit fora dos remotos ou worktree ligada mantêm a cópia, e a conferência repete logo antes do `rmtree`. Origem local sem PR legível no `gh` recusa (fail-closed).
- **Projeto não engana a detecção para chegar a `~/.forge-contrib`.** A detecção só estreita: modo projeto nunca devolve a pasta do home. Um `.forge/wt` versionado como link para `~/.forge-contrib/wt` é recusado, porque a base não é resolvida e o destino é (S1). Um projeto com `.claude-plugin/` falso cai no modo Forge (S5), o mesmo comportamento de antes desta branch, e o sandbox do projeto não libera `~/.forge-contrib` (`templates/projeto/.claude/settings.json`, sem `allowWrite` para ela); a limpeza ali continua presa às conferências de fim do item.
- **Sem escrita nova no sandbox.** Nenhuma configuração de sandbox muda; a cópia do projeto fica dentro da pasta dele, já gravável. `.git/worktrees` continua fechado (a ajuda manda usar clone no projeto, `bin/forge-copia:3`), `.claude/` intocado. Os hooks leem o controle pela raiz da sessão (`CLAUDE_PROJECT_DIR`, `hooks/_comum.py:147-149`), não pelo `.forge/config.json` do clone, então o controle do clone em `.forge/wt/<item>` não vale para a sessão.
- Teste novo: `python3 -m unittest tests.test_forge_copia.Projeto`, 7 testes OK no head. CI: nenhum run nem PR da branch até este parecer; a suíte inteira fica para o CI do PR (portão do merge).

## Achados
- A1 (recomendado) bin/forge-copia:58 · `os.path.exists` + `open(..., "w")` segue link: um `.forge/wt/.gitignore` versionado como link solto faz o forge-copia criar `*\n` no alvo do link, fora de `.forge/wt` (S2). Use `os.open` com `O_CREAT|O_EXCL|O_NOFOLLOW` e ignore `FileExistsError`.
- A2 (recomendado) tests/test_forge_copia.py:523 · faltam na classe `Projeto` os casos de abuso das sondas S1 (`.forge/wt` como link para `~/.forge-contrib/wt`, recusa rc 2 e nada criado lá) e S2 (`.gitignore` link solto, nada escrito no alvo).

## Sondas

## Detalhe dos achados
Sondas executadas (pasta temporária da sessão, `HOME` falso, sem rede): S1 `.forge/wt` link para `~/.forge-contrib/wt`, `clone <proj>/.forge/wt/x` → rc 2 "o destino fica fora de <proj>/.forge/wt", nada criado no home. S2 `.forge/wt/.gitignore` link solto para `alvo_fora`, `clone` → rc 0 e `alvo_fora` criado com `*`. S3 de dentro do projeto, `limpar ~/.forge-contrib/wt/f` → rc 2, a pasta fica. S4 `limpar <proj>/.forge/wt` → rc 2. S5 projeto com `.claude-plugin/` falso, `clone <proj>/.forge/wt/x` → rc 2 (modo Forge, destino fora do home).

- **A1.** Evidência `bin/forge-copia:56-60`, sonda S2. Caminho: quem tem commit no projeto (PR mesclado) versiona `.forge/wt/.gitignore` como link para um caminho inexistente; o próximo `forge-copia clone` no projeto cria esse arquivo com `*\n`. Conteúdo fixo, arquivo só criado (nunca sobrescreve um que exista), modo sem execução e escrita limitada ao sandbox do projeto (que nega o controle do Forge): severidade baixa. Correção mínima: `os.open(arq, os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW, 0o644)` com `FileExistsError` ignorado (o `O_EXCL` também recusa link solto). Esforço P. Dono: autor da branch (`bin/forge-copia`).
- **A2.** Evidência: classe `Projeto` em `tests/test_forge_copia.py:523-597` não cobre link em `.forge/wt` nem no `.gitignore`. Caminho: regressão que resolva `raiz()` com `realpath` passaria a aceitar a pasta do home por link sem teste vermelho. Severidade baixa. Correção mínima: dois testes, S1 (rc 2, `~/.forge-contrib/wt` vazio) e S2 (rc 0 ou 2, alvo do link não criado). Esforço P. Dono: `qa-engineer`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas de varredura de segredo, SAST e dependências ausentes do PATH nesta estação (lacuna registrada; a mudança não traz dependência nem segredo, conferido na leitura do diff).
