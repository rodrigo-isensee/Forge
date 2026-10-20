---
tipo: qa
contrato: 1
pedido: conf-correcao
branch: melhoria/conf-correcao
commit: 568757c630aec8d77111b54e84e1d564902ae92f
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-20
---
# QA - CONF-CORRECAO (passada única, registro citado, `forge-check brief mensagem`)

Sem UX nem API. Código testado em 568757c; o HEAD (4c87f44) só acrescenta `docs/reviews/` e `docs/security/` (`git diff --stat 568757c HEAD`). Obrigações: E1 a E4 do pedido, as decisões do dono do brief `conf-correcao-qa-engineer-1`, `R-QA`, `R-BRIEF`, `R-TETO` (`.githooks/pre-push --status` rc=1 antes da suíte; load 1,2).

## Critério -> teste -> resultado
| ID | Obrigação | Teste (comando real) | Fronteira protegida | Resultado |
|---|---|---|---|---|
| Q-1 | Suíte completa | `python3 -m unittest discover -s tests -q` | n/a | `Ran 1035 tests in 210.620s` / `OK` |
| Q-2 | Plugin válido | `scripts/validar-plugin.sh` | n/a | `Validation passed` (2x) |
| Q-3 | E3: `mensagem` só imprime o texto integral de brief aprovado, com hash | `forge-check brief mensagem --arquivo docs/briefs/conf-correcao-qa-engineer-1.md --pedido conf-correcao --destino forge:qa-engineer` com o brief real | brief aprovado vs reprovado | rc=0; `Brief-sha256: 1d1cd85f...b766b4  Bytes: 6581` igual ao `sha256sum`; os 6581 bytes do arquivo estão contidos na saída |
| Q-4 | Brief reprovado não gera mensagem | cópia sem a decisão "recibo do CONF-CORRECAO"; cópia sem `Pronto quando`/`Relatório` | decisão faltando; seção faltando | rc=1, saída só com `brief mensagem: o brief reprova...` e as linhas do comando; nenhum trecho do brief |
| Q-5 | Delimitador, controle, Cf, Zl, Zp, U+0085 no corpo dão rc 2 | cópia com `<<<BRIEF`, `BRIEF>>>`, U+001B, U+0007, U+007F, U+202E, U+2028, U+2029, U+0085, U+200B, NUL, CR | cada classe de caractere | rc=2 em todos; saída de 73 bytes, só a recusa; TAB e acento (`é`) passam (rc=0) |
| Q-6 | Os mesmos em qualquer campo do cabeçalho | `Base:` com U+2028, U+0085, ESC, U+2029, U+200B; `Agente destino:` com U+2028; `Pedido:` com ESC; `--etapa` com U+2028, U+0085, U+2029, U+200B; `--ref` com ESC | cada campo | rc=2 em todos |
| Q-7 | E2: cobra todas as linhas DECISÃO DO DONO do pedido | brief real: 5 decisões, `decisões: ok (5 linhas de 1 fontes...)`; sem a do recibo: `decisões: falta ... (docs/pedidos/conf-correcao.md:36)` | uma linha faltando | aprovado / reprovado, rc=0 / rc=1 |
| Q-8 | E2: cobra todas as linhas do registro citado em `docs/pedidos/` | pedido de cópia citando `docs/pedidos/reg.md` (2 decisões) | 0, 1 e 2 das linhas presentes | faltam as 2 (`reg.md:2`, `reg.md:3`) / falta `reg.md:3` / `ok (8 linhas de 2 fontes)` |
| Q-9 | Registro citado ausente reprova | citação de `docs/pedidos/naoexiste.md` | arquivo inexistente | `decisões: registro citado ausente "docs/pedidos/naoexiste.md"`, `reprovado`, rc=1 |
| Q-10 | Fonte fora do formato sai "não verificável" com `<arquivo>:<linha>` e não some | decisão citando `docs/migr.md:3` e `docs/migr.md` | com e sem `:<linha>` | `fonte fora da regra "docs/migr.md:3" em docs/pedidos/conf-correcao.md:93 (não verificável)`; sem linha, só o arquivo; a linha existe nos dois casos; não reprova por si (rc=0 com a decisão no brief) |
| Q-11 | E1: ordem fixa de leitura e `tardio:` reprovando, no agente e na R-BRIEF | `grep -n -i 'tardio\|Primeira passada' agents/conferente.md docs/regras/R-BRIEF.md`: `conferente.md:18` (ordem 1 a 4), `:19` (`tardio:` reprova como os outros), `:60` (conta como o campo); R-BRIEF:14 | n/a | presentes; testes `TextosDoAgenteEDaRegra` verdes |
| Q-12 | E4: fragmento do changelog | `git diff --stat 74e5bb7 568757c`: `changelog.d/conf-correcao.md` | n/a | presente; o `forge-check docs` roda na suíte |

## Vermelho antes do verde
- Código: `git archive 568757c` em `$TMPDIR` com `bin/forge-check` de 74e5bb7: as 6 classes novas (50 testes) dão `FAILED (failures=33, errors=1)`.
- Texto: o mesmo com `agents/conferente.md`, `agents/jarvis.md` e `docs/regras/R-BRIEF.md` de 74e5bb7: `TextosDoAgenteEDaRegra` falha 6 de 6 (10 falhas, 1 erro).
- A1, R1 (campos do cabeçalho) e A2 (fonte com linha): `bin/forge-check` e `conferente.md` de 1309956 (antes da volta): `MensagemRecusada.test_campo_de_cabecalho_com_controle_ou_formato_rc_2` (12 subcasos) e `test_campos_do_cabecalho_ficam_em_uma_linha`, `DecisoesCobradas.test_fonte_fora_da_regra_nunca_some` e `..._d_etapas_inst` falham (15 falhas).
- Só guardas (passam com o código de 74e5bb7, porque o subcomando não existe e a recusa é rc 2 do argparse, ou porque nada mudou): `test_arquivo_fora_de_docs_briefs_rc_2`, `test_arquivo_relativo_ao_cwd_nao_vale`, `test_anterior_fora_de_docs_briefs_rc_2`, `test_sem_arquivo_rc_2`, `test_destino_e_ref_invalidos_rc_2`, `test_delimitador_em_qualquer_posicao_rc_2`, `test_delimitador_no_campo_do_cabecalho_rc_2`, `test_controle_e_formato_rc_2`, `test_pedido_com_quebra_de_linha_nao_forja_cabecalho`, `test_so_le_e_imprime_nao_altera_o_disco`, `test_determinismo`, `test_um_nivel_so`. A prova de que a recusa vem do `mensagem` é a manual do Q-5 e do Q-6 (rc=2 com a mensagem do comando; baseline rc=0 com o mesmo brief).
- Instáveis: nenhum teste falhou e passou de novo sem mudança (a suíte rodou uma vez, verde).

## Mutação
A stack do Forge não tem ferramenta de mutação (script e markdown); não se aplica.

## Exploratório
Todos os casos acima rodaram em cópias em `$TMPDIR/r` (`--raiz`), com os briefs reais intactos (`sha256sum` do brief conferido antes e depois: `1d1cd85f...`).

## Observações (não bloqueiam)
- `brief mensagem` sem `--destino` recusa (rc=2) mesmo com `Agente destino:` no brief; é o desenho do E3 (destino explícito), consistente com o `--help`.
- Fonte citada com `~/.forge-contrib/` e referências de segundo nível seguem os riscos já registrados pela segurança (R2, R3), sem mudança aqui.

## Achados
