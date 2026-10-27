---
tipo: review
contrato: 1
pedido: conferente-c2c3
branch: melhoria/conferente-c2c3
commit: a2cb36d03c266fcfd3bbb643bcb900ecb64ae25a
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-27
---
# Code review: conferente-c2c3 (C2, C3 e C1 do CONFERENTE-VELOCIDADE)

Pedido CONFERENTE-VELOCIDADE-REV, etapa E1.1. Lote inteiro lido: `ce1a341..a2cb36d` (3ff5c8d, b60b760, e7f776f, a2cb36d).

## O que foi lido
- `bin/forge-check`: `uso_do_pr` e o desvio em `executar` (rc=2), `linha_do_comando_pr` e a chamada em `avaliar_brief`, `blocos_identicos` e a chamada em `conferir_brief` com `--anterior`, o sufixo `rótulo do verificador: ok` em `conferir_pq`, `cmd_entrega` com `--desde` em `pr`/`merge-integracao`/`pedido-de-merge-ao-dono`, docstring e ajuda do argparse.
- `agents/conferente.md`: as frases novas do item 5, da rodada de confirmação, da linha `PQ-n ... rótulo do verificador: ok` e da volta por delta nas etapas de branch inteira.
- Testes: `tests/test_etapa_do_brief.py`, `tests/test_volta_por_delta.py`, `tests/test_conferencia_base_dono.py`, `tests/test_forge.py`; mutantes em `tests/mutantes/`.

## Ferramentas (citadas, não refeitas)
- Testes do item: `python3 -m unittest tests.test_etapa_do_brief tests.test_volta_por_delta tests.test_conferencia_base_dono` deu `Ran 120 tests ... OK`. A suíte completa fica no pre-push e no CI (M8).
- `docs/engineering/praticas.md` não existe no Forge: as regras "ferramenta" ficam sem comando configurado e entram como pendência, sem review manual.
- Teto M14: 191 linhas de código e teste (`bin/forge-check` 50, `tests/*.py` 141), abaixo de 400. Nenhum arquivo de `hooks/` nem de `PROTEGIDOS`.
- `docs/engineering/achados-recorrentes.md` (PA-7): sem item registrado, nada a conferir.

## C1 (`--desde` em pr e merge): correto
- O delta é `desde..head` cruzado com a branch sobre o Base-sha, e `desde_valido` exige a `conferida` mais recente, ancestral do head. Commit que entrou depois da conferida aparece (teste `test_commit_depois_da_conferida_aparece_no_delta_do_pr`), e o que o merge da base trouxe sai por conteúdo nas etapas de merge (teste `test_merge_da_base_dentro_do_intervalo_do_pr_nao_traz_o_que_veio_da_base`). O `--desde` sem conferida reprova igual às outras etapas. As checagens de ato não passam por `cmd_entrega`. Fica dentro da decisão do dono (C1, "A").
- A frase nova de `agents/conferente.md` (volta por delta) bate com o comando: o `Desde:` vem da mensagem, é conferido contra o Histórico e, sem conferida, vale a branch inteira.

## C3: correto
- `blocos_identicos` só marca bloco igual byte a byte ao anterior, e o bloco alterado não sai (teste). O sufixo `rótulo do verificador: ok` sai só para `conferente`/`autor`, e o agente o lê como rótulo válido, não como PQ cumprido (DECISÃO TÉCNICA do Histórico). A contradição contra decisão do dono segue por leitura.

## C2: dois defeitos provados fora do Forge
O `forge-check pr` casa o parecer pelo campo `pedido:` do frontmatter (`cmd_pr`), e o modelo de projeto manda `pedido: <id-do-pedido>` (`templates/projeto/docs/reviews/_modelo.md:4`). Num projeto, o argumento certo do `forge-check pr` é o **id do pedido**, e a branch é `feature/<slug>` (R-FLUXO). O agente `forge:conferente` vale em todos os projetos.

Reprodução (repositório de teste com `docs/pedidos/CAD-CLIENTE.md` e a branch `feature/cad-cliente`, em `$TMPDIR/tech-lead-conferente-c2c3/proj`):
- `forge-check pr CAD-CLIENTE` no a2cb36d: `uso: use o slug da branch (<slug>), não o id do pedido (CAD-CLIENTE)`, rc=2.
- O mesmo comando no ce1a341: `sem parecer para o pedido CAD-CLIENTE (R-REVIEW)` e o mesmo para R-QA, rc=1 (o caminho normal).
- `linha_do_comando_pr` com `Branch: feature/cad-cliente` imprime `etapa: comando forge-check pr feature/cad-cliente --ref origin/feature/cad-cliente --base develop`. Esse argumento nunca casa com um `pedido:`, e o agente manda copiar a linha sem montar o argumento.

O ajuste do fixture em `tests/test_forge.py:4359`, que tira `docs/pedidos/p1.md` da semente, é sintoma do A1: o cenário de projeto (pedido `p1` com o seu arquivo) passou a sair rc=2, e o teste mudou para não ver isso.

No próprio Forge, o rc=2 prometido não acontece. Os pedidos ficam em `~/.forge-contrib/docs/pedidos/` e `uso_do_pr` só procura em `raiz_principal(raiz)` e em `raiz`. Rodei `forge-check pr CONFERENTE-VELOCIDADE-REV --ref origin/melhoria/conferente-c2c3 --base origin/develop`, com e sem `--raiz-pedidos ~/.forge-contrib`, e as duas vezes saiu rc=1, `sem parecer`. Não aprova nada errado: só a promessa do texto não se cumpre.

## Achados
- A1 (bloqueante) bin/forge-check:617 · defeito provado: no projeto (parecer com pedido: <id-do-pedido>, branch feature/) uso_do_pr recusa com rc=2 o id certo; CAD-CLIENTE: ce1a341 rc=1, a2cb36d rc=2; limitar à convenção melhoria/<slug> e devolver o fixture p1 de tests/test_forge.py:4359
- A2 (bloqueante) bin/forge-check:4280 · defeito provado: linha_do_comando_pr com Branch feature/cad-cliente imprime forge-check pr feature/cad-cliente, que nunca casa com o pedido: de um parecer; fora de melhoria/ não imprimir (ou usar o Pedido: do cabeçalho) e ajustar a frase de agents/conferente.md:53
- A3 (recomendado) bin/forge-check:622 · no Forge os pedidos ficam em ~/.forge-contrib (RAIZES_DE_BRIEF) e uso_do_pr não olha ali: forge-check pr CONFERENTE-VELOCIDADE-REV sai rc=1, não o rc=2 prometido em agents/conferente.md:53
- A4 (recomendado) bin/forge-check:4169 · blocos_identicos roda em todo --anterior, também fora de brief com Volta-de:, e diz "(exigido)" onde a cópia não é exigida; restringir ao brief de volta ou tirar o "(exigido)" nesse caso

## Parecer
**Reprovado** por A1 e A2. C1 e C3 estão corretos e cobertos por teste. Os dois defeitos são do C2 e aparecem só fora da convenção `melhoria/<slug>` do Forge, mas o conferente roda em todos os projetos. A correção é pequena e fica no C2 (`uso_do_pr`, `linha_do_comando_pr`, o fixture `p1` e a frase do item 5). A revalidação lê só o delta (`forge-check delta --parecer docs/reviews/conferente-c2c3.md`).
