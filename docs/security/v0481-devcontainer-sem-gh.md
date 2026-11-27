---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-devcontainer-sem-gh
commit: 046cd9a1b142deccbcf9717b566154cca9f1933d
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (E35.4, #926, DEVCONTAINER-SEM-GH)

1ª rodada completa sobre o head 046cd9a1 (base ee05ee84): `.devcontainer/devcontainer.json`, `scripts/preparar-estacao.sh`, testes e mutantes do diff.

Resposta direta ao brief: **sim, o caminho permite ao agente rodar código como root, fora do sandbox, no próximo início do container**, sem recriar o container, sem ofuscação e sem passar pelo hook (S1, S2). A guarda `FORGE_PREPARO_ESSENCIAL=1` é uma variável lida pelo próprio script que o agente controla; contra esse ataque ela vale zero. A segunda limitação citada ("devcontainer.json protegido pelo hook") não vale na sessão do Forge, que é onde este arquivo vale (S3).

## Gatilhos
Gatilhos: comando executado como root fora do sandbox (postStartCommand), arquivo em vigor (.devcontainer/devcontainer.json), credencial do dono (login do gh no volume ~/.claude), retirada de defesa anterior (B2 da 0.43.1)

## Achados
- A1 (bloqueante) .devcontainer/devcontainer.json:26 · o root roda, a cada início do container e fora do sandbox, scripts/preparar-estacao.sh do work tree /workspaces/Forge, que o agente grava no sandbox (S1) e o hook não protege (S2): escape do sandbox para root com o token do gh do dono; FORGE_PREPARO_ESSENCIAL não limita script forjado
- A2 (recomendado) .devcontainer/devcontainer.json:9 · o comentário dá "este arquivo é protegido pelo hook" como limite do risco, mas na sessão do Forge o hook libera a escrita dele (S3); tirar a afirmação ou trocá-la pela garantia real
- A3 (recomendado) scripts/preparar-estacao.sh:8 · o cabeçalho ainda diz que o postStart é "um clone raso novo da main, nunca ref local", o contrário do que o devcontainer.json passa a fazer; alinhar ao desenho que ficar

## Sondas
- S1 · test -w /workspaces/Forge/scripts/preparar-estacao.sh, no sandbox do agente (sessão do Forge) · espera: não gravável (o que o root executa não pode ser gravado pelo agente) · obtido: gravável
- S2 · hook conformidade do head 046cd9a1 com ~/.forge-contrib/sondas/v0481-e354/s1-write-script.json (Write, devops) e s3-write-script-dev.json (Edit, dev) no script, via rodar.sh · espera: rc=2 · obtido: rc=0 nas duas
- S3 · mesmo hook com ~/.forge-contrib/sondas/v0481-e354/s2-write-devcontainer.json (Write em /workspaces/Forge/.devcontainer/devcontainer.json, sessão do Forge) · espera: rc=2 · obtido: rc=0 (controle s4, projeto com .forge/versao: rc=2)

## Detalhe dos achados
**A1.** Evidência: `.devcontainer/devcontainer.json:26` (postStartCommand roda `bash /workspaces/Forge/scripts/preparar-estacao.sh` como root); `scripts/preparar-estacao.sh:434` em diante; S1 e S2. O hook declara de si mesmo que o sandbox é a garantia (`hooks/conformidade.py:6`), e o sandbox deixa o agente gravar a raiz `/workspaces/Forge` inteira, salvo `.git/config` e o que está em `denyWrite`.
Caminho de ataque: um agente da sessão do Forge, com mau comportamento ou sob injeção de instrução vinda de conteúdo lido (PR, issue, página, saída de ferramenta), acrescenta uma linha ao script com o Edit ou qualquer Bash. Sem malícia o efeito é o mesmo: uma branch não revisada com o script quebrado, posta em `/workspaces/Forge`, também roda como root. No próximo início do container (o container caiu duas vezes em 26/11; reiniciar basta, recriar não é preciso), o root fora do sandbox executa a linha. Com isso lê `/root/.claude/gh` (o login do dono, com escopo `repo` e `workflow`, negado à leitura no sandbox) e grava `~/.claude/settings.json` (desliga o sandbox) e o cache do plugin (os hooks da ADR 0009 deixam de valer). Com o escopo `workflow`, também altera o CI e a `main`. A gravação persiste em `/workspaces`.
Severidade: alta (local, depende de agente desviado e de um reinício, que é rotina; o impacto é total sobre a máquina e a credencial).
O que aperta: o root deixa de acessar a rede com o credential helper do gh no postStart, e a falha aparece (rc 1 e linha `erro:`) em vez de ser engolida.
O que fica neutro: `FORGE_PREPARO_ESSENCIAL=1` (limita só um script honesto e desatualizado), `container_essenciais`, a criação de `~/.config/gh` primeiro, e o modelo de projeto, que continua com o B2 (`tests/test_forge.py`, `test_poststart_do_modelo_roda_so_a_main_do_remoto_nunca_o_ref_local_forjado`).
O que afrouxa: a defesa B2 (o agente não escolhe o que o root executa) sai do Forge, e o caso de abuso que a provava (ref forjado não roda como root) foi apagado para o Forge sem substituto.
Ressalva honesta: o vetor pelo próprio `devcontainer.json` já existia antes (S3). Mas a troca de configuração aparece como mudança no arquivo em vigor e, em regra, só pega ao recriar o container. O vetor novo pega em todo reinício e mora num script que o time edita no dia a dia.
Correção mínima (dono: `devops-engineer`; esforço P). A ordem do dono no cartão diz "usar o script da cópia já presente", então a escolha entre as opções é dele (`R-DECISAO`), levada pelo Jarvis:
1. Recomendada: manter o clone raso novo da `main` (B2), só que sem o gh. Tirar `GH_CONFIG_DIR=/root/.claude/gh` e `-c 'credential.helper=!gh auth git-credential'`, pôr `-c credential.helper=` com `GIT_TERMINAL_PROMPT=0`, manter o `grep` da guarda e trocar o `; rm -rf "$d"; true` do fim pelo aviso com `exit 1` desta branch (limpando `$d` antes). O pedido sai cumprido (sem gh, falha visível) e o B2 continua. Nesta máquina a leitura anônima da `main` funcionou (`git -c credential.helper= ls-remote` da URL do origin, rc 0). Sem rede, a falha aparece e o dono roda o comando manual. Caso de abuso a recolocar: o script forjado no work tree e no ref local não roda; só o da `main` remota roda.
2. Alternativa sem rede: pôr os passos do essencial (criar `/root/.config/gh`, o link `~/.forge-contrib`, instalar o gh e o tmux) direto no postStartCommand, sem executar arquivo gravável pelo agente. É maior e repete a lógica do script.
3. Aceitar o risco como está: só o dono, com `docs/security/aceites/v0481-devcontainer-sem-gh.md` (`pedido: v0481`, `commit: 046cd9a1b142deccbcf9717b566154cca9f1933d`, `aceite: sim`), escrito à mão. Aí o parecer vira `riscos-aceitos`.

**A2.** Evidência: `.devcontainer/devcontainer.json:9` e S3. Na sessão do Forge, o hook só aplica as travas de envio e flags (`hooks/conformidade.py:10`); os caminhos protegidos de `hooks/conformidade.json:35` valem só em projeto. Correção: o comentário passa a citar a defesa que de fato vale. Esforço P. Dono: `devops-engineer`.

**A3.** Evidência: `scripts/preparar-estacao.sh:8`. Comentário que contradiz o código engana o próximo revisor sobre a garantia. Correção: alinhar ao desenho escolhido em A1. Esforço P. Dono: `devops-engineer`.

Cartão (fora do delta, `tech-lead`, dono do hook): na sessão do Forge, o hook conformidade libera Write em `.devcontainer/devcontainer.json` e em `.githooks/` da raiz `/workspaces/Forge` (S3 e o controle s0, rc 0). Os dois são arquivos que rodam fora do sandbox. Propor a proteção desses caminhos também na sessão do Forge, ou, ao dono, `denyWrite` deles no sandbox, sabendo que isso barra o git do Jarvis quando atualiza esses arquivos na raiz.

## Riscos aceitos e ferramentas
Nenhum risco aceito nesta rodada. CI do head 046cd9a1 incompleto na hora do parecer: suítes pendentes e "bateria (pareceres)" vermelha, como esperado sem pareceres. O reprovado não depende do CI: é defeito de desenho, provado por S1 a S3. Ferramentas: só leitura do diff, `test -w` e o hook do próprio head sobre entradas simuladas; nenhum teste da suíte rodado localmente (teto do dono de duas rodadas).
