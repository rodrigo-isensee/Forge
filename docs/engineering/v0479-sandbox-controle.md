# A3: aplicar a trava de escrita do sandbox no Forge (`.claude/settings.json`)

O `.claude/settings.json` do Forge é travado para os agentes (decisão do dono, como o `.githooks/pre-push` do PP1). A decisão A3 do pedido v0478 (dono, 2026-11-18 22:15) pede que o sandbox negue aos agentes a escrita nos arquivos de controle, no Forge e no modelo de projeto, com os hooks seguindo a gravar. O modelo de projeto entrou direto na branch (`templates/projeto/.claude/settings.json`); o Forge vai como patch, `docs/engineering/v0479-sandbox-controle.patch`, provado por `tests/test_sandbox_controle.py` numa cópia temporária. Só o dono aplica.

## Os arquivos de controle (levantamento)

| Arquivo de controle | Quem grava | Caminho no modelo de projeto | Caminho no Forge |
|---|---|---|---|
| Registro de agentes | hook `agentes` (`SubagentStart`/`Stop`, `PreToolUse`) | `.forge/run/agentes.json` | `<diretório comum do git>/forge/run/` (`.git/forge/run` na cópia principal) |
| Teto (e ritmo, piso de memória, pesados) | o dono (`forge ritmo`, `forge-init`, edição à mão) | `.forge/config.json` | `.forge/config.json`, coberto por `.forge/` (na cópia do dono `.forge` é pasta, com `config.json` e `run/`; num clone sem a pasta, o `.gitignore` a lista como ponto de montagem) |
| Trava de tarefa pesada | hook `pesado` | `.forge/run/pesado.json` (a fila do projeto, `.forge/run/pesado.fila`, morreu na MP4: a fila é `~/.forge/maquina/pesado.fila` e saiu da lista) | `.forge/run/pesado.json`, coberta por `.forge/`; `.git/forge/run` quando `.forge` é arquivo |
| Registro da máquina (sessões ativas, fila da máquina) | hooks `_maquina`, `pesado`, `agentes` | `~/.forge/maquina` | `~/.forge/maquina` |

Os hooks rodam pelo harness do Claude Code, fora do sandbox do Bash, e por isso seguem gravando. Nada do time grava nesses caminhos pelo Bash: `forge-pesado`, `forge-status` e `forge-check fila` só leem (conferido em `tests/test_sandbox_controle.py`). O resto de `.forge/run/` (`testes.log`, `quadro.trava`, `meta.json`, `<slug>/run.json`) fica gravável: `forge-testes`, `forge-mutante`, `forge-check` e `forge-run` gravam ali pelo Bash.

## O que muda no Forge

```diff
diff --git a/.claude/settings.json b/.claude/settings.json
--- a/.claude/settings.json
+++ b/.claude/settings.json
@@ -21,7 +21,9 @@
         "/workspaces/.forge-contrib"
       ],
       "denyWrite": [
-        ".forge/"
+        ".forge/",
+        ".git/forge/run",
+        "~/.forge/maquina"
       ]
     },
     "network": {
```

(O patch aplicável, com o índice do git, é `docs/engineering/v0479-sandbox-controle.patch`; o trecho acima só o mostra para revisão.)

No modelo de projeto (já na branch), o `denyWrite` ganha `.forge/config.json`, `.forge/run/agentes.json`, `.forge/run/pesado.json` e `~/.forge/maquina`. A lista do patch do Forge não mudou na volta E29.6 (continua `.forge/`, `.git/forge/run` e `~/.forge/maquina`); o comando de aplicar e o de testar abaixo seguem os mesmos. O `forge-upgrade --ligar-sandbox` une a lista à do projeto.

## Aplicar (o dono, na raiz do clone, na branch que traz o patch)

```bash
git apply --check docs/engineering/v0479-sandbox-controle.patch && git apply docs/engineering/v0479-sandbox-controle.patch
python3 -c "import json; print(json.load(open('.claude/settings.json'))['sandbox']['filesystem']['denyWrite'])"
```

