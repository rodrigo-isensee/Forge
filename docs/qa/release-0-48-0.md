---
tipo: qa
contrato: 1
pedido: release-0.48.0
branch: melhoria/release-0-48-0
commit: 74d2a59cad1d0edf5b69bdaeb191b3cb9cdef2e6
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-28
---
# QA: release-0.48.0

- ci: 74d2a59cad1d0edf5b69bdaeb191b3cb9cdef2e6 verde

Leva da 0.48.0 contra a main (`origin/main..74d2a59c`: 8 commits, 75 arquivos). Passada única, sem rodar a bateria inteira (R-QA, PARECER-LE-O-CI).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Versão 0.48.0 em plugin.json e CHANGELOG batem | `bateria` do CI; leitura: `"version": "0.48.0"` e `## [0.48.0] - 2026-11-28` | n/a | passou |
| CI da develop verde no 502c235b | `gh run list --commit 502c235b…`: CI success | n/a | passou |
| CI do PR verde no head da marca | `gh pr checks 953`, rc=0: suíte 1 a 5 de 5, teto de pulados, bateria (pareceres, passos, verificações longas, python 3.14), catraca e conferência, instalação | n/a | passou |
| Instalação de ponta a ponta | check `instalação (python 3.14)` pass | n/a | passou |
| Placar de mutação da versão | `rel048-placar.log`: `placar: 0.48.0 mortos=53 sobreviveu=0 equivalente=0 invalido=0 sem-veredito=0 sem-veredito-pulado=0 specs=9` | mutante sobrevivente | passou |

## Cenários e resultado real
- CI: `gh pr checks 953` com rc=0 no head 74d2a59c (remoto igual ao head local); nenhum check vermelho nem pendente. Os `skipping` são os de push na develop, que não valem para o PR.
- Placar: li o log gravado em `/root/.forge-contrib/wt/rel048-placar.log`; as 9 specs da amostra (placar, v048-trava-texto-ambiente, v048-versao-ate-9, v0481-espera-amarela 1 a 5, v0481-f1p2-c1b-2) têm rc=0 e nenhum sobrevivente. As demais saem "fora da amostra" no próprio log. Não rerrodei os mutantes: o log não grava a base do run, e a leitura é do registro do autor da marca.
- Pulado único: `MedidaDaVagaPesada` pula no sandbox por /proc de outro namespace (limite do ambiente); o check `teto de pulados` do CI está verde.
- Vermelho antes do verde e mutantes por linha de guarda pertencem aos pedidos de origem (v048, v0481), aprovados nos PRs deles; esta etapa é a marca da versão.
- Segurança, review e devops têm pareceres próprios, fora deste.
