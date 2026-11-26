---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-rotulo-base-alheia
commit: 48034214f4654bf7d00788ea68f0c0790d79783e
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-26
---
# QA: v0481 rotulo-base-alheia (E17.1, #906)

Diff lido contra o merge-base `22ceb2c83cbe` com a develop: `tests/catraca.py` (+6/-3), `tests/test_catraca.py` (+23), `tests/mutantes/v0481-rotulo-base-alheia.json`, fragmento do changelog. `bin/forge-fechar` sem mudança, conferido.

- ci: 48034214f4654bf7d00788ea68f0c0790d79783e verde

Check-runs do `commit:` (API de check-runs): as 14 `suíte (python 3.12/3.14, parte n/5)`, `bateria (python 3.14)`, `bateria (passos)`, `bateria (verificações longas)`, `instalação`, `árvore já provada`, `teto de pulados` x2: concluídos com sucesso. Fora da conta, como manda a regra: `bateria`, `bateria (pareceres)` e `catraca`, que esperam o parecer e o rótulo.

## Achados

## Critério → teste → resultado
Pedido de correção sem especificação de UX; as obrigações são as da decisão do dono (E17.1): o rótulo não cai por parecer de segurança da branch nem pelo merge da base; o aceite do usuário e o controle seguem dentro da comparação.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Parecer `docs/security/<branch>.md` depois do rótulo + merge da base mantém o rótulo (#875) | `test_parecer_de_seguranca_do_pedido_e_merge_da_base_mantem_o_rotulo` | pasta nova em PARECERES, nome igual ao da branch | passou; vermelho na base (ver abaixo); mutante RB2 morre |
| Aceite do usuário nunca sai da comparação | `test_aceite_do_usuario_ou_parecer_de_seguranca_alheio_depois_do_rotulo_invalida` (subteste `docs/security/aceites/ped.md`) | aceite tocado antes do rótulo e alterado depois (o caso em que o "já tocado" o liberaria) | passou; mutante RB1 morre |
| Parecer de segurança de outro pedido continua invalidando | mesmo teste, subteste `docs/security/outro.md` | nome diferente do da branch | passou |

## Cenários e resultado real
- Módulo tocado: `python3 -m unittest tests.test_catraca.RotuloSobreviveAoConteudo`: 23 testes, OK.
- Leitura do código: `PARECERES` só é lido em `pareceres_do_pedido` (linhas 1394 e 1397, grep em `tests/`, `bin/`, `hooks/`); alargá-lo não afeta outra regra. `ACEITES` filtra os dois caminhos que alimentam `livres` (o já tocado no head rotulado e o de nome igual ao da branch), então o aceite não entra em `livres` por nenhuma via. O padrão fica alinhado a `ACEITES_DO_USUARIO` do `forge-check`. Arquivos de controle (`PROTEGIDOS`, `VIGIADOS_DO_ROTULO`) seguem na checagem `protegidos_como_no_rotulo`, que não usa `PARECERES`: nenhum sai da comparação.
- Observação, sem achado: o que o PR já tocava em `docs/security/` (fora de `aceites/`) antes do rótulo passa a ser livre depois dele, como já era em `docs/reviews/` e `docs/qa/` e como `PASTAS_DOS_PARECERES` do `forge-check` já trata a pasta.
- Mutantes: `bin/forge-mutante tests/mutantes/v0481-rotulo-base-alheia.json` (rev=48034214f465): `RB1 · morreu · tests/catraca.py:1394`, `RB2 · morreu · tests/catraca.py:44`. Cobertura (`--cobertura --base 22ceb2c83cbe...`): `coberta · tests/catraca.py:1394 · ...:RB1 · declarado, não provado`; as linhas 44-45 são constantes, a 45 é exercida por RB1 e a 44 por RB2. Um mutante por guarda mudada: lista completa.
- Vermelho antes do verde (`bin/forge-testes --vermelho 22ceb2c83cbe2e6722fbad4ace35c16e66d6e0a9 --modulos test_catraca`): `vermelho: base=22ceb2c83cbe head=48034214f465 módulos=test_catraca (restrito por --modulos)`; `tests.test_catraca.RotuloSobreviveAoConteudo.test_parecer_de_seguranca_do_pedido_e_merge_da_base_mantem_o_rotulo · H=ok · B=falha · prova (asserção)`; contagem: não prova (passa na base)=418; prova (asserção)=1; rc 0. O teste do aceite passa na base por desenho (o aceite nunca esteve em PARECERES); ele guarda a exceção nova e o RB1 prova que cai sem ela.
