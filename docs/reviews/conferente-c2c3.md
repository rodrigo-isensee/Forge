---
tipo: review
contrato: 1
pedido: conferente-c2c3
branch: melhoria/conferente-c2c3
commit: 5818e849140c76b535795feec6238af523d3f68b
parecer: aprovado
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

## Revalidação 2 (delta a2cb36d..cbb5227)
Lido só o que `forge-check delta --parecer docs/reviews/conferente-c2c3.md` lista: `agents/conferente.md`:53, `bin/forge-check`:492-514, 625-642, 956-957, 4189-4190, 4198, 4299-4300, 5227; `tests/test_etapa_do_brief.py`, `tests/test_volta_por_delta.py`, `tests/test_forge.py`:4359 e os mutantes `tests/mutantes/conferente-c1.json` e `conferente-c2c3.json`. O resto do lote (C1 e C3 fora dessas linhas, ajuda do argparse, `tests/test_conferencia_base_dono.py`) fica como "já lido" na primeira passada.

- **A1 resolvido.** `uso_do_pr` só recusa numa branch `melhoria/<slug>` (`branch_da_convencao`, pela `--ref` ou pela branch atual) e quando nenhum parecer da ref leva `pedido: <argumento>`. Num projeto de teste (`$TMPDIR/tech-lead-conferente-c2c3/proj2`, `docs/pedidos/CAD-CLIENTE.md`, branch `feature/cad-cliente`): `forge-check pr CAD-CLIENTE` sem parecer sai `sem parecer para o pedido CAD-CLIENTE` rc=1 (o caminho normal, igual ao ce1a341); com o parecer `pedido: CAD-CLIENTE`, rc=0, também com `--ref <sha>`. O fixture `docs/pedidos/p1.md` voltou a `tests/test_forge.py:4359`, igual ao ce1a341, e `PrAposMergeDaBase` e `BaseShaDoBrief` (que usam `pr p1` em `melhoria/x` com pareceres `pedido: p1`) passam: `Ran 17 tests ... OK`.
- **Mudança de contrato do `forge-check pr`:** o rc=2 vale só em `melhoria/` sem parecer do pedido na ref. Conferido nos testes `test_fora_da_convencao_melhoria_o_id_do_parecer_vale` e `test_com_parecer_do_pedido_na_ref_o_argumento_vale` e nas sondas acima. Sem `--ref` e com HEAD avulso (detached), a recusa não dispara e o comando segue para o rc=1 de `sem parecer`: não aprova nada errado (A5, recomendado).
- **A2 resolvido.** `linha_do_comando_pr` não imprime fora de `melhoria/` (teste `test_fora_da_convencao_melhoria_nao_imprime`), e a frase de `agents/conferente.md:53` diz que fora de `melhoria/` o argumento é o `pedido:` do parecer.
- **A3 resolvido.** `uso_do_pr` procura também em `RAIZES_DE_BRIEF`. No Forge, `forge-check pr CONFERENTE-VELOCIDADE-REV --ref origin/melhoria/conferente-c2c3 --base origin/develop` sai `uso: use o slug da branch (<slug>), não o id do pedido (CONFERENTE-VELOCIDADE-REV)` rc=2, também com `--ref refs/remotes/origin/...`; o slug `conferente-c2c3` vai ao caminho normal (rc=1 enquanto há parecer reprovado).
- **A4 resolvido.** `blocos_identicos` só roda com `Volta-de:` e não marca bloco ausente no anterior (testes `test_brief_sem_volta_de_nao_marca_bloco_identico`, `test_bloco_ausente_no_anterior_nao_e_marcado`, `test_brief_de_volta_marca_os_blocos_identicos_ao_anterior`).
- **Correção da segurança A1 (`desfeitos_da_entrega`), lida como código:** em `arquivos_da_entrega`, o arquivo mudado até a conferida e devolvido à base depois volta ao escopo (interseção com `desde..head`, sem repetir nome). Em `cmd_entrega`, a união em `diferem` só amplia o filtro, e o resultado é mais largo, nunca mais estreito. O teste `test_arquivo_acrescentado_antes_da_conferida_e_apagado_depois_fica_no_escopo` cobre as quatro etapas. O parecer de mérito fica com o `security-engineer` (`docs/security/conferente-c2c3.md`).
- Ferramentas: `python3 -m unittest tests.test_etapa_do_brief tests.test_volta_por_delta tests.test_conferencia_base_dono` deu `Ran 131 tests ... OK`. Teto M14 sobre `ce1a341...cbb5227`: 302 linhas de código e teste (`bin/forge-check` 75, `tests/*.py` 227), abaixo de 400, sem `hooks/` nem `PROTEGIDOS`. PA-7 (`docs/engineering/achados-recorrentes.md`): sem item registrado.

## Revalidação 3 (delta cbb5227..5818e84)
Lido só o que `forge-check delta --parecer docs/reviews/conferente-c2c3.md` lista: `bin/forge-check`:950-951, `tests/test_volta_por_delta.py`:201-236 e `tests/mutantes/conferente-c1-2.json`. O resto fica como "já lido" nas passadas anteriores.

- **A2 da segurança resolvido.** Em `cmd_entrega`, o filtro `diferem_dos_dois_pais` agora soma `desfeitos_da_entrega(raiz, base_sha, valido)` (só com `--desde` válido): o arquivo que a branch pôs até a conferida e o merge da base devolveu à base continua no escopo. A união só alarga o filtro, nunca o estreita; sem `--desde` o conjunto é vazio e nada muda.
- **Três caminhos, quatro etapas.** `desfazer_depois_da_conferida` monta as formas linear, merge da base como último commit e merge seguido de commit; `confere_desfeito` roda `codigo`, `pr`, `merge-integracao` e `pedido-de-merge-ao-dono` e exige `escopo: confira "teste.py" +0 -1` sem `sem commit`.
- **Mutantes.** `bin/forge-mutante tests/mutantes/conferente-c1-2.json`: F1 morreu (bin/forge-check:504), F2 morreu (:951), F3 morreu (:505). Os três mutam as linhas que cada forma exercita.
- Ferramentas: `python3 -m unittest tests.test_volta_por_delta tests.test_etapa_do_brief tests.test_conferencia_base_dono` deu `Ran 134 tests ... OK`. Teto M14 sobre `origin/develop...HEAD`: 341 linhas de código e teste, abaixo de 400, sem `hooks/` nem `PROTEGIDOS`. PA-7: sem item registrado.

## Achados
- A5 (recomendado) bin/forge-check:627 · sem --ref e com HEAD avulso, ou com --ref <sha>, branch_da_convencao dá None e o id do pedido segue ao rc=1 de "sem parecer", não ao rc=2 do item 5 de agents/conferente.md; não aprova nada errado, só a mensagem de uso não aparece

## Parecer
**Aprovado** em 5818e84. A1 a A4 resolvidos e cobertos por teste. As correções da segurança A1 e A2 estão corretas como código, com os três caminhos testados e mutados. A5 é só recomendação e não devolve a entrega.
