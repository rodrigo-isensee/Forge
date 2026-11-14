---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-folga-jarvis
commit: ebeb9161070e947fe03a1a6d8de630cee47be833
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 1
bugs_baixos: 0
data: 2026-11-14
---
# QA: v047 (E1.169, folga do texto do Jarvis P1 a P4 e FOCO-NAS-DECISOES)

Código testado: ebeb9161 (o remoto c4351c3e só soma pareceres de review e segurança). Diff sobre a base e60183d0: texto do Jarvis e das skills (trechos movidos, diretriz 25), `tests/apoio_jarvis.py` (conjunto calculado, presença), fixtures e testes. Escopo mudado fora do previsto, relatado pelo autor (`agents/agile-coach.md`, `falar-com-o-dono`, testes de texto): lido no diff, coerente com a citação da skill `kanban-metricas`.

## Achados

- A1 (bloqueante) tests/apoio_jarvis.py:82 · a checagem de presença das regras com ID passa sempre na árvore real: o índice docs/regras/README.md entra no conjunto (pela R-WIP) e cita todo ID. Reproduzido por sonda de mutação: tirar `R-MAIN` do Jarvis e das skills dá []. Corrigir fora de docs/regras/
- A2 (recomendado) tests/test_jarvis_nucleo.py:334 · o mutante test_id_fora_do_conjunto_reprova não pega A1: a árvore sintética não põe o índice no conjunto. Somar caso em que o Jarvis cita só a regra de índice e outra regra some do texto; precisa reprovar

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Decisão do dono 13/11: toda regra com ID segue presente no Jarvis ou nas skills citadas | `test_cada_regra_com_id_aparece_e_tem_texto` | ID ausente do texto | NÃO prova: passa com o ID removido (A1) |
| Diretriz 25: trecho movido não some, só muda de arquivo | `test_cada_diretriz_tem_entrada_e_a_de_fabrica_aparece`, `test_apagar_o_trecho_reprova_e_diz_onde_procurar` | trecho de 20+ caracteres; trecho apagado | passou |
| Skill citada traz ordem de leitura ("leia"/"antes de") | `test_cada_skill_citada_pelo_jarvis_traz_a_ordem_de_leitura`, `test_citar_sem_leia_nem_antes_de_reprova` | citação sem ordem | passou |
| Conjunto calculado (não lista fixa), com mínimo | `test_o_conjunto_e_calculado_e_traz_as_skills_novas` | mínimo 20 itens (hoje acima) | passou |
| Numeração das diretrizes sem buraco, trecho curto, pendente com cartão e teto | `test_buraco_na_numeracao_reprova`, `test_trecho_curto_reprova`, `test_pendente_*` | vazio, 20 caracteres, máximo de pendentes | passou |
| FOCO-NAS-DECISOES (diretriz 29): resumo no Jarvis, detalhe na skill | `test_o_jarvis_traz_o_resumo_e_manda_ler_a_skill_antes_de_responder`, `test_a_skill_traz_o_detalhe_inteiro` | detalhe só na skill | passou |
| Texto só desce (teto) | `test_metricas_texto`, `test_pesos_teto` | teto por arquivo | passou |

## Cenários e resultado real
- Execução local dos módulos do domínio (`test_jarvis_nucleo`, `test_metricas_texto`, `test_medidas_m14b`, `test_reval_delta`): `Ran 113 tests ... OK (skipped=1)`. O `skipped` é pré-existente, não foi posto por este pedido. A suíte inteira fica no CI do PR; não há PR aberto neste head, então não cito check-run `bateria`.
- Vermelho antes do verde: `forge-testes --vermelho e60183d0a41d28f44ac272197cac744b4891e61e` saiu rc 0: `vermelho: base=e60183d0a41d head=c4351c3efbbc`, com `revertidos à base` os 11 arquivos de texto e `tests/apoio_jarvis.py`, e `mantidos no HEAD` os 8 testes e fixtures. Veredito por teste: ao menos um prova e nenhum cai no HEAD. Aviso da ferramenta: "o mapa não sabe (tests/apoio_jarvis.py sem mapa); suíte completa".
- Sonda de mutação no teste de presença (sobre o código do autor, em `$TMPDIR`): (1) árvore real, `problemas_das_regras` devolve [] (esperado); (2) removi `R-MAIN` de todo texto exceto o índice: devolve [] (esperado: um problema), o mutante sobrevive; (3) árvore sintética com o Jarvis citando só `R-DOIS` (texto só no índice) e `R-UM` fora do Jarvis: devolve [] (esperado: "R-UM: não aparece"). Confirma o achado da segurança com sonda própria.
- Sem rede de proteção alternativa provada por mim: o review nota que o invariante de `tests/config.json` ainda cobre o bloco do Jarvis; não reavaliei isso, e a decisão de 13/11 pede o teste novo como prova.
- Nota para o portão (domínio da segurança, A2 dela): as diretrizes 26 a 28 entram como pendentes (`MAX_PENDENTES = 7`) além das 2, 11, 23 e 24 da decisão; não bloqueio por isso, vai ao dono pelo Jarvis (`R-DECISAO`).
- Bug médio: A1 (controle de guarda vazio). Cartão no quadro pelo tech-lead; correção mínima: procurar o ID só em `agents/jarvis.md` e `skills/*/SKILL.md`. Dono da correção: tech-lead (autor da E1.137).
