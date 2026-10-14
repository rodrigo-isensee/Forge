---
tipo: review
contrato: 1
pedido: primeiro-uso-f6
branch: melhoria/primeiro-uso-f6
commit: 7a630a4
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-14
---
# Parecer de autor: primeiro uso F6 (`forge sugerir`)

Autor e revisor são o mesmo papel aqui: este parecer é de autor e não substitui a review independente do PR.

## O que foi conferido
- **Anonimização** (`bin/forge-sugerir`): tokens (prefixos conhecidos, JWT, hex longo, `chave=valor`), e-mails, endereços de repositório (os do próprio Forge ficam), caminhos absolutos (Unix, `~`, Windows), nome do projeto (`.forge/novo-projeto.json`, remoto `origin`, pasta) e da pessoa (dono, `USER`, pasta pessoal, nome do git). É heurística: a pessoa vê o texto final antes de qualquer envio, e essa é a garantia real.
- **Nada sai sem "s":** recusa, fim de entrada, sem terminal e chamado de dentro do Claude guardam na fila (texto já anonimizado, modo 600); `--fila` recusa dentro do Claude e sem terminal. Falha do `gh` (rede) guarda e sai com 1. Sem rótulo, sem edição, só `gh issue create -R` (repositório trocável por `FORGE_SUGERIR_REPO`, para testes).
- **Hook e regra:** `gh issue create` já passava; ficou travado por fixture. Apertou: `gh issue create --label|-l` no Forge, de sessão de projeto, é barrado (rótulo é da sessão do Forge). `R-CONTRIB` diz que issue nova é permitida. Confere com a catraca: o único afrouxamento aparente (`gh issue create` explícito) não muda o comportamento, e a mudança no hook é restrição.
- **Testes:** 14 em `tests/test_sugerir.py` (12 falhavam sem a mudança) com `gh` falso e pty, e 3 fixtures de hook (2 vermelhas antes). Suíte completa 473 OK; `validar-plugin.sh` ok; `shellcheck bin/forge` limpo (`forge-sugerir` é Python).

## Riscos e pendências
- Altera `hooks/conformidade.py`: o PR precisa do rótulo `afrouxa-regra` do dono.
- O texto vai por issue pela conta da pessoa (P1 = A); o envio por bot e `Forge-contrib` fica para depois.
- A sugestão é pública se o repositório do Forge for público; o aviso diz que aparece com o nome de usuário.
- O PR é empilhado: depende de #111, #110, #103 e #102.

## Review independente

Segunda leitura por outra instância do `tech-lead` (R-REVIEW), sobre o HEAD 9c55a3f (`d0ab6a7..9c55a3f`). Parecer: **reprovado**. O foco é vazamento de dados e segurança; o código está legível, os testes passam, mas a garantia "nada do projeto chega ao Forge sem a pessoa ver" não se sustenta.

### Bateria local (cota do Actions esgotada)
- `python3 -m unittest discover -s tests`: 473 testes, OK.
- `scripts/validar-plugin.sh`: ok. `shellcheck` (lista do CI mais `bin/forge`): limpo.
- `tests/catraca.py --base origin/develop` (regras): sai 1 só por R-CONFORMIDADE em `hooks/_comum.py`, `conformidade.py`, `parecer.py` (PR empilhado; rótulo `afrouxa-regra` do dono pendente); contra `d0ab6a7` (só a F6), sai 0 com o mesmo aviso de `conformidade.py`.
- `--modo pareceres` (ramo e base do CI): 0. `--modo pr-texto` com o corpo do #112: 0.
- Versão e changelog: `plugin.json` 0.12.0 igual à base; linha nova da F6 em `## [Não publicado]`: ok.

