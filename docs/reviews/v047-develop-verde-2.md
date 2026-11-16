---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-develop-verde-2
commit: 4143d00d3ddeaf462345d19d3327f89e46fbee14
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-15
---
# Code review: develop verde de novo (contagem do mapa do forge-check, E2.81)

Escopo: pedido v047, etapa E2.86 (`R-REVIEW`), classe T, sobre o head `4143d00d` (Base-sha `bf475209`, igual à `origin/develop` na hora do review), instância que não fez a entrega. Li o diff inteiro de `bf475209..4143d00d`: um commit, 2 arquivos (`tests/test_testes_tocados.py` +1 -1, `changelog.d/v047-develop-verde-2.md` +2).

## Achados

## Sondas

## Parecer
**Aprovado.** Faz o que a E2.81 pede, nem mais nem menos:
- `tests/test_testes_tocados.py:67`: a contagem dos módulos que `bin/forge-testes` roda para `bin/forge-check` passa de 83 a 84. Na `bf475209` os PRs #559 (`test_conferida_por_branch`) e #564 (`test_conferencia_dois_pedidos`) entraram cada um com a sua conta (83), e juntos o mapa tem 84; a asserção segue exata (`assertEqual`), sem afrouxar para `>=`. O comentário registra as duas entradas, no padrão das anteriores.
- `changelog.d/v047-develop-verde-2.md`: fragmento `### Corrigido`, sem editar o `CHANGELOG.md`.
- Sem guarda nova nem mudada (só um literal de teste): não há mutante a declarar. Nenhum invariante de `tests/config.json` tocado. Commit em Conventional Commits, em português.
- Tamanho (M14): 2 linhas contadas, um comportamento só.

Verificação (regra 5 de `docs/economia-de-tokens.md`; sem PR nem CI ainda, rodo o teste alterado):
- `python3 -I tests/test_testes_tocados.py Mapa.test_forge_check_roda_os_modulos_dele` no head, ambiente limpo (`env -i`): `Ran 1 test` `OK`; como a asserção é igualdade, isso prova que o mapa tem 84 módulos no head.
- O módulo inteiro no sandbox: `Ran 151 tests`, 3 falhas fora do diff (`ExecucaoAfetados` x2, rc 1 do lançador paralelo; `MedidaDaVagaPesada`, `exigir("proc")` fora de `PODEM_PULAR`), todas dependentes do sandbox (processos e `/proc`), em métodos que não leem a linha 67. A suíte completa fica com o CI do PR, obrigatório para o merge.

Achados recorrentes (PA-7) conferidos: nenhum se aplica a um literal de teste (sem guarda, sem subprocesso novo, sem ambiente herdado novo).
