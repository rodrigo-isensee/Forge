---
tipo: qa
contrato: 1
pedido: vermelho-filtro
branch: melhoria/vermelho-filtro
commit: 1ffab3bd13fdb6b0edefcba546206b422cc1dfb4
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-30
---
# QA: VERMELHO-FILTRO

Base 9e6fa28978d742bbdd47975a34c7e1795919ea70, head 1ffab3bd13fdb6b0edefcba546206b422cc1dfb4. Correção em `bin/forge-testes`: o `--vermelho` sem `--modulos` deixa de ir à suíte completa por causa dos dados de teste do diff (spec de mutantes, fixtures, corpus); `tests/config.json` e o próprio script seguem ao plano (ALTERA_O_MAPA). Não há especificação de UX nem CA-n: as obrigações são as da correção (FT1 do fragmento) e a M14.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| FT1: spec e fixture no diff rodam só o plano do mapa, sem aviso | `Vermelho.test_vermelho_com_spec_e_fixture_no_diff_roda_so_o_plano_do_mapa` | dado de teste sem mapa não vira suíte completa | passou no HEAD, falha na base (prova por asserção) |
| FT1: caminho sem mapa continua na suíte completa e diz o motivo numa linha | `Vermelho.test_vermelho_com_caminho_sem_mapa_avisa_e_roda_a_suite_completa` | falha fechada preservada | passou no HEAD, falha na base (prova por asserção) |
| FT1: `tests/config.json` no diff segue na suíte completa | `Vermelho.test_vermelho_com_config_no_diff_segue_na_suite_completa` | o filtro não afrouxa o mapa | passou no HEAD, falha na base (prova por asserção) |
| FT1: com `--modulos` nada muda e não há aviso | `Vermelho.test_vermelho_com_modulos_ignora_o_mapa_e_nao_avisa` | restrição explícita | passou; guarda de regressão, passa na base de propósito |
| M14 (teto por PR) | contagem do diff | 150 linhas | 9 de código + 42 de teste = 51 (97 com a spec de mutantes): cumpre |

## Cenários e resultado real
- Vermelho (`R-QA`): `bin/forge-testes --vermelho 9e6fa28978d742bbdd47975a34c7e1795919ea70 --modulos test_testes_tocados` saiu 0. Abertura: `vermelho: base=9e6fa28978d7 head=1ffab3bd13fd módulos=test_testes_tocados (restrito por --modulos)`; revertidos à base: bin/forge-testes e os documentos; mantidos: spec e módulo de teste. Contagem: `prova (asserção)=3`, `não prova (passa na base)=82`. Os três que provam são os três primeiros da tabela. Nenhum teste cai no HEAD.
- Sem `--modulos` sobre este diff: o diff toca `bin/forge-testes` (ALTERA_O_MAPA), então o plano é a suíte completa por desenho, e a rodada excede o prazo da sessão de QA (duas passadas da suíte inteira). Não foi esperada até o fim; o comportamento sem `--modulos` está coberto pelos três testes da tabela, que montam o repositório e o diff sintéticos.
- Vermelho à mão, cópia temporária em `$TMPDIR`: HEAD com o `bin/forge-testes` da base e `python3 -m unittest tests.test_testes_tocados.Vermelho`: `Ran 27 tests`, `FAILED (failures=3)`, os mesmos três testes.
- HEAD: `python3 -m unittest tests.test_testes_tocados`: `Ran 85 tests ... OK`.
- Mutação (`bin/forge-mutante tests/mutantes/vermelho-filtro.json`), saída 0:
  - `M1 · morreu · bin/forge-testes:417`
  - `M2 · morreu · bin/forge-testes:417`
  - `M3 · morreu · bin/forge-testes:419`
  - `M4 · morreu · bin/forge-testes:418`
- Conferência da lista contra o diff: as linhas de guarda mudadas são 417 (condição do filtro, M1 e M2) e 418 (`if modo == "completo"`, M4); a 419 é o aviso (M3). `forge-mutante --cobertura --base 9e6fa28...` lista 417 e 418 como cobertas e nada sem mutante. Nenhuma linha de guarda sem mutante, nenhum sobrevivente.
- `scripts/validar-plugin.sh`: `Validation passed`.
- Suíte completa: fica ao pre-push deste envio e ao CI do PR (decisão M8); não rodada por inteiro nesta sessão pelo prazo acima.

## Recomendações (não bloqueiam)
- A de cosmética do review em `bin/forge-testes:419` continua valendo; sem efeito no comportamento.
- O teste de `tests/config.json` também falha na base por asserção (prova), embora descreva a falha fechada já existente; é prova válida do aviso novo, sem ação.

## Meta M14
A branch cumpre a M14 (agents/tech-lead.md:19): 51 linhas de código e teste, abaixo de 150.
