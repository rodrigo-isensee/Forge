---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-catraca-ajudante
commit: e05f8faab1b446658ee262461a6483829eae5c7b
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: v0481-catraca-ajudante (#891, volta E14.23, delta ab293a4e..e05f8faa, E14.28)

A1 e A2 do parecer anterior (ab293a4e) estão resolvidos; o desvio do teto foi julgado com sonda e aceito.

## Achados
- A1 (recomendado) tests/catraca.py:775 · módulo que estoura o teto cai calado para só asserções diretas, sem aviso ao revisor. Se base e head estouram, remover asserção de ajudante passa (igual à catraca de 220ba3fa, não à de ab293a4e). Imprimir uma linha "módulo X estourou o teto" fecha o ponto cego.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A1 anterior: specs D3B5/D3C5/D3D2/D3H7 (e CA6/CA7) realinhadas | `forge-mutante --conferir --todas` | `de` aparece 1 vez | passou: 26 linhas, as mesmas da base 220ba3fa (diff vazio); nenhuma é do pedido |
| A2: argumentos constantes e corpo do ajudante como valor esperado | CA18, CA19, CA20 (spec -3) + teste de valor esperado | argumento/nomeado constante | morreram |
| A2: ajudante em cadeia de 3 níveis | test_ajudante_em_cadeia_conta_ate_o_fim; CA21 (FUNDO=1) | cadeia de 3 níveis | passou (vermelho: asserção); CA21 morreu |
| Teto de expansões por módulo | test_modulo_que_estoura_o_teto_conta_so_as_diretas... (tempo < 10 s, teto=10 e 100); CA14, CA15 | no teto / acima | passou (vermelho: asserção); CA14 e CA15 morreram |
| Mensagem "perdeu asserção (estava no ajudante X)" | mesmos testes; CA16, CA17 | com e sem ajudante | morreram |
| Mesma guarda e nada que barrava deixa de barrar | sonda 1 | monotonia contra a base | 0 diferenças |

## Provas
- Vermelho (`bin/forge-testes --vermelho ab293a4e --modulos test_catraca`): `vermelho: base=ab293a4e9da5 head=e05f8faab1b4 módulos=test_catraca (restrito por --modulos)`; revertidos à base: changelog, pareceres e tests/catraca.py. Prova (asserção): test_ajudante_em_cadeia_conta_ate_o_fim, test_chamada_ao_ajudante_tirada_ou_ajudante_sem_assercao_barra, test_modulo_que_estoura_o_teto_conta_so_as_diretas_e_barra_quem_perde_as_dos_ajudantes. Contagem: prova 3, passa na base 412; nenhum cai no HEAD.
- Mutantes (`bin/forge-mutante tests/mutantes/v0481-catraca-ajudante.json tests/mutantes/v0481-catraca-ajudante-3.json`, rev=e05f8faab1b4): CA1 a CA8, CA14 a CA21, 16 de 16 morreram, sem sobrevivente nem equivalente; condições mudadas no diff cobertas (teto 720/775, mensagem 786/787, ajudante 744, FUNDO 685).
- `forge-mutante --conferir --todas`: 26 linhas no head e 26 na base 220ba3fa, diff vazio (dívida antiga, nenhuma de v0481).
- CI do sha e05f8faa: suíte partes 1 a 5 (3.12 e 3.14) e teto de pulados verdes; `bateria (pareceres)` falha por faltar parecer aprovado no head (este); `catraca` falha: rodei o script da base (tests/catraca.py de 220ba3fa, com --base 220ba3fa) e a única violação é "mudança em tests/catraca.py: só passa com o rótulo afrouxa-regra do dono", sem teste afrouxado. Esperado, decisão do dono.

## Sonda do desvio (teto: só as diretas em vez de ilegível)
Arquivo de sonda fora da branch (/tmp/claude-0/sonda_teto.py), perfis de base 220ba3fa, ab293a4e e head:
1. 268 módulos tests/*.py, 6714 testes, com teto=1 (estoura sempre): 0 diferem do perfil da base 220ba3fa (asserções, pulos, vazio e valores esperados). A contagem "só diretas" é a da catraca antes da mudança.
2. Teste que só assere via ajudante, e o ajudante perde a asserção: base 220ba3fa `[]`; ab293a4e barra; head sem estouro barra com "(estava no ajudante h)".
3. Só o head estoura (base não): barra como "perdeu asserção (estava no ajudante h)": falha fechada, vale (preencher o módulo para estourar não esconde a perda).
4. Só a base estoura, head não: `[]` (head conta mais, nada a barrar).
5. Base e head estouram: `[]`. É o ponto cego do A1: passa calada a perda que ab293a4e barraria; igual à catraca de 220ba3fa, então nada que barra hoje deixa de barrar. Chegar aí exige um PR anterior que estourou o módulo, e esse PR já barra (caso 3) sempre que há teste dependente de ajudante.
6. Tempo: leque de 100 ajudantes chamando 100 (a sonda S9) em 1,2 s (teto 10 s do teste); leques de 30 e 50 abaixo do teto em 0,15 s e 0,63 s; o de 70 estoura sem travar.
Conclusão: o autor tem razão em "nada que barra hoje deixa de barrar"; "falha fechada" vale só quando um dos lados estoura, e o A1 recomenda tornar isso visível.

## Observações
- PR que faz o módulo passar do teto barra todo teste que dependia de ajudante, até o rótulo do dono: ruído do desenho, não defeito.
- Sem bugs abertos; sem arquivo em docs/qa/bugs/.
