---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-hook-raiz-forge
commit: 3c1bd3823c82f5383b9df5e289bf7889d4774e97
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-27
---
# Review de segurança: v0481 (E37.25, #930, sondas contra a proteção nova do ambiente)

Gatilhos: hook de bloqueio (`hooks/conformidade.py`), R-CONFORMIDADE, R-VERIFY (pre-push da raiz), o que roda fora do sandbox (postStart do container como root), o manifesto que decide as travas da sessão.

## Resumo
- Delta lido (`forge-check parecer delta`, `3c1bd382..381ded9f`): nenhum arquivo do domínio mudou. O código revisado é o mesmo da volta 5. O que mudou foi o ambiente.
- A proteção nova está em `/workspaces/Forge/.claude/settings.local.json:26-31` (`sandbox.filesystem.denyWrite`). Não é versionada. Ela cobre:
  - `/workspaces/Forge/.githooks`
  - `/workspaces/Forge/.devcontainer`
  - `/workspaces/Forge/.devcontainer.json`
  - `/workspaces/Forge/.claude-plugin`
  - `/workspaces/Forge/scripts/preparar-estacao.sh`
  
  O versionado já força o sandbox (`.claude/settings.json`: `enabled`, `failIfUnavailable`, `allowUnsandboxedCommands: false`).
- Resultado: o furo do Bash fecha na raiz do Forge desta estação. Cada caminho protegido é uma montagem somente leitura própria (`/proc/self/mountinfo`). O kernel nega pelo inode, qualquer que seja a grafia. As variantes S1 a S20 só enganavam a leitura do texto pelo hook. Contra a montagem, elas caem todas no mesmo EROFS.
- O postStart não lê nada da árvore local além do `.git/config` (protegido). Ele clona a `main` do remoto e roda o `preparar-estacao.sh` de lá.
- Estado dos achados anteriores:
  - A16: passa a `recomendado`. critério mudou: o sandbox desta estação nega a escrita nas cinco entradas por qualquer grafia (S21 a S25), e o Bash não sai do sandbox (`allowUnsandboxedCommands: false`).
  - A17, A14, A10 e A11: sem mudança (recomendados, cartões).
- O #930 pode encolher. A guarda por análise de grafia no Bash da raiz (`destino_opaco`, `colada_em_vigor`) vira redundante onde a proteção existe. Ficam duas coisas:
  - a guarda de Write/Edit da raiz (caminho literal, sem o problema de grafia), porque o sandbox do SO cobre só o Bash e não há regra `Edit(...)` de negação para essas entradas;
  - a guarda do projeto.
  
  Fechar ou encolher é decisão do dono (R-DECISAO).
- ci: o CI do head `381ded9f` (run 45961006150) está verde na suíte (5 partes), na instalação, nos passos, no python 3.14, nas verificações longas e no teto de pulados. Vermelhos só `bateria`/`bateria (pareceres)` e `catraca`, por processo (o parecer anterior, reprovado), sem código no delta.

## Achados
- A16 (recomendado) hooks/conformidade.py:4192 · critério mudou: na raiz do Forge desta estação o sandbox nega a escrita por qualquer grafia (S21-S25); a guarda por grafia do Bash fica redundante aqui e só vale onde a proteção local falta; encolher o #930 é decisão do dono
- A18 (recomendado) .claude/settings.json:23 · a proteção está só em settings.local.json (não versionada); outra estação do Forge não a tem, e Write/Edit não passam pelo sandbox do SO; versionar o denyWrite e uma negação Edit(...) das cinco entradas, ou manter a guarda de Write/Edit do hook
- A17 (recomendado) hooks/conformidade.py:4381 · cartão, fora desta branch: nos projetos não há a proteção do ambiente; a colagem por aspas grava o pre-push do projeto (rc 0), que roda fora do sandbox no push da pessoa; a guarda do hook segue sendo o controle lá
- A14 (recomendado) hooks/conformidade.py:4381 · aberto, cartão: a lista de `for` com curinga ou chaves passa na raiz e no projeto; na raiz desta estação o sandbox nega
- A10 (recomendado) hooks/conformidade.py:130 · aberto, sem mudança: ESCRITA_NO_TEXTO não vê `open(…,'r+')` com `print(file=)` nem `subprocess`; o controle de fato é o sandbox
- A11 (recomendado) hooks/conformidade.py:4314 · aberto, sem mudança: checar_texto do clone só casa a entrada literal; hoje o sandbox nega `.git/hooks` (montagem somente leitura)

## Detalhe
As sondas desta volta usaram só um arquivo vazio, de nome inerte (`_sonda-sec145-vazia`). O pre-push e o conteúdo executável ficaram de fora: se a escrita passasse, nada rodaria. Nenhuma gravou, então não houve o que apagar.
- S21: `touch` do nome inerte em `.githooks`, `.devcontainer` e `.claude-plugin`, pela grafia direta. Obtido: `Read-only file system` nas três.
- S22: a mesma escrita por um link simbólico no rascunho (`$TMPDIR/sec145/l<pasta>`), que resolve o caminho por outro nome, como as variantes do hook. Obtido: `Read-only file system` nas três.
- S23: abrir em modo de acréscimo, sem bytes, `.devcontainer.json` e `scripts/preparar-estacao.sh`. Obtido: `Read-only file system` nos dois.
- S24: renomear `.githooks` para tirá-la de cima da montagem. Obtido: `Device or resource busy`, e a pasta segue no lugar.
- S25: `/proc/self/mountinfo` mostra `ro` em cada entrada protegida e também em `.git/config`, `.git/hooks`, `.gitconfig` e `scripts/`.

O que ainda tem caminho:
1. Write/Edit na raiz, fora do sandbox do SO. Lá a guarda do hook, por caminho literal, é o controle. Não sondei para não arriscar um arquivo que o Bash do sandbox não conseguiria apagar. Ela é coberta pelas fixtures `raiz-forge-write-*`, verdes no CI.
2. As cópias em `wt/`: os ganchos delas rodam no push do agente, dentro do sandbox. Isso é residual só se o dono der push de uma cópia fora do sandbox.
3. Os projetos (A17), onde a proteção não existe.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Varreduras de segredos, SAST e workflows não se aplicam: o delta é vazio no domínio. A suíte foi lida do CI do head.
