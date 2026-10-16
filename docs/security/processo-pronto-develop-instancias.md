---
tipo: revisao-seguranca
contrato: 1
pedido: processo-pronto-develop-instancias
branch: melhoria/processo-pronto-develop-instancias
commit: 694edc7a2d1a2d5574a541cfc06f3941b88bec30
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-15
---
# Review de segurança: processo-pronto-develop-instancias (volta 1)

Pedido de origem: `~/.forge-contrib/docs/pedidos/k2-e-processo.md` (E2, etapa E3.2). Diffs revisados: a entrega inteira sobre a develop atual (`930d6bb...694edc7`, 14 arquivos) e o delta da volta (`5f3a6c4..694edc7`, sem `changelog.d/conferente-k1.md`; o resto do delta é a develop mesclada). Parecer anterior: reprovado sobre `61b4382` (M1, M2, M3, B1, B2, I1, I2).

## Gatilhos
`R-SEGURANCA`: a entrega muda regras da fábrica (`R-WIP`, `R-FLUXO`, `R-REVIEW`) e controles do Forge: `bin/forge-check` (checagem de WIP por agente, que o hook `quadro` roda), `hooks/pesado.py` (passa a agir no clone do Forge) e `tests/config.json` (invariantes).

## Resumo
Os sete achados da volta anterior estão resolvidos. Nenhum controle mecânico foi afrouxado. O `forge-check kanban` continua barrando 2 ou mais cartões por agente quando eles não trazem `worktree: <nome>` distinto, e nunca aceita mais de min(3, `teto_maximo`, `teto_agentes`) cartões. O hook `pesado` só ganha alcance no clone do Forge: a lista fixa soma-se à config, `hooks_desligados` não o desliga lá, e a trava fica na cópia principal, compartilhada pelas worktrees. Os invariantes novos protegem as travas, e não só os títulos. Os achados novos são baixos ou informativos: o `forge-check` confia no que o cartão declara, e a detecção da suíte pesada cai com variações do comando. Nenhum deles tem caminho de ataque externo nem bloqueia a entrega.

## Achados da volta anterior
| ID | Situação | Evidência |
|---|---|---|
| M1 | Resolvido | Formato `worktree: <nome>` na Obs. (`docs/regras/R-WIP.md:10`, `agents/jarvis.md:46`). Checagem em `bin/forge-check:179-210` (`teto_instancias`, `instancias_do_agente`), testes `test_instancias_worktrees_distintas_passam`, `test_cartoes_sem_worktree_barram` e `test_instancias_acima_do_teto_barram`. O texto proíbe o contorno pela troca do responsável. Resta uma lacuna mecânica, ver B3. |
| M2 | Resolvido | `docs/regras/R-FLUXO.md:26` e `agents/tech-lead.md:24`: quem resolveu o conflito não decide o alcance; o `forge-check pr` aponta, e quem deu o parecer revalida. Ressalva de redação em I3. |
| M3 | Resolvido | `tests/config.json` (só acréscimos) protege "sem folga no teto, a fila espera", o `R-TETO` inteiro, o limite de 3, o campo `worktree: <nome>`, a revalidação depois do QA (`R-FLUXO`, `tech-lead`), o comando de pronto rodado da raiz (Jarvis e skill) e a regra do review por outra instância. Sugestão complementar em I4. |
| B1 | Resolvido | `docs/regras/R-WIP.md:11` enumera o teto de agentes, as 2 worktrees, as pesadas uma por vez e os extras em trabalho leve. |
| B2 | Resolvido | `docs/regras/R-REVIEW.md:12` e `docs/regras/R-WIP.md:11`, com invariante nos dois. |
| I1 | Resolvido | `skills/engineering-practices/SKILL.md:30`: a devolução não abre rodada de review nem conta como volta de `R-QA`, e o Jarvis a confere pela prova `PQ-n`. |
| I2 | Resolvido | Seções "No Forge e no projeto" (`docs/regras/R-FLUXO.md:24`) e "No Forge e nos projetos" (`agents/tech-lead.md:23`). |

