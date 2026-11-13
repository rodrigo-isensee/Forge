---
tipo: qa
contrato: 1
pedido: v046
branch: melhoria/pr-hook-prazo
commit: e8c4cd55cb291e562c454b1cb15f16f4b3a875cf
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-12
---
# QA: v046 (E20.5, PR-HOOK-PRAZO)

Diff: `origin/develop...b08296cd` (código do 4ae51318; depois só pareceres de segurança e review). O `forge-check pr` grava o resultado por head em `<git-common-dir>/forge/pr/<head>/` e o hook `parecer` libera a abertura do PR só lendo o aprovado do mesmo head, branch e base. Não há especificação de UX (ferramenta do Forge): as obrigações vêm da E20.1 do pedido e de `R-REVIEW`; os testes são os do autor, conferidos e rodados por mim.

## Achados
- A2 (bloqueante) bin/forge-check:1544 · a guarda `not velha.is_symlink()` da poda (apagaria arquivos dentro de pasta apontada por link) não tem mutante nem teste: `and True and` sobrevive (meu Q3, rc 1); declare o mutante e crie link sha40 na pasta do teste
- A3 (recomendado) bin/forge-check:1544 · `velha.is_dir()` e `velha != pasta` trocadas por `True` também sobrevivem (Q4, Q1); declare mutante, ou equivalente justificado (head recém-gravado é ponta)

