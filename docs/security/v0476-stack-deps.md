---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0476-stack-deps
commit: 89f7ef2f801d5a9d93d973497e7df5caf658027f
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0474 (E3.237, branch melhoria/v0476-stack-deps)

Escopo: diff a1674911..89f7ef2f em `bin/forge-copia` (`--instalar`), os dois `stacks/<stack>/instalar.json` novos, a frase da skill `trabalho-em-paralelo` (que torna `--instalar` o padrão das cópias), testes e mutantes. Pergunta do portão: a instalação automática abre caminho que antes não havia? Resposta: sim, num ponto (A1).

## Gatilhos
Gatilhos: execução de comando externo por ferramenta do Forge, cadeia de suprimentos (dependências de terceiros instaladas na cópia), segredo no ambiente (token do bot)

## Achados
- A1 (bloqueante) stacks/python/instalar.json:1 · instala dependências sem lockfile nem hash conferido (instalação editável resolve as versões na hora), contra o requisito da própria stack (stacks/python/seguranca.md:15); com o --instalar padrão, toda cópia baixa e executa versões não fixadas, com o token do bot no ambiente (A2).
- A2 (recomendado) bin/forge-copia:71 · subprocess.run herda o ambiente inteiro: código de instalação de terceiros lê o GH_TOKEN do bot (sonda S1). Passar env= sem as variáveis de credencial listadas no detalhe; reduz o impacto de A1 e de qualquer dependência comprometida.

## Sondas
- S1 · cópia de bin/forge-copia com stacks/s/instalar.json {"detecta":["marca"],"comandos":[["sh","-c","test -n \"$GH_TOKEN\" && echo TOKEN_VISIVEL || echo sem_token"]]}, GH_TOKEN=fake, instalar(<cópia com marca>) · espera: sem_token · obtido: TOKEN_VISIVEL, rc 0

## Detalhe dos achados
**O que está correto (sem achado).**
- Origem do `instalar.json`: `bin/forge-copia:50` resolve `stacks/` a partir de `os.path.realpath(__file__)`, isto é, do plugin instalado, nunca da cópia nem do projeto. O projeto não troca o arquivo; quem o troca é quem publica o plugin (PR até a `main`, `R-MAIN`) ou quem já escreve no cache do plugin (que já executaria o próprio `bin/`). Rodando o `bin/forge-copia` de um clone do Forge, as stacks vêm daquela branch: mesma confiança do código que está rodando, nada novo.
- Execução: argv em lista, sem shell (`bin/forge-copia:71`); o `instalar.json` exige lista de strings não vazia (`:59`), e o inválido sai 1 (`:62-64`). `cwd=copia` (`:71`): os caminhos relativos do comando resolvem dentro da cópia, que já está confinada à pasta liberada (checagem anterior, sem mudança). O `detecta` vem do plugin e só passa por `os.path.exists`; não há escrita fora da cópia.
- O código do próprio projeto que a instalação executa (script do pacote raiz, backend de build do pacote local) é do mesmo repositório que o agente já testa e executa na cópia: sem fronteira nova.
- Rede: só o gerenciador de pacotes da stack, pelo filtro de rede do sandbox; o Forge não abre conexão própria.
- A stack de front instala com lockfile congelado (`stacks/node-react/instalar.json:1`), conforme o `seguranca.md` dela: versões fixadas pelo lockfile do projeto.

**A1, instalação sem lockfile na outra stack** (`stacks/python/instalar.json:1`). O segundo comando instala o pacote local em modo editável e resolve as dependências de terceiros pelas faixas do manifesto, no índice público, sem lockfile e sem hash. O `seguranca.md` da mesma stack (`stacks/python/seguranca.md:15`) exige lockfile versionado e instalação com hash conferido: o pacote da stack contradiz o próprio requisito. Caminho de ataque: quem publica (ou toma a conta do mantenedor de) uma versão nova de uma dependência dentro da faixa declarada, ou de uma dependência transitiva, tem o código dela executado na instalação (pacote só de fonte roda o build na máquina) em cada cópia criada por agente, sem humano no meio, com rede e com o token do bot no ambiente (S1); ganha o token (escrita nos repositórios do bot, fora das branches protegidas) e leitura do que o sandbox deixa ler. Antes desta mudança a instalação era um passo deliberado; com a skill pondo `--instalar` como padrão (`skills/trabalho-em-paralelo/SKILL.md:11`), passa a ser automática em toda cópia. Severidade: média (exige comprometer o índice ou um mantenedor, impacto no token e na estação). Correção mínima: o `instalar.json` dessa stack só instala a partir do lockfile com hash (modo que exige hash em toda linha, sem resolver dependência fora do lockfile) e instala o pacote local sem dependências; o `detecta` aponta o lockfile, não o manifesto, para que projeto sem lockfile não instale nada e receba o aviso de "nada a instalar" (ou uma recusa explícita com o motivo). Se a stack ainda não fixa o nome do lockfile, fixar no `pronto.md` dela, junto. Teste: cópia com só o manifesto não roda comando; cópia com lockfile roda o comando com a exigência de hash no argv. Esforço P. Dono: `forge:devops-engineer` (autor de E3.235).

**A2, ambiente herdado** (`bin/forge-copia:71`). Sem `env=`, o processo de instalação e tudo o que ele executa (scripts de instalação, builds de pacote) recebem o ambiente do agente, que no Forge carrega o token do bot (`bin/forge-init:118`). Severidade: baixa isolada (com lockfile fixado e scripts de terceiros bloqueados pelo gerenciador, o código executado é o revisado no lockfile), média somada a A1. Correção mínima: passar `env=` com o ambiente sem as variáveis `GH_TOKEN`, `GITHUB_TOKEN`, `GH_ENTERPRISE_TOKEN`, `GITHUB_ENTERPRISE_TOKEN`, `GIT_ASKPASS`, `SSH_AUTH_SOCK`, `GIT_CONFIG_COUNT` e todas as `GIT_CONFIG_KEY_<n>` e `GIT_CONFIG_VALUE_<n>`; teste com a sonda S1 esperando `sem_token`. Esforço P. Dono: `forge:devops-engineer`. Fica como recomendação porque, corrigido A1, o caminho exige comprometer versão já fixada no lockfile.

## Revalidação
Primeira rodada; sem delta anterior.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Provas rodadas: `python3 -I tests/catraca.py --base origin/develop` (rc 0); `python3 -m unittest tests.test_forge_copia` (26 testes, OK); sonda S1. CI: sem rodada no head 89f7ef2f (a branch ainda não tem PR); a suíte inteira fica para o CI do PR. Ferramentas: `gitleaks`, `osv-scanner` e `semgrep` não usados (o diff não adiciona dependência nem segredo; a revisão foi de leitura e sonda).
