---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-fechar-lote
commit: 97e0b6e7d860dde35ae33b39c0265ae3f2fdd7a8
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 (E15.2, lote do bin/forge-fechar)

Diff `82bb9e57..97e0b6e7`: quatro cartões, um commit cada (FORGE-FECHAR-CLONE-LIMPAR 5f8202df, TESTE-FECHAR-L5-CORRIDA fa79eb1d, FECHAR-HOMOLOG-FRESCA 63063345, FECHAR-DRY-RUN-1C 97e0b6e7), com fragmento em `changelog.d/v0478-fechar-lote.md`. Código do `bin/forge-fechar`: +71/-14, abaixo do teto por item (H1).

## Guardas conferidas à mão contra os mutantes (o `--cobertura` não lê shell)
- `-h|--help)` (linha 103): FL-M1.
- detecção da cópia principal, `.git` da árvore igual ao `--git-common-dir` (647): FL-M2.
- `[ -n "$sha_local" ] && [ -z "$propria" ]` (703): FL-M3.
- `copia_propria`: `sem_merge = 1` (616) FL-M4; o `elif` da pasta `wt` resolvida (620) FL-M5 (link) e FL-M6 (fora de `wt`).
- remota não apagada pela cópia principal (747) FL-M7; sem comando de `push --delete` (778) FL-M8.
- `wait "$pid_err"` do L5 (382): FL-M9, morto pelo teste do `sed` lento.
- `promovivel`: `if ! git fetch` (947) FH-M1 reescrito; `if homolog_local=` (948) FL-M10; aviso sem local (951) FH-M2.
- `conferir_1c`: a nota `${2:-}` da recusa (964) FL-M13; `[ -f "$promover" ] || die` e `rc_1c` seguem com os FH-M4..M8 e o z075.
- `--dry-run`: `if [ "$ref_dry" = "refs/heads/$ref" ]` (1221) FL-M11 (roda) e FL-M12 (sem branch local não roda).

Toda linha de guarda mudada tem mutante, e cada um tem teste de comportamento do ramo de falha (subprocesso, sem ler a fonte). Os três JSONs antigos (`v047-fechar-sem-homolog`, `v0474-mp6-disco`, `z075-fechar-promovivel`) só trocam o teste renomeado ou o trecho movido; o `de` de cada um casa no head (os mutantes rodaram).

## Leitura
- Escopo: faz o que a etapa E15 pede, nada além; o `--help` entrou no cartão FORGE-FECHAR-CLONE-LIMPAR, como o changelog diz.
- `copia_propria` lê `sem_merge`, que a `limpar_entrega` calcula antes da detecção (linha 641); com a cópia própria a pendência é sempre não vazia, então o código 3 sai certo.
- O comando `git branch -D` impresso na cópia fora de `wt` só aparece sem `sem_merge` (sha mesclado), igual às pendências já existentes.
- O 1c do `--dry-run` só alcança a base `origin/develop` (o `case` da linha 173 recusa as outras), lê a `origin/homolog` local sem busca e não chama `gh` nem `forge-check` (o teste confere as chamadas).
- O teste do `sed` lento é determinístico no sentido que importa: o atraso favorece o defeito, e o FL-M9 prova que ele o pega.

## Ferramentas
- `bin/forge-mutante --processos 1` no head 97e0b6e7: FL-M1 a FL-M13 morreram; FH-M1 a FH-M8 morreram.
- `shellcheck`: ausente neste clone; vale o job do CI do PR (pendência do CI, não do review).
- Suíte: não rerrodada (fica no CI do PR).

## Parecer
Aprovado. Sem achado: as quatro mudanças estão corretas, pequenas e com uma guarda testada por linha.
