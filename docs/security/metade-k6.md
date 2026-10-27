---
tipo: revisao-seguranca
contrato: 1
pedido: metade-k6
branch: melhoria/metade-k6
commit: 053f4162e17079a796ee77ef71e5d0b80bf3b261
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-27
---
# Review de segurança: metade-k6

Escopo: diff `ce1a341b9874143cf3fb8c998a76eb473adc1df3...053f4162e17079a796ee77ef71e5d0b80bf3b261` (K6: `scripts/suite-paralela.py` reaproveita a execução verde sobre a mesma árvore; frase nova em `docs/regras/R-QA.md`; testes e mutantes). Decisão do dono de 2026-10-27 (K6, "A"): reuso com hash pelo git, **sem pareceres e changelog**, o CI do PR roda tudo.

## Gatilhos
`R-SEGURANCA`: controle do Forge (portão de suíte da `R-QA`, afrouxado em parte por decisão do dono).

## Achados
- A1 (bloqueante) scripts/suite-paralela.py:53 · requisito e defeito provado: FORA_DO_HASH tira a pasta inteira (docs/security/_modelo.md, README, docs/qa/bugs/), não só pareceres; tests/test_modelos_citados.py:47 lê o _modelo, que muda sem mudar o hash: reuso dá OK sobre suíte vermelha
- A2 (recomendado) scripts/suite-paralela.py:486 · o carimbo grava o hash calculado antes da execução (linha 445) sem recalcular no fim: commit feito durante a suíte (sujo e limpo de novo) marca verde a árvore antiga, que pode não ter sido a testada
- A3 (recomendado) scripts/suite-paralela.py:234 · git status não vê arquivo com skip-worktree ou assume-unchanged (inclui sparse-checkout): a árvore de trabalho pode diferir do HEAD com status limpo; recusar reuso e carimbo se git ls-files -v tiver marca minúscula ou S
- A4 (recomendado) docs/regras/R-QA.md:11 · os pareceres e fragmentos fora do hash são lidos pela suíte (Neutralidade e Referencias em tests/test_forge.py:347 e :335 varrem docs/): um parecer com termo proibido passa no reuso e só cai no CI; registrar esse resíduo na frase da R-QA

## Detalhe dos achados

**A1 (bloqueante).** Evidência: `scripts/suite-paralela.py:53` (`FORA_DO_HASH = ("docs/reviews/", "docs/qa/", "docs/devops/", "docs/security/", "changelog.d/")`) e `:241` (exclusão por prefixo de pasta). O requisito do dono é "sem pareceres e changelog"; a implementação exclui também os arquivos dessas pastas que não são parecer e que a suíte lê: `docs/security/_modelo.md` (lido por `tests/test_modelos_citados.py:47`, que o compara byte a byte com `templates/projeto/docs/security/_modelo.md`, e por `tests/test_volta_por_delta.py:656`), `docs/*/_modelo.md`, `docs/reviews/README.md`, `docs/qa/bugs/`, `docs/security/ameacas/` e `docs/security/aceites/`. Prova (sonda em clone descartável no `$TMPDIR`, a partir do HEAD revisado): `hash_da_arvore` devolve `464a48a5…17c6` antes e depois de um commit que altera só `docs/security/_modelo.md`, e `python3 -m unittest tests.test_modelos_citados` nessa árvore dá `FAILED (failures=1)`. Caminho: um agente (ou o autor) roda a suíte verde, outro commita uma alteração no modelo (o hook `conformidade` dá ao `security-engineer` escrita exclusiva em `docs/security/`, e o commit "só de parecer" também não roda a suíte no pre-push, corte 2); o QA chama a suíte à mão, recebe `suite: reusa <hash>` e `OK`, e registra como sua uma execução que não cobre a árvore entregue. O CI do PR pega, então o impacto é de portão local enganado, não de código vermelho mesclado. Severidade: média (controle do Forge que declara verde o que é vermelho). Correção mínima: excluir só os pareceres, isto é, arquivos `*.md` diretamente em `docs/reviews/`, `docs/qa/`, `docs/devops/` e `docs/security/` cujo nome não começa com `_` e não é `README.md`, e `changelog.d/*.md` de primeiro nível; subpastas e modelos entram no hash. Teste: alterar `docs/security/_modelo.md`, `docs/qa/bugs/x.md` ou `docs/security/ameacas/x.md` muda o hash; com o mutante que volta à exclusão por pasta. Esforço: P. Dono: `tech-lead` (autor do K6).

**A2 (recomendado).** Evidência: `scripts/suite-paralela.py:445` calcula o hash antes de iniciar os processos e `:486` grava esse mesmo valor ao fechar verde. A conferência `conferir_arvore` compara só o `git status` de antes e de depois, que fica igual (limpo) se alguém editar e commitar no meio da execução. Caminho: worktree compartilhada por dois agentes; a suíte testou em parte o código novo e o carimbo declara verde a árvore antiga, que depois pode ser reusada por quem voltar a ela. Probabilidade baixa (worktree por agente é a regra). Severidade: baixa. Correção mínima: recalcular `hash_da_arvore(RAIZ)` no fim e só gravar se for igual ao do começo. Esforço: P. Dono: `tech-lead`.

