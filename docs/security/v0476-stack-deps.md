---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0476-stack-deps
commit: 95605e662d55742e4af9b64e640878ea0bfa085b
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0474 (E3.248, branch melhoria/v0476-stack-deps)

Revalidação por delta da rodada que reprovou no head 89f7ef2f (E3.237). Delta lido: `forge-check parecer delta docs/security/v0476-stack-deps.md`, intervalo 89f7ef2f..95605e66 (`bin/forge-copia`, os dois `stacks/<stack>/instalar.json`, os dois `pronto.md`, ADR 0001; teste e mutante fora do domínio, lidos só para conferir a prova).

## Gatilhos
Gatilhos: execução de comando externo por ferramenta do Forge, cadeia de suprimentos (dependências de terceiros instaladas na cópia), segredo no ambiente (token do bot)

## Achados
- A3 (recomendado) bin/forge-copia:50 · a lista fixa deixa passar GIT_CONFIG_PARAMETERS (config do git injetada; nesta estação traz um helper de credencial) e variáveis com TOKEN no nome vindas da estação; somar GIT_CONFIG_PARAMETERS e tirar todo nome com TOKEN, SECRET ou PASSWORD.
- A4 (recomendado) stacks/python/instalar.json:1 · a instalação do pacote local (e de pacote só de fonte do lockfile) usa o isolamento de build do gerenciador, que baixa o backend de build do índice sem hash; resíduo de A1, estreito (só o backend de build) e já sem o token.

## Sondas

## Detalhe dos achados
**A1 (bloqueante na rodada anterior): corrigido.** `stacks/python/instalar.json:1` detecta só o lockfile e instala com exigência de hash em toda linha e sem resolver dependência fora dele, depois o pacote local sem dependências; `stacks/node-react/instalar.json:1` detecta o lockfile e instala congelado. Sonda: cópia com só os manifestos das duas stacks → "nenhuma stack detectada (sem lockfile...)", rc 0, nenhum comando rodou. O teste `test_todo_instalar_json_usa_modo_congelado_ou_hash_e_detecta_o_lockfile` (`tests/test_forge_copia.py`) trava o formato para stack futura. O `pronto.md` de cada stack fixa o nome do lockfile e a ADR 0001 registra o contrato.

**A2 (recomendado na rodada anterior): corrigido.** `bin/forge-copia:48-52` (`env_sem_credencial`) e `:78` (`env=`). A lista tirada confere, item por item, com a correção pedida: `GH_TOKEN`, `GITHUB_TOKEN`, `GH_ENTERPRISE_TOKEN`, `GITHUB_ENTERPRISE_TOKEN`, `GIT_ASKPASS`, `SSH_AUTH_SOCK`, `GIT_CONFIG_COUNT` e todo `GIT_CONFIG_KEY_<n>` e `GIT_CONFIG_VALUE_<n>` (por prefixo). O resto do ambiente segue (`test_ambiente_da_instalacao_mantem_o_resto`). Sonda S1 refeita no head 95605e66 (mesma entrada da rodada anterior, mais `GITHUB_TOKEN`, `GIT_ASKPASS`, `SSH_AUTH_SOCK` e `GIT_CONFIG_COUNT/KEY_0/VALUE_0` no ambiente): obtido `sem_token`, rc 0; nenhuma dessas variáveis chegou ao processo.

**A3, lista fixa incompleta** (`bin/forge-copia:50`). A mesma sonda listou os nomes (nunca os valores) do que ainda chega ao comando com credencial no nome ou na função: `GIT_CONFIG_PARAMETERS` (forma antiga de config injetada do git, mesma classe dos `GIT_CONFIG_KEY_<n>` já tirados; nesta estação carrega a chave de um helper de credencial do proxy) e três variáveis com `TOKEN` no nome postas pelo ambiente da estação (agente do workspace, mensageria, editor). A falha é da lista que eu pedi na rodada anterior, não da implementação. Caminho: dependência comprometida dentro de versão já fixada no lockfile lê essas variáveis; o token do bot (o ativo principal) já não chega. Severidade: baixa (exige comprometer versão fixada; o valor depende da estação). Correção mínima: somar `GIT_CONFIG_PARAMETERS` ao conjunto e tirar todo nome que contenha `TOKEN`, `SECRET` ou `PASSWORD` (maiúsculas), com o teste da sonda cobrindo um nome de cada padrão. Esforço P. Dono: `forge:devops-engineer`. Não devolve (R-REVIEW: recomendação, critério não mudou).

**A4, backend de build sem hash** (`stacks/python/instalar.json:1`, terceiro comando; também o segundo, quando o lockfile tem pacote só de fonte). O isolamento de build do gerenciador instala os requisitos de build do índice público, sem passar pelo lockfile nem pela exigência de hash. Caminho: versão maliciosa de um backend de build publicada no índice roda na criação de cada cópia, agora sem o token do bot no ambiente (A2). Severidade: baixa (backends de build são poucos e muito vigiados; impacto limitado à estação, sem o token). Correção mínima, proporcional: documentar no `pronto.md` da stack que o lockfile inclua os requisitos de build com hash e passar ao gerenciador a opção que desliga o isolamento de build no comando do pacote local; ou aceitar o resíduo e registrá-lo no `seguranca.md` da stack. Esforço P. Dono: `forge:devops-engineer`.

## Revalidação
Delta 89f7ef2f..95605e66 lido inteiro no domínio (citado acima); o que estava correto na rodada anterior (origem do `instalar.json` no plugin, argv sem shell, `cwd` na cópia confinada, rede só pelo filtro do sandbox) não foi tocado pelo delta. Estado: A1 corrigido, A2 corrigido, A3 e A4 novos e recomendados (vistos na sonda e na leitura do comando novo).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Provas rodadas no head 95605e66: `python3 -I tests/catraca.py --base origin/develop` (rc 0); `python3 -m unittest tests.test_forge_copia` (30 testes, OK); `python3 -m unittest tests.test_ambiente_git` (20 testes, OK); sonda S1 e a sonda sem lockfile. CI: a branch não tem PR, sem rodada no head 95605e66; a suíte inteira fica para o CI do PR, que é obrigatório para o merge. Ferramentas: `gitleaks`, `osv-scanner` e `semgrep` não usados (o delta não adiciona dependência nem segredo; revisão por leitura e sonda).
