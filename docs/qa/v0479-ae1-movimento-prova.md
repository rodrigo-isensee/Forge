---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae1-movimento-prova
commit: 8bdb976e63e52fb1deaba33e99999f86bc373595
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0479-ae1-movimento-prova (AE1.2, `forge-check movimento --prova`, E58.19 e E58.24; E58.28)

Código testado: `8bdb976e`, clone `~/.forge-contrib/wt/v0479-ae1-movimento-prova-E5828`, árvore limpa. Sem PR e sem `bateria` do CI neste head: a suíte inteira fica para o CI do PR; aqui só os arquivos tocados, com `TMPDIR`. Sem `docs/ux` nem contrato de API; os critérios vêm do escopo da E58.19/E58.24 e do docstring de `cmd_movimento` e `prova_do_movimento`.

## Achados
- A1 (bloqueante) tests/test_fechar_forge_check_real.py:123 · Regressão provada: com o forge-check real, forge-fechar --cartao sai 3 e não move o cartão (módulo vizinho, não tocado pelo diff, que eu não havia rodado); passa na base ed5bfa02. Bug QA-AE12-1.
- A2 (recomendado) bin/forge_onde.py:167 · `--cobertura` lista sem mutante `title or ''`, `body or ''` (linha 167) e `tipo or '-'` (201): efeito só no texto da recusa. Declarar equivalente ou mutante depois do merge; vira cartão.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1 Pronto ou Fechado* exige `--prova`; prova só com esses destinos, nada gravado no desencontro | `test_sobreposicao_quadro` (movimento com prova); mutantes MV1..MV8 | prova ausente, prova com outro destino, `Fechado*` | passou |
| CA-2 `pr:#N` só mesclado na develop e que cita o cartão inteiro; `commit:<sha>` ancestral da develop que cita o cartão | `test_forge_onde` (prova do movimento); MV9..MV23, MV26..MV30 | PR aberto, base errada, cartão `AE1` x `AE10`/`AE1.1`, sha fora da forma | passou |
| CA-3 `rodar:<slug>` lê o `run.json` do slug com rc 0; `juntado:<ID>` só outro cartão ativo | `test_forge_onde`; MV24, MV25, MV31 | slug inválido, link simbólico, rc diferente de 0, o próprio cartão, cartão já final | passou |
| CA-4 leitura que falha (`gh`/`git` lento) deixa o cartão em "Aguardando sua validação" (rc 1), com aviso; prova recusada não grava | `test_sobreposicao_quadro`; `test_forge_onde` | `nao-verificavel` nunca vira `ok`; quadro sem a coluna: nada gravado | passou |
| CA-5 `forge-fechar` passa `pr:#N` (ou `commit:` quando o head já estava na base) ao mover o cartão, também no `--limpar`, no `--dry-run` e no comando de recuo | `test_fechar_move_cartao` (14); FP1..FP4 | PR mesclado achado só por head igual; sem PR lido; movimento que falha vira pendência 3 | passou |
| CA-6 skill do quadro cita `--prova` | `test_sobreposicao_quadro.RegrasEmTexto` | `n/a` | passou |

## Cenários e resultado real
- Testes dos módulos tocados, `python3 -I -m unittest discover -s tests -p <arq>`: `test_forge_onde` 48 OK, `test_fechar_move_cartao` 14 OK, `test_sobreposicao_quadro` 64 OK.
- Vermelho (`bin/forge-testes --vermelho ed5bfa0284c3bbf2ac006d546daf96b1346886ff --modulos tests.test_forge_onde,tests.test_fechar_move_cartao,tests.test_sobreposicao_quadro`), rc 0: `vermelho: base=ed5bfa0284c3 head=8bdb976e63e5 módulos=test_forge_onde,test_fechar_move_cartao,test_sobreposicao_quadro (restrito por --modulos)`; `contagem: não prova (passa na base)=96; prova (API ausente)=16; prova (asserção)=14`. Os 30 testes novos provam; os 96 já existiam e passam na base.
- Mutação (`bin/forge-mutante --processos 3` nas 7 specs `v0478-ae1-movimento{,-2,-3,-4}`, `ae1-fechar-prova`, `ae1-onde-2`, `ae1-onde-5`), rc 0: `forge-mutante: pedido=v0478 rev=8bdb976e63e5`, todos os mutantes `morreu` (MV1..MV31, FP1..FP4, M9..M16, M33..M40), nenhum sobrevivente, nenhum equivalente.
- Cobertura (`--cobertura --base ed5bfa02...`): `mb=ed5bfa02`, `rev=8bdb976e`; guardas Python cobertas, exceto as três linhas do A1; `bin/forge-fechar` sai `não coberto` por ser shell, mas tem FP1..FP4 nas linhas 810, 1353 e 1536; `spec editada` em `ae1-onde-2` e `ae1-onde-5` (4 linhas cada, mutantes seguem matando).
- Falha no vizinho: `python3 -I -m unittest discover -s tests -p test_fechar_forge_check_real.py` no head: 5 testes, `FAILED (failures=1)`, `fim: código 3` (confere o review A1). Os testes dos arquivos tocados passam porque o mock do forge-check aceita a prova; a integração real a recusa.
- Não rodei a suíte inteira (CI do PR) nem `claude plugin validate`.
