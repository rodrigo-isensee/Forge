---
tipo: revisao-seguranca
contrato: 1
pedido: conf-base-dono
branch: melhoria/conf-base-dono
commit: d47d1b4728cae7d6811a21649eb333025b264d7b
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-23
---
# Review de segurança: conf-base-dono

Pedido CONF-BASE-DONO (pareceres em CONF-BASE-DONO-REV, E2.1). **Revalidação por delta** da volta `557c602..d47d1b4`: quatro commits de correção (`05bab4a`, `1a8e223`, `6eeecad`, `f7f2fdc`; diff `557c602..f7f2fdc`: `bin/forge-check`, `agents/conferente.md`, `tests/test_conferencia_base_dono.py`) e o merge da `develop` `d47d1b4`, cujo `git show --cc` sai vazio (não traz nada além dos dois pais). Revisão estática, com sondas num repositório temporário (`HOME` próprio em `$TMPDIR`) que rodam o `bin/forge-check` da branch. `tests.test_conferencia_base_dono`: 21 testes, OK.

## Gatilhos
- `controles do Forge`: `bin/forge-check` (`forge-check entrega`, a conferência `R-PROVA`), `agents/conferente.md`.

## Revalidação (d47d1b4): os achados anteriores
- **A1 (bloqueante) resolvido.** `diferem_dos_dois_pais` (`bin/forge-check:833-854`) só vale quando o head é o único commit próprio do intervalo (`rev-list de..head --not <base>` igual a `[head]`), um pai é o `--desde` e o outro é ancestral da base. Sonda dos dois merges (M1 com `X.txt` novo, M2 limpo, `--desde` antes de M1): sai `confira "X.txt"`, sem a linha `integração da base`. Teste `test_dois_merges_seguidos_nao_escondem_arquivo_do_autor`.
- **A2 (recomendado) resolvido em parte.** `BASE_DO_DONO` (`bin/forge-check:638`) exige a forma exata no começo da linha. A minha sonda antiga (`- proposta recusada: base do delta fixada pelo dono <sha> não vale`) agora é recusada (`escopo: --desde sem conferência anterior`, rc 1), e um pedido sem nenhuma `DECISÃO DO DONO` também. Fica uma folga, a R1 abaixo.
- **A3 (recomendado) resolvido.** Base do dono igual ao head é recusada (`bin/forge-check:745-746`; sonda: rc 1). Teste `test_base_do_dono_igual_ao_head_recusa_o_delta_vazio`.
- **A4 (recomendado) resolvido em parte.** `--raiz-pedidos` fora de `~/.forge-contrib` e da raiz do repositório sai rc 2 (sonda com `$TMPDIR/outro`). Fica a folga das subpastas, a R2 abaixo.
- **A volta abre outro caminho para encurtar a conferência?** Não. O `brief gerar --volta` agora propõe o `--desde` pela mesma `bases_do_pedido` que o `entrega` valida, então não aceita nada a mais. No escopo de integração, as contagens passam a ser o maior `+`/`-` contra os dois pais, o que fecha o A4 do review: a regra do anexo com remoção não pode mais ser enganada. O merge `d47d1b4` não mexe em `bin/forge-check` além do que vem dos pais.

## Achados

## Detalhe dos achados
São recomendações, sem caminho de ataque que bloqueie: quem grava o pedido e escolhe a pasta é o Jarvis, num canal que o autor não escreve. Cada uma vira cartão.

**R1 · recomendado · baixa.** Evidência: `bin/forge-check:731` (`com_decisao = bool(linhas_de_decisao(texto))`). Qualquer `DECISÃO DO DONO` do pedido abre a linha da base do dono, mesmo uma que não cite o sha40 dela. Sonda: com a decisão `"outra coisa qualquer"`, a base vale (rc 0, `base: fixada pelo dono`). Quase todo pedido tem alguma decisão do dono, então a exigência pesa pouco. Correção mínima: exigir uma linha `DECISÃO DO DONO` que cite o sha da base. Esforço P. Dono: `tech-lead`.

**R2 · recomendado · média.** Evidência: `bin/forge-check:4542` (`p.resolve() in escolhida.parents`). Vale qualquer subpasta de `~/.forge-contrib` ou da raiz do repositório. Sondas: `--raiz-pedidos ~/.forge-contrib/wt/qq` e `--raiz-pedidos <raiz>/sub` leem o `docs/pedidos/P1.md` dali (rc 0, com a linha `origem:`). O hook `conformidade` só guarda `docs/pedidos/` relativo à raiz da sessão e `~/.forge-contrib/docs/pedidos/` (`hooks/conformidade.py:569-590`). Então qualquer papel pode escrever um pedido numa worktree (`~/.forge-contrib/wt/<x>/docs/pedidos/`) ou em `templates/projeto/docs/pedidos/`, pasta que o `pedido_na_entrega` também não olha (`bin/forge-check:753`, pathspec só `docs/pedidos/`). O mesmo vale para `~/.forge-contrib/forge/docs/pedidos/`, a raiz real: é o A1 do review, que vai para o HOOK-RAIZ-CONTRIB. Correção mínima: o HOOK-RAIZ-CONTRIB guarda todo `docs/pedidos/` sob `~/.forge-contrib/`, worktrees incluídas, ou o `--raiz-pedidos` aceita só as raízes exatas (`~/.forge-contrib`, `~/.forge-contrib/forge`, a raiz e a cópia principal). Esforço P. Dono: `tech-lead`, junto com o HOOK-RAIZ-CONTRIB.

**R3 · recomendado · baixa, anterior à branch.** Com `--desde`, o `forge-check entrega` não vê um merge da base que desfaz uma mudança da base (`git merge -s ours develop`, ou um conflito resolvido com o lado da branch). Sonda: a `develop` corrige `seg.txt` e a branch integra com `-s ours`. O `forge-check` da branch e o da `origin/develop` dão a mesma saída, `escopo: sem commit (nada a conferir)`, rc 0. Até a etapa `pr` (pelo Base-sha antigo) mostra só `c.txt`, enquanto `git diff develop melhoria/y` mostra o `seg.txt` revertido. A mudança não abre esse caminho, porque o diff contra o `--desde` já não via a reversão, e o PR no GitHub (diff contra a ponta da base) a mostra ao usuário. Correção mínima: quando há merge da base no intervalo, listar também os arquivos que a base mudou desde a integração anterior e que o head não traz iguais aos da base. Esforço M. Dono: `tech-lead`, num cartão próprio.

## Rodada anterior (8c24358, reprovado)
Os achados de então:
- A1 (bloqueante): dois merges seguidos escondiam arquivo do autor.
- A2 (recomendado): a linha do dono valia em qualquer ponto da linha e sem decisão.
- A3 (recomendado): a base do dono igual ao head zerava o delta.
- A4 (recomendado): o `--raiz-pedidos` aceitava qualquer pasta.

Respostas de então:
- A linha do dono herda a proteção do arquivo do pedido (`hooks/conformidade.json:48-49`, só `jarvis`).
- O `pedido_na_entrega` reprova a linha gravada na própria entrega.
- O `desde_valido` recusa a base do dono fora da branch ou depois da entrega.

A situação de cada achado está na seção de revalidação acima.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do delta, sondas locais com o `forge-check` da branch e o da `origin/develop`, `python3 -m unittest tests.test_conferencia_base_dono`. Lacunas: `gitleaks`, `semgrep`, `osv-scanner`, `zizmor` e `actionlint` não estão no PATH. A volta não toca workflow, dependência nem configuração com segredo.
