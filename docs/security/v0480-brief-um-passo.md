---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-brief-um-passo
commit: 91958d3ec525ada0a983241d372d89f980b084ed
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-23
---
# Review de segurança: receita do envio de parecer (PR #816, v0478 E130.5)

Escopo: `git diff 0e59c446..91958d3e` (E130.1 em `e3eb537e` mais o parecer de review em `91958d3e`, que não toca texto de agente). Seis arquivos de texto: `agents/tech-lead.md`, `agents/qa-engineer.md`, `agents/security-engineer.md`, `skills/briefs-e-conferencia/SKILL.md`, a receita nova `skills/briefs-e-conferencia/envio-de-parecer.md` e o fragmento `changelog.d/v0480-brief-um-passo.md`. Nenhum hook, guarda, teste ou regra com ID mudou.

## Gatilhos
Gatilhos: nenhum da lista de `R-SEGURANCA` tocado diretamente; parecer pedido por ser texto dos agentes de portão (o modo de gravar e enviar parecer).

## Classificação: neutro
O item é **neutro** para a postura: não afrouxa nenhuma trava e não cria trava nova. O que muda é o modo de fazer; o que obriga (só o parecer, só em `docs/security/` e nunca em `docs/security/aceites/`, envio, `R-REVIEW`, `R-VERIFY`) continua no texto do agente. Há dois apertos pequenos de redação, que não mudam guarda: a receita proíbe por extenso `git add .` e `-A` (`envio-de-parecer.md:7`) e fixa `origin <branch>` no pull (`envio-de-parecer.md:10`), o que evita pull de upstream errado.

## A receita não ensina a contornar trava (R-CONFORMIDADE)
- **Write ou Edit em vez de heredoc** (`envio-de-parecer.md:5`): o Write não escapa do controle. `hooks/hooks.json:36` e `:108` casam `Bash|Write|Edit|MultiEdit|NotebookEdit`, e `hooks/conformidade.py:53` (`FERRAMENTAS_DE_ARQUIVO`) aplica ao Write a mesma escrita por papel; a segurança segue presa a `docs/security/`.
- **Uma ação por chamada, sem `$VAR`, `$?`, `${...}`, heredoc nem `&&`** (`envio-de-parecer.md:6-9`): pede o comando literal para que o hook o resolva; é o oposto de ofuscar. Separar add, commit e push não tira nenhuma ação do exame do hook: cada chamada é lida inteira.
- **Envio recusado** (`envio-de-parecer.md:10`): só `git pull --rebase origin <branch>` e novo push; nada de `--force`, `--no-verify` nem merge.
- **Sem ID curto de mutante** (`envio-de-parecer.md:12`): troca uma citação que colide com o detector por hash (`Neutralidade` em `tests/test_forge.py`) por outra rastreável (`arquivo:linha` da guarda ou o arquivo de `tests/mutantes/`). Não ensina reescrever termo de projeto para escapar do `R-NEUTRO`: o alvo é o falso positivo do ID, e a prova (a guarda) continua citada.

## Nada saiu dos agentes de portão sem destino
Conferi cada trecho tirado, contra o diff:
- `git add <caminho>` explícito (tech-lead, qa-engineer, security-engineer): na receita, `envio-de-parecer.md:7`, mais forte.
- Pull atrás do remoto (tech-lead "Atrás do remoto", segurança "recusado por corrida (`behind`)"): comando no agente com `origin <branch>`; a condição está na receita, `envio-de-parecer.md:10` (A2 do review cobre a leitura).
- Lista de pastas de controle (`bin/`, `hooks/`, `.githooks/`, `tests/catraca.py`) tirada de `agents/qa-engineer.md:21`: igual em `skills/qa-testing/SKILL.md:93`, skill carregada pelo qa-engineer. O mutante de pedido de controle segue obrigatório no agente.
- Aviso de 300 caracteres e regra pelo ID (`skills/briefs-e-conferencia/SKILL.md:27`): na receita, `envio-de-parecer.md:5`, e nos três agentes pelo bloco `Achados`.
- Na segurança, ficaram intactos: só `docs/security/`, nunca `docs/security/aceites/`, nunca código, parecer só na árvore não vale (`agents/security-engineer.md:16`).

Observação sem achado: a receita não repete `R-VERIFY` no passo de recusa e o qa-engineer não cita o ID; sem caminho realista, porque o passo de recusa manda só pull com rebase e o `pre-push` e o hook seguem barrando `--force` e `--no-verify`.

## Testes e CI
- Local, dos arquivos tocados: `python3 -m unittest tests.test_forge.Neutralidade tests.test_forge.RegrasInviolaveis tests.test_forge.RegrasComId tests.test_orcamento_instrucao`: `Ran 17 tests … OK`.
- CI do PR no sha `91958d3e` (run 45273814578): tudo verde menos `suíte (python 3.12, parte 1/5)` e o agregado `bateria`; a falha é `test_hooks.Hooks.test_muitos_heredocs_recusam_dentro_do_orcamento`, orçamento de CPU do hook (3.04 s e 3.05 s contra 3.0 s). O diff não toca hook nem o teste: não é atribuível ao item. O merge espera o verde; a reexecução cabe com o motivo escrito (carga do executor, no log).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, `grep` e os testes acima; sem varredura de segredo ou dependência, porque o diff é só texto.
