---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-ae3-1-controle
commit: 59ad2edc89d3ae5d030c994c1c2b0bd67fae90c0
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-22
---
# Review de segurança: v0478 (E108.6, revalidação da AE3.1 `bin/forge_controle.py`)

Volta única sobre o parecer reprovado da E108.3 (head 98882c49, no git). Head 59ad2edc.

Gatilhos: controle do Forge que roda git na pasta de controle e decide o que entra no commit, chamado pelo relógio da AE3.2 fora do sandbox (D7).

## Delta lido
`forge-check parecer delta` de 98882c49..59ad2edc, sem o que veio da develop: no domínio só `bin/forge_controle.py` (lido inteiro, 145 linhas). Fora do domínio: o fragmento do changelog, os mutantes, `tests/pesos-d4.json` e `tests/test_forge_controle.py` (rodado, não relido).

## Achados anteriores
- A1 (bloqueante): corrigido. `_comando_na_config` (`bin/forge_controle.py:60-72`) lê `git config -z --list` (todas as origens, com includes) antes de qualquer `status`/`add`/`commit` e sai `nao-verificavel` com `core.fsmonitor` ou `commit.gpgsign` diferentes de falso, com `filter.<nome>.clean|smudge|process`, `gpg.program`, `gpg.<formato>.program` e `gpg.ssh.defaultkeycommand`. A chave vem em minúsculas (inclusive a subseção do filtro, `:67`); a chave sem valor conta como ligada; nada na config é trocado. Sondas refeitas no head, num repositório descartável em `$TMPDIR`: S1 (`core.fsmonitor`) `('nao-verificavel', 'comando na config core.fsmonitor')`, 0 execuções; S2 (`commit.gpgsign` + `gpg.program`) `nao-verificavel`, 0 execuções; S3 (`filter.Z.clean`, com caixa alta, e `*.md filter=Z`) `('nao-verificavel', 'comando na config filter.z.clean')`, 0 execuções. Variantes a mais: `core.fsmonitor` só por `include.path`, `gpg.format=ssh` com `gpg.ssh.program` e `commitGpgSign=yes`, e `[core] fsmonitor` sem valor: todas `nao-verificavel`, 0 execuções.
- A2 (recomendado): corrigido. `:111-117` pede `--git-path` relativo (o absoluto resolvia o link), abre com `O_WRONLY|O_CREAT|O_NOFOLLOW` e `0o600` e sai `nao-verificavel` no erro. Sonda: link em `.git/forge-controle.lock` para fora da pasta deu `('nao-verificavel', 'trava ilegível: Too many levels of symbolic links')` e o destino não foi criado.
- A3 (recomendado): corrigido, com o QA A1. `SEGREDO` (`:23-24`) soma `.netrc`, `credentials*`, `secrets*`, `.kdbx`, `.jks`, `.keystore`, `.p8`, com `re.IGNORECASE`. Conferidos `docs/CREDENTIALS.json`, `docs/x/Secrets.yml`, `docs/.NETRC`, `docs/a.KDBX`, `docs/b.Jks`, `docs/c.keystore`, `docs/d.P8`, `docs/.ENV.local` e `docs/ID_RSA` (recusados) e `docs/notas.md` e `docs/credenciais.md` (passam).

**Conferido e sem achado.** Outras chaves que rodam comando (`core.editor`, `core.pager`, `diff.external`, `diff.<x>.textconv`, `trailer.<x>.command`, `core.sshCommand`, `credential.helper`) não disparam em `status`, `add` nem `commit -m` sem terminal, e a manutenção automática segue desligada por `-c` (`:29`). A checagem da config fica sob a trava; a janela entre ela e o commit continua residual aceitável (quem grava a config na janela já tinha o mesmo acesso antes). Efeito de disponibilidade, não de segurança: uma estação com `filter.lfs.*` ou `commit.gpgsign` na config global deixa todo `salvar` `nao-verificavel`; é o lado seguro, mas a AE3.2 deve mostrar o motivo ao usuário em vez de falhar calada. Um FIFO plantado no lugar da trava travaria o `open` sem `O_NONBLOCK`; sem ganho para quem já escreve no `.git`, fica como nota.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodados: `tests.test_forge_controle` (41 testes, OK) e as sondas acima. A suíte inteira fica para o CI do PR (o brief manda não rodar a suíte local; ainda não há PR nem execução de CI para esta branch). SAST e varredura de segredos não estão no PATH: lacuna registrada.
