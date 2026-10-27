---
tipo: revisao-seguranca
contrato: 1
pedido: conferente-c2c3
branch: melhoria/conferente-c2c3
commit: cbb522765094be22586e61487bd1f54970829453
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-27
---
# Review de segurança: conferente-c2c3 (C2, C3 e C1 do CONFERENTE-VELOCIDADE), volta 1

Pedido de revisão: CONFERENTE-VELOCIDADE-REV (E2.1). Base `develop`, Base-sha `ce1a341b9874143cf3fb8c998a76eb473adc1df3`, head revisado `cbb5227`. Revalidação por delta do parecer anterior (`8fa51fd`, head `a2cb36d`): `forge-check delta --parecer` listou `bin/forge-check` (492-514, 625-642, 956-957, 4189-4198, 4299-4300, 5227), `agents/conferente.md:53` e os testes e mutantes; todos lidos. Como o delta toca controle do Forge, reli também o caminho de `cmd_entrega` em volta dele (`bin/forge-check:927-960`, incluindo `diferem_dos_dois_pais`).

## Gatilhos
- Controles do Forge (`R-SEGURANCA`): `bin/forge-check` (o conferente de entrega e o `forge-check pr`) e `agents/conferente.md`.
- O C1 afrouxa em parte `R-PROVA` por decisão do dono (2026-10-27, "A"), no tamanho do E4: o escopo é o delta desde a última `conferida`, sem deixar de ver um commit do delta.

## Achados
- A2 (bloqueante) bin/forge-check:949 · defeito provado, mesma classe do A1 (gatilho controles do Forge, tardio): com --desde, um commit de integração da base sobre a conferida que devolve à base um arquivo da entrega (teste apagado no merge) some do escopo; pr e merge saem "sem commit (nada a conferir)", rc 0

## Detalhe dos achados
**A1 (parecer `8fa51fd`) · resolvido no caminho linear.** `desfeitos_da_entrega` (`bin/forge-check:509-512`) soma, em `arquivos_da_entrega` (`:504-505`), o que a branch mudou em `base...desde` e mudou de novo em `desde..head`; nas etapas de merge, `:956-957` soma o mesmo ao filtro por conteúdo. Sonda (`$TMPDIR/security-engineer-conferente-c2c3/sonda2`): arquivo acrescentado antes da conferida e apagado depois, arquivo modificado e devolvido ao conteúdo da base, e parecer apagado aparecem como `escopo: confira` em `codigo`, `pr`, `merge-integracao` e `pedido-de-merge-ao-dono`; com um commit comum depois de um merge, também. O teste `test_arquivo_acrescentado_antes_da_conferida_e_apagado_depois_fica_no_escopo` cobre o caso linear. `desfeitos_da_entrega` só entra por união (`+` em `:505`, `|=` em `:957`), sobre nomes já em `desde..head`: não há caminho por ele para tirar arquivo do escopo; no máximo acrescenta um nome a conferir.

**A2 · o commit de integração esconde o desfeito.**
- Evidência: `bin/forge-check:949-951`. Depois de `arquivos_da_entrega` (com os desfeitos somados), `diferem_dos_dois_pais(raiz, de, head, base_ref)` filtra os arquivos para os que diferem dos **dois** pais do merge. Arquivo que a branch acrescentou até a conferida e que o merge apaga é igual ao pai da base (ausente nos dois) e sai do escopo; o mesmo para arquivo devolvido ao conteúdo da base. Com o C1, `de` é a conferida, que é um pai do merge: o caminho passa a valer em `pr`, `merge-integracao` e `pedido-de-merge-ao-dono`.
- Prova (sonda2, branch `melhoria/y`): sobre a conferida (`teste.py`, `cod.py`, `mod.txt` mudado), `git merge --no-ff --no-commit develop`, `git rm teste.py`, `mod.txt` devolvido à base, commit. `forge-check entrega ... --desde <conferida>`: em `pr`, `merge-integracao` e `pedido-de-merge-ao-dono` sai `escopo: integração da base (o que difere dos dois pais)` e `escopo: sem commit (nada a conferir)`, rc 0; em `codigo` sai `pendente:` (rc 1). Com um commit comum depois do merge (`melhoria/z`), `teste.py` e `mod.txt` voltam a aparecer: o buraco é só o merge como último commit.
- Caminho de ataque: o autor com push na branch integra a `develop` depois da conferida e, na resolução do merge, apaga o teste ou o controle que cumpria um item do "Entregar". Na etapa de PR ou de merge, o conferente lê só o delta (C1), recebe "nada a conferir" e não vê o item desfeito. Defesa que sobra: o `forge-check pr` (parecer com diff efetivo diferente do commit dele não vale) e a leitura do review e do QA, se feitos depois do merge.
- Severidade: média (controle do Forge; precisa de push na branch; há defesa em profundidade). Bloqueante por ser o mesmo defeito do A1 por outro mecanismo, contra o requisito do E4 e o pedido desta revisão. Tardio: `diferem_dos_dois_pais` já estava em `a2cb36d`; na primeira rodada a matriz do A1 não cobriu a dimensão "mecanismo: commit de merge".
- Correção mínima: no ramo `dos_dois_pais` (`:949-951`), com `valido`, manter também os arquivos de `desfeitos_da_entrega(raiz, base_sha, valido)` que estão em `nomes_do_intervalo(raiz, valido, head)` (e a contagem deles de `valido..head`). Teste: o caso da sonda2 (merge da base como último commit, com `git rm` de um arquivo da entrega e outro devolvido à base) em `pr`, `merge-integracao` e `pedido-de-merge-ao-dono`, e o mesmo com parecer apagado. Esforço: P. Dono: `tech-lead` (autor do lote).

**Conferido sem achado no delta:**
- C2, `uso_do_pr` (`:625-642`): passa a recusar só em branch `melhoria/<slug>` (`branch_da_convencao`), lê o pedido também em `RAIZES_DE_BRIEF` e não recusa quando um parecer da ref leva `pedido: <argumento>`. Continua só recusa (rc 2), nunca troca argumento nem `--ref`; o padrão `[A-Za-z0-9._-]+` mantém o caminho dentro de `docs/pedidos/`. A leitura dos pareceres da ref só desliga a recusa: não abre caminho para conferir outra branch.
- C2, `linha_do_comando_pr` (`:4299-4300`): só imprime para `melhoria/`; a base também passa pela validação de caracteres (teste novo).
- C3 (`:4189-4190`, `:4198`): a linha `volta: bloco ... idêntico` só sai em brief com `Volta-de:` e só para bloco presente nos dois; segue informativa, não reprova nem aprova. `agents/conferente.md:53` só descreve o recorte do C2.
- Testes do item (`tests.test_volta_por_delta`, `tests.test_etapa_do_brief`): 110 testes, OK. Nenhum cobre o A2.

## Riscos aceitos e ferramentas
- Risco aceito pelo dono: o afrouxamento parcial de `R-PROVA` do C1 (decisão de 2026-10-27), no tamanho do E4. O A2 fica fora desse aceite.
- Ferramentas: leitura estática do delta e sonda local com o próprio `forge-check` num repositório descartável em `$TMPDIR`. Não há dependência, segredo nem workflow no diff; `gitleaks`, `osv-scanner`, `zizmor` e `actionlint` não se aplicam.
