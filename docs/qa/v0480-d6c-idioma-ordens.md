---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-d6c-idioma-ordens
commit: 748f2975c6cf77ce2c14d58a435a82c91901f99f
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: idioma das mensagens ao dono na linha fixa das ordens reinjetadas (v0478 E174.7, PR #866)

## Achados
- A1 (bloqueante) hooks/ordens.py:78 · Config aninhada abaixo de 64 KiB ('[' * 20000 + ']' * 20000) levanta RecursionError, fora do except (OSError, ValueError): o hook sai sem as ordens, contra o contrato do módulo (as ordens seguem). Reproduzido em sonda (R-QA).

## Critério → teste → resultado
Obrigações: o pedido E174.5 (D6 c) e o contrato escrito em `hooks/ordens.py` (linhas 11 a 13); não há `docs/ux` para este item.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Linha fixa leva o idioma de `idioma_do_dono` (en, es) | `test_idioma_do_dono_pela_config_e_sem_ela_portugues`, fixture `idioma-do-config-entra-na-linha-fixa` | código na lista | passou |
| Sem config ou sem a chave: português | mesmo teste; fixtures antigas atualizadas (`injeta-no-userpromptsubmit`, `sessionstart-compact-injeta`, `sessao-do-forge-le-o-contrib`, `s5-...`, `teto-*`) | config ausente, chave ausente | passou |
| Código fora da lista (texto livre, `fr`, lista, null): sem idioma e sem texto da config no contexto | `test_idioma_torto_sai_none_sem_erro`, `test_linha_fixa_com_e_sem_o_idioma`, fixture `idioma-fora-da-lista-sai-sem-o-idioma` | injeção por texto livre | passou |
| Config torta ou FIFO: ordens seguem | `test_idioma_torto_sai_none_sem_erro` (`{x`, `[]`, FIFO) | JSON inválido, não objeto, não regular | passou |
| Config torta por aninhamento: ordens seguem | nenhum teste | JSON profundo (abaixo de 64 KiB) | FALHOU (A1) |
| Teto e ordens não mudam | `teto-linhas-corta-e-avisa`, `teto-caracteres-corta-e-avisa` | limite do teto | passou |

## Cenários e resultado real
- Sonda (`python3 -I`, arquivo pelo Write): `idioma_do_dono` com config `'[' * 20000 + ']' * 20000` levanta `RecursionError`; `'[' * 5000 + ']' * 5000` e `1e999999999` dão `None`. O erro sobe a `executar` (`hooks/_comum.py`), que sai 0 sem imprimir: as ordens somem. Confirma a S1 do parecer de segurança (E174.8) e o A1 do review (E174.6); a correção é `except (OSError, ValueError, RecursionError)` (ou `Exception`) mais caso no teste e fixture no clone do Forge.
- Head: `python3 -I -m unittest discover -s tests -p test_hooks.py -k OrdensEmVigor`: 23 testes, OK (inclui `test_fixtures` de `tests/hooks/ordens`).

## Provas
Vermelho antes do verde:
```
forge-testes --vermelho aabc476c5dbad3b3efced688e578bb5c71c5f722 --modulos test_hooks
vermelho: base=aabc476c5dba head=748f2975c6cf módulos=test_hooks (restrito por --modulos)
revertidos à base: changelog.d/v0480-d6c-idioma-ordens.md, docs/hooks-fixtures.md, hooks/ordens.py
test_hooks · sem veredito (prazo, sinal ou executor sem registro em H,B)
vermelho: [1/1] test_hooks H 600.0 s, B 600.1 s; 1203 s no total   (carga da máquina 19; módulo de 3572 fixtures)
```
Sem veredito: não vale como vermelho. Recuo manual, equivalente ao que o comando faz: cópia do head em `$TMPDIR` com `hooks/ordens.py` devolvido à base, `python3 -I -m unittest discover -s tests -p test_hooks.py -k OrdensEmVigor -k fixtures_fatia`. Resultado na base: `test_idioma_do_dono_pela_config_e_sem_ela_portugues` ERROR; `test_idioma_torto_sai_none_sem_erro` ERROR (5 subtestes e o FIFO); fixtures `ordens/idioma-do-config-entra-na-linha-fixa`, `s5-worktree-forjada-injeta-so-o-dono`, `teto-caracteres-corta-e-avisa`, `teto-linhas-corta-e-avisa`, `injeta-no-userpromptsubmit`, `sessao-do-forge-le-o-contrib`, `sessionstart-compact-injeta` FAIL; no head, os mesmos 23 testes de `OrdensEmVigor` passam.

Mutantes (`bin/forge-mutante tests/mutantes/v0480-d6c-idioma-ordens.json`): M1 a M7 `morreu`, nenhum sobrevivente (M1, M2, M3, M4, M6 por erro do teste sob o mutante com o controle verde).
`bin/forge-mutante --cobertura --base aabc476c...`: linhas 77, 80, 81 e 124 de `hooks/ordens.py` cobertas por M1, M4, M6 e M7 (declarado, não provado pela cobertura; a rodada acima prova). Lacuna: não há mutante nem teste para a linha 78 contra RecursionError, que é o A1.

CI: a suíte inteira não rodou aqui; o check-run `bateria` do PR #866 no mesmo sha segue obrigatório para o merge.
