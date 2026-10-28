---
tipo: revisao-seguranca
contrato: 1
pedido: metade-k6
branch: melhoria/metade-k6
commit: 6dda8fdf285d5c5c2387c8ac4594fe1d0299a17d
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-27
---
# Review de segurança: metade-k6

Escopo: volta 2 do K6, diff `ce1a341b9874143cf3fb8c998a76eb473adc1df3...6dda8fdf285d5c5c2387c8ac4594fe1d0299a17d`, revalidado por delta `053f4162e17079a796ee77ef71e5d0b80bf3b261..6dda8fdf285d5c5c2387c8ac4594fe1d0299a17d` (`forge-check delta --parecer docs/security/metade-k6.md`: `scripts/suite-paralela.py`, `tests/test_suite_paralela.py`, `tests/test_suite_reuso.py`, `tests/mutantes/metade-k6.json` e `metade-k6-2.json`). Este parecer substitui o anterior (commit `053f416`, reprovado por A1). Decisão do dono de 2026-10-27 (K6, "A"): reuso com hash pelo git, sem pareceres e changelog, e o CI do PR roda tudo.

## Gatilhos
`R-SEGURANCA`: controle do Forge (portão de suíte da `R-QA`, afrouxado em parte por decisão do dono).

## Achados

## Detalhe dos achados

**A1 do parecer anterior (bloqueante): resolvido.** `scripts/suite-paralela.py:234-237` (`fora_do_hash`) tira do hash só os `*.md` diretamente em `docs/reviews/`, `docs/qa/`, `docs/devops/`, `docs/security/` e `changelog.d/`, sem `_*` nem `README.md`; subpastas e outros tipos entram. Sonda em clone descartável no `$TMPDIR`, a partir de `6dda8fd`, um commit por caminho: `docs/security/_modelo.md`, `docs/security/ameacas/sonda.md` e `docs/qa/bugs/sonda.md` mudam o hash; `docs/security/sonda-parecer.md` e `changelog.d/sonda.md` não mudam (o que o dono decidiu). Nenhum teste lê pelo nome um parecer real dessas pastas (os nomes citados em `tests/` são de repositórios temporários). Teste novo: `tests/test_suite_reuso.py:111`.

**A2 do parecer anterior (recomendado): resolvido.** `scripts/suite-paralela.py:497-498` recalcula o hash no fim e só carimba se for o do começo (linha 456); hash `None` nos dois lados não grava, porque `gravar_carimbo` sai com hash vazio (linha 267). Sonda: `tests.test_suite_paralela.Brinquedo.test_commit_no_meio_da_suite_nao_grava_carimbo` passa em `6dda8fd` e falha (`FAILED (failures=1)`) com o mutante que troca a condição por `if True:`. Resíduo informativo: editar e desfazer um arquivo durante a execução (mesmo conteúdo no fim) passa pela guarda, e há uma janela curta entre o hash final e a escrita; os dois pedem alguém mexendo de propósito na worktree durante a suíte, não dão nada além do que imprimir `OK` já daria, e o CI cobre.

**A3 do parecer anterior (recomendado): resolvido.** `scripts/suite-paralela.py:245-247` devolve `None` se `git ls-files -v -z` tiver marca minúscula (assume-unchanged) ou `S` (skip-worktree, inclusive do sparse-checkout). Sonda: com `README.md` marcado e alterado, `git status --porcelain` fica vazio e `hash_da_arvore` devolve `None` para `--skip-worktree` e para `--assume-unchanged`; tirando a marca, volta a dar hash. Teste novo: `tests/test_suite_reuso.py:120`.

**A4 do parecer anterior (recomendado): segue em aberto, não bloqueia.** `docs/regras/R-QA.md:11` não mudou no delta. O conteúdo dos pareceres e fragmentos fora do hash é lido por `Neutralidade` e `Referencias` (`tests/test_forge.py`), então um parecer com termo proibido passa no reuso local e só cai no CI. É o mesmo resíduo aceito no corte 2 (decisão ACELERA-RODADA). Correção mínima: dizer na frase da `R-QA` que o reuso não cobre o conteúdo de parecer e de changelog e que o CI cobre. Esforço: P. Dono: `tech-lead`.

**CI fora do ambiente do teste.** `tests/test_suite_paralela.py:147` tira `CI` do ambiente do brinquedo, para o teste de reuso não depender de rodar fora do CI (no CI, `reuso` devolve `None` e o teste não provaria o reuso). Não muda o script: com `CI` definido ele continua rodando tudo.

## O que foi conferido e está correto
Sem mudança desde o parecer anterior, e conferido de novo no delta: o pre-push continua rodando a suíte (o reuso só vale com `FORGE_SUITE_TRAVA` ausente), o CI nunca reusa, árvore suja ou arquivo não rastreado roda a suíte, o carimbo fica no `--git-common-dir` do próprio usuário, `_git` tira as variáveis `GIT_*`, e carimbo ausente, ilegível, de outro Python ou de outro hash roda a suíte (falha fechada).

## Riscos aceitos e ferramentas
Riscos aceitos: o afrouxamento em parte da `R-QA` pelo reuso local (decisão do dono de 2026-10-27, K6), com o CI do PR rodando tudo. Nenhum risco aceito novo neste parecer.
Ferramentas: `forge-check delta`, revisão manual do diff, sondas em clone descartável no `$TMPDIR` (script de sonda e um mutante) e os testes do item (`tests.test_suite_reuso` e o teste do commit no meio, 15 testes OK). Faltam no ambiente, e não foram instaladas (`R-CUSTO`): `gitleaks`, `semgrep`, `osv-scanner`, `zizmor`, `actionlint`. O delta não traz segredo, dependência nem workflow.
