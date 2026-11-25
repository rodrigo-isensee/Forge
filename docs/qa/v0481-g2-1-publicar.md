---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-g2-1-publicar
commit: c78bfe22110b57436b64bcc2866af1c03542938e
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0481-g2-1-publicar (E6.19, PR #878, G2.1: forge-check parecer publicar; classe C), volta por delta

Base 30dde218, head c78bfe22; delta lido: `git diff 0048e0c4..c78bfe22` (E6.17: `forge_pareceres.py`, `recusa_do_publicar`, hook `conformidade`, 5 fixtures, mutantes M24 a M33). Parecer anterior (0048e0c4) reprovado por A1. Sem CI da suíte lido neste head; local, só os cenários do módulo, com o `gh` falso do próprio teste; nenhum status de verdade gravado. A suíte inteira fica para o check-run `bateria` do PR.

## Critério → teste → resultado (delta; o quadro do parecer anterior segue de pé: os 29 testes de antes passam)
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A1 (QA): falha da API depois do status do papel não deixa `success` velho no agregado | test_falha_entre_o_papel_e_o_agregado_nao_deixa_success, test_publica_comentario_status_e_agregado (ordem pending, papel, agregado) | `gh` cai entre o status do papel e o agregado | passou |
| Recusa depois de gravar diz o que ficou | test_falha_antes_do_status_diz_o_que_ficou | falha na leitura do comentário | passou |
| M14.1 aceite do dono só vale para o `commit:` dele | test_c15_aceite_de_outro_commit | aceite de outro commit | passou |
| Arquivo sem frontmatter e lista de PRs ilegível recusam | test_sem_frontmatter, test_lista_de_prs_ilegivel | frontmatter ausente, `prs` não lista | passou |
| Item do agregado que não é objeto fica de fora | test_item_que_nao_e_objeto_fica_de_fora | status não objeto | passou |
| Hook barra o `publicar` com alvo no Forge em sessão de projeto (R-CONTRIB) | test_fixtures_do_publicar (5 fixtures V0481-PUBLICAR, lados 0 e 2) | `GH_REPO`, `--raiz` no Forge, sessão do Forge, projeto, outro subcomando | passou |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_forge_pareceres.py`: 35 testes, OK. `test_catraca.py`: OK. `test_hooks.py -k fixtures_do_publicar`: 1 teste, OK.
- Vermelho (`bin/forge-testes --vermelho 30dde2189bb640346aa202e407478fcb9f122e8b --modulos test_forge_pareceres`): `contagem: não prova (passa na base)=1; prova (API ausente)=32; prova (asserção)=2`; o único que não prova segue sendo `test_nenhum_workflow_usa_secrets` (guarda de regressão, aceito). Os novos do delta (`test_falha_entre_o_papel_e_o_agregado_nao_deixa_success`, `test_falha_antes_do_status_diz_o_que_ficou`, `test_lista_de_prs_ilegivel`) provam.
- Mutantes (`bin/forge-mutante --processos 2 tests/mutantes/v0481-g2-1-publicar{,-2,-3,-4,-5,-6}.json`, `rev=c78bfe22110b`): M1 a M33 `morreu`, rc 0, 1m48s. M21, M24, M25, M27 e M28 morrem por erro do teste sob o mutante com o controle verde (aceito). A de `is_absolute` saiu por equivalente (pathlib troca a raiz por caminho absoluto; `raiz / arquivo` mantém o comportamento).
- `--cobertura --base 30dde218`: toda condição Python do diff sai `coberta · … · declarado, não provado`, incluindo `forge_pareceres.py:38/49/58/69` e `hooks/conformidade.py:2564/2567`; só `hooks/conformidade.json` e `tests/pesos-d4.json` seguem "não coberto" (dados, provados por teste). Nenhuma linha de guarda mudada sem mutante.
- Sondas refeitas (arquivo `/root/.forge-contrib/wt/v0481-g2-1-publicar-qa-sonda/sonda_publicar.py`, `gh` falso): S1 (sem `refs/remotes/origin/develop`) inalterada, agregado `pending (faltam: parecer-qa)`. S2 corrigida: com o agregado antigo `success` e o `agregado()` falhando, o `pareceres pending` é gravado antes do `parecer-review failure`, o mais novo do agregado fica `pending` e a recusa diz `já gravado: o comentário no PR #7, pareceres pending, parecer-review failure`, rc 1. S3 (hook `autoria` sem `.forge/pareceres/`) segue igual: A3 continua.
- Leitura do diff: o delta troca `None` por `""` em `texto` (a recusa vem da checagem de caminho e frontmatter, coberta por `test_sem_frontmatter` e M21/M28), embrulha o `publicar` num `try` que reempacota `Recusa, KeyError, TypeError, AttributeError, ValueError` com o que ficou gravado, e soma um ramo novo no hook que só barra, sem relaxar guarda existente. Teto de linhas excedido declarado pelo autor (169): a conferência do tamanho é do review.

## O corte deixa o publicar seguro para entrar agora?
Sim. A1 está corrigido e provado vermelho/verde; o hook fecha a lacuna da sessão de projeto. Seguem como estavam os cartões A2 (pré-requisito escrito do G2.2: M1.4, M4.1, M4.2, M9.2, M9.3, M10.1, M10.2, M18.1) e A3 (hook `autoria` em `.forge/pareceres/`), recomendados, sem bloquear: nada lê o que o `publicar` grava.

## Achados
- A2 (recomendado) bin/forge_pareceres.py:1 · Cartão: M1.4, M4.1, M4.2, M9.2, M9.3, M10.1, M10.2 e M18.1 cortadas do G2.1; sem elas o G2.2 (leitura) não pode entrar. Registrar como pré-requisito escrito do G2.2 e corrigir o texto do PR sobre a permissão do token.
- A3 (recomendado) hooks/conformidade.py:3962 · M9.2 fica sem o hook `autoria` em `.forge/pareceres/`: o `publicar` recusa sempre (S3) e a medida do G2 não se move. Abrir cartão com prioridade antes do G2.2.

## Parecer
Aprovado no head c78bfe22. A1 (bloqueante) resolvido; 35 testes, vermelho provado, 33 mutantes mortos, cobertura sem lacuna de guarda. A2 e A3 viram cartões depois do merge.
