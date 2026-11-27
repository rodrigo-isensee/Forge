---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-versao-com-20
commit: b19c7f53a1a564059901a406a0e7ddf74ae63b24
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-27
---
# QA: v0481 versão com 20 itens (#928, E36.8; volta 1 por delta, 6e77f72a..b19c7f53)

Delta lido por `forge-check parecer delta`: tech-lead.md, nao-trava.md, templates/projeto/CLAUDE.md, tests/config.json, ADR 0018, `cmd_corte` renomeada `cmd_ler_ato`, specs de mutantes e três testes. Nenhum `cmd_corte` resta em bin/ ou tests/.

- ci: b19c7f53a1a564059901a406a0e7ddf74ae63b24 verde

## Achados
- A3 (recomendado) tests/config.json:849 · a chave de `invariantes_motivo_trecho` de templates/projeto/CLAUDE.md ainda traz o texto antigo ("até 2 por dia"); o invariante novo ("soma 20 itens") ficou sem motivo próprio. Atualizar a chave no próximo toque; vira cartão.

## Revalidação dos achados da 1ª rodada
- A1: resolvido. O teste usa "pode mesclar a main 0.47.3, o time decide" e afirma o conjunto fora do vocabulário nos dois vocabulários; M6 morre.
- A2: resolvido. Os três textos dizem "20 itens, sem versão por dia" e o invariante do modelo de projeto foi trocado; a busca por "2 por dia" não acha mais nada nos textos do time.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Abaixo do teto o --corte nada corta, nem às 06:00 | `test_fechar_corte.Corte.test_abaixo_do_teto_nao_ha_corte_diario`; mutante M1 (v0481-versao-com-20.json) | 1 item, 06:00, sem leitura de autorização | passou (vermelho na base; M1 morreu) |
| Ato `corte-diario` não grava nem lê | `test_autorizacao_gravar.AtosFixos.test_corte_diario_saiu_e_nao_grava`; `test_autorizacao.AtosFixos.test_alvo_fixo_e_validade_fixa_so_nos_atos_fixos_e_eles_so_com_eles` | ato e palavras `corte diario` fora do vocabulário | passou (vermelho na base) |
| No teto a marca continua saindo, sem linha de autorização no corpo | `test_fechar_corte.Corte.test_no_teto_grava_a_marca_e_abre_o_pr_em_rascunho` e demais da classe | contador 20 de 20 | passou |
| Textos do time e invariantes dizem "20 itens" | `tests/config.json` (invariantes novos); jarvis.md, fluxo-do-pedido, ritmo-e-corte | texto removido ou antigo | passou em todos, tech-lead.md, nao-trava.md e modelo de projeto inclusos |
| Specs antigas seguem válidas após a edição | `forge-mutante` das três specs editadas | mutante de teste adaptado | passou na volta: M6 morreu |

## Cenários e resultado real
Mutantes do delta, sob flock da trava:
```
base=6e77f72a3a6a38e3dbdcc12b43e0525f5cb26113 rev=b19c7f53a1a564059901a406a0e7ddf74ae63b24
forge-mutante: pedido=v0481-autorizacoes-fixas rev=b19c7f53a1a5
M1 a M9 · morreu (M6 · bin/forge_autorizacao.py:378; M7 · erro do teste sob o mutante, morreu)
```
Vermelho antes do verde: o teste alterado só troca a frase de M6, que sobrevivia no head anterior; a prova é o M6 morto agora. Não rerrodei a suíte: CI do head lido (G3).