## Critério → teste → resultado
| Obrigação (E20.1) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Aprovado do head libera só lendo, dentro do prazo de 3 s | test_aprovado_do_head_libera_so_lendo_dentro_do_prazo | prazo de produção; hook não refaz a checagem (saída 97) | passou |
| Reprovado do head recusa com a violação | test_reprovado_do_head_recusa_so_lendo | resultado reprovado | passou |
| Sem resultado do head: recusa e diz o comando | test_head_diferente_recusa_e_diz_o_comando, test_sem_resultado_recusa_mesmo_sem_violacao | outro head; resultado ausente | passou |
| Outra base, outra branch, outro head, registro ilegível ou estranho não valem | test_resultado_de_outra_base_recusa, test_ilegivel_de_outra_branch_ou_de_outro_head_nao_vale | base nula x develop; JSON quebrado ao lado do aprovado | passou |
| Pedido da branch sem resultado, branch sem pedido, lista malformada | test_pedido_da_branch_sem_resultado_recusa, test_branch_sem_pedido_gravado_recusa, test_pedidos_da_branch_malformado_nao_derruba_a_leitura | vazio; tipo errado | passou |
| Merge segue a conferência de sempre | test_merge_segue_a_conferencia_de_sempre | merge sem cache (v0455) | passou |
| `forge-check pr` grava reprovado/aprovado; previo e HEAD sem branch não gravam | test_pr_grava_o_reprovado_e_o_hook_o_le, test_pr_aprovado_grava_e_o_hook_libera_so_lendo, test_previo_e_head_sem_branch_nao_gravam | modo 0700; sem branch | passou (ver A1) |
| Ref ou base que não resolvem são ausentes | test_ref_ou_base_que_nao_resolvem_sao_ausentes | ref inexistente; base nula | passou |
| Falha ao gravar avisa e não muda o código | test_falha_ao_gravar_avisa_e_nao_muda_o_codigo | `.git/forge` é arquivo | passou |
| Fixtures do hook parecer seguem verdes com o `resultado_do_pr` | 454 fixtures de tests/hooks/parecer | permissões, rascunho, merge | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_pr_hook_prazo`: Ran 15 tests in 49.602s, OK.
- Fixtures do hook parecer (as 454 sem prazo de produção, pelo executar_em_lote do test_hooks): 454 de 454, OK (175 s). O `test_fixtures` inteiro estoura 500 s nesta máquina, por isso o recorte. As 5 falhas de agentes/* e pesado/mesma-sessao-libera citadas no brief estão fora da pasta parecer e caem também na develop (review E20.3); não as rodei.
- Mutantes: `forge-mutante --cobertura --base d3453407` rc 0, toda condição mudada com mutante declarado; 2 isentas lidas (`base_sha or ''` só compõe o nome do arquivo, a leitura casa pelo conteúdo; `'veja a saída dele'` é texto de reserva), aceitas. As 5 specs: 33 de 33 morreram, rc 0. M25 morreu por erro do teste declarado, não por asserção (mesma causa do A1).
- Vermelho antes do verde (`forge-testes --vermelho d3453407 --modulos test_pr_hook_prazo`): 13 de 15 provam (3 por asserção, 10 por API ausente); test_previo_e_head_sem_branch_nao_gravam passa na base (guarda negativa, provada pelos mutantes); test_pr_grava_o_reprovado_e_o_hook_o_le sem veredito; saída rc 2 (A1).
- Fora desta entrega: o forjamento do aprovado por escrita em `.git/forge/` (A2 da segurança, E20.6).
- Prova de CI: a suíte inteira roda no CI do PR (check-run `bateria` do mesmo sha); o PR ainda não existe, não citei.

## Revalidação por delta (b08296cd..c6577dbb)
O A1 anterior (vermelho rc 2) está resolvido em tests/test_pr_hook_prazo.py:91: `um_registro` conta antes de desempacotar e `str()` na leitura da violação; `forge-testes --vermelho` sai rc 0 e M25 morre por asserção.

`forge-check parecer delta` listou no domínio: bin/forge-check, hooks/_comum.py, hooks/parecer.py, changelog.d, tests/apoio_volta_unica.py, test_pr_hook_prazo.py e as specs de mutante. Obrigações novas (E20.11): registro com escritor (sha256 do forge-check), poda dos heads que não são ponta, contorno "rode antes forge-check pr" só no `gh pr create` sem resultado, changelog do `--draft`.

| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Registro de outro escritor ou sem escritor não vale | test_ilegivel_de_outra_branch_ou_de_outro_head_nao_vale (subtestes "outro escritor", "sem escritor"); M38 | escritor ausente/outro | passou |
| Poda apaga só head que não é ponta; sem lista de pontas, nada; falha só avisa; falha ao gravar não poda | test_gravar_poda_os_heads_que_nao_sao_mais_ponta, test_falha_ao_gravar_avisa_e_nao_muda_o_codigo; M34-M37, M41 | ponta de branch; não-head; erro ao apagar | passou (ver A2, A3) |
| Prazo vencido diz "rode antes" só no `gh pr create` sem resultado; merge segue o contorno de sempre | test_prazo_vencido_diz_rode_antes_so_no_pr_create_sem_resultado; M39, M40 | create x merge | passou |
| A1 do QA: vermelho sem veredito | um_registro nos 5 testes; M25 | registro ausente na base | passou |

- `python3 -m unittest tests.test_pr_hook_prazo`: Ran 17 tests in 27.215s, OK.
- `bin/forge-testes --vermelho d3453407 --modulos test_pr_hook_prazo`: rc 0; `vermelho: base=d3453407cd9a head=c6577dbb3253`; 17 testes: prova (asserção)=5, prova (API ausente)=11, não prova (passa na base)=1 (test_previo_e_head_sem_branch_nao_gravam, guarda negativa provada por mutantes).
- `forge-mutante` das 6 specs numa rodada: rc 0, 41 de 41 morreram (M25 morreu em bin/forge-check:1562). M34-M41 conferidos: um por linha de guarda nova, salvo A2 e A3. `--cobertura --base d3453407`: toda condição coberta, 2 isentas já aceitas.
- Meus mutantes extras na poda (spec fora do repositório): Q1 `velha != pasta` sobreviveu, Q2 `SHA40.match` morreu, Q3 `not velha.is_symlink()` sobreviveu, Q4 `velha.is_dir()` sobreviveu.
- Prova de CI: o PR ainda não existe; não citei `bateria`.

## Revalidação por delta (c6577dbb..cf1cc45d, volta E20.25)
`forge-check parecer delta` listou no domínio só tests/test_pr_hook_prazo.py e tests/mutantes/v046-pr-hook-prazo-7.json; sem código de produção (bin/forge-check intacto). Teste novo test_poda_nao_segue_link_nem_abre_arquivo_nem_apaga_a_gravada (link sha40 para pasta de fora com alvo.json, arquivo sha40, head fora das pontas).

| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A2: a poda não segue link com nome de sha | teste novo; M42 | link para pasta de fora | passou; M42 morreu por `o link não é seguido: nada na pasta apontada se apaga` |
| A3: a poda não abre arquivo sha40 como pasta, nem apaga a gravada | teste novo; M43, M44 | arquivo no lugar de pasta; head gravado fora das pontas | passou; M43 morreu por `resultados antigos ... Not a directory`; M44 por `um registro gravado para o head` (0 != 1) |

- `python3 -m unittest tests.test_pr_hook_prazo` (worktree destacada minha em cf1cc45d): Ran 18 tests in 44.461s, OK.
- `bin/forge-mutante tests/mutantes/v046-pr-hook-prazo-7.json`: M42, M43 e M44 morreram, todos em bin/forge-check:1544. Reaplicados à mão um a um: cada um cai só no teste novo, pela asserção acima (motivo certo, não erro de carga). `--cobertura --base d3453407`: rc 0.
- Os A2 e A3 estão resolvidos; nenhum achado aberto. Prova de CI: o PR ainda não existe; não citei `bateria`.

## Revalidação por delta (cf1cc45d..e8c4cd55, merge da develop)
`forge-check parecer delta` (escopo sem o que veio da base) listou no domínio só `bin/forge-testes` (MAPA: `test_hook_git_comum` entra em FORGE_CHECK; linhas de scripts/templates vindas da develop) e `tests/test_testes_tocados.py` (contagem 79 para 80, + test_hook_git_comum). `bin/forge-check`, hooks e tests/test_pr_hook_prazo.py intactos; o `.claude/CLAUDE.md` mudado veio da base, fora do meu domínio.

| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Mapa dirigido de `bin/forge-check` cobre os módulos, com a contagem exata | test_forge_check_roda_os_modulos_dele | contagem 80 (módulo novo do merge) | passou |
| Hook parecer segue verde no head | test_pr_hook_prazo (18) | prazo, escritor, poda | passou |

- `python3 -m unittest tests.test_testes_tocados tests.test_hook_git_comum tests.test_pr_hook_prazo`: Ran 168 tests, OK (skipped=1, ambiente: /proc de outro namespace, teste da vaga pesada, não meu).
- Sem código de guarda novo: nenhum mutante a conferir; vermelho e mutação do cf1cc45d valem. Prova de CI: o PR ainda não existe; não citei `bateria`.
- Nenhum achado aberto.
