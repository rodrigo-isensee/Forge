---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-catraca-ajudante
commit: ab293a4e9da5ca4969ff60e8734b020d7b07bced
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: v0481-catraca-ajudante (#891, E14.17)

## Achados
- A1 (bloqueante) tests/mutantes/v0480-d3-teste-enfraquecido-2.json:1 · a PR muda linhas que 3 specs antigas citam (D3B5 no -2, D3C5 no -3, D3D2 no -4: "aparece 0 vezes"). `forge-mutante --conferir --todas` acusa e o check bateria do sha falha em test_forge_mutante.py:1564. Atualize `de`/`para`.
- A2 (bloqueante) tests/test_catraca.py:817 · mutantes sobreviventes: Q1/Q2/Q7 (tirar `e` dos valores do ajudante, ou os argumentos/nomeados constantes da chamada, em catraca.py:729) e Q4 (FUNDO=1). O teste só compara FUNDO consigo mesmo. Troca de argumento ou ajudante em cadeia sem teste.

## Critério → teste → resultado
| Critério (brief) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Conta ajudante self./cls./base do módulo/função do módulo | test_ajudante_com_assercao_conta_e_o_sem_assercao_nao | ajudante sem asserção = 0; base em laço | passou (vermelho: API ausente na base) |
| Tirar a chamada ou a asserção do ajudante barra | test_chamada_ao_ajudante_tirada_ou_ajudante_sem_assercao_barra | 4 variantes | passou (vermelho: asserção) |
| Troca `self.fica`→`self.sai` vista | test_ajudante_invertido_fica_listado_para_o_revisor | só em `valores_para_conferir`, não barra na 1ª entrega (desenho D3) | passou (vermelho: asserção) |
| Teste de 0 asserções não pareia como renomeado | test_renomeado_sem_assercao_barra_e_com_ajudante_passa | 0 asserção | passou (vermelho: asserção) |
| Argumentos constantes contam como valor esperado | nenhum | n/a | sem prova: Q2 e Q7 sobreviveram (A2) |
| Ajudante recursivo / de outro módulo não quebra | test_ajudante_com_assercao_... (laço, recursivo); sonda | recursão (8 níveis), mútua, outro módulo | passou; encadeamento > 1 nível sem teste (Q4) |
| Nada que barra hoje deixa de barrar | sonda (abaixo) | monotonia | passou |

## Cenários e resultado real
- Vermelho (`bin/forge-testes --vermelho 220ba3fa27fe68bf9f7d52c703fffaeaaf8de41d --modulos test_catraca`, rc 0): `vermelho: base=220ba3fa27fe head=ab293a4e9da5 módulos=test_catraca (restrito por --modulos)`; revertidos: changelog.d/v0481-catraca-ajudante.md, tests/catraca.py. 4 provas: 3 "prova (asserção)" e 1 "prova (API ausente)" nos 4 testes novos; nenhum cai no HEAD.
- Mutantes do autor: `forge-mutante` nas duas specs, 13 de 13 morreram (CA1-CA13); `--cobertura --base` lista as 11 condições mudadas como cobertas.
- Mutantes meus (spec em arquivo, fora da branch), saída: Q1 sobreviveu (catraca.py:729), Q2 sobreviveu (729), Q3 morreu (730), Q4 sobreviveu (685), Q5 morreu (726), Q6 morreu (739), Q7 sobreviveu (729), Q8 morreu (708). rc 1.
- Sonda sobre todos os `tests/*.py` da branch, perfil antigo contra o novo: 6711 testes, 1702 sobem de contagem, 0 baixam, 0 perdem valor esperado, 0 mudam pulos. Os 1736 de 6824 do brief são da develop inteira, não reconferi essa contagem.
- Sonda de bordas (nenhuma explode): ajudante mutuamente recursivo conta 8 e termina; `chk()` importado, `util.chk()`, `self.nao_existe()`, `super().h()` e ajudante só com asserção vácua dão 0, como na base; `@classmethod`/`@staticmethod` por `self.`, `T.s()` (nome de classe) e `async` funcionam ou ficam em 0 sem erro; `class A(A)` termina.
- Observação (não bloqueia, vem da base): o `skipTest` dentro de ajudante não soma pulo ao teste que o chama; só as asserções do ajudante somam.
- CI do sha (check-run `bateria`): failure. `suíte parte 4/5` (3.12 e 3.14) falha em tests/test_forge_mutante.py:1564 (`ConferirTodas...`), reproduzido local por `forge-mutante --conferir --todas` (A1). O check `catraca` também falhou no mesmo run; o motivo não foi lido (log fora do alcance do sandbox).
- Bugs: A1 é bug alto (bloqueia o CI); sem arquivo em `docs/qa/bugs/`, o achado carrega os passos.