## Achados novos

### B3 (baixa): o `forge-check kanban` aceita o que o cartão declara, sem conferir a worktree nem o agente
- **Evidência:** `bin/forge-check:206` lê o nome da worktree na Obs. e só confere a presença e a distinção. Não compara com `git worktree list`. `bin/forge-check:47` (`ID_RESP`) aceita qualquer `forge:<slug>`, então `forge:tech-lead-b` também passa.
- **Caminho de ataque:** não há atacante externo. Uma única instância põe 3 cartões em "Em andamento" com `worktree: a`, `b` e `c`, sem que essas worktrees existam, e o WIP efetivo dela vai de 1 para 3. Outra opção é registrar o responsável como `forge:tech-lead-2` e sair da contagem do agente base. Nos dois casos, o agente precisa escrever uma informação falsa no quadro, coisa que o texto já proíbe (`R-WIP.md:10`, `R-CONFORMIDADE`). O limite real de agentes simultâneos continua com o hook `agentes`. O impacto é de fluxo (WIP), não de recurso.
- **Correção mínima:** aceitar só os nomes de `git worktree list` (nome da pasta) mais `principal`, e validar o `Responsável` contra os agentes conhecidos (os do plugin e os das stacks). Isso vai em cartão próprio, sem bloquear este PR. Enquanto isso, o `agile-coach` confere, na auditoria do quadro, se os nomes batem com as worktrees.
- **Esforço:** M. **Dono:** `tech-lead`.

### B4 (baixa): a suíte do Forge escapa da trava de pesados com variações do comando
- **Evidência:** `hooks/pesado.py:27` (`PESADOS_DO_FORGE`) e `hooks/pesado.py:65` (`inicios`). Conferi chamando a função `pesado()` direto (sem rodar suíte nenhuma). Ela não reconhece estas variações: `timeout 600 python3 -m unittest discover`, `nice -n 10 python3 ...`, `/usr/bin/python3 -m ...`, `python3.12 -m ...`, `python3 -I -m ...` e `bash -c "..."`. Ela reconhece a forma canônica de `CLAUDE.md` e a forma com `cd ... &&` e atribuições.
- **Caminho de ataque:** não há atacante externo. Um agente com pressa para fugir do bloqueio, ou um brief que use `timeout`, roda a segunda suíte junto com a primeira, e a memória da estação se esgota (o histórico do `R-TETO`). A limitação é a mesma que já existia para os `pesados` dos projetos, agora estendida ao Forge. Fugir de propósito do bloqueio é contorno (`R-CONFORMIDADE`).
- **Correção mínima:** no `inicios`, normalizar a primeira palavra pelo nome base (`/usr/bin/python3` vira `python3`, e `python3.N` vira `python3`), incluir `timeout` entre os lançadores e pular as opções dos lançadores (`nice -n N`, `timeout N`). Isso vai em cartão próprio.
- **Esforço:** P. **Dono:** `tech-lead`.

### I3 (informativa): "invalida os pareceres dos arquivos que ela tocou" é mais estreito que a ferramenta
`docs/regras/R-FLUXO.md:26`. O `commit_vale` (`bin/forge-check:347-366`) invalida **todo** parecer quando qualquer arquivo fora de `LIVRES` diverge, sem olhar o domínio de quem o assinou. A frase seguinte já manda seguir a ferramenta, então não há afrouxamento. Mesmo assim, a leitura "só os pareceres do domínio tocado" pode criar expectativa errada. Sugestão: "invalida os pareceres que o `forge-check pr <pedido>` apontar", com o invariante acompanhando.

