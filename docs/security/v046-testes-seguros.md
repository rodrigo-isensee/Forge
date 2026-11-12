---
tipo: revisao-seguranca
contrato: 1
pedido: v046
branch: melhoria/testes-seguros
commit: 8fc857c94212789ba54f2db909cd09bb9325525f
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-11
---
# Review de segurança: v046 (E2.2, testes seguros)

Escopo: `git diff origin/develop...ebdde388` (base ed021b71), 3 commits: 9788148f (claude falso no `--simular`), b7e42b80 (travessia `../../x.md` com cwd controlado), ebdde388 (fragmento do changelog). Só leitura da branch (Z10); suíte não rerrodada; uma sonda local sobre o script da branch extraído para `$TMPDIR`.

## Gatilhos
`R-CUSTO` (teste não pode tentar rede para API paga) e a fronteira de leitura do `forge-check brief` (travessia e link para fora das raízes de brief).

## Achados
- A2 (recomendado) scripts/preparar-estacao.sh:247 · resta, no --simular, a leitura de /etc/os-release e /proc/version (estado do sistema, sem rede, custo nem escrita); o dpkg-query já é falso. Registrar a fronteira do item ou falsificar a checagem do sistema.

## Sondas

## Revalidação (volta 1, head 8fc857c9)
Delta lido: `git diff ebdde388..8fc857c9` (1 commit, 8fc857c9: `tests/test_forge.py`, `tests/test_pedido_fora.py`, fragmento do changelog). Estado dos achados:
- A1 resolvido. `tests/test_forge.py:1340-1347` contamina de propósito o ambiente com `NVM_DIR` apontando para um `nvm.sh` sentinela fora do HOME falso, fixa `NVM_DIR=<home>/.nvm` no `env.update` e afirma que a marca não existe (`:1351`); o teste do `--container` (`:1393`) recebeu a mesma fixação. Sonda de revalidação: `NVM_DIR=<tmp>/nv` (com `nvm.sh` que grava `SOURCED`) exportado ao rodar `tests.test_forge.PrepararEstacao` e `tests.test_pedido_fora` · espera: 0 falhas e nenhuma marca · obtido: 31 testes OK, só o `nvm.sh` no diretório, sem `SOURCED`. A S1 da rodada anterior (que provou o bloqueante em ebdde388) deixa de valer como prova de defeito aberto.
- A2 parcialmente resolvido, segue recomendado: `dpkg-query` falso (`tests/test_forge.py:1331-1333`, sai 1, o script lista os pacotes como faltantes e só imprime o `sudo apt-get`); permanece a leitura de `/etc/os-release` e `/proc/version` (`scripts/preparar-estacao.sh:247`), informativa.
- A3 resolvido. O comentário (`tests/test_pedido_fora.py:83-84`) atribui o rc 2 à leitura que falha, e a asserção nova (`:91-92`) exige a linha `brief: não consegui ler` (emitida em `bin/forge-check:8288`), então o teste não passa por outro motivo.
Sem achado novo no delta: os arquivos falsos e a sentinela ficam no diretório temporário do teste; nenhuma rede, segredo nem escrita fora dele.

## Detalhe dos achados
Histórico da rodada de ebdde388 (estado atual na seção de revalidação acima).
**A1.** Evidência: `tests/test_forge.py:1335-1336` monta o ambiente com `ambiente_limpo()` (que só tira `GIT_*`, `FORGE_*` e `CLAUDE_PROJECT_DIR`, `tests/test_forge.py:677-679`) e troca `HOME` e `PATH`; `scripts/preparar-estacao.sh:269` usa `NVM_DIR="${NVM_DIR:-$HOME/.nvm}"`, então um `NVM_DIR` exportado no shell do desenvolvedor (o instalador do gerenciador de versões grava esse `export` no perfil) vence o HOME temporário; as linhas 274-281 fazem `source` desse arquivo e chamam `nvm ls`. A sonda S1 provou o caminho: o arquivo plantado foi carregado e executado. Caminho de risco: não há atacante externo (o arquivo é do próprio desenvolvedor), por isso a severidade é baixa; mas é defeito provado contra o requisito literal do item TESTE-FORA-DO-CLONE ("nenhum teste lê arquivo fora do clone") no mesmo teste que esta entrega diz ter deixado de depender do ambiente (fragmento `changelog.d/testes-seguros.md`), e o teste passa a executar código de fora do clone. No ambiente desta revisão `NVM_DIR` não está exportado, por isso a suíte local e o CI não mostram o efeito. Correção mínima: no `env.update` da linha 1336, acrescentar `NVM_DIR=str(home / ".nvm")` (ou `env.pop("NVM_DIR", None)`); opcional, afirmar que nada em `home/.nvm` foi criado (já coberto pelo laço das linhas 1345-1346). Esforço P. Dono: tech-lead.

**A2.** Evidência: `scripts/preparar-estacao.sh:247` lê `/etc/os-release` e `/proc/version`; `:256` roda `dpkg-query`, que lê a base de pacotes do sistema. Sem rede, sem custo, sem escrita (o `sudo apt-get` é impresso, não executado, no modo simular). Severidade informativa. Correção mínima: incluir `dpkg-query` na lista de falsos do teste (linha 1325, `("sudo", "curl", "apt-get", "gh")`, que passaria a ser `("sudo", "curl", "apt-get", "gh", "dpkg-query")`), ou registrar no pedido que leitura de estado do sistema operacional fica fora da fronteira do item. Esforço P. Dono: tech-lead.

**A3.** Evidência: em `bin/forge-check` (`cmd_brief_conferir`), o brief é tentado primeiro relativo ao cwd; só se não existir cai em `caminho_de_brief`, que recusa `../../x.md` porque `dentro_da_raiz` resolve `<raiz de brief>/../../x.md` para fora da raiz; a seguir o `read_bytes` do caminho relativo ao cwd falha e sai 2. O teste novo é correto e útil: o alvo plantado em `self.tmp/x.md` é exatamente onde a junção ingênua `~/.forge-contrib/../../x.md` cairia, e a ausência de `origem:` e `conferencia-brief-regra:` prova que ele não foi lido; o cwd em `c1/c2/c3` acaba com a leitura fora do clone que o teste antigo fazia (cwd no clone). Só o comentário da linha 84 atribui o rc 2 à regra de raízes; afirmar a linha de erro deixaria o motivo explícito. Severidade informativa. Esforço P. Dono: tech-lead.

**Conferido sem achado.** Commit 9788148f: o `claude` falso fica no início do PATH; o `export PATH="$HOME/.local/bin:$PATH"` do script (linha 311) aponta para o HOME temporário, onde não há `claude`, então o falso continua vencendo; a asserção `claude_log == ["plugin list"]` prova que nenhuma outra chamada (marketplace add, plugin install) foi feita de verdade, e a saída `[simular] claude plugin install` prova que o ramo do plugin ausente foi percorrido. Nenhuma rede para API paga resta neste teste (`R-CUSTO`). Commit b7e42b80: `rodar_em` reproduz `rodar` (mesmo HOME temporário, mesma escolha entre script direto e cache) só mudando o cwd; sem escrita fora de `self.tmp`. Fragmento do changelog sem dado sensível.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff e sonda local com bash e arquivos falsos em `$TMPDIR`; gitleaks, zizmor, actionlint e semgrep ausentes do PATH (lacuna registrada; o diff não toca workflow nem traz segredo à leitura).
