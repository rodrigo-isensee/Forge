---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-conferencia-dois-pedidos
commit: a7872bf5094a4f84d48a802a1fcf810b0d1e1fb3
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-14
---
# QA: v047 · conferência com briefs de dois pedidos (E1.277, parecer E1.291)

Pedido de correção sem especificação de UX: as obrigações são a E1.277 do pedido (pedido único pelo brief de codigo; parecer mandado por brief selado do portão conta como anexo) e `R-PROVA` (não afrouxar a conferência).

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Dois pedidos, um só com brief de codigo: a conferência é dele | PedidoDaConferencia.test_dois_pedidos_um_so_com_codigo_e_o_da_conferencia | exatamente um com codigo | passou (prova: cai na base) |
| Dois pedidos com codigo, ou nenhum com codigo: falha fechada | test_dois_pedidos_com_codigo_falha_fechado, test_dois_pedidos_sem_codigo_falha_fechado | 2 codigos; 0 codigo | passou |
| Pedido único, sem brief, sem branch, brief ilegível: comportamento anterior | test_um_pedido_sem_codigo_segue_valendo, test_sem_brief_da_branch_nao_ha_pedido, test_sem_branch_nao_le_os_briefs, test_brief_ilegivel_e_pulado | vazio, ilegível | passou |
| Parecer mandado por brief selado do portão (do pedido ou de outro da branch) é anexo | test_mandado_pelo_portao_do_pedido_e_anexo, test_mandado_pelo_portao_de_outro_pedido_da_branch_e_anexo | pedido: e commit: do brief | passou (provam: caem na base) |
| Não afrouxa (R-PROVA): sem selo, selo no pedido errado, arquivo não declarado, pedido ou commit não mandado, papel errado, veredito inválido, sem frontmatter, veredito trocado, fora de código | 9 testes `segue_fora`/`nao_ancora`/`nao_e_anexo` | cada condição da guarda | passou (guardas, passam na base por desenho; cada uma morta por mutante) |

## Cenários e resultado real
- `python3 -m unittest tests.test_conferencia_dois_pedidos`: 19 testes, OK (83 s sob carga ~10).
- Vermelho antes do verde (`bin/forge-testes --vermelho origin/develop --modulos test_conferencia_dois_pedidos`), rc 0:
  ```
  vermelho: base=c5c3a449d7c3 head=a7872bf5094a módulos=test_conferencia_dois_pedidos (restrito por --modulos)
  revertidos à base: bin/forge-check, changelog.d/v047-conferencia-dois-pedidos.md
  contagem: não prova (passa na base)=16; prova (asserção)=3
  ```
  Os 3 que provam são os de comportamento novo; os 16 são guardas negativas que passam na base por desenho.
- Mutação (`bin/forge-mutante --processos 3` das duas specs juntas, rc 0): 16 de 16 morreram (M1-M16), nenhum sobrevivente, nenhum equivalente. M1 morreu por erro do teste declarado sob o mutante (que passa sem ele), aceito.
- Cobertura (`forge-mutante --cobertura --base c5c3a449`): toda condição mudada em bin/forge-check (1386, 1387, 2585, 2586, 2596, 2601, 2603, 2801) tem mutante declarado; só a linha apagada da base (1378, `len(ids) > 1`) sai "apagada", coberta por M3/M4.
- Análise de afrouxamento (R-PROVA): a nova isenção exige tipo, branch e veredito válidos no frontmatter, brief de papel do portão do tipo, pedido do brief, arquivo no escopo declarado do brief, `pedido:` e `commit:` iguais aos do brief e nenhum veredito trocado no mesmo commit. Pedido ambíguo (0 ou 2+ com codigo) segue falha fechada. Não vi caminho que aceite mais do que o brief selado mandou.
- Suíte inteira: fica para o check-run `bateria` do CI do PR (ainda não existe; sem PR neste pedido).
