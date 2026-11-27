---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-f1-parecer-fora
commit: edaf7bc08b371efafbd4eeb58dcab39bcb0143eb
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-27
---
# QA: v0481 (E29.7, #925, F1 corte 1: leitura do parecer no status do commit)

Sem especificação de UX nem contrato de API: as obrigações são as do E29.1 (pedido) e as mitigações do modelo de ameaças do G2 (M1.1 a M19.1) citadas nos testes e mutantes. Sem oráculo: o corte não toca hook, `.githooks/`, catraca nem CI, e `ler` não tem chamador.

- ci: edaf7bc08b371efafbd4eeb58dcab39bcb0143eb verde

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E29.1 `ler` devolve aprovado/reprovado só com comentário íntegro | `Ler.test_aprovado_com_comentario_integro`, `test_reprovado_vale_como_reprovado` | n/a | passou |
| M1.1/M1.2 filtro de conta antes do mais novo | `test_c1_status_do_bot_ignorado`, `test_c2_bot_mais_novo_nao_esconde_failure_da_conta`, `test_c19_conta_fora_da_lista_ignorada` (M8, M17) | conta fora da lista | passou |
| M1.1 `contas` = conjunto de logins não vazios | `test_contas_que_nao_sao_conjunto_recusadas`, `test_contas_com_login_vazio_recusadas`, `test_contas_frozenset_vale` (M18, M19) | str (substring), login vazio | passou |
| M2.1 contexto por igualdade exata | `test_c3_contexto_parecido` (M12) | contexto parecido | passou |
| M5.1 comentário editado ou apagado | `test_c6_comentario_editado`, `test_c6_comentario_apagado` (M5) | corpo diferente do sha256 | passou |
| M5.2 autor do comentário na lista | `test_c7_comentario_de_outra_conta` (M11, M4) | autor fora | passou |
| M6.1 `target_url` presa ao PR do head | `test_c8_target_url_fora_do_formato`, `test_comentario_de_outro_pr_pelo_mesmo_id` (M3, M4, M10) | URL fora, outro PR, id igual | passou |
| M7.1/M8.1 descrição e frontmatter amarrados ao head e ao estado | `test_c9_descricao_fora_da_forma`, `test_c10_*` (M2, M6, M9) | descrição fora da forma, commit/pedido/tipo/veredito diferentes | passou |
| M19.1 resposta do gh fora do contrato é Recusa | `test_c17_*`, `test_resposta_fora_do_contrato_vira_recusa`, `test_status_sem_descricao_ou_sem_target_url` (M7, M13 a M16, M20) | páginas ilegíveis, API com erro, item que não é objeto | passou |
| Frontmatter: sem bloco ou sem abertura é vazio | `test_sem_frontmatter`, `test_frontmatter_sem_a_linha_de_abertura` (M1) | vazio | passou |
| Volta 1 (E29.4): `de` do M27 único; índice regerado | CI: `test_forge_mutante.ConferirTodas`, `test_indice_forge` (3.12 e 3.14); `forge-mutante --conferir --base` | n/a | passou |

## Vermelho antes do verde
`bin/forge-testes --vermelho ee05ee8439f8dac1743ecd61c8b64dab29688a41 --modulos test_forge_pareceres` (rc=0):
```
vermelho: base=ee05ee8439f8 head=edaf7bc08b37 módulos=test_forge_pareceres (restrito por --modulos)
contagem: não prova (passa na base)=40; prova (API ausente)=29
```
Os 29 testes da classe `Ler` falham na base e passam no head; os 40 restantes são anteriores ao corte.

## Mutação
`bin/forge-mutante --base ee05ee84… tests/mutantes/v0481-f1-parecer-fora.json -2.json -3.json` (rc=0): M1 a M20 morreram (M13 a M17 e M20 por erro do teste declarado, que passa sem o mutante). `--conferir --base`: "o trecho de cada spec do diff está no lugar". `--cobertura --base` (rc=0): toda condição mudada (linhas 105 a 148) tem mutante declarado e provado acima; nenhuma `não coberto`.

## Cenários e resultado real
- Local, com a trava `/root/.forge-contrib/trava-teste-a.lock` (a 1ª tentativa sem espera foi negada; depois esperei a vez): `python3 -m unittest tests.test_forge_pareceres`, Ran 69 tests, OK. Nada acima de 10 minutos.
- CI no `commit:` (run 45935176061, headSha conferido): suíte 3.12 e 3.14, partes 1 a 5, bateria (passos), bateria (python 3.14), verificações longas, instalação, teto de pulados e árvore já provada: todos pass. `bateria`, `bateria (pareceres)` e `catraca` falham por esperar parecer ou rótulo `afrouxa-regra` (previsto no brief; fora do que o G3 exige).
- D2 local `test_pre_push_trava`: falha também na develop local e passa no CI; fora deste PR (cartão registrado pelo portão).
- Corte sem chamador: `ler`, `conferir` e `frontmatter` só aparecem nos testes. A forja pela mesma conta via Bash (M4.1, M4.2) fica para os cortes anteriores ao chamador, como a segurança declarou.
