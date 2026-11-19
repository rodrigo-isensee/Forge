---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-sandbox-controle
commit: 03448b3d8050f9e865791f50b6bd300df51ec001
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0478 E29.1 (A3, trava de escrita do sandbox nos arquivos de controle)

## Achados
- A1 (bloqueante) tests/test_apoio_sandbox.py:77 · test_bwrap_ausente_ou_que_nao_monta_falta_e_o_que_monta_nao está recuado dentro de ambiente_sem_ci, depois do return: nenhum teste o coleta (22 rodam, 0 de bwrap). Mutante falta_bwrap sempre None sobrevive. Mova-o para a classe Sondas.
- A2 (recomendado) tests/test_sandbox_controle.py:178 · o hook grava fora do sandbox; o bwrap vivo ao lado não influi, então "e o hook grava" é verdade trivial. Prove-o pelo denyWrite não cobrir o que o hook grava (já feito na Estrutura) ou tire a alegação do nome.
- A3 (recomendado) .github/workflows/ci.yml:1 · o CI não instala nem sonda bubblewrap; se o runner não monta namespace, os dois testes de sandbox reprovam (exigir falha com CI). Cite o check-run do PR; sem ele a prova do CI não existe.

## Critério → teste → resultado
Obrigação: decisão A3 do dono (denyWrite nos arquivos de controle, hooks gravando, teste com find -delete, tar e chmod recusados), Forge e modelo.
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A3 modelo nega os 5 caminhos | Estrutura.test_modelo_de_projeto_nega_os_cinco_caminhos_de_controle | permissão (denyWrite) | passou; mutante denyWrite vazio morre (3 falhas, 1 erro) |
| A3 Forge via patch | Estrutura.test_forge_com_o_patch_nega_o_clone_e_o_registro_da_maquina, test_o_patch_so_acrescenta_dois_caminhos_ao_denywrite | permissão | passou |
| hooks seguem gravando nos mesmos caminhos | Estrutura.test_os_caminhos_negados_sao_os_que_os_hooks_gravam, test_nada_do_time_grava_nos_caminhos_negados_pelo_bash | permissão | passou (H=ok, B=ok: não prova na base) |
| N6 arquivo versionado | Estrutura.test_o_denywrite_do_forge_nao_cobre_arquivo_versionado | limite | passou; prova (asserção) |
| recusa por find -delete, tar e chmod | SandboxNegaEscrita (2 testes) | permissão | pulado aqui (bwrap sem namespace); sem veredito |
| sonda falta_bwrap | test_bwrap_ausente... | vazio, erro, timeout | nunca roda (A1) |

## Cenários e resultado real
Local, `TMPDIR` próprio: `test_sandbox_controle` 8 testes, 6 ok, 2 pulados (bwrap: Operation not permitted); `test_apoio_sandbox` 22 ok (o novo não está entre eles).

Vermelho (`forge-testes --vermelho 738424449cf9... --modulos test_sandbox_controle,test_apoio_sandbox --prazo 120`), saída rc 2:
```
vermelho: base=738424449cf9 head=03448b3d8050 módulos=test_sandbox_controle,test_apoio_sandbox (restrito por --modulos)
...SandboxNegaEscrita.test_forge_com_o_patch_recusa_find_tar_e_chmod · H=pulado · B=falha · pulado
...SandboxNegaEscrita.test_modelo_de_projeto_recusa_find_tar_e_chmod_e_o_hook_grava · H=pulado · B=falha · pulado
contagem: não prova (passa na base)=22; prova (API ausente)=1; prova (asserção)=4; pulado=2; sem veredito=1
sem veredito: volta ao autor; não vale como vermelho nem como já falhava.
```
A rodada sem `--modulos` estourou 550 s sem saída (rc 124), sem veredito.

## Pergunta do dono: a prova no CI basta, e o teste reprovaria sem a trava?
- Reprovaria, por leitura e não por execução: `ataca` monta o bwrap com um `--ro-bind` por alvo e exige rc diferente de 0, alvo e modo intactos. Sem a trava (denyWrite vazio) não há alvos, e o controle `livre` do mesmo ataque já prova que o ataque funciona sem `--ro-bind`. Aqui só o lado estrutural foi visto cair (mutante denyWrite vazio: 3 falhas e 1 erro). O lado bwrap nunca foi visto vermelho nem verde em máquina alguma.
- Limite: o teste monta o `--ro-bind` ele mesmo, como o runtime do Claude Code faria; prova que o `--ro-bind` recusa os três ataques, não que o runtime transforma o `denyWrite` em `--ro-bind` nem o que faz com caminho inexistente (o devops admite). Esse elo não tem prova.
- Suficiente só com condição: o check-run `bateria` do mesmo sha com os dois testes verdes e sem pulo (no CI `exigir` reprova, não pula). Hoje não há run para o sha (`gh run list` vazio para a branch, sem PR); o bwrap do runner não é garantido (A3). Sem esse verde, não basta.
