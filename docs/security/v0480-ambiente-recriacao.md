---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-ambiente-recriacao
commit: 09457540dde8f8b4d47c47d32cc6d57e9b883b10
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-22
---
# Review de segurança: v0480-ambiente-recriacao (E119.2, AMBIENTE-SOBREVIVE-RECRIACAO)

Revisão completa única do diff `38c37de9..09457540`: `scripts/preparar-estacao.sh`, `templates/projeto/.devcontainer/preparar-ambiente.sh`, os testes (`tests/test_ambiente_recriacao.py`, ajustes em `tests/test_ambiente_hook.py` e `tests/test_forge.py`), a spec de mutantes, `tests/pesos-d4.json` e o fragmento do changelog. Os dois `devcontainer.json` não mudaram, e a guarda B2 continua valendo: o postStart executa o script de um clone raso novo da `main` remota, nunca o do work tree (parecer `v047-ambiente-sobrevive`, A1 fechado).

## Gatilhos
Gatilhos: comando como root fora do sandbox a cada início do container (postStart), download e execução de código de terceiro (cadeia de suprimentos), alteração do PATH do shell de root, modelo de projeto (chega a todos os projetos).

## Achados
- A1 (recomendado) scripts/preparar-estacao.sh:210 · curl do instalador sem limite de tempo nem https exigido (o timeout 300 só cobre o bash); rede parada prende o postStart. Somar --proto '=https' --proto-redir '=https' --connect-timeout 20 --max-time 120. Idem templates/projeto/.devcontainer/preparar-ambiente.sh:97.
- A2 (recomendado) scripts/preparar-estacao.sh:214 · A falta manda o dono rodar como root `curl ... | bash`, o pipe que a entrega evita (download cortado executa parte do script). Dar o comando em dois passos (baixar para arquivo, depois bash). Idem :205 e templates/projeto/.devcontainer/preparar-ambiente.sh:101 e :105.

## Sondas

## Detalhe dos achados

**Decisão pedida no brief: aceito por escrito o instalador oficial sem sha256 fixo.** Não vai ao dono como decisão de segurança, porque o risco residual é o mesmo que o ambiente já aceita hoje.
- **Risco.** Root executa, fora do sandbox, um script baixado de `https://claude.ai/install.sh`. Nesta revisão ele redirecionou para `downloads.claude.ai/claude-code-releases/bootstrap.sh` (261 linhas, sha256 `2c5506d1…0b44` hoje). O script baixa o binário da mesma origem e o executa (`claude install`). Quem comprometer a distribuição (a origem ou o TLS dela) ganha execução como root no container, com acesso ao volume `/root/.claude`, inclusive ao login do gh.
- **Por que o sha256 fixo do script não reduz esse risco.** O script é só o bootstrap. Ele confere o binário contra o `manifest.json` baixado da mesma origem por https, então a âncora de confiança continua sendo o TLS de `claude.ai` e `downloads.claude.ai`, com ou sem a soma fixa. Além disso, o binário instalado se atualiza sozinho da mesma origem e já roda como root em toda sessão (`remoteUser: root`). O modo estação já faz `curl … | bash` do mesmo instalador (`scripts/preparar-estacao.sh:569`), e o Forge confia nessa origem desde lá. Uma soma fixa só quebraria a cada versão: falharia fechado, sem instalar, e viraria `falta:`, com custo de manutenção e nenhum ganho contra quem controla a origem.
- **Mitigações presentes (conferidas).** Download só por https para arquivo, sem pipe, então um download cortado não executa nada (`curl -f` falha, e o `&&` impede o `bash`) (`scripts/preparar-estacao.sh:210-211`, `templates/projeto/.devcontainer/preparar-ambiente.sh:97-98`). O diretório vem de `mktemp -d` no /tmp do root, que o sandbox do agente não grava, e o `set -euo pipefail` aborta se o `mktemp` falhar. O stdin vem de /dev/null e há `timeout 300`. Só instala se `~/.local/bin/claude` faltar. O script executado vem do clone novo da `main` (B2). O binário é conferido pelo sha256 do manifesto antes de executar, e o download dele fica em `/root/.claude/downloads`, fora da escrita do sandbox. A falha vira `falta:` e não impede o container de subir.
- **PATH.** `export PATH="$HOME/.local/bin:$PATH"` no `.bashrc` de root (`scripts/preparar-estacao.sh:197`, `templates/projeto/.devcontainer/preparar-ambiente.sh:109`) não abre sombra de comando. `~/.local/bin` e `~/.bashrc` estão fora da escrita do sandbox: `allowWrite` em `.claude/settings.json` e no modelo só traz `~/.forge-contrib` e `/workspaces/.forge-contrib`, além da pasta do projeto. Os atalhos que já moram lá são trampolins para o plugin instalado (`scripts/preparar-estacao.sh:402-414`). Se essa pasta um dia entrar em `allowWrite`, a ordem do PATH vira escalada para root, e o achado precisa ser reaberto.
- **Recomendação ao dono, se ele quiser ir além (opcional, não bloqueia):** fixar a versão (`bash instalar.sh <VERSÃO>`, já aceito pelo script) em vez da soma do script. Isso troca atualização sozinha por atualização de propósito, na linha da orientação de AMBIENTE-SEM-AUTO-UPDATE. É uma decisão de produto, não de segurança.

