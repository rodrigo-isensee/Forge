---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-g4-f1-aviso
commit: eb747918dc99b4fd57c67846a28f6e87bc1c4c4d
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: v0481 G4 F1 (modo aviso por grupo, só infra; classe C), delta 3682aeba..eb747918

## Achados
- A2 (recomendado) hooks/conformidade.py:4203 · `GuardaDaProva.barrar` chama `super().barrar` e segue: com grupo em `avisar` o retorno cai nos `if` seguintes e pode registrar duas vezes ou levantar `ForaDaProva`. Latente na F1 (todos em barrar); tratar antes de qualquer grupo ir a `avisar`. Segue aberto, fora deste delta; não segura o item (ordem do dono de 25/11), vira cartão.

## Delta lido
`git diff 3682aeba..eb747918`, parte da branch: o #886 (`hooks/conformidade.py`: `perfil_iniciante` lê o perfil sem FIFO e sem `git`; `hooks/_comum.py`: `ler_marca_do_git` só aceita arquivo regular) fecha o A2 da segurança; `PrazoVencido` na escolha do texto cai no texto técnico. As specs de mutante foram realinhadas (M16 do G4 F1; M2, M5 e M7 do perfil-fifo). O resto do diff entrou pelo merge da develop e é de outros pedidos.

## Critério → teste → resultado
Sem especificação de UX; obrigações do brief e do A2/A1 da segurança no #885/#886.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A2: FIFO no `.forge/perfil` não trava e a recusa mantém a regra | `RecusaComFifoNoPerfil.test_recusa_com_a_regra_dela_e_sem_prazo_vencido`, `test_fifo_no_perfil_nao_espera_e_vale_experiente` | FIFO no lugar do perfil | passou |
| Prazo vencido na escolha do texto não vira `prazo_vencido` | `test_prazo_vencido_na_escolha_do_texto_recusa_com_o_texto_tecnico` | `PrazoVencido` | passou |
| Perfil iniciante dá o texto simples; worktree lê o da cópia principal | `test_perfil_iniciante_recebe_o_texto_simples`, `test_worktree_com_fifo_le_o_perfil_da_copia_principal` | iniciante; worktree | passou |
| A1 (#886): FIFO em `.git`/`gitdir` da worktree não espera nem vale | `test_fifo_no_ponto_git_da_worktree_nao_espera`, `test_fifo_com_conteudo_no_gitdir_nao_vale` | FIFO; só arquivo regular | passou |
| Obrigações das voltas anteriores (aviso, grupo, registro, FIFO no registro) | demais de `ModoPorGrupo` e `RecusaComFifoNoRegistro` | n/a | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_hooks.RecusaComFifoNoPerfil tests.test_hooks.ModoPorGrupo tests.test_hooks.RecusaComFifoNoRegistro`: 18 testes, OK (9,2 s). Só as classes tocadas; a suíte vale pelo CI.
- Mutantes, `bin/forge-mutante --processos 3 --base 3682aeba` (base=3682aebaa39bbb2607e45db5d699cc5e7293a65b, rev=eb747918dc99): G4 F1 (duas specs) M1 a M16 todos `morreu`; perfil-fifo (duas specs) M1 a M9 todos `morreu`. Nenhum sobrevivente; cobrem as linhas de guarda mudadas (`perfil_iniciante`, `ler_marca_do_git`, o `try/except PrazoVencido`).
- Vermelho antes do verde: não refeito por `forge-testes --vermelho` (rodaria o módulo inteiro); a prova vai pelos 25 mutantes mortos e pela sonda do parecer anterior.
- ci: eb747918dc99b4fd57c67846a28f6e87bc1c4c4d verde
  Partes que contam: suíte 3.12 e 3.14 (partes 1 a 5), teto de pulados 3.12/3.14, bateria (python 3.14), bateria (verificações longas), bateria (passos) e árvore já provada: success. Falham `bateria (pareceres)` (espera este parecer), `catraca` e o agregado `bateria`. Causa da catraca (log lido com `XDG_CACHE_HOME` gravável): `tests/test_hooks.py` com asserções 618 para 644 e pulos 6 para 9 contra a develop, e mudança em `hooks/conformidade.py`; ambos pedem o rótulo `afrouxa-regra` do dono (ADR 0008), decisão do dono, não defeito. O delta não acrescenta `skip` (9 antes e depois).

## Bugs
Nenhum aberto. O A2 da segurança (FIFO no perfil) está corrigido; o A2 recomendado acima (GuardaDaProva) segue como cartão.
