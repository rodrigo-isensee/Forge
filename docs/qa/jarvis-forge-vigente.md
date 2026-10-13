---
tipo: qa
contrato: 1
pedido: jarvis-forge-vigente
branch: melhoria/jarvis-forge-vigente
commit: 6432242
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-13
---
# QA - jarvis-forge com cópia vigente

Links: ADR 0009 (seção 4), README (seção do jarvis-forge), CHANGELOG `[Não publicado]`, código em `scripts/jarvis-forge`.

## Escopo
Coberto: `scripts/jarvis-forge` (criação da cópia vigente, reuso sem atualização automática, `--atualizar-vigente`, recusa com mudanças locais, `--dev`, argumentos, fluxo tmux, falhas de origem), e a suíte estrutural (`python3 -m unittest discover -s tests`), shellcheck e a catraca contra `origin/develop`.
Não coberto: uso real com o `claude` e o `tmux` reais (proibido nesta rodada; foram usados stubs que só registram argumentos), canal do Telegram, `pgrep` de sessão já aberta, e a interface (o atalho é CLI; não há tela, então acessibilidade e navegação por teclado não se aplicam).

## Ambiente de teste
- Git real; origin local de teste (repositório bare com `develop`); `$HOME` e `XDG_DATA_HOME` temporários, removidos ao fim.
- Stubs de `claude` e `tmux` no PATH, que só gravam os argumentos e o diretório atual.
- Harness: 44 checagens, em `scratchpad` da sessão (não versionado).

## Cenários
| ID | Cenário | Tipo | Prioridade | Automatizado | Resultado |
|---|---|---|---|---|---|
| CT-JF-01 | Primeira execução cria a cópia vigente a partir da origin/develop e passa `--plugin-dir` para ela, rodando em `~/Forge` | Integração (shell) | Alta | sim (harness) | Aprovado (T1.1 a T1.7) |
| CT-JF-02 | Segunda execução não altera a cópia (HEAD, mtimes e tamanhos iguais, sem comando git), mesmo com origin à frente | Integração | Alta | sim (harness) | Aprovado (T2.1 a T2.6) |
| CT-JF-03 | `--atualizar-vigente` leva a cópia à origin/develop e ignora outras branches | Integração | Alta | sim (harness) | Aprovado (T3.1 a T3.5) |
| CT-JF-04 | Arquivo modificado ou não rastreado na cópia faz `--atualizar-vigente` recusar, sem alterar nada | Integração | Alta | sim (harness) | Aprovado (T4.1 a T4.6) |
| CT-JF-05 | Depois de limpar a cópia, a atualização volta a funcionar | Integração | Média | sim (harness) | Aprovado (T4.7) |
| CT-JF-06 | `--dev` usa `--plugin-dir .`, avisa no stderr e não toca a cópia vigente | Integração | Alta | sim (harness) | Aprovado (T5.1 a T5.4) |
| CT-JF-07 | `--dev` combinado com `--atualizar-vigente` é recusado (código 2) | Integração | Média | sim (harness) | Aprovado (T5.5) |
| CT-JF-08 | `--dev` sem cópia vigente não a cria | Integração | Média | sim (harness) | Aprovado (T5.6) |
| CT-JF-09 | Argumento desconhecido (código 2) e `-h` (código 0, citando `--atualizar-vigente`) | Entrada inválida | Baixa | sim (harness) | Aprovado (T6.1, T6.2) |
| CT-JF-10 | Sem flags, abre o tmux (`new-session -A -s jarvis-Forge`); `--dev` é repassado; com `TMUX` definido, não recria a sessão | Integração | Média | sim (harness) | Aprovado (T7.1 a T7.4) |
| CT-JF-11 | Origin inalcançável na criação: código 1, mensagem do script, sem cópia parcial, sem abrir o claude | Falha da origem | Alta | sim (harness) | Aprovado (T8.1 a T8.3; T8.3 repetido com log limpo, por causa de um artefato do harness) |
| CT-JF-12 | `~/Forge` sem remote `origin`: falha sem criar cópia | Falha da origem | Média | sim (harness) | Aprovado com ressalva: falha sem cópia, mas a mensagem é do git, não do script (JFV-03, baixa) |
| CT-JF-13 | Diretório da cópia já existente sem `.git` não é apagado (criação e `--atualizar-vigente`) | Dados / borda | Alta | sim (harness) | Reprovado: o script apaga o diretório e o conteúdo do usuário (JFV-01, crítica) |
| CT-JF-14 | Commit local não publicado na cópia impede `--atualizar-vigente` ou fica preservado | Borda | Média | sim (harness) | Reprovado: o commit some do HEAD sem aviso, rc 0 (JFV-02, média) |
| CT-JF-15 | Suíte unitária (`python3 -m unittest discover -s tests`) | Unitário / estrutural | Alta | sim | Aprovado: 193 testes OK |
| CT-JF-16 | shellcheck em `scripts/jarvis-forge` | Estático | Média | sim | Aprovado: sem avisos |
| CT-JF-17 | Catraca contra `origin/develop` (`python3 tests/catraca.py --base origin/develop`) | Estrutural | Alta | sim | Aprovado: código 0 |
| CT-JF-18 | Acessibilidade e navegação por teclado | Acessibilidade | - | não aplicável | Não se aplica (CLI sem interface) |
| CT-JF-19 | Permissão: quem não é o dono do repositório não deve conseguir alterar a cópia vigente pelo atalho | Permissão | Média | não | Não automatizado nesta rodada; o script só atua em `~/.local/share` do próprio usuário |