**A3 (recomendado).** Evidência: `scripts/suite-paralela.py:234` usa `git status --porcelain`, que não lista mudança em arquivo marcado `--skip-worktree` ou `--assume-unchanged` (o sparse-checkout marca skip-worktree). Caminho: só o próprio usuário cria essas marcas; numa worktree esparsa a suíte roda sobre um subconjunto e grava o hash do HEAD completo, que outra worktree do mesmo repositório (carimbo em `--git-common-dir`) reusa. Severidade: baixa. Correção mínima: em `hash_da_arvore`, devolver `None` se `git ls-files -v` tiver alguma linha com marca minúscula ou `S`. Esforço: P. Dono: `tech-lead`.

**A4 (recomendado).** Evidência: `docs/regras/R-QA.md:11`; `tests/test_forge.py:72` (`arquivos_texto` varre `docs/` inteira), usado por `Neutralidade.test_sem_termos_de_projeto` (`:347`) e `Referencias` (`:335`). Mesmo com A1 corrigido, o conteúdo dos pareceres fica fora do hash por decisão do dono e é lido por esses testes: parecer com termo proibido ou referência quebrada passa no reuso local. É o mesmo resíduo já aceito no corte 2 (commit só de parecer não roda a suíte no pre-push) e o CI do PR o cobre; por isso não bloqueia. Correção mínima: dizer na frase da `R-QA` que o reuso não cobre o conteúdo de parecer e de changelog (o CI cobre). Esforço: P. Dono: `tech-lead`.

## O que foi conferido e está correto
- **Pre-push continua rodando a suíte:** `.githooks/pre-push` não muda no diff; ele sempre exporta `FORGE_SUITE_TRAVA` não vazio (`trava_arquivo` sai com 1 se falhar, linhas 88 e 155) e o reuso só é consultado com a variável ausente ou vazia (`scripts/suite-paralela.py:520`). O modo `--suite` (chamada à mão) passa pelo reuso antes do `execv` e, sem carimbo igual, roda a suíte inteira pela trava.
- **CI nunca reusa:** `reuso` devolve `None` com `CI` definido (o GitHub Actions o define em todo job; `.github/workflows/ci.yml:35`, `:57`, `:235` chamam o script direto) e o checkout do CI não traz o carimbo, que mora no `.git` local.
- **Arquivo não rastreado:** `--untracked-files=all` deixa a árvore suja e o reuso recusa (teste `test_arquivo_novo_nao_versionado_roda`). Arquivo ignorado que a suíte lê: no `.gitignore` só há `__pycache__`, `*.pyc` (o Python invalida pelo fonte), `.env*` e pontos de montagem do sandbox; nenhum teste os lê como entrada de código.
- **Submódulo:** o Forge não tem submódulo (`/.gitmodules` é ponto de montagem ignorado); um gitlink entraria no hash pelo SHA, e mudança dentro dele aparece no `git status` sem `ignore=` configurado.
- **Troca de branch com a mesma árvore:** o hash é do conteúdo (`ls-tree -r` com modo, tipo, objeto e caminho), não da branch; mesma árvore é o mesmo código, salvo os pontos de A1 e A4.
- **Carimbo de outro usuário ou outro clone:** o carimbo fica em `$(git rev-parse --git-common-dir)/forge-suite-verde`, com as permissões do `.git` do dono; outro clone tem outro `.git`. `_git` remove as variáveis `GIT_*` (sem desvio por `GIT_DIR` ou `GIT_INDEX_FILE`).
- **Forja do carimbo:** quem escreve no `.git` (o próprio usuário ou um agente dele) consegue gravar um JSON com o hash certo e passar a chamada à mão; não ganha nada que não teria imprimindo `OK`, porque o pre-push e o CI não leem o carimbo. Informativo: a linha `suite: reusa <hash>` é autodeclarada, como a execução que ela substitui; o portão real continua no CI.
- **Falha fechada:** carimbo ausente, ilegível, de outro tipo, de outro Python, ou árvore suja roda a suíte (testes em `tests/test_suite_reuso.py`); a escrita é atômica (`os.replace`) e erro de escrita só deixa de carimbar. Suíte vermelha não grava (`test_vermelho_nao_grava_carimbo`).
- **Ambiente:** o carimbo amarra a versão do Python, não as ferramentas do PATH (shellcheck, CLI do Claude) que fazem testes pularem; o reuso é no mesmo `.git` da mesma máquina, então o risco é pequeno e o CI cobre. Informativo.

## Riscos aceitos e ferramentas
Riscos aceitos: o afrouxamento em parte da `R-QA` pelo reuso local (decisão do dono de 2026-10-27, K6), com o CI do PR rodando tudo; nenhum risco aceito novo neste parecer.
Ferramentas: revisão manual do diff e sonda local em clone descartável no `$TMPDIR`. Faltaram no ambiente (não instaladas, `R-CUSTO`): `gitleaks`, `semgrep`, `osv-scanner`, `zizmor`, `actionlint`; o diff não traz segredo, dependência nem workflow.
