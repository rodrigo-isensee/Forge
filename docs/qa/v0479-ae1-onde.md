---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae1-onde
commit: bef021c1cf681e4ca46590b0bc01eafcc3194025
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0479-ae1-onde (AE1.1, `forge-check onde`, E58.1)

Código testado: `bef021c1`, clone `~/.forge-contrib/wt/v0479-ae1-onde-E588`, árvore limpa. Sem PR e sem `bateria` do CI neste head: a suíte inteira fica para o CI do PR; aqui só os arquivos tocados, com `TMPDIR`. Não há `docs/ux` nem contrato de API para o AE1.1; os critérios vêm do escopo da E58.1 e do cabeçalho de `bin/forge_onde.py`.

## Achados
- A1 (recomendado) bin/forge-testes:656 · `--vermelho` roda o executor com o script do HEAD; módulo novo de `bin/` importado por `sys.path` sai "passa na base" (29 de 30 aqui); cópia da base à mão falha no import. Vira cartão.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1 alvo inválido (opção, `..`, `.lock`, quebra de linha) sai rc 2 sem chegar ao git | `Alvo.test_entrada_invalida_nao_chega_ao_git`, `Alvo.test_branch_com_prefixo_e_sem_barra`; sonda `onde -- --x`, `a..b/c`, `#12` seguido de quebra de linha: rc 2 | começo com `-`, `..`, final `.lock`, quebra de linha | passou |
| CA-2 versão e commit: presença em develop, homolog e main por `merge-base --is-ancestor` com o sha lido | `VersaoECommit.*` (7 testes); sonda `v0.47.10` (main sim; develop e homolog nao) | tag ausente rc 1, base sem branch, merge-base que falha | passou |
| CA-3 falha de leitura é `nao-verificavel`, nunca `sim` | `test_merge_base_que_falha_e_nao_verificavel_nunca_sim`, `test_sem_nenhuma_base_no_clone_e_nao_verificavel`, `test_rev_parse_com_saida_que_nao_e_sha_nao_vale` | rc do git fora de 0/1; saída que não é sha | passou |
| CA-4 PR: estado, base, head, quem mesclou e onde o commit do merge está | `Pr.*` (8 testes); sonda real `#722` e `pr:722` (develop sim) | gh lento, resposta de outro PR, commit do merge ausente ou que não é sha, PR aberto | passou |
| CA-5 branch: origin vence a local, frente e atrás da develop, PR de nome exato | `Branch.*`; sonda `branch:melhoria/v0479-ae1-onde` (rc 0) e `branch:melhoria/inexistente` (rc 1) | nome inexistente, PR de head parecido, item que não é PR | passou |
| CA-6 cartão: ID inteiro (`AE1` não casa `AE10` nem `AE1.1`), commit mais novo por base | `Cartao.*`; sondas `A` (rc 0) e `RETROS-V047-A-V0478` (rc 1) | prefixo de outro ID, base sem branch, nenhum commit | passou |
| CA-7 saída sem caractere de controle e só leitura | `Pr.test_texto_do_gh_sai_sem_controle`, `PeloForgeCheck.test_subcomando_onde_imprime_e_sai_com_o_rc` | ANSI e controle vindos do gh | passou |

## Execução
- `python3 -I -m unittest discover -s tests -p test_forge_onde.py`: `Ran 30 tests ... OK`.
- `forge-mutante --cobertura --base 5ccac0bf`: rc 0; 41 linhas `coberta`; `não coberto: tests/pesos-d4.json` é dado (JSON), sem condição de guarda. Nenhuma condição Python mudada sem mutante.
- `forge-mutante --processos 2` sobre as 7 specs `tests/mutantes/v0478-ae1-onde*.json`: 49 mutantes (M1 a M49), 49 `morreu`, zero sobrevivente, zero sem veredito, rc 0. Os `(erro)` morreram com o controle verde.
- Vermelho: `forge-testes --vermelho 5ccac0bf... --modulos test_forge_onde`: `vermelho: base=5ccac0bf616c head=bef021c1cf68`; `contagem: não prova (passa na base)=29; prova (asserção)=1`, rc 0. Os 29 "passam na base" são falso negativo da ferramenta (A1): numa cópia da base com o teste novo, `python3 -I -m unittest discover -s tests -p test_forge_onde.py` dá `ModuleNotFoundError: No module named 'forge_onde'`, ou seja, todos os testes caem na base.

## Bugs
Nenhum aberto.
