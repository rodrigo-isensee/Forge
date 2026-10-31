---
tipo: qa
contrato: 1
pedido: impl-catraca-2
branch: melhoria/impl-catraca-2-c2
commit: 305d716cb71aac8e66e90c8db9dfb46d87db5664
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-31
---
# QA: impl-catraca-2 (branch c2)

## Achados

## Critério → teste → resultado
Item entregue: E2 (S16-TESTE-CHAVES). Diff lido: `234dbe0..305d716`; só `tests/test_catraca.py` (70 linhas contadas, mais fragmento e pareceres). M14 (`agents/tech-lead.md:19`): abaixo de 150, um comportamento, sem `hooks/` nem `PROTEGIDOS`. Cumpre.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E2: as 15 formas de violação de chave seguem pedindo o rótulo dentro do PR mesclado | `RotuloDePrMesclado.test_rotulo_de_pr_mesclado_nao_cobre_nenhuma_chave_do_config` (15 subtestes) | cada chave do config, inclusive base com entrada em `termos_proibidos_hash` | passou |
| E2: guarda de completude | `test_toda_forma_de_violacao_de_chave_tem_um_caso` | forma nova sem caso; piso 15; sem repetição | passou |
| E2: contagem de testes segue pedindo | `test_violacao_sem_arquivo_continua_pedindo` | docstring ajustada, asserção intacta | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_catraca tests.test_ambiente_git` no head: 278 testes, OK.
- Mutação "filtrar o None de arquivos" (`tests/catraca.py:1017`), cópia em `$TMPDIR`: 14 dos 15 subtestes caem, como o review. O 15º, `custo_permitido novo`, segue verde porque a violação de custo nunca chega ao caminho do PR mesclado; é guarda do outro controle, não defeito.
- Guarda de completude: com uma chamada `msg(` a mais em `regra_termos_proibidos` (cópia), `test_toda_forma_de_violacao_de_chave_tem_um_caso` cai.
- Vermelho: a mudança é só de teste (não há implementação a reverter); a prova de vermelho é a mutação acima.
- `forge-mutante`: não se aplica, o diff não toca `bin/`, `hooks/`, `.githooks/` nem `tests/catraca.py`.
- Bugs: nenhum.