O `--check` falha sem tocar em nada se o arquivo em vigor já mudou (por exemplo, se o patch já foi aplicado). Commite o arquivo sozinho em `melhoria/*`, com o rótulo `afrouxa-regra` só se a catraca pedir (a mudança aperta um controle). Reabra a sessão do Claude Code para valer.

## Testar depois de aplicado

```bash
python3 -m unittest tests.test_sandbox_controle tests.test_apoio_sandbox
```

Com o arquivo já remendado, o teste confere o arquivo em vigor e não aplica o patch de novo. Os dois testes do sandbox montam o bubblewrap com o `denyWrite` e tentam `find -delete`, `tar` por cima, `chmod`, a escrita direta (`>`, `sort -o`), `git init` na pasta e `mv` por cima em cada alvo, que devem ser recusados; sem bubblewrap utilizável pulam com o motivo fora do CI e reprovam no CI.

## Consequências e o que não foi provado

- `.forge/config.json` negado: `forge ritmo <valor>` rodado por um agente deixa de gravar; o dono roda no terminal (o passo "Ritmo" da skill `novo-projeto` passa a ser do dono). O teto, o piso de memória e a lista `pesados` só mudam por ele.
- `.forge/config.json` costuma ser versionado no projeto: um merge, pull ou checkout no checkout do projeto que mude esse arquivo falha dentro do sandbox (o mesmo risco N6 do `denyWrite` de arquivo versionado). Rodar o merge fora do sandbox, como o dono faz, resolve.
- O runtime do sandbox cria, no disco, um arquivo vazio 0444 para cada caminho negado que não existe dentro da área gravável (sondado pela segurança: `.git/config.lock`, `.zshrc`). Por isso os arquivos de controle negados passam a existir antes do primeiro Bash da sessão: o `forge-init` cria `.forge/run/agentes.json` (`{"agentes": []}`) e `.forge/run/pesado.json` (`null`), e o hook `doutor` do início de sessão cria o que faltar (projeto já criado, ou ligado com `--ligar-sandbox` depois), sem regravar o que existe. O hook `pesado` grava `null` ao soltar, em vez de apagar o arquivo. E só o `pesado.json` de 0 byte ou `null` vale como sem trava (`_comum.ler_trava`), o mesmo que a ausência; o `agentes.json` de 0 byte segue ilegível e recusa o disparo (`agentes.ler_estado`, HOOK-ESTADO-ILEGIVEL-LIBERA), e o dono o confere no terminal; JSON quebrado também segue ilegível. O `.forge/config.json` é versionado e criado pelo `forge-init`, então já existe.
- Limite (A2 da segurança, recomendado): o `rename(2)` só recusa quando o próprio caminho é ponto de montagem, então um interpretador que renomeie a pasta mãe (`.forge`, pasta de `.forge/config.json`; `.forge/run` no modelo; `.git/forge` no Forge) e recrie o estado forjado escapa da trava por arquivo. Não se nega a pasta mãe porque o resto de `.forge/run/` (`testes.log`, `quadro.trava`, `meta.json`, `<slug>/run.json`, `erros.log`) é gravado pelo Bash por `forge-testes`, `forge-mutante`, `forge-check` e `forge-run`, e `.git/forge` guarda `pr/`, que o `forge-check pr` grava pelo Bash. Fechar de verdade pede que o hook confira a identidade da pasta (inode guardado fora da área gravável, em `~/.forge/maquina`): cartão de melhoria.
- O bubblewrap deste ambiente não cria namespace aninhado (`Operation not permitted`): os testes do sandbox pulam aqui e a prova de que a recusa acontece é o CI. A prova local é a estrutural (o `denyWrite` do modelo e do patch, os caminhos batendo com os que os hooks gravam).
- Limite do hook de `PATH` (D7, opção b): registrado em `docs/hooks.md`, coberto por esta trava.
