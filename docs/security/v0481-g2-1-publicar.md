---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-g2-1-publicar
commit: c78bfe22110b57436b64bcc2866af1c03542938e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0481 (E6.20, #878, G2.1 `forge-check parecer publicar`), volta por delta

Revalidação por delta da rodada que reprovou em 0048e0c4 (E6.16; texto no git). Delta lido: `forge-check parecer delta` deste arquivo e `git diff 0048e0c4..c78bfe22` (19 arquivos; no domínio `bin/forge-check`, `bin/forge-testes`, `bin/forge_pareceres.py`, `hooks/conformidade.py`, `tests/test_hooks.py` e as 5 fixtures `contrib-publicar-*`). Veredito: o delta só aperta ou é neutro; A1 corrigido e provado, A2 resolvido.

## Achados

## Sondas

## Gatilhos
Gatilhos: controles-do-forge, autorizacao, ci-cd.

## Achados anteriores
- A1 (bloqueante): corrigido. `hooks/conformidade.py:2465` chama `forge_check_publica` (`:2560-2568`) em toda linha que roda o `forge-check`; na sessão de projeto, `parecer publicar` com alvo no Forge (`GH_REPO` da linha ou do `export`, a pasta do `--raiz` ou do `cd`) barra por R-CONTRIB, pela mesma `alvo_do_forge` do `gh_contrib`; a sessão do Forge não passa. Fixtures V0481-PUBLICAR (3 libera, 2 recusa) e `test_fixtures_do_publicar` verdes aqui; mutantes M31, M32 e M33 mortos.
- A2 (recomendado): resolvido. `test_c15_aceite_de_outro_commit` (`tests/test_forge_pareceres.py:328`) recusa o aceite com `commit:` de outro commit; a comparação fica em `aceite_do_usuario`, função anterior ao pedido.

## Sondas rerodadas (gh falso; nenhuma chamada ao GitHub)
Pela máquina de `tests/test_hooks.py` (`rodar_dados`), sessão de projeto, alvo `GH_REPO=<forge>` salvo onde dito. S1 (`gh pr comment`) e S2 (`forge-check parecer publicar`), que provaram o A1: agora código 2, `R-CONTRIB`. Variações de contorno, todas código 2: `env GH_REPO=`, `export GH_REPO=...;`, `bash -c '...'`, `python3 <caminho>/forge-check`, caminho absoluto do `bin/forge-check`, `timeout 60`, `xargs`, `env -S`, `GH_REPO` como URL, `--raiz=<clone do Forge>`, `--raiz` depois do subcomando, `cd <clone do Forge> &&`. Corpus de legítimos, código 0: publicar no próprio projeto, `parecer delta` com `GH_REPO=<forge>`, publicar na sessão do Forge. A abreviação `--ra` é ambígua no argparse (`--raiz` e `--raiz-pedidos` nos dois parsers, `bin/forge-check:10729-10735`) e não contorna.

## O delta, mudança por mudança
- `bin/forge_pareceres.py:78-103`: o agregado `pareceres` vai a `pending` antes do status do papel e é recalculado depois; falha em qualquer passo deixa o mais novo em `pending`, nunca um `success` velho (falha fechada; `test_falha_entre_o_papel_e_o_agregado_nao_deixa_success`, mutante M29). A recusa diz o que já ficou gravado (M30). O `except` só converte em `Recusa` erros de leitura da resposta; não libera nada. Aperta.
- `bin/forge-check:3751`: sai o ramo `is_absolute`; `raiz / arquivo` com `arquivo` absoluto dá o próprio `arquivo` (pathlib), equivalente. `texto` passa de `None` a `""`; arquivo ausente ou sem frontmatter cai na mesma recusa pelo caminho (`test_arquivo_ausente`, `test_sem_frontmatter`, M21, M28). Neutro.
- `bin/forge-testes:153`: só um espaço na tupla. Neutro.
- `hooks/conformidade.py`: só acrescenta a trava; nenhuma regra, fixture nem entrada de `PROTEGIDOS`, `conformidade.json` ou `catraca` sai ou afrouxa. Aperta.
- Mutantes (`tests/mutantes/v0481-g2-1-publicar-4.json` a `-6.json`): M21 a M33 mortos no `forge-mutante` local, no head c78bfe22.

Continua valendo a condição da rodada anterior para o G2.2 (primeira leitura de status): M1.4, M4.1, M4.2, M9.2 (hook), M9.3, M10.1 e M18.1 antes dela, e o filtro `isCrossRepository` no `pr_aberto` (`bin/forge_pareceres.py:48`).

## Suíte e CI
CI do head c78bfe22 (#878) em andamento na leitura: `bateria (passos)`, `bateria (verificações longas)` e `instalação` verdes; `bateria (pareceres)` e `catraca` em falha esperada (pareceres e rótulo ainda ausentes no head); partes da suíte pendentes. Rodei aqui `tests.test_forge_pareceres` (35 OK), `test_hooks.Hooks.test_fixtures_do_publicar` (OK), o `forge-mutante` das três specs e as sondas.

## Riscos aceitos e ferramentas
Nenhum risco aceito. `gitleaks`, `semgrep`, `zizmor`, `actionlint` e `osv-scanner` ausentes do PATH: lacuna registrada, nada instalado (`R-CUSTO`). Revisão estática; nenhuma chamada de escrita à API.