### Ajustes necessários
1. **Bloqueia. O agente cria issue no Forge sem a pessoa** (`hooks/conformidade.py:759`, `tests/hooks/conformidade/contrib-issue-create-libera.json`). A fixture nova garante que, de sessão de projeto, `gh issue create -R rodrigo-isensee/Forge --title t --body-file s.md` passa: qualquer agente publica texto arbitrário (sem anonimização, sem confirmação) e o "só fila dentro do Claude" do `forge sugerir` vira enfeite. Testado também: `gh api repos/rodrigo-isensee/Forge/issues -f 'labels[]=bug'` e `gh api -X POST .../issues --input corpo.json` passam (rótulo pela API, contra o novo texto da `R-CONTRIB`), e `--assignee`/`--milestone` também. **Decisão:** o hook barra, em sessão de projeto, toda criação de issue no Forge (`gh issue create` com alvo no Forge, `gh api` POST em `repos/<forge>/issues` e a mutação GraphQL `createIssue`). Não custa nada ao fluxo: o envio é da pessoa, no terminal dela, fora do Claude, onde o hook não roda. Inverter a fixture para `-bloqueia`, acrescentar as variantes de API e ajustar a `R-CONTRIB` ("issue nova no Forge só pela pessoa, com `forge sugerir`, fora do Claude; a sessão de projeto não cria issue"). Recomendado no mesmo passo: barrar `forge sugerir --fila`/`forge-sugerir --fila` no Bash do agente (o `dentro_do_claude` cai com `env -u CLAUDECODE -u CLAUDE_CODE_ENTRYPOINT setsid -f script ...`, que tira o `claude` da linhagem e dá um pty).
2. **Bloqueia. O texto mostrado pode esconder parte do enviado** (`bin/forge-sugerir:138-143`, `:171`). Nada filtra caracteres de controle: `\x1b[8m...\x1b[0m` (texto invisível), `\r`, sequências de cursor e caracteres de formatação Unicode (`U+202E`, largura zero) passam ao terminal e ao `gh` (conferido: `anonimizar` devolve `\x1b[8mSEGREDO\x1b[0m` intacto, também no título). Arquivo da fila escrito por agente é o vetor. Correção: antes de mostrar, remover ou recusar categorias `Cc` (exceto `\n` e `\t`) e `Cf`, no corpo e no título; teste com ESC, CR e U+202E.
3. **Bloqueia. Segredos que passam** (`bin/forge-sugerir:30-37`): bloco PEM inteiro (`-----BEGIN RSA PRIVATE KEY-----` com o corpo base64) sai intacto; segredo AWS (`aws_secret_access_key=wJalr...` e a chave de 40 caracteres sozinha; `\bsecret\b` não casa dentro de `aws_secret_access_key`); `password:"p4ss w0rd"` deixa `w0rd"`; `Authorization: Basic dXNlcjpwYXNz` passa. Correção: trocar blocos `-----BEGIN ...-----`..`-----END ...-----` inteiros; chave de segredo também dentro de identificadores (`\w*(secret|token|password|passwd|senha|api_?key|private_?key)\w*`), valor entre aspas inteiro; `Basic`/`Bearer`; sequências base64 longas (40+).
4. **Bloqueia. Dados do projeto que passam e o aviso que afirma o contrário** (`bin/forge-sugerir:27-28`, `:56-97`). Com o projeto `Sistema-Ação` (remoto `gitlab.empresa.local/time-x/...`, `CLAUDE.md` com cliente, host e IP), saíram: `Sistema-Acao`, `Sistema Ação`, `SistemaAção`, `sistema_acao`; IPv4 `10.20.30.40` e IPv6; `db01.corp.interno`; URLs que não são de repositório (`https://intranet.empresa.local/wiki/Sistema`, `www.empresa.local/sistema`); `C:/Users/<usuário>/app` com barra normal e UNC `\\servidor\share`; `https://github.com/rodrigo-isensee/Forge/../../outro/repo` fica por parecer do Forge; o nome do cliente do `CLAUDE.md`. Caminhos `~`, `/home/x`, `C:\Users\x`, e-mails, `ghp_`, `github_pat_`, `sk-`, `AKIA`, JWT e o nome em maiúsculas, minúsculas e com hífen saíram bem. Correção: variantes do nome (NFKD sem acento; separadores `[-_ ]?` opcionais entre as partes); IPs; toda URL e todo nome de host com ponto fora de uma lista curta de públicos (o Forge, `github.com` sem caminho) vira `[url]`/`[host]`; Forge só se o caminho normalizado ficar no repositório; caminhos `X:/` e UNC. O nome de cliente não sai por heurística: o `AVISO` não pode dizer "já não tem dados do seu projeto"; diga "tirei caminhos, e-mails, tokens e o nome do projeto; leia e confira se sobrou algo (nomes de cliente, servidores)".
5. **Bloqueia. A skill manda o agente gravar texto bruto na fila** (`skills/modo-iniciante/SKILL.md:32`): "Guarde o texto ... em `~/.local/state/forge/sugestoes/<data>-<tema>.md`" continua, com a ferramenta de escrita do agente: sem anonimização e sem o modo 600. Deixar só `forge sugerir "<texto>"`.
6. Recomendado. `guardar_na_fila` (`bin/forge-sugerir:110-120`) grava com o umask e só depois aplica 600 (janela de leitura) e cria a pasta com 755 (o nome do arquivo leva o tema). Usar `os.open(..., O_CREAT|O_EXCL|O_WRONLY, 0o600)` e `mkdir(mode=0o700)` com `chmod` da pasta.

