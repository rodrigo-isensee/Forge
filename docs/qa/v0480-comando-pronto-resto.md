---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-comando-pronto-resto
commit: dff23f769706eb32c04432a1a1c35fc3a9f2c5f1
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-23
---
# QA: comando pronto, resto (PR #826, etapa E139.8)

Escopo: texto das skills `qa-testing` (e `comandos.md`) e `esperar-estado` (e `envio-longo.md`), mapa do `bin/forge-testes`, os testes `test_comando_pronto` e `test_esperar_estado` e a spec de mutantes do item. Sem especificação de UX nem contrato de API: as obrigações vêm da entrada do changelog (`changelog.d/v0480-comando-pronto-resto.md`) e do pedido (E138.2, E138.7). O remoto avançou só com o parecer do review (3062ea01), sem código novo.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| O laço do PR trata `no checks reported` como pendente (PR recém-aberto) | `LacoDoPr.test_pr_recem_aberto_sem_checks_e_pendente` (laço curto e laço longo; checks com falha real continua saindo `checks:1`) | PR sem checks ainda; falha real não vira pendência | passou (vermelho na base) |
| O erro do `gh pr view` não vaza para a saída do laço | `LacoDoPr.test_gh_que_falha_sai_com_erro` (stderr vazio nos dois laços) | gh que falha | passou (vermelho na base) |
| O laço sem teto mudou para `envio-longo.md` e segue válido | `laco_longo()` lê os blocos dos dois arquivos, exige um só; `BlocosPassamPelosHooks` passa blocos do detalhe pelos hooks parecer e conformidade | exatamente um laço sem teto; blocos aceitos pelos hooks | passou |
| Comando pronto das duas skills confere com o `--help`: `--vermelho` com `--modulos`, spec do mutante pelo caminho em `tests/mutantes/` | `TestComandoPronto.test_skills_tocadas_citam_comando_pronto` e `test_ramos_de_falha` (cinco ramos novos de `formas_que_falham`) | citação sem `--modulos`; spec pelo nome do pedido; `--cobertura --base` sem spec | passou (vermelho na base) |
| Mapa do `forge-testes` roda os dois testes quando a skill muda | linhas novas do `MAPA` (esperar-estado leva os dois; qa-testing leva `test_comando_pronto`) | arquivo novo `comandos.md` e `envio-longo.md` cobertos pelo padrão | conferido por leitura do diff e pela rodada dos dois módulos |

## Cenários e resultado real
- `python3 -m unittest tests.test_esperar_estado tests.test_comando_pronto` (da raiz, sem `-I`) no head dff23f76: `Ran 19 tests ... OK`.
- Vermelho antes do verde, `bin/forge-testes --vermelho 0e59c446 --modulos test_esperar_estado,test_comando_pronto`: 3 testes provam (falham na base, passam no head): `test_skills_tocadas_citam_comando_pronto`, `test_gh_que_falha_sai_com_erro`, `test_pr_recem_aberto_sem_checks_e_pendente`; contagem `não prova (passa na base)=16; prova (asserção)=3`; saída 0. Os 16 restantes são testes já existentes, sem alteração de comportamento. A rodada sem `--modulos` caiu por infraestrutura do sandbox (`fatal library error, lookup self`) e não vale como evidência; a com `--modulos` é a do parecer.
- Mutação, `bin/forge-mutante tests/mutantes/v0480-comando-pronto-resto.json --base 0e59c446`: `base=0e59c446... mb=0e59c446... rev=dff23f769706`, oito mutantes do delta, todos `morreu`: `skills/esperar-estado/SKILL.md:22` (duas), `skills/esperar-estado/envio-longo.md:25` (duas), `skills/qa-testing/SKILL.md:75`, `skills/qa-testing/SKILL.md:92`, `skills/qa-testing/comandos.md:25`, `skills/esperar-estado/SKILL.md:48`. Nenhum sobrevivente.
- Cobertura da lista, `bin/forge-mutante --cobertura --base 0e59c446`: só a linha `base=...`, sem condição Python mudada sem mutante. As mudanças do diff em `bin/forge-testes` são linhas de dados do `MAPA`, sem condição de guarda; o diff não toca `hooks/`, `.githooks/` nem `tests/catraca.py`.
- Bordas lidas: stderr do gh nos dois laços, PR que fecha durante pendência (`MERGED` na 4ª leitura), checks com falha real, gh que falha, suíte vazia (`len(casos)` conta os blocos do detalhe, então pasta renomeada derruba).
- Suíte inteira: fica no CI do PR; este parecer não a roda.