**A1 (recomendado; disponibilidade e defesa em profundidade).** Evidência: `scripts/preparar-estacao.sh:210` e `templates/projeto/.devcontainer/preparar-ambiente.sh:97` não têm `--max-time` nem `--connect-timeout`. O `timeout 300` envolve só o `bash`. Caminho: com a rede presa, sem recusa nem resposta, o curl espera indefinidamente. Ele roda antes dos passos seguintes do preparo (persistência do gh, link, `core.hooksPath` no modelo), e esses passos só rodam depois dele. Um redirecionamento para http só viria da própria origem autenticada por TLS, então `--proto` aqui é endurecimento, não correção de falha provada. Severidade: baixa. Correção mínima (P): nas duas chamadas, `--proto '=https' --proto-redir '=https' --connect-timeout 20 --max-time 120`. Se quiser, mover o passo do Claude Code para depois do link e do `core.hooksPath`. Dono: `devops-engineer`.

**A2 (recomendado).** Evidência: `scripts/preparar-estacao.sh:205` e `:214`, `templates/projeto/.devcontainer/preparar-ambiente.sh:101` e `:105`. A mensagem `falta:` propõe ao dono, que roda como root, `curl -fsSL https://claude.ai/install.sh | bash`. O bootstrap não está dentro de uma função principal (lido por inteiro), então uma conexão cortada no meio executaria só parte dele. Severidade: baixa (depende de ação humana e de falha de rede no momento exato). Correção mínima (P): o texto da falta passa a ser `curl -fsSL -o /tmp/instalar-claude.sh https://claude.ai/install.sh && bash /tmp/instalar-claude.sh`, ou aponta para rodar de novo o próprio preparo (`rode $preparo`), que já baixa para arquivo. Dono: `devops-engineer`.

**Conferido sem achado.**
- `--verificar` só testa `-x ~/.local/bin/claude`, sem rede. O teste `test_verificar_diz_o_que_falta_sem_alterar_nada` prova que nada é criado e que o curl não é chamado.
- O `claude` antigo do PATH da imagem não conta como instalado (M1 e M2 da spec).
- `--simular` não baixa nada.
- Nenhum segredo nos arquivos do diff, por varredura manual: nenhum token, chave nem credencial. O changelog e os testes não tocam controle.
- O teste usa curl falso e nunca acessa a rede (`R-CUSTO`).
- Neutralidade (`R-NEUTRO`): o modelo não ganha nome de projeto.

## Riscos aceitos e ferramentas
Nenhum risco aceito pelo dono. O instalador sem soma fixa foi aceito acima por este parecer, como risco igual ao de base, e não vai a `R-DECISAO`. Testes rodados: `python3 -m unittest tests.test_ambiente_recriacao tests.test_ambiente_hook` (16, OK). A suíte inteira não foi rodada (brief: sem suíte local), e não há PR nem CI para citar: o CI verde do PR continua sendo condição do merge (`R-SEGURANCA`, `R-REVIEW`). Leitura passiva do instalador público (download para o scratchpad, sem executar). Faltaram shellcheck, gitleaks, zizmor e actionlint (fora do PATH; lacuna registrada, nada instalado).