O que está certo: só "s"/"sim" envia (Enter, outra resposta e EOF guardam); dentro do Claude ou sem terminal só fila, e `--fila` recusa nos dois casos; o texto e o título mostrados são os mesmos enviados (fora o item 2); `gh` com argv em lista e `stdin` nulo, sem shell; o hook barra `--label`, `--label=`, `-lX`, `GH_REPO`, URL em `--repo` e `bash -c`; `gh issue edit|close|reopen` seguem barrados e a `R-CONTRIB` não perdeu nenhuma proibição.


## Re-review independente

Terceira leitura por outra instância do `tech-lead` (R-REVIEW), sobre o HEAD 7a630a4 (`d793fed..7a630a4`). Parecer: **reprovado**. Três dos quatro bloqueios estão fechados; o envio sem a pessoa continua possível por outro caminho, e um segredo comum ainda vaza.

### Bateria local (cota do Actions esgotada)
- `python3 -m unittest discover -s tests`: 490 testes, OK.
- `scripts/validar-plugin.sh`: ok. `shellcheck` (lista do CI mais `bin/forge`): limpo.
- `tests/catraca.py --base origin/develop` (regras): sai 1 só por R-CONFORMIDADE em `hooks/_comum.py`, `conformidade.py`, `parecer.py` (PR empilhado; rótulo `afrouxa-regra` do dono pendente); contra `d0ab6a7` (só a F6), sai 1 só por `hooks/conformidade.py`, o mesmo rótulo.
- `--modo pareceres` (`--ramo=melhoria/primeiro-uso-f6 --base-ref develop`): sai 1, esperado, porque o último parecer é reprovado. `--modo pr-texto`: não rodei com o corpo do #112 (o repositório não responde à API sem autenticação e esta revisão usa só o `gh` falso); o corpo não mudou desde a review anterior, que deu 0.
- Versão e changelog: `plugin.json` 0.12.0 igual à `develop`; linha da F6 em `## [Não publicado]`: ok.

### Os quatro bloqueios anteriores
1. **Fechado no hook.** De sessão de projeto, `gh issue create -R rodrigo-isensee/Forge`, `gh api repos/rodrigo-isensee/Forge/issues -f ...` e a mutação `createIssue` saem com 2 e R-CONTRIB (conferido no hook e nas sete fixtures novas). Mas veja o item 1 abaixo: o script chama o `gh` por dentro.
2. **Fechado.** `limpar_controle` tira ANSI, OSC, `\r`, `Cc` e `Cf` do corpo e do título; ESC `[8m`, CR, U+202E e U+200B saem; o texto antes escondido fica visível.
3. **Fechado.** PEM inteiro, `aws_secret_access_key=` e a chave solta de 40, `password:"p4ss w0rd"`, `Authorization: Basic` e base64 de 40+ viram `[chave]`/`[token]`.
4. **Fechado.** As grafias do nome (`Sistema-Acao`, `Sistema Ação`, `SistemaAção`, `sistema_acao`, maiúsculas), IPv4/IPv6, `db01.corp.interno`, URLs que não são do Forge, `C:/`, UNC e o `../../` no caminho do Forge saem; o `AVISO` não promete mais anonimato. A skill `modo-iniciante` usa só `forge sugerir --guardar`; a fila nasce com pasta 700 e arquivo 600 (`O_EXCL`), e o `--fila` anonimiza de novo o que lê.

