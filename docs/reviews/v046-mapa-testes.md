---
tipo: review
contrato: 1
pedido: v046
branch: melhoria/v046-mapa-testes
commit: e6565be2d303c831772be74974eb84df2352fb4f
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-12
---
# Review: v046 (E22.2, melhoria/v046-mapa-testes)

Diff lido: `origin/develop...e6565be2` (base a1318e88), 3 arquivos, 18 linhas de código e teste pelo `--numstat` (bin/forge-testes 6+1, tests/test_testes_tocados.py 12+1) mais o fragmento de changelog. Sem linha de guarda mudada: a ausência de spec de mutante está correta (R-QA).

## Achados
- A1 (recomendado) bin/forge-testes:119 · a falha proposital com a fechar-lote é aceitável, mas as duas branches não têm arquivo em comum e o forge-check sobreposicao não as ordena: registre no corpo do PR e no cartão da fechar-lote que a segunda a entrar acrescenta test_doutor_branch_atrasada aqui e em tests/test_testes_tocados.py:55
- A2 (recomendado) tests/test_testes_tocados.py:92 · a detecção só vê self.doutor( e DOUTOR; módulo que rode o script por outro nome (td.HOOK, auxiliar próprio) escapa sem aviso; vale um cartão para derivar a regra de quem importa test_doutor, em vez de lista à mão

## Sondas

## Parecer
**Aprovado.** Faz o que os cartões MAPA-FORGE-DOUTOR e TESTE-RITMO-SEM-MAPA pedem, nem mais nem menos.

- Regra do `bin/forge-doutor`: dos seis `tests/test_*doutor*.py`, cinco rodam o script (contagem de `self.doutor(`/`DOUTOR`: 35, 12, 18, 3, 3); `test_qa_doutor_034` roda `td.HOOK`, e o comentário em bin/forge-testes:118 diz isso. Os quatro acrescentados batem com a varredura.
- Regra do `tests/test_ritmo.py`: só o próprio módulo o cita por nome; `test_ambiente_git`, `test_forge`, `test_pre_push_trava` e `test_testes_tocados` casam `VARRE_OS_TESTES`; `test_apoio_sandbox` varre `tests/` por `rglob("*.py")` (tests/test_apoio_sandbox.py:292). Incluir a mais é o lado seguro, e o teste do critério C.2 (tests/test_testes_tocados.py:831) passa.
- Teste novo (tests/test_testes_tocados.py:88): afirma mínimo de itens na varredura (≥6) e nos que rodam (≥5), como pede o item 11 do checklist; a comparação é de subconjunto, então não falha por módulo extra na regra.

**Falha proposital com a melhoria/v046-fechar-lote (pergunta do brief).** Aceitável, e não há outra forma agora: `test_todo_modulo_do_mapa_existe` (tests/test_testes_tocados.py:172) recusa no MAPA um módulo que ainda não existe na develop, então `test_doutor_branch_atrasada` não pode entrar antes da branch que o cria. A falha é o próprio teste de deriva funcionando: sem ele, o módulo novo cairia fora da regra em silêncio, que é o defeito que este item corrige. Pela `R-FLUXO` a branch se atualiza com a develop na hora do merge e o CI do PR roda de novo, então quem entrar em segundo vê o vermelho antes de mesclar, e o conserto é uma linha em cada um dos dois lugares. O risco que fica é de processo (A1): a fila por arquivo não enxerga esse conflito, e acrescentar a linha muda o patch da segunda branch, cujo alcance de revalidação o `forge-check pr` aponta.

Verificadores: `python3 -m unittest tests.test_testes_tocados` no head, 150 testes, OK (skipped=1), a mesma contagem da entrega (R-TETO: só esse módulo). `docs/engineering/praticas.md` não existe no Forge; sem regra "leitura" a aplicar além do checklist da skill. Achados recorrentes (AR-1 a AR-12) conferidos: nenhum se aplica a este diff (sem guarda, sem subprocesso novo, sem spec de mutante).
