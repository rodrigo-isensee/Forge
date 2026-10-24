---
tipo: revisao-seguranca
contrato: 1
pedido: conf-base-dono
branch: melhoria/conf-base-dono
commit: 0bb264163d0d60c5ef8d49cf376755964654a9cf
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-23
---
# Review de segurança: conf-base-dono

Pedido CONF-BASE-DONO (pareceres em CONF-BASE-DONO-INTEG-REV, E2.1). **Revalidação por delta** da integração `09e6b3d..0bb2641`, o merge da `develop` `f744533` (pais `09e6b3d` e `f744533`, base comum `139a3b4`). O parecer anterior aprovou `d47d1b4`; os commits `a0a52af`, `aa7d3d1` e `09e6b3d` só gravam pareceres. Revisão estática com sondas locais. `tests.test_testes_tocados` e `tests.test_conferencia_base_dono` rodados na worktree com `HOME` isolado: 86 testes, OK.

## Gatilhos
- `controles do Forge`: `bin/forge-check` (`forge-check entrega`, a conferência `R-PROVA`), `agents/conferente.md` e `bin/forge-testes` (o mapa dos testes dirigidos do pre-push).

## Revalidação (0bb2641): o delta da integração
- **Os arquivos mesclados sozinhos não enfraquecem a correção da branch.** `bin/forge-check`, `agents/conferente.md` e `agents/jarvis.md` em `0bb2641` são, blob a blob, o resultado do `git merge-tree --write-tree 09e6b3d f744533`. Não houve edição à mão. Conferido nos dois sentidos: as linhas que a branch mudou desde `139a3b4` aparecem idênticas em `git diff f744533 0bb2641`, e as que a `develop` mudou aparecem idênticas em `git diff 09e6b3d 0bb2641`. Seguem como foram aprovados: `BASE_DO_DONO` (`bin/forge-check:664`), com a forma exata e exigindo `DECISÃO DO DONO`; `bases_do_pedido` e `desde_valido` (`:752`, `:766`), que recusam a base do dono igual ao head; e `diferem_dos_dois_pais` (`:860`), com o único commit próprio, um pai igual ao `--desde` e o outro ancestral da base, o que impede dois merges seguidos de esconder arquivo. Nenhuma função que a correção usa mudou de sentido na `develop`. O `caminho_do_pedido` continua lendo primeiro a cópia principal. O texto novo da `develop` no `conferente.md` trata do corte, da etapa e da isenção de QA, não da volta por delta.
- **A resolução não tira teste da correção do mapa.** Em `bin/forge-testes:61`, `FORGE_CHECK` é a união: os 15 módulos da branch e os 20 da `develop`, 21 no total. `test_conferencia_base_dono` está na lista, ao lado de `test_hooks`, `test_catraca`, `test_guarda_*` e `test_volta_por_delta`. `tests/test_testes_tocados.py:57` confere os 21 e cita `test_conferencia_base_dono` pelo nome. O `MapaDoForgeCheck`, que compara a lista com os arquivos que importam o script, passa. Nenhum teste foi removido.
- **Combinação com o que a `develop` trouxe.** O `forge-check anotar --tipo historico` (`bin/forge-check:1713`) grava `- <data hora>: <literal>`. Essa linha cabe tanto em `BASE_DO_DONO` quanto em `CONFERIDA`. O `--tipo decisao` grava a `DECISÃO DO DONO`. A branch não amplia esse caminho: forjar a `conferida` pelo `anotar` já encurtava o delta sem precisar de decisão, e é o resíduo registrado em `docs/security/lote-forge-check-0.28.0.md` (o hook ainda não trata o `anotar` como escrita na pasta do Jarvis). Fica para o cartão desse lote, sem achado aqui.

## Achados

## Riscos aceitos e ferramentas
Nenhum risco aceito. As recomendações R1, R2 e R3 do parecer anterior (`d47d1b4`) seguem como cartões; o delta não as muda. Ferramentas usadas: `git diff`, `git merge-tree`, `git show --cc`, `forge-check delta --parecer` e os dois módulos de teste. Lacunas: `gitleaks`, `semgrep`, `osv-scanner`, `zizmor` e `actionlint` não estão no PATH. O delta não toca workflow, dependência nem configuração com segredo.
