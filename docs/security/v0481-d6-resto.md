---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-d6-resto
commit: 1afd54b5fe5b5a25dd2a96fd490c57469228e9bb
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0481 E11.9 (#877, D6 parte a: hook `salvar`, volta E11.6)

## Gatilhos
Gatilhos: hook novo fora do sandbox, rede em hook (afrouxa a ADR 0003 item 2), push automático, controle do git (R-MAIN, R-VERIFY)

Delta lido (`forge-check parecer delta`, `9a708f86..1afd54b5`): no domínio, `hooks/salvar.py`, `docs/adr/0003-hooks-deterministicos-e-silenciosos.md` (emenda D6), `docs/regras/R-LIMITES.md` e `tests/test_hooks.py` (classe `SalvarAoParar`, 8 testes novos); fora do domínio, `changelog.d/` e `tests/mutantes/`. Já lido na rodada anterior: o resto do hook, `hooks/hooks.json`, `ler_brief`, `caminhos_de_brief` e `de_escrita`. Testes: os 31 de `SalvarAoParar` rodados no clone em `1afd54b5` (OK, junto com a sonda abaixo); o PR não tem CI registrado no head atual (`gh pr checks 877`: nenhum check), e o merge espera o CI inteiro.

Estado dos achados anteriores (parecer em `9a708f86`):
- A1 (bloqueante, config da cópia): **corrigido.** `config_permitida` (`hooks/salvar.py:57`) lê a config local sem includes antes de qualquer outro git (`:116`), com lista positiva casada inteira e origin igual à da cópia principal; `ambiente()` (`:38`) tira `GIT_*`, `XDG_CONFIG_HOME`, `BASH_ENV` e `ENV`. S1 e S2 refeitas pelo caminho inteiro do hook, e mais `Filter.x.Clean` com maiúsculas: nada roda, nada é enviado. Testes `tests/test_hooks.py:4480`, `:4505`, `:4515`. O `.git` em arquivo que aponte para fora não é mais preciso: a config conferida é a mesma que o git usa.
- A2 (bloqueante, segredo): **corrigido em parte.** Não rastreado fica fora (`:127`, teste `:4528`) e a varredura roda antes do envio (`:146`, testes `:4539`, `:4548`), mas a base dela não cobre tudo o que o push leva: A4.
- A3 (recomendado, prazo): **corrigido.** `PRAZO_TOTAL_S` (`:26`) descontado em `rodar`, teste `:4560`.

## Achados
- A4 (bloqueante) hooks/salvar.py:145 · A base da varredura sai de ref local que não diz o que o push leva: na branch nova é HEAD^ e commit local anterior com segredo sai sem varredura (S4); com a branch no remoto, refs/remotes/origin/<branch> é gravável pelo agente (S5). Base do estado real do remoto.
- A5 (recomendado) hooks/salvar.py:116 · A config da cópia é conferida uma vez, no plano; o commit, a varredura e o push vêm segundos depois. Processo do agente ainda vivo (tarefa em segundo plano, outro agente na mesma pasta das cópias) pode gravar a chave nesse intervalo. Reconferir logo antes do commit e do push.

## Sondas
- S4 · sonda_salvar2.py: branch nova não enviada, commit local de docs/b.md com segredo sintético, depois hooks/x.py mudado no escopo e o hook parado · espera: nada enviado, commit na cópia · obtido: "melhoria/x 96ab761 1 arquivo(s) enviado", docs/b.md com o segredo no remoto
- S5 · sonda_salvar2.py: branch já no remoto, commit local de docs/b.md com segredo, `git update-ref refs/remotes/origin/melhoria/x HEAD`, depois hooks/x.py mudado e o hook parado · espera: nada enviado · obtido: "1 arquivo(s) enviado", docs/b.md no remoto

## Detalhe dos achados
**A4 (média; vazamento de segredo).** Evidência: `hooks/salvar.py:144-146`. Caminho (S4, sem má-fé): o agente cria a branch na cópia, commita localmente algo com um token (fixture, log) e cai antes de enviar; no `SubagentStop` o hook faz o commit WIP, varre só `HEAD^..HEAD` e envia a branch inteira; o segredo chega ao remoto e pede rotação. O `.githooks/pre-push` varre desde o merge-base com a develop nesse caso. Caminho (S5, agente hostil ou injetado): `refs/remotes/origin/<branch>` é ref da cópia, que o sandbox deixa gravar, e o agente a avança para esconder commits da varredura; `refs/remotes/origin/develop`, sugerida pelo QA, tem o mesmo defeito. O pre-push não sofre disso porque recebe do próprio git o sha do remoto. Correção mínima: tirar a base do remoto real, `git ls-remote origin refs/heads/<branch>` (a rede já está na exceção, dentro do prazo total); presente, varrer desde esse sha, que precisa existir na cópia (`cat-file -e`, senão não envia); ausente (branch nova), varrer desde o merge-base de HEAD com o sha da branch base do brief tirado do mesmo `ls-remote` (ou o `Base-sha:` do brief), e sem ele não enviar. Testes: S4 e S5 como casos de `SalvarAoParar`, mais o mutante da base. Esforço P/M. Dono: o autor do hook (quem fez o E11.6). Converge com o A1 do review (E11.7) e o bug do QA `docs/qa/bugs/v0481-salvar-segredo-em-commit-anterior.md`; S5 acrescenta que a base não pode vir de ref local.

**A5 (baixa; corrida).** Evidência: `hooks/salvar.py:116` (uma conferência só), `:140-149` (commit, varredura e push depois, até 50 s). Caminho: o agente deixa um processo em segundo plano que espera o commit WIP aparecer e então grava `remote.origin.receivepack` ou `core.sshCommand` no `.git/config` da cópia, antes do push; o comando roda fora do sandbox. Exige agente hostil e processo sobrevivendo à parada, por isso recomendado. Correção mínima: chamar `config_permitida` de novo imediatamente antes do `commit` e do `push` (estreita a janela a milissegundos) e registrar o risco residual na emenda. Esforço P. Dono: o autor do hook.

## O que aperta, o que é neutro e o que afrouxa
- **Aperta:** a config local da cópia passa a ser conferida por lista positiva antes de qualquer git fora do sandbox (fecha o A1); não rastreado fica fora do commit; varredura de segredo antes do envio; `GIT_CONFIG_*`, `XDG_CONFIG_HOME`, `BASH_ENV` e `ENV` fora do ambiente; prazo total de 50 s; critério de reversão ampliado na emenda (comando da config da cópia rodando no hook, segredo enviado).
- **Script da varredura (julgado):** o do plugin (`VARREDURA`, `hooks/salvar.py:35`) é a escolha certa. O pre-push lê o de `origin/develop` porque roda dentro da cópia; aqui o hook roda fora do sandbox e `refs/remotes/origin/develop` da cópia é ref que o agente grava (a mesma razão do S5), enquanto o cache do plugin instalado não é gravável no sandbox. Ressalva neutra: com `--plugin-dir` apontando para uma cópia gravável, o script e o próprio hook ficam ao alcance do agente, como todos os hooks; não é deste PR.
- **Neutro:** `R-MAIN` e `R-FLUXO` (refspec explícito, nunca as branches de integração, CI do PR segue o portão); `R-CUSTO` (sem mudança no escopo, nem commit nem envio).
- **Afrouxa (declarado, à espera do dono):** (1) a ADR 0003 item 2, rede num hook; (2) o `R-VERIFY` no `core.hooksPath` vazio, agora escrito como exceção em `docs/regras/R-LIMITES.md:33` e no título do PR; o `pre-commit` do projeto não roda no commit WIP (o CI cobre). A exceção diz que o hook "repõe a varredura de segredo"; com A4 aberto, repõe em parte. Não declarado: nada.

## Riscos aceitos e ferramentas
Nenhum risco aceito. O merge espera a correção de A4 e A5 e a decisão do dono sobre os dois afrouxamentos. Ferramentas: `gitleaks`, Semgrep, `zizmor` e `actionlint` ausentes no PATH (lacuna); revisão manual, com a sonda local `sonda_salvar2.py` (subclasse de `SalvarAoParar`, repositórios em `$TMPDIR`, remoto local, sem rede).
