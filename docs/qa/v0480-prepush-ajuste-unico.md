---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0480-prepush-ajuste-unico
commit: 61997e21f1b1b2164fa943cef707b7c634148ef4
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0481 E4.3 (PR #871, ajuste único do pre-push, head 61997e21, delta do 082f1f9e)

Escopo: `patches/prepush-unico.patch` (envio local + D2 num patch só), roteiro do dono, `tests/test_prepush_unico.py` (substitui `test_prepush_lote_pp1.py`, saída autorizada pelo dono, R-VERIFY), specs de mutantes, mapa do `bin/forge-testes`. Sem UX (pedido de controle do Forge). O patch foi aplicado numa cópia descartável do head (`git apply --check` e `git apply` rc 0, `bash -n .githooks/pre-push` rc 0; só `.githooks/pre-push` mudou, 148 inserções, 3 remoções).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Texto da trava lido pelo fd 9, falha fechada | test_prepush_unico (trava) | fd fechado → texto vazio | passou, mutantes das linhas do fd e do intervalo mortos |
| `FORGE_FILA_INTERVALO` 0 ou 00 recusado, lido em base 10 (08, 09) | test_prepush_unico (intervalo) | zero, octal inválido | passou |
| Índice das fixtures em dia quando o envio toca o corpus | test_prepush_unico (índice) | pasta tocada, ferramenta ausente só avisa | passou |
| Teste pulado novo em tests/ reprova | test_prepush_unico (pulos) | contagem antes/depois, erro de contagem só avisa | passou |
| D2: índice do Forge, teto H1, texto do PR; só avisa em envio só de parecer | test_pre_push_d2 (22 testes) | sem PR, ref nova, ponta ≠ HEAD | passou |
| PP1 segue provado com o ajuste único aplicado | test_pre_push_patch | patch aplicável | passou |

## Provas
- Aplicação: `git apply --check` + `git apply` + `bash -n` no head, cópia em /tmp/claude-0/qa871: rc 0.
- `python3 -m unittest tests.test_prepush_unico tests.test_pre_push_d2 tests.test_pre_push_patch` (hook remendado): Ran 54 tests, OK (32 s).
- `bin/forge-mutante` das 3 specs `v0480-prepush-ajuste-unico*.json` (`rev=13063422d1fc`): M1 a M20 todos `morreu`, rc 0.
- `bin/forge-mutante` das 2 specs `v0480-d2-portao-entrega*.json` (`rev=13063422d1fc`): M1 a M16 todos `morreu`, rc 0. As duas specs apontam agora para o patch novo.
- Cada guarda do diff do patch (fd, intervalo zero/base 10, índice, pulos, D2, `d2_so_avisa`) tem mutante; conferido à mão porque `--cobertura` só lê Python.
- Vermelho antes do verde: `test_prepush_unico` e `test_pre_push_d2` leem o patch, que não existe como hook na base; o veredito vem do mutante morto com o controle verde, não de `forge-testes --vermelho`.
- `test_pre_push_trava.test_texto_da_trava_sai_limitado_e_sem_controle` falha (618 > 600) no sandbox, com e sem o patch (conferido com `git stash`): não vem do ajuste, é o do roteiro (649 na develop pura).
- CI do sha: check-runs `suíte` (3.12 e 3.14, partes 1 a 5) e `teto de pulados` success. A `bateria` agregada, `bateria (pareceres)` e `catraca` estavam em falha; não consegui ler o log (rede do sandbox negada para o armazenamento de logs). Pela natureza do PR, a catraca pede o rótulo `afrouxa-regra` do dono (roteiro) e a bateria de pareceres espera os pareceres deste ciclo; confirmar no CI após os pareceres e o rótulo.

## Cenários e resultado real
Suíte completa local não rodada (brief; roda no CI). Hook em vigor, não editado nesta cópia: o dono o aplica pelo roteiro.

## Delta 082f1f9e..61997e21 (revalidação, v0481 E4.8)
Dois merges da develop (D4 #869, D7 #868). Do que é da branch, só mudou `bin/forge-testes` (FORGE_CHECK: entra `test_criterios`, que vem da develop; sai `test_prepush_lote_pp1`, arquivo removido por este PR; zero referências restantes a ele em `bin/forge-testes`, e `tests/test_criterios.py` existe no head). `patches/`, `test_prepush_unico`, `test_pre_push_d2`, `test_pre_push_patch`, roteiro e `.githooks/` sem diferença no intervalo. O veredito anterior se mantém.
- `python3 -I -m unittest discover` de `test_prepush_unico` (20 OK, 11 s), `test_pre_push_d2` (22 OK, 29 s), `test_pre_push_patch` (12 OK, 8 s) e `test_criterios` (10 OK), no head.
- `bin/forge-mutante` das 3 specs `v0480-prepush-ajuste-unico*.json` no head (`rev=61997e21f1b1`): M1 a M20 todos `morreu`, rc 0.
- CI: citar o check-run `bateria` do sha 61997e21 no PR; não rerrodei a suíte inteira.
