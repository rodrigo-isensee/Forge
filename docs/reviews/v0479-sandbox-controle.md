---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-sandbox-controle
commit: 03448b3d8050f9e865791f50b6bd300df51ec001
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 (E29.3, A3 SANDBOX-TRAVA-CONTROLE, head 03448b3d)

Escopo: diff `73842444..03448b3d` (9 arquivos). Classe C pela ferramenta (`forge-check pr v0479-sandbox-controle --previo`: "classe C (sensível da catraca: bin/forge-testes)"). Suíte inteira não rodada (fica no CI do PR); rodei só o teste novo: `python3 -m unittest tests.test_sandbox_controle` deu `Ran 8 tests ... OK (skipped=2)`, os dois do bubblewrap pulados com "Creating new namespace failed: Operation not permitted".

## Achados
- A1 (bloqueante) tests/test_apoio_sandbox.py:77 · o teste de falta_bwrap está indentado dentro da função ambiente_sem_ci, depois do return: nunca é coletado (S3). Os três ramos de falta_bwrap (sem bwrap, rc diferente de 0, exceção) ficam sem teste e sem mutante declarado (classe C). Mova-o para a classe de Sondas e declare os mutantes.
- A2 (bloqueante) templates/projeto/.claude/settings.json:39 · denyWrite de caminho inexistente vira arquivo vazio só de leitura no disco (S1); agentes.json de 0 byte é EstadoIlegivel e recusa todo disparo, sem regravar (S2): projeto sem agentes.json na abertura fica sem time. Crie-o antes (forge-init ou hook) ou tire a entrada; idem pesado.fila.
- A3 (bloqueante) skills/novo-projeto/SKILL.md:27 · a skill manda o agente gravar o ritmo com `forge ritmo`, que grava .forge/config.json, agora negado sem saída fora do sandbox (allowUnsandboxedCommands false). O próprio docs/devops/v0479-sandbox-controle.md:58 diz que o passo passa ao dono; a skill e skills/fluxo-do-pedido/SKILL.md:44 não mudaram.
- A4 (recomendado) docs/devops/v0479-sandbox-controle.patch:11 · no Forge, negar .git/forge/run inteiro nega também meta.json (forge-check meta --armar grava em Hook.run(), que no clone é essa pasta), ao contrário do que diz docs/devops/v0479-sandbox-controle.md:14. Negue só agentes.json, ou registre a perda.
- A5 (recomendado) tests/test_sandbox_controle.py:140 · o teste monta o próprio bwrap com o mapeamento de caminho_real: prova o --ro-bind, não o runtime do Claude Code lendo o settings (resolução de relativo, de ~, de pasta). E o ci.yml não instala bubblewrap: se a imagem não o trouxer, o exigir reprova no CI.
- A6 (recomendado) templates/projeto/.claude/settings.json:42 · ~/.forge/maquina já está fora da área gravável no modelo (sem allowWrite) e no Forge (allowWrite só .forge-contrib): a entrada é redundante. Não faz mal (fora da área gravável o runtime não cria o arquivo, S1), mas o teste a torna gravável com --bind da casa.

## Sondas
- S1 · stat de denyWrite inexistentes nesta sessão (/workspaces/Forge/.mcp.json, .gitmodules, .claude/agents; /root/.claude/loop.md) · espera: ausentes · obtido: na área gravável, arquivos vazios -r--r--r-- de 2026-11-04 21:10:58, montados ro; fora dela (loop.md) ausente
- S2 · agentes.ler_estado num agentes.json de 0 byte · espera: {"agentes": []} (começo legítimo) · obtido: EstadoIlegivel JSONDecodeError Expecting value (recusa o disparo, HOOK-ESTADO-ILEGIVEL-LIBERA)
- S3 · loadTestsFromModule(test_apoio_sandbox), procurar "bwrap" nos ids · espera: 1 teste de falta_bwrap · obtido: 22 testes, nenhum com bwrap

## Parecer
Reprovado. A estrutura está certa e segue a A3: o modelo ganha o denyWrite, o Forge vai por patch no molde do PP1, os hooks rodam fora do sandbox e seguem gravando, e o limite do PATH (D7, opção b) foi registrado em docs/hooks.md. Três defeitos bloqueiam.

A1 é um teste morto: o código parece testado, mas o teste não roda. A2 responde à dúvida (2) do brief e a confirma: o próprio runtime desta sessão mostra que um denyWrite de caminho inexistente dentro da área gravável vira, no disco, um arquivo vazio só de leitura, que fica lá entre sessões. Para o agentes.json isso é um defeito com gatilho: o hook trata o arquivo vazio como ilegível e recusa todos os disparos, e por desenho não o regrava. Um projeto novo, ou recém ligado com --ligar-sandbox antes do primeiro agente, perde o time. Para o pesado.fila (pasta) e o pesado.json do projeto vale o mesmo. A3: a skill manda o agente fazer o que agora é negado.

O que é decisão do dono, sem bloquear:
- (1) Negar .forge/config.json no modelo. A A3 do dono lista o teto entre os arquivos de controle, e o ritmo e o piso estão no mesmo arquivo. A consequência real: o `forge ritmo` passa a ser só do dono; e git pull, merge ou checkout que mude esse arquivo versionado falha na cópia principal do projeto, sem saída porque allowUnsandboxedCommands é false. As worktrees ficam de fora, já que o caminho é relativo à raiz da sessão. A alternativa é pôr o teto num arquivo próprio fora do git. O dono escolhe; a A3 bloqueante cobre só a documentação que contradiz a escolha atual.
- (3) A prova da recusa só existe no CI. Mesmo verde, o CI prova o bwrap montado pelo teste, não o runtime (A5). Se o dono quiser a prova do runtime, o caminho sem custo é o sandbox-runtime de código aberto rodando com o settings; isso pede o parecer do devops-engineer sobre o CI.
