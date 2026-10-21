---
tipo: review
contrato: 1
pedido: forge-testes-mapa
branch: melhoria/forge-testes-mapa
commit: c61752f3e4bc41175476e0a0208408d469e73702
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-21
---
# Parecer de code review: mapa FORGE_CHECK do `bin/forge-testes`

Escopo: `26f7189..c61752f` (3 arquivos: `bin/forge-testes`, `tests/test_testes_tocados.py`, fragmento do changelog). Sem gatilho de segurança.

## Leitura
- O mapa passou de 6 para 13 módulos. O critério do autor (módulo que importa ou executa o script, mais quem importa de um deles) é coerente: `test_fechar` fica de fora porque usa um `forge-check` falso (variável de ambiente), e `test_doutor` porque só grava um falso na semente. `test_guarda_git` entra por importar de `test_forge`.
- `MapaDoForgeCheck` cobre falta e sobra, com piso de 8 módulos (R-TESTE de ausência com mínimo). A exceção `test_catraca` por inclusão manual está comentada com o motivo.
- `NaoEPortao` ignora `__pycache__`, mudança mínima, com motivo no comentário; o piso de 5 arquivos continua.
- Rodei `tests.test_testes_tocados`: 29 testes, OK.

## Recomendações (não bloqueiam)
- A regex `CITA` não pega referência ao script montada de outro jeito; o teste de sobra/falta é heurístico, aceitável para o fim.

## Achados