### Ajustes necessários
1. **Bloqueia. O agente ainda envia sem a pessoa, pelo próprio `forge sugerir`** (`bin/forge_versoes.py:405-417`, `bin/forge-sugerir:277-301`, `hooks/conformidade.py`). Com `CLAUDECODE` ou `CLAUDE_CODE_ENTRYPOINT`, o envio normal só guarda e o `--fila` sai com 2, como no `forge-atualizar` e no `forge-voltar-versao`: ok. Só que basta tirar as duas variáveis: dentro do sandbox do Bash o processo está num namespace de PID próprio (a linhagem vista termina em `bash`, PID 2), então a busca por um ancestral `claude` nunca acha nada. Reproduzido do Bash do agente, com `gh` falso: `env -i HOME=... PATH=... script -qec "python3 bin/forge-sugerir --fila" /dev/null` com `s` na entrada chegou ao `gh issue create -R rodrigo-isensee/Forge` e "enviou" a sugestão; o hook `conformidade` libera `forge sugerir --fila`, `env -u CLAUDECODE -u CLAUDE_CODE_ENTRYPOINT script -qec 'printf "s\n" | forge sugerir --fila' /dev/null` e `env -i ... script -qec 'yes s | forge sugerir "x"'` (todos saíram com 0). O hook barra o `gh`, mas o script chama o `gh` por dentro, e o "s" é do agente, não da pessoa. A review anterior já recomendava barrar isso no hook. Correção: o hook `conformidade` barra, em sessão de projeto (e de preferência em toda sessão), `forge sugerir` e `forge-sugerir` (também por caminho, `bash -c`, `env`, `script`, `setsid` e `python3 .../forge-sugerir`) sempre que não for `--guardar`, ou seja, `--fila`, texto solto e `--arquivo`; fixtures com essas três formas. A checagem por variável continua como segunda camada. Vale a mesma fragilidade para `forge atualizar` e `forge voltar-versao` (antiga, fora deste PR; registrar).
2. **Bloqueia. Chave em JSON escapado vaza** (`bin/forge-sugerir:39`). `{\"api_key\": \"AbCdEf123456\"}`, `{\"token\":\"abc\"}`, `"{\"password\":\"hunter2\"}"` e `{\\\"secret\\\": \\\"zzz\\\"}` saem intactos: o separador `[\"']?\s*[:=]` não aceita a barra antes da aspa, e o valor `\"...\"` também não. É o formato de log e de corpo de requisição colado em sugestões. Correção: aceitar `\\*["']?` depois da chave e valor `\\*"(?:[^"\\\n]|\\.)*?\\*"`; testes com um e dois níveis de escape.
3. Recomendado. Nome do projeto separado por ponto passa (`Sistema.Acao`, `sistema.acao.app`), e `Sistema--Acao` também: incluir `.` e repetição em `[-_ .]*` entre as partes. Valor em URL codificada passa (`token%3Dabcdef123456`, `password%3Dhunter2`): decodificar `%3D`/`%3A` antes do `SEGREDO` ou aceitar o separador codificado. Base64 de menos de 40 (`dG9rZW49YWJjZGVmMTIzNDU2Nzg5`, que é `token=abcdef123456789`) passa; aceitável pela heurística, já que o aviso pede conferência. `https://api.empresa.com/v1?token=x` vira `<url>]` (resto do `[token]`): cosmético.

O que está certo, além dos quatro itens: e-mail com `+` sai; `?token=` e `?access_token=` em URL do Forge viram `[token]` e em outra URL a URL inteira sai; o nome do projeto dentro de caminho (`build/Sistema-Acao/src`, `./sistemaacao/x`, `repo/SistemaAção.git`) sai; Enter, EOF e outra resposta seguem guardando; o `gh` segue com argv em lista e `stdin` nulo.