### I4 (informativa): os limites do código são protegidos só pelos testes
`INSTANCIAS_MAX = 3` (`bin/forge-check:180`) e `PESADOS_DO_FORGE` (`hooks/pesado.py:27`) ficam presos pelos testes novos, mas os nomes desses testes não estão em `invariantes` (`tests/config.json`, lista `tests/test_forge.py`). Uma edição que suba o número e apague o teste passa verde. Sugestão: invariantes para `INSTANCIAS_MAX = 3` e para os três testes de instância e o `test_suite_do_forge_e_pesada`. Há ainda uma diferença menor: o `R-WIP.md:10` cita só `teto_maximo`, e o código também reduz o limite por `teto_agentes`. O código é mais restrito que o texto, então não há risco.

### Conferências pedidas sem achado
- **`worktree: <nome>` repetido:** barrado (`len(set(nomes)) < q`), com teste. Um cartão sem o campo, ao lado de outros com o campo, também é barrado. O mesmo nome em agentes diferentes é aceito, e isso está certo: o review e a segurança rodam na mesma worktree do autor.
- **Limite min(3, `teto_maximo`, `teto_agentes`):** o valor da config só **reduz** o limite. Valor inválido, zero, booleano ou config ilegível cai no 3, nunca acima dele. O `max(teto, limite)` deixa o cabeçalho da coluna `(WIP N por agente)` subir o limite, mas isso já valia antes desta entrega. O cabeçalho é editável no quadro, e o `agile-coach` o confere contra o modelo.
- **Hook `pesado` no clone do Forge:** `hook.projeto(..., clone_do_forge=True)` só cai em `raiz_de_estado` fora de projeto (`hooks/_comum.py:484-494`), então o comportamento nos projetos não muda. No clone, a lista fixa **soma-se** a qualquer `pesados` local, e o retorno antecipado não consulta `hooks_desligados`, então o hook não pode ser desligado lá. A trava fica em `.forge/run/pesado.json` da cópia principal (`Hook.run`, `copia_principal` pelo `--git-common-dir`). As worktrees de `~/.forge-contrib/wt/` têm a cópia principal em `~/Forge`, então todas veem a mesma trava (conferido com `git worktree list`). A trava expira (`TRAVA_S` = 600 s, ou quando o PID morre), então um bloqueio indevido no clone dura no máximo 10 min. O manifesto do Forge pode ser escrito em qualquer pasta, mas aqui ele só **acrescenta** guarda, nunca a tira (`tem_manifesto_do_forge`).
- **Invariantes:** nenhum item existente foi removido nem alterado (o diff de `tests/config.json` só acrescenta). Os trechos literais "**1 cartão em "Em andamento" por agente.**" e "**uma vez, antes do review**" continuam.
- **Brief único (S-11):** junta as devoluções, sem dispensar nenhum parecer.

## Plano em cartões
1. B3: validar `worktree:` contra `git worktree list` e o `Responsável` contra os agentes conhecidos, com testes. Dono: `tech-lead`. Fica fora deste PR.
2. B4: normalizar o lançador e o nome base do interpretador em `hooks/pesado.py`, com teste. Dono: `tech-lead`. Fica fora deste PR.
3. I3 e I4: ajuste de texto e invariantes, na próxima volta que tocar esses arquivos. Dono: `tech-lead`.

## Riscos aceitos e ferramentas
- Riscos aceitos: nenhum. B3 e B4 são baixos, sem caminho externo, e ficam como cartões. Não é risco aceito do dono.
- Ferramentas: leitura estática dos diffs, de `bin/forge-check` (`cmd_kanban`, `commit_vale`), de `hooks/pesado.py`, `hooks/quadro.py` e `hooks/_comum.py`, mais uma chamada direta à função `pesado()` com variações do comando. `gitleaks`, `osv-scanner`, `semgrep`, `zizmor`, `actionlint` e `trivy` não estão no PATH (lacuna registrada). O diff não traz dependência, workflow nem segredo.
- A suíte completa não foi rodada, conforme o brief: o autor já a rodou, e o review corre em paralelo na mesma worktree.
