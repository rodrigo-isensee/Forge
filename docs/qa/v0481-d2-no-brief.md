---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-d2-no-brief
commit: 6c2bbf42d868a13c8a6344c440789aa562ed5022
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-26
---
# QA: v0481 (E14.84, #903, D2-NO-BRIEF, volta por delta de 7cacc94c a 6c2bbf42)

Clone `/root/.forge-contrib/wt/v0481-d2-no-brief-qa`, head `6c2bbf42d868`. Li só `git diff 7cacc94c..6c2bbf42` no domínio do QA (código, testes, specs de mutante, textos de regra e skill). O A1 da 1ª rodada (sem worktree, o D2 não reprovava) está corrigido.

- ci: 6c2bbf42d868a13c8a6344c440789aa562ed5022 verde

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| (2) sem worktree com o head do Forge (manifesto sem `.forge/versao`, lido pelo git): reprova pedindo `--worktree` (A1) | `ProvaDoPronto.test_sem_worktree_com_o_head_no_forge_reprova_pedindo_worktree` (M14, M15) e `Entrega.test_sem_worktree_com_o_head_no_forge_nao_cumpre` (M16, M17) | pasta None; `--so-leitura` não reprova; projeto com `.forge/versao` só informa; entrega não gravada | passou |
| (2) `--so-leitura`, pasta None fora do Forge e pasta sem manifesto só informam | `ProvaDoPronto.test_so_leitura_sem_worktree_fora_do_forge_e_fora_do_forge_nao_rodam` (M9) | quem confere não roda código da branch | passou |
| (1) a PQ do D2 manda `--raiz <sua cópia>` e o forge-check de um clone da develop | `Gerar.test_codigo_do_forge_manda_rodar_o_d2_e_fora_do_forge_nao` (M8) | dentro x fora do Forge | passou |
| (2), (3), (4) da 1ª rodada | sem mudança no delta | n/a | passou antes e hoje (módulos acima rodam verdes) |

## Cenários e resultado real
- **CI** (PARECER-LE-O-CI): check-runs do sha exato `6c2bbf42`, lidos por `gh api .../check-runs`: suíte 3.12 e 3.14 (partes 1 a 5), bateria (passos), bateria (verificações longas), instalação 3.14 e árvore já provada, todos `success`. Vermelhos: só `bateria (pareceres)`, `bateria` (agregada) e `catraca`, que esperam os pareceres e o rótulo do dono (R-CONFORMIDADE em `bin/forge-check`, já dito na rodada anterior); não contam.
- **Módulos tocados, no head**: `python3 -m unittest tests.test_forge_pronto tests.test_pre_envio_brief` deu `Ran 59 tests ... OK`; os dois testes de `test_selo_e_entrega.Entrega` do D2 deram `Ran 2 tests ... OK`.
- **Vermelho** (`bin/forge-testes --vermelho 7cacc94c8fe74c3fba5cd9368d5c388d1007b910 --modulos test_forge_pronto,test_pre_envio_brief`): `base=7cacc94c8fe7 head=6c2bbf42d868`; revertidos à base `bin/forge-check` e os textos; `Gerar.test_codigo_do_forge_manda_rodar_o_d2...` prova (asserção); os 4 testes de `ProvaDoPronto` ficam `B=erro · sem veredito` (TypeError: `forge_no_head` não existe na base, que a ferramenta não conta como prova). Contagem: `não prova (passa na base)=53; prova (asserção)=1; sem veredito=5`. A prova desses testes é a dos mutantes M14 a M17: o teste cai quando a guarda é trocada.
- **Mutantes** (`bin/forge-mutante` nas 3 specs `v0481-d2-no-brief`, `-2` e `-3`, `--processos 4`, rc 0): M1 a M17 todos `morreu`, nenhum sobrevivente (novos: M14 forge-check:10453, M15 :10453, M16 :10627, M17 :10626). `--cobertura --base 7cacc94c`: as condições mudadas (:10453, :10626, :10627) `coberta`, nenhuma sem mutante.
- **Mudanças extras, uma a uma:**
  - `--worktree` em `agents/jarvis.md:30` e na skill `briefs-e-conferencia` com o arquivo novo `conferencia-da-entrega.md`: **fica**; é texto e bate com o comportamento testado (sem a cópia, a entrega pede `--worktree`).
  - PQ do D2 com o forge-check do clone da develop (`PQ_DO_D2`): **fica**; coberta por M8 e pelo teste de `Gerar` (`nunca o da branch`).
  - Exceção "base velha" em `docs/regras/R-FLUXO.md` com a medida em `ritmo-e-corte.md`: **fica**. É regra com ID, mas aperta (exige trazer a base antes quando ela está velha) e não afrouxa trecho protegido; os cortes de palavras ("padrão", "a integração") não mudam o sentido. O destaque de aperto no título do PR é do portão que mescla; a medida e a revisão (mais de 1 volta por item) estão registradas.
  - Cortes de palavras nos tetos de texto: **ficam**; nenhum trecho de `invariantes` sumiu (o CI estrutural passa).
- **Fora do alcance:** E2E e acessibilidade não se aplicam (ferramenta de linha de comando, sem UI).
