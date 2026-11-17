---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-texto-dir32-33
commit: ac34647c888de410dc1a97bd65f878cd0ed6725c
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-17
---
# QA: v047 (diretrizes 32 e 33 e o teto do H6 nos textos, E2.714)

Item só de texto (acréscimo) mais invariantes em `tests/config.json` e a tabela de diretrizes; sem código de produção. Base `4cc2153e`, head `ac34647c`. Testes rodados local, com `TMPDIR` próprio, `unittest` sem `-I`; a suíte inteira fica para o CI do PR.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E2.714: diretriz 32 no Jarvis, tech-lead, skill e modelo | `test_jarvis_nucleo` (diretrizes 32 e 33 de fábrica aparecem), `test_forge -k RegrasInviolaveis` (trechos obrigatórios) | trecho apagado ou alterado derruba teste | passou |
| E2.714: diretriz 33 | idem | idem | passou |
| E2.714: teto do H6 (20 agentes, 12 branches) | `test_forge` invariantes de `agents/jarvis.md`, `agents/tech-lead.md`, `ritmo-e-corte.md`, modelo | idem | passou |
| E2.714: Jarvis dentro do teto de caracteres | `test_metricas_texto`, `test_jarvis_n_jar_a` | tamanho do núcleo | passou |
| E2.714: números do arquivo do dono com entrada | `test_cada_numero_do_arquivo_do_dono_tem_entrada` | número 30 a 33 sem entrada | passou |

## Cenários e resultado real
- `test_metricas_texto`: Ran 2, OK.
- `test_jarvis_nucleo` (padrão, usa o exemplo neutro): Ran 43, OK.
- `test_jarvis_nucleo` com `FORGE_DIRETRIZES_DONO` apontando para um arquivo sintético com os números 1 a 33: Ran 43, OK. Limite: o arquivo real do dono não existe nesta máquina; o sintético prova que 1 a 33 têm entrada, não o conteúdo do arquivo do dono.
- `test_jarvis_n_jar_a`: Ran 2, OK.
- `test_forge -k RegrasInviolaveis`: Ran 3, OK.
- Sonda 1: apaguei em `agents/tech-lead.md` "No máximo 12 branches abertas e 20 agentes" (trocado por "No máximo X"): `test_forge` `test_trechos_obrigatorios` caiu (`Regex didn't match: 'No máximo 12 branches abertas e 20 agentes'`), FAILED (failures=1).
- Sonda 2: apaguei em `agents/jarvis.md` "cartões nos mesmos arquivos vão ao mesmo agente" (diretriz 33): `test_jarvis_nucleo` caiu em `test_cada_diretriz_tem_entrada_e_a_de_fabrica_aparece` e `test_cada_numero_do_arquivo_do_dono_tem_entrada` (failures=2). Árvore restaurada (`git status` limpo).
- Vermelho antes do verde: não se aplica no sentido de código; as duas sondas fazem o papel (o texto sem o trecho derruba o teste).

## Observações (não bloqueiam)
- O diff também troca as diretrizes 26 e 27 de `pendente` para `fabrica` em `tests/fixtures/diretrizes-do-dono.json`, além do pedido literal (32, 33 e a tabela 30 a 33). Os testes passam, o que mostra que os trechos já existem nos textos; só registro para o review.
- Mutação e `forge-mutante`: não se aplicam (sem código em `bin/`, `hooks/`, `.githooks/`, `catraca`).
