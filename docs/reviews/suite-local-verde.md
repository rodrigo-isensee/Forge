---
tipo: review
contrato: 1
pedido: suite-local-verde
branch: melhoria/suite-local-verde
commit: 124c521ed00fca3280ea1e88c02f877a9e28aca6
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-22
---
# Review: suite-local-verde

Pedido FIX-SUITE-LOCAL-PR (E1.1), sobre a entrega de FIX-SUITE-LOCAL. Base `af79bef`, 3 commits (`b8aeba3`, `86769ff`, `124c521`). Feito por uma instância que não implementou (`R-REVIEW`). Primeira rodada, sem delta.

## Achados

## Evidência de execução (ambiente: Python 3.14.4, shellcheck 0.11.0, sandbox)
- Suíte completa no HEAD `124c521`: `Ran 1594 tests in 344.380s · OK (skipped=1)`. O teste pulado é `test_changelog.FragmentoTemONomeDaBranch`, porque a worktree de review está destacada (`branch 'HEAD' não é de melhoria`). O fragmento se chama `changelog.d/suite-local-verde.md`, que é o nome da branch.
- `shellcheck .githooks/pre-push templates/projeto/.githooks/pre-push`: rc=0.
- Cada commit revertido sozinho (`git revert --no-commit`, aplica sem conflito) e `tests.test_pre_push_shellcheck tests.test_hooks tests.test_changelog`:
  - sem `b8aeba3`: só `test_shellcheck_no_hook` falha (1).
  - sem `86769ff`: só `test_erro_interno_com_lista_de_permissao_falha_fechado [forge-dev:aq]` (`0 != 2`) e as duas fixtures `contrib-falha-fechada-pela-raiz-cwd-home-bloqueia` (`0 != 2`) e `-cwd-wt-bloqueia` (a mensagem `R-CONTRIB` em vez de `R-CONFORMIDADE: erro interno`) falham (3).
  - sem `124c521`: `OK (skipped=1)`.
  - Conclusão: os três commits são independentes e cada um corrige só o que diz corrigir. Revertido sozinho, cada um deixa a suíte verde no CI (3.12 e shellcheck 0.10). Aqui, na 3.14 com shellcheck 0.11, só o teste que ele corrige volta a falhar. O `124c521` sai sem efeito na suíte.

## Parecer
**Aprovado.** A correção ataca a causa e não afrouxa controle: o hook `conformidade` não muda, `tests/config.json` não muda, nenhum teste é desligado nem perde asserção.

- `b8aeba3` `.githooks/pre-push:242`: a diretiva continua local à função `parar` e mantém o motivo na mesma linha (o `test_diretiva_shellcheck_disable_tem_motivo` segue valendo). Ela só ganha o código novo da 0.11 (SC2329, função nunca chamada, que substitui o SC2317 neste caso). O shellcheck não valida código desconhecido em `disable`, então a 0.10 do CI aceita a linha. O modelo `templates/projeto/.githooks/pre-push` não tem a diretiva e passa sem ela.
- `86769ff` `tests/apoio_pathlib_312/sitecustomize.py`: reproduz fielmente o `Path.exists` da 3.12. Levanta o `OSError` fora de ENOENT, ENOTDIR, EBADF e ELOOP e devolve False no `ValueError`. Para `is_dir` e `is_file`, faz o mesmo sobre `os.stat` com `S_ISDIR` e `S_ISREG`. Só entra no processo do hook por `PYTHONPATH` e só em 3 casos: a chave `pathlib_312` das duas fixtures e o teste de lista de permissão. O lançador (`sys.executable -c`) e o `subprocess` direto não usam `-I`, `-E` nem `-S`, então o `sitecustomize` carrega. O lançador põe `hooks/` em `sys.path` sozinho, então trocar o `PYTHONPATH` não tira nada do hook. Fica sombreado o `sitecustomize` do sistema (`/usr/lib/python3.14/sitecustomize.py`, gancho do apport), sem efeito no teste.
- O teste de falha fechada prova na 3.12 o que provava antes? **Sim.** Na 3.12 o módulo apenas reinstala a semântica que a 3.12 já tem, então o caminho de execução do hook é idêntico ao do `af79bef`. Na 3.14 ele recria o mesmo gatilho (PermissionError, ENAMETOOLONG) e prova o mesmo mecanismo: erro interno com papel de lista de permissão bloqueia (`erro interno do hook conformidade para o papel aq`), o outro papel libera e push com erro interno bloqueia (`R-CONFORMIDADE: erro interno`). As asserções de código e de stderr não mudaram. Não rodei a 3.12 aqui (o sandbox só tem a 3.14): esta conclusão vem da leitura da semântica da 3.12, e a prova de execução fica com o CI do PR.
- `124c521` `changelog.d/suite-local-verde.md`: o fragmento fica em `### Corrigido`, com o nome da branch, e o `CHANGELOG.md` não foi editado.
- Commits: Conventional Commits em português, um por mudança coerente, mensagens claras (checklist 9). `R-NEUTRO`: nada específico de projeto. `R-CUSTO`: nada pago. `R-VERIFY`: nada contorna o pre-push.

Observações, sem bloquear:
- **Para o `security-engineer` (E1.3), cartão:** o vermelho da 3.14 mostrava uma diferença real do hook em produção, que roda com o `python3` da máquina (`#!/usr/bin/env python3`, 3.14 nesta estação). Sem o apoio, a fixture `cwd-home` **libera** (rc 0) o `cd <nome longo>; git push origin HEAD`, que na 3.12 bloqueia por erro interno. O teste de lista de permissão libera o `aq` em `docs/propostas/ilegivel/sub/x.md`. Pela minha leitura, as duas liberações são decisões corretas e não um furo:
  - o caminho de nome longo não existe, o `cd` falha e o push roda em `~`, que não é repositório;
  - `docs/propostas/` está na `escrita_permitida` do `aq`.

  Ainda assim, a branch cobre o mecanismo de falha fechada e não cobre a decisão da 3.14 sobre essas entradas. Cabe ao parecer de segurança confirmar essa leitura ou pedir uma fixture que fixe a decisão da 3.14 sem o apoio. Também não houve review de lógica de segurança aqui, conforme os limites do papel.
- **Recomendado, para o futuro:** se o gatilho de erro interno por `Path.exists` sumir também do CI (quando ele subir para 3.13 ou 3.14), o apoio continua garantindo o teste. Vale registrar no módulo quando ele pode sair: no dia em que o hook tiver um gatilho de erro interno que não dependa da versão do Python.

Devops (`docs/devops/`) e segurança (`docs/security/`) têm parecer próprio nesta rodada (E1.2 e E1.3) e não são refeitos aqui.
