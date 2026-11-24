---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-clone-nome-unico
commit: d33eb54d678d9032d6901f733797534c6f625ab4
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 E172.17 (PR #860, E172.7: brief gerar sugere a cópia só do agente; id do pedido fora da forma sai PREENCHER)

Base 5f1c6e97, head revisado d33eb54d (2 commits: 4eb87381 feat, d33eb54d test). Diff: `bin/forge-check` (+31/-3), `bin/forge-copia` (+1 doc), fragmento de changelog, spec de mutantes, `tests/test_forge_copia.py` (+88). Código abaixo do teto H1 (cerca de 33 linhas), um comportamento por commit.

## Achados
- A1 (bloqueante) bin/forge-testes:153 · `tests/test_forge_copia.py` passou a usar o `forge-check` (importa `fc` de `test_pre_envio_brief`) e não entrou no mapa `FORGE_CHECK`; `test_testes_tocados.MapaDoForgeCheck` falha no CI (suíte parte 1/5, 3.12 e 3.14) e localmente. Incluir `test_forge_copia` no mapa.
- A2 (recomendado) changelog.d/v0480-clone-nome-unico.md:2 · diz que o brief "recusa o pedido com id fora da forma", mas o código avisa e põe PREENCHER no lugar (rc 0); trocar por "põe a marca a preencher no lugar do id fora da forma".

## Sondas
- S1 · `cd tests && python3 -m unittest test_testes_tocados.MapaDoForgeCheck.test_mapa_lista_todo_modulo_que_usa_o_forge_check` no d33eb54d · espera: OK · obtido: FAILED, `['test_forge_copia'] != []`, faltam no mapa FORGE_CHECK

## O que foi lido
- `copia_sugerida`: valida papel (`[a-z0-9][a-z0-9-]*`) e branch (`valor_de_shell_seguro`), carrega o `forge-copia` por `SourceFileLoader` (o script tem guarda `__main__`, sem efeito na carga) e reusa `nome_unico`; pasta no Forge `~/.forge-contrib/wt`, no projeto `<projeto>/.forge/wt` também de dentro de uma cópia (corte pela `MARCA`). Uma fonte só para o nome, sem duplicar a regra.
- `montar_brief`: `id_impresso` substitui o id nas três saídas que o interpolavam com crase (`comece por`, `forge-fechar`, `decisões:`); as demais usam `interpolacao_segura` ou só leem. A linha da cópia só sai com o caminho seguro para shell.
- Testes de comportamento dos ramos de falha (papel/branch fora da forma, `forge-copia` ausente, HOME com espaço, sem `--branch`, id com crase); nenhum lê o texto da fonte.

## Ferramentas (citadas, sem refazer a suíte)
- `bin/forge-mutante tests/mutantes/v0478-clone-nome-unico.json --rev d33eb54d --processos 1`: M1 a M7 morreram (rc 0).
- `bin/forge-mutante --cobertura --base 5f1c6e97 --rev d33eb54d`: guardas 9527, 9537, 9567, 9627 e 9628 cobertas (rc 0).
- `python3 -m unittest test_forge_copia` (pasta `tests`): 76 testes OK.
- CI do head d33eb54d: vermelho; suíte parte 1/5 pela A1; `catraca`, `bateria` e `bateria (pareceres)` vermelhas, sem anotação legível daqui (os pareceres faltavam no head).

## Parecer
Reprovado pela A1: defeito provado, CI vermelho no head e reproduzido localmente. Correção de uma linha no mapa do `bin/forge-testes`; a A2 é recomendação. Na volta, revalido só o delta.
