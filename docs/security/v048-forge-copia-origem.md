---
tipo: revisao-seguranca
contrato: 1
pedido: v048
branch: melhoria/v048-forge-copia-origem
commit: 6c8fd19ce2675be5c3206cf2fcba6679886ded1d
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-28
---
# Review de segurança: v048 (PR #956, FORGE-COPIA-ORIGEM-LOCAL e FORGE-COPIA-D2)

1ª rodada completa no head 6c8fd19c (E4.5), em paralelo ao review e ao QA. Lido: o diff inteiro de `bin/forge-copia` desde a base a90a7a93, os testes novos de `tests/test_forge_copia.py` e os mutantes. Classe C (sensível da catraca: `bin/forge-copia`). CI do head todo verde (run 46136867176, catraca 46136867271), e rodei no computador `tests.test_forge_copia` e o teste de custo `tests.test_hooks_volta_corpus` (ordem do dono 28/11 07:41): 136 testes OK.

## Gatilhos
Gatilhos: execução de git sobre configuração de repositório local (origem local), resolução de URL de remoto para clone, apagar ref (desfazer da worktree).

## Achados
- A1 (recomendado) bin/forge-copia:182 · Desfazer da worktree com janela entre a checagem `antes` e o `worktree add -b`: branch criada por outro processo nesse intervalo, no mesmo sha, é apagada e a mensagem diz que foi a worktree que a criou (sonda S8). Criar a branch de forma atômica e só então a worktree.

## Sondas

## Detalhe dos achados
**A1.** Evidência: `bin/forge-copia:182` lê `antes` (a branch existe?) e `:186` roda `git worktree add --no-track -b`; se o add falha, `:189` apaga `refs/heads/<branch>` com o valor antigo igual ao sha do ponto. Sonda S8 (HOME descartável, um `git` de embrulho no PATH que, só no `worktree add`, cria `melhoria/alheia` em `origin/develop` antes de chamar o git real, simulando o processo concorrente): `forge-copia worktree <destino> --branch melhoria/alheia --base origin/develop` · espera: rc 1 e a branch alheia fica · obtido: rc 1, "apaguei a branch melhoria/alheia que ela criou", branch apagada. Caminho: dois agentes (ou duas chamadas) criando a mesma branch no mesmo repositório ao mesmo tempo; não há atacante externo. Severidade: baixa. A checagem do valor antigo garante que nenhum commit se perde (a ref apagada aponta para o próprio ponto, que segue alcançável pela base ou por `origin/<branch>`), mas a worktree do outro fica com HEAD numa branch inexistente (o próximo commit nasce sem pai) e a mensagem é falsa. Correção mínima: provar a posse antes do add: `git update-ref refs/heads/<branch> <sha> ""` (o valor antigo vazio falha se a branch já existe; aí sai 1 sem apagar nada), depois `git worktree add -- <destino> <branch>` sem `-b`, e na falha `git update-ref -d refs/heads/<branch> <sha>`; um teste com a branch criada entre a checagem e o add. Esforço: P. Dono: o autor do E4.1 (tech-lead).

**Pontos conferidos sem achado** (pedido do brief):
- Git sobre a cópia gravável: o único git novo sobre pasta que não é a cópia nova é `git -C <origem> remote get-url origin` (`bin/forge-copia:171`). Esse comando não lê o índice nem roda hook; sonda com `core.fsmonitor` apontando para um script na config da origem: o script não rodou e o clone saiu 0. Hook `post-checkout` na `.git/hooks` da origem: não foi ao clone nem rodou. O `switch` roda na cópia nova, cuja config e hooks vêm do clone (modelo global), não da origem.
- Protocolo da URL do origin: a URL lida vai ao `git clone --` (`bin/forge-copia:368`) depois do `--`. Sondas: `ext::sh -c ...` · obtido "transport 'ext' not allowed", rc 1, sem marca; `ssh://-oProxyCommand=...` · obtido "strange hostname ... blocked", rc 1; URL `--upload-pack=...` gravada na config · obtido "repository ... does not exist", rc 1, sem marca. A config de protocolo da origem não vale para o clone (só a global e a do sistema, que são do usuário). O caminho relativo resolve a partir da origem, como o git faz.
- Desfazer: a branch que já existia antes não é apagada (sonda S6: rc 1, "already exists", branch fica); a criada pelo add que falha é apagada (S7: pai do destino é arquivo, rc 1, branch apagada); o apagar usa o valor antigo, então branch que andou nunca sai. A janela de corrida é o A1.
- D2: `--d2` só no clone, sem `--branch` e sem `--revisao` (recusa em `bin/forge-copia:333`); a base continua recusada quando começa com `-`; sem a base, o clone é apagado; o nome único usa `d2`.
- Credenciais: o clone por URL herda o ambiente como antes (sem mudança de postura); a URL lida não é impressa (a mensagem cita só a pasta de origem).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: só sondas locais em HOME descartável e os testes; o varredor de segredos, o SAST e o linter de workflow não estão no PATH (lacuna registrada; o diff não toca workflow nem traz segredo, conferido na leitura).
