---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-g2-1-publicar
commit: 0048e0c4160e62e66f5a166b068911e58c9ce848
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 1
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0481-g2-1-publicar (E6.15, PR #878, G2.1: forge-check parecer publicar; classe C)

Base 30dde218, head 0048e0c4. Fontes: ADR 0019 (develop), modelo de ameaças `docs/security/ameacas/g2-parecer-status.md` (#876, head a88163c9), corpo do PR. Sem CI da suíte neste head: o check-run `bateria` do run 45520013266 falhou só no job `bateria (pareceres)` (parecer ainda não existe, esperado) e as suítes foram canceladas; a suíte inteira fica para o CI depois do parecer. Local: só os cenários do módulo, com o `gh` falso do próprio teste; nenhum status de verdade gravado.

## Critério → teste → resultado
Obrigações: mitigações do modelo de ameaças que o §3 atribui ao G2.1, mais a ADR 0019 (§2 e §3).
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| M2.1 contexto fora da lista recusado na escrita | test_c3_tipo_ou_veredito_fora_da_lista | contexto/veredito fora da lista | passou |
| M5.3 corpo devolvido difere do local, status não gravado | test_c20_corpo_devolvido_difere_do_local, test_crlf_devolvido_vale | fim de linha, caractere trocado | passou |
| M7.1 sha256 de 64 hex, descrição até 140 | test_c9_sha256_inteiro_e_teto_de_140 | 140 exato e 141 | passou |
| M9.1 sem registro de autoria, recusa; papel autor recusa | test_c11_sem_autoria_jsonl_recusa, test_c11_papel_autor_publica, test_texto_mudado_depois_da_autoria | arquivo ausente, papel errado, texto mudado | passou |
| M13.1 agregado recalculado, exigido inválido deixa pending | test_agregado_pending_com_exigido_invalido, test_todos_os_exigidos_success | exigido ausente, failure, descrição fora da forma | passou |
| M14.1 riscos-aceitos sem aceite | test_c15_riscos_aceitos_sem_aceite | sem aceite | passou |
| M19.1 erro/ausência do gh, statuses ilegíveis | test_c17_gh_com_erro_ou_ausente, test_statuses_ilegiveis_recusam | gh ausente, saída ilegível | passou |
| ADR 0019 §3 só o PR aberto da branch, head igual ao `commit:` | test_commit_que_nao_e_head_do_pr, test_dois_prs_da_branch, test_branch_de_nome_parecido_nao_casa, test_comentario_de_outro_pr | 0, 2 PRs; head velho; nome parecido | passou |
| ADR 0019 §1.2 caminho `.forge/pareceres/<pedido>/<tipo>.md` | test_caminho_fora_de_forge_pareceres, test_pedido_ou_tipo_diferente_do_caminho, test_arquivo_ausente | caminho fora, id diferente | passou |
| M1.3 nenhum workflow usa secrets | test_nenhum_workflow_usa_secrets | n/a (passa na base: guarda de regressão, ver vermelho) | passou |
| Regra de caminho por papel em `.forge/pareceres/*` | test_caminho_por_papel_em_forge_pareceres | papel errado no caminho | passou |
| M1.4, M4.1, M4.2, M9.2, M9.3, M10.1, M10.2, M18.1 | sem teste: cortados pelo autor | n/a | ver Achados A2 |
| Falha da API depois de gravar o status do papel: o agregado não pode ficar `success` | nenhum; sonda S2 | `gh` falha entre o status do papel e o agregado | FALHOU (A1) |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_forge_pareceres.py`: 29 testes, OK. `test_catraca.py`: OK.
- Vermelho (`bin/forge-testes --vermelho 30dde2189bb640346aa202e407478fcb9f122e8b --modulos test_forge_pareceres`): `vermelho: base=30dde2189bb6 head=0048e0c4160e módulos=test_forge_pareceres (restrito por --modulos)`; `contagem: não prova (passa na base)=1; prova (API ausente)=26; prova (asserção)=2`; rc 0. O único que não prova é `test_nenhum_workflow_usa_secrets` (guarda de regressão do estado de hoje, aceito).
- Mutantes (`bin/forge-mutante --processos 2 tests/mutantes/v0481-g2-1-publicar{,-2,-3,-4}.json`, `rev=0048e0c4160e`): M1 a M23 `morreu`, rc 0 (M21 por erro do teste sob o mutante, com controle verde). `--cobertura --base 30dde218` lista sem mutante: `bin/forge-check:3751` (`is_absolute`, equivalente em pathlib), `:3754` (`texto is not None`, coberto por M21), `bin/forge_pareceres.py:38`, `:49` (`isinstance(prs, list)`), `:58` (`url`), `:69` (`isinstance(s, dict)`); todas defensivas de tipo, sem efeito observável a mais; `hooks/conformidade.json` e `tests/pesos-d4.json` são "não coberto" (dados, provados por `test_caminho_por_papel_em_forge_pareceres`). Nenhum mutante sobrevivente.
- Sonda S1 (sem `refs/remotes/origin/develop`): `exigidos_do_pr` cai em review e QA, agregado `pending (faltam: parecer-qa)`; não abre para menos.
- Sonda S2 (arquivo `/root/.forge-contrib/wt/v0481-g2-1-publicar-qa-sonda/sonda_publicar.py`, `gh` falso): com o agregado antigo `success` e o `agregado()` falhando (API caiu) depois do POST do status do papel como `reprovado`: `rc 1`, `parecer-review failure` gravado, `pareceres success` continua. Ordem em `bin/forge_pareceres.py:91-93`.
- Sonda S3: o hook `autoria` (`hooks/conformidade.py:3956-3973`) só registra `docs/{reviews,qa,devops,security}/`; o texto escrito em `.forge/pareceres/` não gera registro. Consequência: o `publicar` do texto gravado no caminho que ele mesmo exige recusa sempre por "autoria: sem registro" (M9.1 sem M9.2). Falha fechada, mas o fluxo ponta a ponta do G2.1 não roda até o item do hook.

## O corte deixa o publicar seguro para entrar agora?
Sim, com A1 corrigido e a condição de A2, porque hoje nada lê o que ele grava: o `forge-check pr`, o `forge-fechar` e o hook `parecer` seguem pelos arquivos (G2.2 ainda não existe) e o contexto `pareceres` não está nos checks exigidos da `develop` (D3 a do dono, não aplicada). Status forjado ou publicação sem o registro (M4.1, M4.2, M10.1, M10.2, M18.1, M1.4) não destrava merge nenhum. O texto do PR afirma que o publicar "recusa por falha fechada sem a permissão do token"; a premissa não vale: o token de hoje é o clássico do dono com `repo` e já grava status e comentário (modelo, M17.2). O que o torna inerte hoje é a falta de registro de autoria (S3), por acidente. As oito mitigações cortadas eram requisito do G2.1 a G2.4 pelo §2 do modelo; entram como cartões e como pré-requisito do G2.2 (A2).
Nada que barra hoje deixa de barrar: o diff só soma (`recusa_do_publicar`, `cmd_parecer_publicar` e o argparse são ramos novos; `conformidade.json` só ganha quatro entradas; `PROTEGIDOS` ganha um item; `forge-testes` ganha o módulo no mapa). Conferido por leitura do diff, sem linha de guarda existente alterada.

## Achados
- A1 (bloqueante) bin/forge_pareceres.py:91 · Falha fechada incompleta: o status do papel é gravado antes do agregado. Se o `agregado()` falha (sonda S2), o `pareceres` antigo `success` fica ao lado de `parecer-review failure`. Recalcular antes de gravar ou, em falha, gravar `pending`; teste.
- A2 (recomendado) bin/forge_pareceres.py:1 · Cartão: M1.4, M4.1, M4.2, M9.2, M9.3, M10.1, M10.2 e M18.1 cortadas do G2.1; sem elas o G2.2 (leitura) não pode entrar. Registrar como pré-requisito escrito do G2.2 e corrigir o texto do PR sobre a permissão do token.
- A3 (recomendado) hooks/conformidade.py:3962 · M9.2 fica sem o hook `autoria` em `.forge/pareceres/`: o `publicar` recusa sempre (S3) e a medida do G2 não se move. Abrir cartão com prioridade antes do G2.2.

## Parecer
Reprovado por A1, defeito provado por sonda em controle (bug médio: nada lê o agregado ainda). O restante cumpre o que o modelo atribui ao G2.1 e que não foi cortado, com 29 testes, vermelho provado e 23 mutantes mortos. Com A1 corrigido, aprovo o corte para entrar agora, com A2 e A3 como cartões e pré-requisitos do G2.2.
