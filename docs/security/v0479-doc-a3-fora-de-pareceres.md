---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-doc-a3-fora-de-pareceres
commit: 0d656a84a470ccb3ea48dd0dd3aa854290fe1a2e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0478 E55.4 (documento e patch da A3 fora de docs/devops/)

Escopo: `git diff -M 5ccac0bf..0d656a84` (base `develop` 5ccac0bf). Sete arquivos, 11+/9-: renomeação de `docs/devops/v0479-sandbox-controle.{md,patch}` para `docs/engineering/`, troca do caminho em `bin/forge-testes:202`, `tests/test_sandbox_controle.py:7,32,368`, `docs/hooks.md:143`, no fragmento `changelog.d/v0479-sandbox-controle.md` e fragmento novo `changelog.d/v0479-doc-a3-fora-de-pareceres.md`.

## Gatilhos
Gatilhos: controle do Forge (trava de escrita do sandbox, A3; teste que a prova)

## Achados

## Sondas

## Detalhe dos achados
Nenhum controle mudou de sentido:
- O patch é idêntico byte a byte (rename 100%; sha256 `28d1a5348ac6bdadb2f7ae3dc243677355166bfcbb109a1a97aaf193dc99b6bc` igual em `5ccac0bf:docs/devops/…patch` e em `docs/engineering/…patch`). O `.claude/settings.json` não muda no diff; o `denyWrite` em vigor (`.claude/settings.json:23-27`) já traz `.forge/`, `.git/forge/run` e `~/.forge/maquina` desde 169d5783, então o `git apply --check` falhar hoje é esperado (já aplicado) e o teste usa o arquivo em vigor (`tests/test_sandbox_controle.py:44-45`).
- O documento `.md` muda só as três menções de caminho (similaridade 93%); a lista de controle e os comandos seguem os mesmos. A linha de `docs/hooks.md:143` só troca o caminho.
- O teste segue achando o patch: `PATCH` em `tests/test_sandbox_controle.py:32` aponta para `docs/engineering/`, e `test_o_patch_so_acrescenta_dois_caminhos_ao_denywrite` (que lê o arquivo) passa. O mapa de testes afetados (`bin/forge-testes:202`) segue disparando `test_sandbox_controle` quando o patch muda.
- Sem referência órfã: `git grep "devops/v0479-sandbox-controle" HEAD` vazio.
- Posse de escrita: `docs/devops/` é só do devops (`hooks/conformidade.json:74`); `docs/engineering/` não tem dono no hook. Sem caminho de ataque realista: o patch já está aplicado, o arquivo virou registro, e uma edição dele que fuja dos dois caminhos derruba `test_o_patch_so_acrescenta_dois_caminhos_ao_denywrite` no CI. O precedente `docs/engineering/v0479-bp3-s2-container.patch` já vive ali.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Provas locais: `python3 -m unittest tests.test_sandbox_controle.Estrutura` (6 testes, OK) e `git apply --check` (recusa por já aplicado). A suíte inteira fica para o CI do PR (sem bateria local, por brief). Ferramenta ausente: `gitleaks` fora do PATH (diff sem segredo, só caminhos).
