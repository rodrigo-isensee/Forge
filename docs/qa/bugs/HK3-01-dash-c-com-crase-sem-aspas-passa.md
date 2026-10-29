# HK3-01 - `git -C` com crase sem aspas, seguido de merge, passa o hook parecer
- Severidade: alta
- Responsável sugerido: tech-lead (hooks/parecer.py)
- Ambiente: branch melhoria/hk3-parecer-pasta, commit 212203a39fd4419c45dd797ea0737b7d05001d19

## Passos para reproduzir
1. Repositório de projeto com HEAD em `develop` (pasta P) e uma worktree de trabalho W em `melhoria/x`, sem parecer da branch.
2. Hook `hooks/parecer.py` com a entrada Bash: `git -C` + crase-echo-P-crase (sem aspas) + `merge melhoria/x`, cwd = W.
3. Comparar com a crase entre aspas, com `$(echo P)` e com `cd` + crase.

## Resultado esperado
rc=2 "merge ou pull numa pasta que o hook não resolve" (regra do modelo de ameaças: o que o hook não resolve recusa, substituição inclusa; a pasta de verdade é P, a integração).

## Resultado obtido
rc=0 só na forma com crase sem aspas; as outras três formas dão rc=2. O git roda em P (develop) e o merge entra na integração sem parecer. Não há fixture no corpus para a forma.

## Evidência
Sonda própria em `$TMPDIR/qa-engineer-hk3-parecer-pasta/s` (script `sonda.sh` do QA): a forma com crase sem aspas deu `rc=0`; `$( )`, crase entre aspas e `cd` com crase deram `rc=2 R-REVIEW: merge ou pull numa pasta que o hook não resolve`.

## Estado
Fechado em bfd9e70ad2325fd5a04a2104fe041d4346384042: `juntar_crases` e a guarda de substituição em `resolver` (`hooks/parecer.py:213,249`); fixtures `pasta-barra-dash-c-com-crase-sem-aspas`, `-e-pull` e `pasta-barra-dash-c-com-crase-e-ponto-ponto` no corpus (77 fixtures `pasta-*`, todas verdes); reaberto em forma vizinha como HK3-02.
