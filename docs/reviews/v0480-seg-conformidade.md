---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-seg-conformidade
commit: b96cab3cbfbb3f625f6cb1732a018a8178f8c92c
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 (E113.16, melhoria/v0480-seg-conformidade)

Revalidação da 3ª volta (H2/H3, R-REVIEW, regra do dono de 22/11 07:20), que responde aos achados A5 (resto), A6, A7 e A8 da segurança ec727021 e ao A6 do QA. Delta lido: `forge-check parecer delta` deste parecer, intervalo `bf57b17e..b96cab3c` sem o que veio da `develop`: `hooks/conformidade.py` (`FIM_DE_LISTA`, `PIPE`, `VOLTA_NO_TIL`, `ALVO_DO_T`, `COPIA_RECURSIVA`, `alvo_do_t`, os `inicios` de lista na leitura, a pasta `None` depois da volta, o `rsync` e a extração para opaco), 40 fixtures novas (`a5-resto-*`, `a6-*`, `a7-*`, `a8-*`, `opaco-u4-…-recursiva-bloqueia`), uma fixture mudada, `tests/mutantes/v0480-seg-conformidade-{7,8,9}.json`, `tests/test_conformidade_seg_v0480.py`, `docs/hooks-fixtures.md` e o fragmento do changelog. `tests/pesos-d4.json` mudou só com nomes de testes vindos da `develop`.

## Sondas
- S1 · main, `cd /tmp & git push origin` e `cd /tmp | true; git push origin` · espera: código 2 · obtido: 2 R-MAIN
- S2 · main, `cd /tmp && true & git push origin`, `cd /tmp |& true` + quebra + push, `cd /tmp & wait; git merge develop` · espera: código 2 · obtido: 2 R-MAIN
- S3 · main, `cd /tmp; cd -; …`, `pushd /tmp; popd; …`, `cd /tmp; cd ~1; …`, `cd -- -; git push origin` · espera: código 2 · obtido: 2 R-CONFORMIDADE
- S4 · feature/x, `cp --recur -T ev "$X"`, `cp -rt"$X" ev`, `cp --target-dir "$X" ev/config` · espera: código 2 · obtido: 2
- S5 · feature/x, `tar -xf a.tar -C "$X"`, `unzip -o a.zip -d "$X"`, `rsync -r ev/ "$X"`, `rsync -avz ev/ "$X"` · espera: código 2 · obtido: 2
- S6 · feature/x, `cp -r ev "$(mktemp -d)"`, `cd src && ls; git status`, `git status | cat; ls`, `cd src; git status &`, `cd src; cd -`, `rsync -t ev/a "$X"` · espera: código 0 · obtido: 0
- S7 · feature/x, `cd -P /tmp; git status` · espera: código 0 (pasta escrita) · obtido: 2 R-CONFORMIDADE "comando depois de `cd -`" (A9)

## Parecer
Aprovado. O delta só corrige o apontado. A6: cada lado de pipe volta à pasta de antes dele e a lista que termina em `&` volta à pasta do começo dela (`inicios`, em par com a pilha de subshells). A7: `cd -`, `cd ~-`, `cd ~N`, `popd` e `pushd` sem pasta ou com `+N` dão pasta desconhecida, e o comando seguinte recusa, com falha fechada. A5 (resto): `alvo_do_t` lê `-t` colado e no grupo e toda abreviação de `--target-directory`; `COPIA_RECURSIVA` aceita as abreviações longas. A8: `tar -C`, `unzip -d` e `rsync -r` para valor de fora da linha recusam; no `rsync`, `-t` não é alvo.

Nenhum teste afrouxado. Nenhuma fixture antiga apagada; a única mudada, `opaco-u4-prefixo-do-ambiente-maiusculo-libera` (A6 do QA), trocou `cp -rT` por `cp -T` e segue livre, e o caso `-rT` foi para a fixture nova `…-recursiva-bloqueia`, que recusa: a cobertura ficou mais dura, não mais frouxa. `test_conformidade_seg_v0480.py` só ganhou quatro testes, sem baixar mínimo dos antigos.

Verificadores: `python3 -I tests/test_conformidade_seg_v0480.py` no head b96cab3c, com o ambiente limpo: 15 testes OK (40 s). `bin/forge-mutante` nas specs 7, 8 e 9: os 21 mutantes morreram, um por linha de guarda mudada. `--cobertura --base bf57b17e`: todas as linhas de guarda de `hooks/conformidade.py` cobertas; as duas apagadas (1851 e 1852 da base) viraram `alvo_do_t`. A suíte inteira fica com o CI do PR (V2), sem rerrodar aqui.

## Achados anteriores
- A5 resto (segurança ec727021): **fechado**. S4 recusa; `cp -r ev "$(mktemp -d)"` segue livre.
- A6 (segurança ec727021): **fechado**. S1 e S2 recusam; S6 segue livre.
- A7 (segurança ec727021): **fechado**. S3 recusa; a volta no fim da linha segue livre.
- A8 (segurança ec727021): **fechado**. S5 recusa; `rsync -t ev/a "$X"` segue livre.
- A6 do QA (fixture u4 quebrada pelo A5): **fechado**, sem afrouxar (ver Parecer).

## Achados
- A9 (recomendado) hooks/conformidade.py:2521 · `cd -P /tmp; git status` recusa com "comando depois de `cd -`" (S7): o `alvo[:1] == "-"` toma a opção `-P`/`-L` como volta. Falha fechada, não bloqueia, mas recusa uso comum; pular as opções antes do alvo, como no `pushd`.
