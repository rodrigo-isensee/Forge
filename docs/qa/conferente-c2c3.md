---
tipo: qa
contrato: 1
pedido: conferente-c2c3
branch: melhoria/conferente-c2c3
commit: cbb522765094be22586e61487bd1f54970829453
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-27
---
# QA: conferente-c2c3 (CONFERENTE-VELOCIDADE-REV, E3.1, revalidação 2 por delta a2cb36d..cbb5227)

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| C2 comando do pr só para `melhoria/` | TabelaDePareceres.test_brief_da_etapa_imprime_o_comando_com_o_slug (CLI `forge-check brief`) | branch fora de `melhoria/`, base inválida | passou; mutantes C5, M1, M2 mortos |
| C2 `uso_do_pr` só em `melhoria/<slug>`, pedido em qualquer raiz | RecusaDoIdDoPedido (CLI, rc=2) | fora da convenção, branch só em origin/, id com barra, pedido só na raiz principal ou em RAIZES_DE_BRIEF, parecer com o `pedido:` | passou; C7, C8, M4 a M7 mortos |
| C3 bloco idêntico só no brief de volta | BriefDeVolta.test_brief_de_volta_marca_os_blocos_identicos_ao_anterior; BriefAnterior.test_brief_sem_volta_de_nao_marca_bloco_identico | bloco ausente no anterior, brief sem `Volta-de:` | passou; C6, C3, M3, M8 mortos |
| C3 rótulo do verificador | VerificadorOk | cmd do conferente e do autor | passou; C4 morto |
| C1 `--desde` com arquivo desfeito depois da conferida | Entrega.test_arquivo_acrescentado_antes_da_conferida_e_apagado_depois_fica_no_escopo | 4 etapas (codigo, pr, merge-integracao, pedido-de-merge-ao-dono) | passou; C6 e C7 do c1 mortos |

## Cenários e resultado real
- `python3 -m unittest` em tests.test_etapa_do_brief (52), tests.test_volta_por_delta (58), tests.test_conferencia_base_dono (21), tests.test_forge (432): todos `OK`.
- `bin/forge-mutante tests/mutantes/conferente-c1.json`: C1 a C8 morreram, rc=0.
- `bin/forge-mutante tests/mutantes/conferente-c2c3.json`: C1 a C8 morreram, rc=0.
- Lista contra o diff: cada guarda nova tem mutante (desfeitos: c1 C6/C7; convenção `melhoria/`: c1 C8; origin e regex do id: c2c3 C7/C8; fiação do pr e da volta: C5/C6; bloco ausente: C3).
- Mutação à mão (cópia em `$TMPDIR/qa-engineer-conferente-c2c3/m`) das guardas sem mutante declarado: `startswith("melhoria/")` do comando, regex da base, `nome in antigos`, `RAIZES_DE_BRIEF`, `raiz_principal`, parecer com `pedido:`, `origin/` da ref e `Volta-de:`: todas morreram (M8 só cai em BriefAnterior, que é onde está o teste). A1 a A4 da rodada anterior estão cobertos.
- Vermelho antes do verde: o vermelho de cada comportamento novo é a mutação acima (teste cai sem a guarda); `forge-testes --vermelho` não rodado (sem suíte completa neste brief).
- Bugs abertos: nenhum.
