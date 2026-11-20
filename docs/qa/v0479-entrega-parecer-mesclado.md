---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-parecer-mesclado
commit: cdf62e0a29a1dabf34c600bb0b802e9fd65bcf55
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0478 E50.4 (ENTREGA-PARECER-MESCLADO-ANTES-DO-AUTOR), volta E50.5

Head testado: `cdf62e0a` (E50.5 sobre o `48153733` do brief selado; a volta da segurança fechou A1 e A2 e o review A1). Sem suíte local: a suíte inteira fica com o CI do PR.

## Achados
- A1 (recomendado) bin/forge-check:3017 · com `commit:` igual ao Desde, o parecer de QA que revalida o código novo do autor (`commit:` = head da correção) sai `fora do declarado`: `melhoria/v0479-vermelho-evals`, `commit: bdc7eb53`, Desde `8b5d4a5f`. Efeito da decisão do dono; revalidar com brief novo (Desde = head corrigido).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E50.1: parecer mesclado e commitado antes da volta é anexo do portão (caso real `bp1-q1-leitor`) | `ParecerMescladoNaVolta.test_caso_real_parecer_mesclado_e_commitado_antes_da_volta_e_anexo`; `forge-check entrega --so-leitura` real | `commit:` = Desde | passou (14 de 14; real: `cumpriu`) |
| E50.1: autor que toca o parecer junto do código, merge resolvido à mão, sem conferida, frontmatter de outra branch/pedido/tipo, `commit:` abreviado ou fora, sem frontmatter, veredito trocado, git que falha | `test_autor_que_edita...`, `test_merge_com_o_parecer_resolvido_a_mao...`, `test_sem_conferida...`, `test_frontmatter_de_outra_branch...`, `test_commit_fora_do_intervalo_ou_abreviado...`, `test_parecer_sem_frontmatter...`, `test_veredito_trocado...`, `test_git_que_falha...` | recusas do autor | passou |
| E50.5 A1: `commit:` igual ao Desde; autor que forja aprovado citando o próprio código, ou troca o reprovado do portão | `test_autor_que_forja_aprovado_citando_o_proprio_codigo...`, `test_reprovado_do_portao_trocado_por_aprovado_com_outro_commit...` (S1, S3) | `commit:` entre o Desde e o head | passou |
| E50.5 A2: um commit com pareceres de várias pastas, ou com `docs/security/aceites/`, fica fora | `test_um_commit_com_pareceres_de_varias_pastas...`, `test_parecer_de_seguranca_com_aceite_no_mesmo_commit...` (S2) | pasta do tipo; aceites do usuário | passou |
| Review A1: ramo `cod` do rev-list recusa | `test_rev_list_que_falha_recusa` | git que falha, `all([])` | passou |

## Cenários e resultado real
- Classe: `python3 -I -m unittest discover -s tests -p test_selo_e_entrega.py -k ParecerMescladoNaVolta` → `Ran 14 tests ... OK`.
- `python3 -I -m unittest discover -s tests -p test_forge_mutante.py -k ConferirTodas` → `Ran 4 tests ... OK`.
- Mutantes de `tests/mutantes/v0479-entrega-parecer-mesclado-2.json`: `M9 · morreu · bin/forge-check:3024`, `M10 · morreu · :3001`, `M11 · morreu · :3012`, `M12 · morreu · :3002`, `M13 · morreu · :3002`, `M14 · morreu · :3022`. Spec 1: `M2` a `M8 · morreu` (`:2997` a `:3022`), rc 0 (a linha de M1 saiu do corte do `tail`; não relida). Spec `v0457-escopo-ponto-2.json` (trecho do M12 reescrito): `M12 · morreu · bin/forge-check:2951`.
- Vermelho: cada mutante M9-M14 morto prova teste que cai sem a guarda; `forge-testes --vermelho 48153733` estourou o prazo de 580 s sem veredito (não vale como vermelho).
- Casos reais, `forge-check entrega --so-leitura --pedido v0478 --etapa codigo`:
  - `melhoria/v0479-bp1-q1-leitor` (`df0251ca..eec2c1c1`): `escopo: ok (anexo do portão: parecer de tech-lead commitado na volta só com parecer)` e o de `seguranca`; `resultado: cumpriu`.
  - `melhoria/v0479-vermelho-evals` (`8b5d4a5f..f913faea`): `escopo: fora do declarado no brief "docs/qa/v0479-vermelho-evals.md"`; `resultado: não cumpriu`. Com o `forge-check` do `48153733` o mesmo caso dá `cumpriu`: o aperto A1 o tira (parecer de QA com `commit: bdc7eb53`, o código novo do autor, não o Desde). É o efeito pedido pelo dono, não defeito; vira o A1 recomendado.

## Cópia
`/root/.forge-contrib/wt/v0479-entrega-parecer-mesclado-E504` trazida por fast-forward até `cdf62e0a`. Criei só as refs locais `melhoria/v0479-bp1-q1-leitor` e `melhoria/v0479-vermelho-evals` nessa cópia para a conferência.
