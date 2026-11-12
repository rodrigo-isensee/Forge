---
id: R-LIMITES
titulo: Limites do time - main, hooks, custo, contribuição e cópias
verificada_por: cada trecho abaixo diz a sua (hooks, permissões, catraca do CI, revisão); invariantes em tests/config.json
---
# R-LIMITES: Limites do time

Propósito: texto único de cinco regras de limite (AV5, 2026-11-10); os outros arquivos citam o ID do trecho. Público: todo o time.

Revisar em: 2027-01-07
Medida: 25 pontos de recusa no código e 0 cópias; a de cada trecho vem nele

## R-MAIN: A main é do usuário

verificada_por: hook `.githooks/pre-push` do Forge e do modelo de projeto (teste HookPrePush); `permissions` do modelo de projeto; invariantes em `tests/config.json`

Medida: 6 pontos de recusa `barrar("R-MAIN"` em `hooks/conformidade.py` mais o `pre-push` (a main protegida não custa nada no caminho feliz)

- A **`main` é do usuário**: nenhum agente faz commit, merge, rebase, reset, cherry-pick ou push nela, nem com `--force` (`R-VERIFY`), no Forge e em cada projeto.
- Toda mudança chega por PR: a `main` do Forge e a de cada projeto só mudam com o PR validado e mesclado pelo usuário. O `tech-lead` abre o PR; mesclar é do usuário.
- O hook `.githooks/pre-push` recusa envio para a `main`.
- Para atualizar a sua branch com a `main`: `git fetch` e `git merge origin/main` **na sua branch**, nunca o contrário.
- Se a branch atual for a `main`, crie uma branch de trabalho antes de mudar qualquer arquivo.
- Só o usuário move um cartão para "Pronto", ao fazer o merge.

## R-VERIFY: Nunca `--no-verify` nem `--force`

verificada_por: `permissions.deny` do modelo de projeto (`templates/projeto/.claude/settings.json`); invariantes em `tests/config.json`

Medida: 9 pontos de recusa `barrar("R-VERIFY"` em `hooks/conformidade.py` (vale por permissão negada, sem custo de processo)

- Nunca `--no-verify` nem `--force`: hooks e checagens não se contornam. O `--no-verify` é proibido em qualquer comando git; `--force` (e `-f`, `--force-with-lease`) em qualquer push, em qualquer branch.
- Não desative nem troque o caminho dos hooks (`core.hooksPath`).
- Hook ou teste falhou: corrija a causa e rode de novo.
- Confirme com o usuário antes de apagar ou reescrever uma branch já enviada. Exceção: a limpeza da branch de trabalho depois do merge (`R-FLUXO`), nunca de `main`, `master`, `develop`, `homolog` nem da integração.

## R-CUSTO: Nada que custe dinheiro sem autorização

verificada_por: revisão (code review do `tech-lead` em toda melhoria do Forge) e a catraca (`custo_permitido` em `tests/catraca.py`)

Medida: 2 pontos de recusa `msg("R-CUSTO"` em `tests/catraca.py`; custo do Forge hoje: 0

- Nada no Forge (CI, testes, scripts, fluxo) consome API paga ou serviço cobrado.
- Nada que custe dinheiro (API paga, serviço cobrado) entra no Forge sem autorização expressa do usuário, dono do Forge. Vale também para melhoria de fábrica vinda de qualquer projeto.

## R-CONTRIB: Contribuição ao Forge: projeto abre PR, nunca mescla

verificada_por: hooks `parecer` e `conformidade`, rulesets e catraca do CI (ADR 0008; vale em qualquer projeto)

Medida: 6 pontos de recusa `barrar("R-CONTRIB"` em `hooks/conformidade.py` e 2 `msg("R-CONTRIB"` em `tests/catraca.py`

- **Quem trabalha em um projeto abre PR para a `develop` do Forge e nunca o mescla**; mescla a sessão do próprio Forge e, na `main`, o usuário.
- **Nenhum portão tem exceção, nem para o dono:** os portões da classe da entrega, os checks e os rótulos valem para todos os autores.
- **O rótulo `afrouxa-regra` é só do dono do Forge.** O agente só o aplica, e só cria ou renomeia um rótulo com esse nome, com a conta dona do repositório e decisão do dono registrada; fora disso, aplicar ou delegar esse rótulo a um agente é **proibido**. O rótulo vale para o conteúdo dos arquivos protegidos que o dono viu: push sem arquivo protegido não o derruba.
- **O `tech-lead` abre e mescla o PR**, não o Jarvis (FILA-22, hook `conformidade`). **Checklist de merge:** na `develop` e na `homolog`, só com todos os checks verdes (`gh pr checks`), pareceres válidos (`forge-check pr`) e, se a catraca pedir, o rótulo do dono; na `main`, nunca (`R-MAIN`).
- **Sessão de outro projeto só propõe.** Pode: criar **uma** branch própria `melhoria/<projeto>-<tema>` a partir da `develop`; abrir o PR. Não pode: commitar ou enviar em branch que não criou; resolver conflitos nem revalidar pareceres de PR alheio; mesclar; fechar ou editar PR alheio; aplicar rótulos; criar issue (dentro do Claude, só `forge sugerir --guardar "<texto>"`). Aberto o PR, avisa o usuário e **para**. O hook `conformidade` barra o resto pela raiz da sessão e falha fechado.
- A sessão de projeto usa só `~/.forge-contrib/<projeto>` e `~/.forge-contrib/<projeto>-wt/*`.

## R-COPIA: Não copiar agentes e skills para o projeto

verificada_por: revisão (a skill `iniciar-projeto` avisa sobre cópias)

Medida: 0 cópias de agentes ou skills em `.claude/` do Forge, conferido por `find . -path '*/.claude/agents'`

- Nunca copie agentes ou skills do Forge para `.claude/agents/` ou `.claude/skills/` do projeto para "consertar rápido": a cópia tem prioridade sobre o plugin e vira uma versão paralela que diverge da fábrica.
- Nunca edite o cache do plugin em `~/.claude/plugins/`.
- Projeto que já tem cópias dos agentes do time: avise o usuário e proponha removê-las, para o projeto usar a fábrica.
- O conserto vai ao Forge por PR (skill `contribuir-com-o-forge`) e chega ao projeto pela atualização do plugin.