## Cobertura de testes existentes
Os testes em `tests/test_forge.py` (classe de cópia vigente, com stubs) cobrem criação, reuso, atualização e recusa com arquivo modificado. Não cobrem: diretório existente sem `.git` (CT-JF-13), commit local não publicado (CT-JF-14) e mensagem sem origin (CT-JF-12). Sugestão ao `node-backend`: incluir esses três casos antes de corrigir os bugs, para que a correção fique travada.

## Dados de teste
Origin local com `develop` (commits c1 a c4) e branch `melhoria/x` com commit próprio (não deve ser puxada). Nenhuma credencial, nenhum acesso à rede, nenhum `claude` ou `tmux` real.

## Resultado da execução
Data: 2026-10-13. Ambiente: Linux (WSL2), bash, git real, Python da biblioteca padrão.
- Aprovados: 13 cenários (CT-JF-01 a 11, 15 a 17), mais CT-JF-12 com ressalva.
- Reprovados: 2 cenários (CT-JF-13 e CT-JF-14), com 3 bugs: JFV-01 (crítica), JFV-02 (média), JFV-03 (baixa).
- Bugs abertos: crítico 1, alto 0, médio 1, baixo 1.
- Parecer: reprovado. O bug crítico (JFV-01) bloqueia a aprovação; a correção pede a volta ao `node-backend` e novo QA incremental.

Bugs (em `docs/qa/bugs/`, ainda não versionados nesta rodada):
- `JFV-01-diretorio-sem-git-e-apagado.md` (crítica, node-backend)
- `JFV-02-commit-local-descartado-na-atualizacao.md` (média, node-backend)
- `JFV-03-erro-sem-origin-sem-mensagem-do-script.md` (baixa, node-backend)

Observação: a suíte, o shellcheck e a catraca passam no commit b51cd3a, mas os três defeitos estão fora do que os testes atuais cobrem.

## Revalidação (6432242)
Escopo incremental, ambiente igual ao da rodada anterior (git real, origin local, HOME e XDG_DATA_HOME temporários removidos ao fim, stubs de claude e tmux).
- Suíte: 202 testes OK. shellcheck: sem avisos. Catraca contra origin/develop: código 0.
- CT-JF-13 (JFV-01): diretório existente com arquivo do usuário, na criação e no `--atualizar-vigente`: código 1, mensagem do script, arquivo intacto. Aprovado.
- CT-JF-14 (JFV-02): commit local não publicado: `--atualizar-vigente` recusa (código 1) e o commit fica no HEAD. Aprovado.
- CT-JF-12 (JFV-03): sem origin, a mensagem é do script e sugere `--dev`; nenhuma cópia criada. Aprovado.
- Regressão aprovada: criação normal; segunda execução sem tocar na cópia (HEAD igual, arquivo novo da origin não aparece); `--atualizar-vigente` limpo atualiza; `--dev` usa `--plugin-dir .` e não toca a cópia (também sem origin); tmux com sessões `jarvis-Forge` e `jarvis-Forge-dev` por modo; XDG_DATA_HOME com espaço funciona; relativo é recusado (código 2) sem criar nada.
- Bugs abertos: crítico 0, alto 0, médio 0, baixo 0. JFV-01, JFV-02 e JFV-03 resolvidos.
- Parecer: aprovado. Observação: o aviso de sessão tmux aberta apareceu no teste porque o stub do tmux sempre responde que a sessão existe; não é defeito.
