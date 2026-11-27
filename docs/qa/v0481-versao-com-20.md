---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-versao-com-20
commit: 6e77f72a3a6a38e3dbdcc12b43e0525f5cb26113
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-26
---
# QA: v0481 versão com 20 itens (#928, E36.4; 1ª rodada completa no 6e77f72a)

Diff lido contra a base 346a7860: `bin/forge-fechar` (sai `corte_diario` e a autorização do corpo da marca; o V4 só corta com o contador no teto), `bin/forge_autorizacao.py` (sai o ato `corte-diario` e o vocabulário dele), textos do time, `tests/config.json` (invariantes), ADR 0018 (retirada), testes e specs de mutantes.

- ci: 6e77f72a3a6a38e3dbdcc12b43e0525f5cb26113 verde (`gh pr checks 928`: suíte 3.12 e 3.14 partes 1 a 5, passos, verificações longas, catraca, instalação e teto de pulados verdes; só `bateria` e `bateria (pareceres)` vermelhos, que esperam os pareceres)

## Achados
- A1 (bloqueante) tests/test_autorizacao_gravar.py:527 · mutante M6 de v0481-autorizacoes-fixas.json (VOCABULARIO_FIXO if True) SOBREVIVE no head: o teste de vocabulário usava "todo dia", palavra que o diff tirou de VOCABULARIO_FIXO; "dia, todo" fica fora com ou sem a guarda.
- A2 (bloqueante) agents/tech-lead.md:44 · o tech-lead ainda manda marcar versão "até 2 por dia", contra a ordem do dono (20 itens, sem versão por dia); o mesmo texto em skills/falar-com-o-dono/nao-trava.md:19 e templates/projeto/CLAUDE.md:15 (R-FLUXO).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Abaixo do teto o --corte nada corta, nem às 06:00 | `test_fechar_corte.Corte.test_abaixo_do_teto_nao_ha_corte_diario`; mutante M1 (v0481-versao-com-20.json) | 1 item, 06:00, sem leitura de autorização | passou (vermelho na base; M1 morreu) |
| Ato `corte-diario` não grava nem lê | `test_autorizacao_gravar.AtosFixos.test_corte_diario_saiu_e_nao_grava`; `test_autorizacao.AtosFixos.test_alvo_fixo_e_validade_fixa_so_nos_atos_fixos_e_eles_so_com_eles` | ato e palavras `corte diario` fora do vocabulário | passou (vermelho na base) |
| No teto a marca continua saindo, sem linha de autorização no corpo | `test_fechar_corte.Corte.test_no_teto_grava_a_marca_e_abre_o_pr_em_rascunho` e demais da classe | contador 20 de 20 | passou |
| Textos do time e invariantes dizem "20 itens" | `tests/config.json` (invariantes novos); jarvis.md, fluxo-do-pedido, ritmo-e-corte | texto removido ou antigo | passou nos três arquivos; falhou em tech-lead.md, nao-trava.md e no modelo de projeto (A2) |
| Specs antigas seguem válidas após a edição | `forge-mutante` das três specs editadas | mutante de teste adaptado | falhou: M6 sobreviveu (A1) |

## Cenários e resultado real
Vermelho antes do verde, sob flock da trava:
```
vermelho: base=346a7860515c head=6e77f72a3a6a módulos=test_fechar_corte,test_autorizacao,test_autorizacao_gravar (restrito por --modulos)
tests.test_autorizacao.AtosFixos.test_alvo_fixo_e_validade_fixa_so_nos_atos_fixos_e_eles_so_com_eles · H=ok · B=falha · prova (asserção)
tests.test_autorizacao_gravar.AtosFixos.test_corte_diario_saiu_e_nao_grava · H=ok · B=falha · prova (asserção)
tests.test_fechar_corte.Corte.test_abaixo_do_teto_nao_ha_corte_diario · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=98; prova (asserção)=3   (rc=0, nenhum teste cai no head)
```
Mutantes:
```
forge-mutante tests/mutantes/v0481-versao-com-20.json: M1 · morreu · bin/forge-fechar:1636 (rc=0)
v0480-d4-corte-contador-4: M25 a M32 morreram
v0481-autorizacoes-fixas (e -2): M1 a M5 e M7 a M9 morreram; M6 · sobreviveu · bin/forge_autorizacao.py:378
v0481-rotulo-pelo-time-2: M9 e M10 morreram
```
`forge-mutante --cobertura --base 346a7860`: `não coberto: bin/forge-fechar` (shell, esperado; a linha de guarda 1636 tem o M1 declarado) e cinco "spec editada" (quatro rodadas acima; a `-3` foi apagada).
Não rerrodei a suíte: CI do head lido (G3).
