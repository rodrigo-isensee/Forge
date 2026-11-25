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
# QA: v0481 G4 F1 (modo aviso por grupo; classe C), delta 3682aeba..eb747918

- ci: eb747918dc99b4fd57c67846a28f6e87bc1c4c4d verde

## Achados
- A2 (recomendado) hooks/conformidade.py:4203 · `GuardaDaProva.barrar` chama `super().barrar` e segue; latente com grupo em `avisar`. Segue aberto, fora deste delta, vira cartão.
- A3 (recomendado) hooks/conformidade.py:4366 · mutante M40 de `tests/mutantes/v0479-conformidade-sessao-forge-6.json` sobrevive no head (a linha e a spec não são deste delta; vêm do #742): `le_o_here_string = nome in SHELLS` sem `or palavra in FONTES` não derruba `HookSessaoDoForge.test_travas_do_conformidade`. Problema antigo: vira cartão, não segura o item (ordem do dono de 25/11).

## Delta lido
`git diff 3682aeba..eb747918` pelos primeiros pais (as três voltas da develop trazem o resto): `perfil_iniciante` em `hooks/conformidade.py` (A2 da segurança: perfil só do disco, `O_NONBLOCK|O_NOFOLLOW`, só `S_ISREG`, 64 bytes; `PrazoVencido` na escolha do texto cai no texto técnico), `hooks/_comum.py` (`diretorio_comum` sem `git`; FIFO em `.git` da worktree), classe `RecusaComFifoNoPerfil` com 7 testes, e specs de mutante realinhadas (M1 v0478, M15 v0479, M16 G4 F1, M2/M5/M7 perfil-fifo).

## Critério → teste → resultado
Sem especificação de UX; obrigações vêm do brief (E7.42) e dos achados A1/A2/S3 da segurança.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Perfil FIFO não trava a recusa, regra certa, sem `prazo_vencido` | `RecusaComFifoNoPerfil.test_recusa_com_a_regra_dela_e_sem_prazo_vencido` | FIFO no `.forge/perfil`, sessões Forge e projeto | passou |
| Prazo vencido na escolha do texto cai no texto técnico | `test_prazo_vencido_na_escolha_do_texto_recusa_com_o_texto_tecnico` | `PrazoVencido` | passou |
| Iniciante recebe o texto simples | `test_perfil_iniciante_recebe_o_texto_simples` | perfil regular | passou |
| FIFO no perfil vale experiente | `test_fifo_no_perfil_nao_espera_e_vale_experiente` | FIFO | passou |
| Worktree lê o perfil da cópia principal | `test_worktree_com_fifo_le_o_perfil_da_copia_principal` | worktree | passou |
| FIFO no `.git` da worktree não espera; só regular vale | `test_fifo_no_ponto_git_da_worktree_nao_espera`, `test_fifo_com_conteudo_no_gitdir_nao_vale` | FIFO com e sem conteúdo | passou |
| Obrigações das voltas anteriores (aviso, grupo, registro) | `ModoPorGrupo`, `RecusaComFifoNoRegistro` | n/a | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_hooks.ModoPorGrupo tests.test_hooks.RecusaComFifoNoRegistro tests.test_hooks.RecusaComFifoNoPerfil`: 18 testes, OK (2,8 s). Só as classes tocadas; a suíte inteira vale pelo CI.
- Mutantes (`bin/forge-mutante --processos 2`): G4 F1 (`v0481-g4-f1-aviso.json` + `-2`): M1 a M16 todos `morreu` (M16 realinhado morreu); perfil-fifo (`v0481-perfil-fifo.json` + `-2`): M1 a M9 todos `morreu` (M2, M5, M7 realinhados). Specs realinhadas fora do pedido: v0478-guardas-conformidade M1 `morreu` (conformidade.py:4249); v0479-conformidade-sessao-forge M15 `morreu` (conformidade.py:3211). Na mesma rodada só M40 sobreviveu (A3, antigo, fora do delta).
- Vermelho antes do verde: os testes novos do delta estão guardados pelos mutantes mortos acima (M1 a M9 do perfil-fifo removem a guarda e derrubam o teste declarado); a sonda de FIFO do parecer anterior já provou o vermelho na base d92b3a07.
- CI do PR #885 no head exato (`gh pr checks`, `XDG_CACHE_HOME` gravável): verdes `suíte (python 3.12 e 3.14, partes 1 a 5)`, `bateria (passos)`, `bateria (python 3.14)`, `bateria (verificações longas)`, `instalação (python 3.14)`, `teto de pulados`, `árvore já provada na develop`. Vermelhos esperados: `bateria` e `bateria (pareceres)` (falta de pareceres no head, `pareceres: failure`), `catraca` (log: `R-CONFORMIDADE` por mudança em `hooks/conformidade.py`, `hooks/conformidade.json` e `tests/test_hooks.py` com mais pulos; pede o rótulo `afrouxa-regra` do dono depois do último push).

## Bugs
Nenhum aberto.
