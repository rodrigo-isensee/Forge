---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-comando-pronto
commit: 4b75cbd1359d2af46c95a40a546cb453f4cf4b1f
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: v0479-comando-pronto (E66.5)

Obrigação testada: COMANDO-PRONTO-NO-TEXTO (v0478 E66.1). O pedido não tem `CA-n`; a obrigação vira os cenários abaixo. Diff conferido contra a base `bead3e53`: três skills, `ritmo-e-corte.md`, `test_comando_pronto.py`, mapa/pesos de `bin/forge-testes`, uma asserção de `test_anotar.py`. Sem código de decisão em `bin/` além do mapa de testes.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Citação sem subcomando, opção inventada ou sem opção obrigatória é acusada | `test_ramos_de_falha` | subcomando ausente/inexistente, opção fora do --help, obrigatória faltando, alternativa `a ou b` | passou |
| Skills tocadas citam comando pronto | `test_skills_tocadas_citam_comando_pronto` | mínimo de 20 citações e 5 arquivos (suíte vazia); exceção sem uso reprova | passou |
| Só vale entre crases, com caminho e prefixo | `test_citacoes_acha_so_entre_crases` | `forge-checks`, texto solto | passou |
| Asserção de `test_anotar` segue o texto novo | `test_anotar.py` (18) | n/a | passou |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_comando_pronto.py` com TMPDIR: 3 testes, OK. `test_anotar.py`: 18, OK.
- Vermelho: `bin/forge-testes --vermelho bead3e53` estourou o prazo (rc 143, sem veredito). Recuo manual: cópia do head com as três skills restauradas da base: `Ran 3 tests ... FAILED (failures=1)`, o teste de skills cai.
- Mutação manual no diff: `forge-fechar <pedido> --ref <branch>` trocado por `forge-fechar <pedido>` em `ritmo-e-corte.md`: `FAILED (failures=1)`, acusa `ritmo-e-corte.md:31 forge-fechar: falta --ref`. Mutante morto.
- A exceção `SEM_OBRIGATORIAS` (escape registrar) tem motivo escrito e é checada como usada.
- Suíte inteira: do CI do PR, não rodada aqui.

## Revalidação no head 4b75cbd1 (E66.10)
Delta de `forge-check parecer delta` (34b6bf7b..e6417e77, sem a base): uma linha em `tests/test_qa_lote_l09.py`, `test_skill_manda_uma_mensagem_por_brief` agora cobra `forge-check brief mensagem --arquivo <brief> --pedido <p>` na skill (o comando completo, obrigação COMANDO-PRONTO-NO-TEXTO). Os demais testes e cenários acima não mudaram.
- `python3 -I -m unittest discover -s tests -p test_qa_lote_l09.py` com TMPDIR: 4 testes, OK.
- Vermelho: `forge-testes --vermelho 4b75cbd1~1 --modulos test_qa_lote_l09` saiu `nenhum teste prova a mudança` (base=c6984fb3f263, 4 testes `passa na base`): esperado, porque a skill já trazia o comando completo e o delta só endureceu a asserção. Recuo manual numa cópia em TMPDIR com a skill voltada a `forge-check brief mensagem` sem opções: `Ran 4 tests ... FAILED (failures=1)`, cai `test_skill_manda_uma_mensagem_por_brief`. Mutante morto.
- Suíte inteira: do CI do PR, não rodada aqui.
