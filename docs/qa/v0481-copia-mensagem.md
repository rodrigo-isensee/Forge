---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-copia-mensagem
commit: 7bdd25d54a37943b23faf6d3dcd3fc558544eebc
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: v0481 copia-mensagem (#889, classe C)

Escopo: `bin/forge-copia` (FORGE-COPIA-MENSAGEM e COPIA-REVISAO). Diff lido contra Base-sha 8833d0f6: `bin/forge-copia`, `tests/test_forge_copia.py`, `tests/mutantes/v0481-copia-mensagem.json`, `tests/mutantes/v0481-copia-base.json` (M2 ajustado), fragmento do changelog.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Mensagem cita só as refs tentadas, sem `origin/origin/` | `test_mensagem_sem_ponto_cita_as_refs_tentadas_sem_origin_duplicado`; sonda s3/s4 contra o remoto real | `--base origin/x` e `--base x` | passou |
| Falha do `git switch` cita a ref de partida | `test_switch_que_falha_apaga_a_copia` (`o git switch falhou a partir de origin/develop`) | branch já existente | passou |
| `clone --revisao` nasce no head remoto, sem upstream | `test_clone_de_revisao_parte_do_head_remoto_sem_upstream`; sonda s7 (HEAD = 7bdd25d5, sem `branch.*.remote`) | `--base` dada junto não pesa | passou |
| `--revisao` com branch fora do remoto: apaga o clone, sai 1, não cai na base | `test_branch_fora_do_remoto_nao_cai_na_base`; sonda s1 e s5 (`--base develop --revisao`, clone apagado) | base válida presente | passou |
| `worktree --revisao` sai 2 e não cria nada | `test_worktree_de_revisao_e_recusada`; sonda s6 | modo worktree | passou |
| Nada que barrava deixa de barrar | classes `Recusa`, `Projeto`, `Limpar` verdes e inalteradas; sonda s8/s9 (opção-like, rc 2) | destino, `..`, opção | passou |

Nenhum caminho deixa clone na main nem sobre ref errada: todo retorno 1 depois do clone passa pelo `rmtree`; no modo revisão `ponto_de_partida` só devolve `origin/<branch>` ou `None`; sem `--revisao` o comportamento de COPIA-BASE é o mesmo (sonda s2: `--base develop` sem a branch no remoto cria a branch a partir de origin/develop, rc 0).

## Provas
- Clone de revisão criado com o próprio `--revisao` da branch: `forge-copia clone .../v0481-copia-mensagem-qa --branch melhoria/v0481-copia-mensagem --origem <remoto> --revisao` → rc 0, HEAD 7bdd25d5, sem upstream.
- Sonda (arquivo `_qa-v0481-copia-sonda.sh`, contra o remoto real): s1 rc 1 e clone apagado; s3 `origin/melhoria/nao-existe-xyz, origin/xx-nao-existe`; s4 `..., xx-nao-existe, origin/xx-nao-existe`; s5 rc 1, clone apagado; s6 rc 2, sem worktree; s7 sem upstream; s8/s9 rc 2.
- Vermelho: `forge-testes --vermelho 8833d0f69953017f4c5947d4c5f8dc33aca55bfa --modulos tests.test_forge_copia` → `vermelho: base=8833d0f69953 head=7bdd25d54a37 módulos=test_forge_copia (restrito por --modulos)`; `prova (asserção)=5; não prova (passa na base)=80` (os 80 são anteriores); rc 0.
- Mutação: `forge-mutante tests/mutantes/v0481-copia-mensagem.json` rev=7bdd25d54a37, M1 a M6 todos `morreu` (linhas 135, 145, 155, 157, 301, 331), rc 0. `v0481-copia-base.json` M1 a M7 todos `morreu`, rc 0. `--cobertura --base 8833d0f6` lista as condições 135, 145, 155, 157 e 301 cobertas ("declarado, não provado" é o rótulo da checagem; a prova é a rodada acima); a linha 331 é troca de argumento, com M6.
- Suíte inteira: no CI do PR (check-run `bateria`); na consulta, as partes da suíte do sha 7bdd25d5 estavam `in_progress`, então a bateria não foi citada como verde aqui e não foi rerrodada.
