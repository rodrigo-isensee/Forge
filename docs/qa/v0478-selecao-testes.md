---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0478-selecao-testes
commit: 95c7fc2ff9f42c6c071f7943b5424dd571f21562
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-19
---
# QA: v0478 seleção de testes (E18.1, 4 cartões, 6 mutantes)

Passada única no head 53f89698 (`R-QA`). Máquina carregada: só os testes dos arquivos do diff, com `TMPDIR`; a suíte inteira fica para o check-run `bateria` do CI do PR.

## Achados
- A1 (recomendado) tests/test_suite_paralela.py:405 · No `forge-testes --vermelho`, `test_medir_modulo_que_nao_existe_sai_2_sem_rodar_nem_gravar` sai "B=erro · sem veredito" (rc 2 da ferramenta). A morte pelo mutante M1 compensa; o autor deve apontar a causa do erro na base ou separar o teste.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| VERMELHO-COM-PROGRESSO | `test_vermelho_escreve_progresso_com_o_teto_e_os_modulos_do_diff_primeiro` | teto 2×módulos×prazo; ordem do diff primeiro; stdout inalterado | passou; M6 morreu |
| `--medir` roda e regrava só o módulo | `test_medir_roda_so_o_modulo_e_regrava_so_o_peso_dele` | pesos de outros módulos intactos | passou; vermelho: prova (asserção) |
| `--medir` módulo inexistente | `test_medir_modulo_que_nao_existe_...` | nome inválido (`a`, `../test_a`, `test_a.T`), rc 2 | passou; M1 morreu; vermelho: sem veredito (A1) |
| `--medir` vermelho | `test_medir_modulo_vermelho_sai_1_sem_regravar` | não regrava | passou; M2 morreu; vermelho: prova (asserção) |
| `--medir` completude | `test_medir_com_guarda_de_completude_reprovada_nao_regrava` | guarda reprovada | passou; M3 morreu; vermelho: prova (API ausente) |
| `--medir` sinal | `test_medir_interrompido_sai_com_o_sinal_sem_regravar` | 128+SIGTERM | passou; M4 morreu; vermelho: prova (asserção) |
| `--medir` uso | `test_medir_sem_modulo_ou_com_mais_argumentos_mostra_o_uso` | zero e dois módulos, rc 2 | passou; M5 morreu; vermelho: prova (asserção) |
| DEFEITO-CONTAGEM-FIXA-FORGE-CHECK | `Mapa.test_forge_check_roda_os_modulos_dele` | piso de 90 módulos, nada extra no plano | passou |
| CITA-BIN-BARRA | `MapaDoForgeCheck.test_cita_reconhece_as_formas_do_caminho_do_script` | `BIN / "forge-check"` sim; `SBIN`, `forge-changelog`, `forge_check.py` não | passou |
| `--medir` verde não grava o carimbo (A1 da segurança) | `test_medir_verde_nao_grava_o_carimbo_da_suite_verde` | `.git/*verde*` vazio após `--medir`; sem carimbo a suíte roda inteira, sem `suite: reusa` | passou; M7 morreu; vermelho: prova (asserção) |
| PesosDaSuite (mensagem) | `PesosDaSuite` em `tests/test_forge.py` | n/a | passou |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_suite_paralela.py`: 74 testes, OK (154 s).
- `test_testes_tocados.py` (`-k` do progresso, `MapaDoForgeCheck`, `test_forge_check_roda_os_modulos_dele`): 5 testes, OK. `PesosDaSuite`: 1 teste, OK.
- Vermelho: `forge-testes --vermelho 0c47762a --modulos test_suite_paralela`, rc 2 só pelo A1. Contagem da 1ª rodada: `não prova (passa na base)=68; prova (API ausente)=1; prova (asserção)=4; sem veredito=1`. Os 4 testes de `--medir` com asserção e o de API ausente provam o vermelho.
- Mutantes: `bin/forge-mutante tests/mutantes/v0478-selecao-testes.json`, 6 de 6 morreram:
  `forge-mutante: pedido=v0478 rev=53f8969816a5 spec=d8883b29b88d…`; `M1 morreu · scripts/suite-paralela.py:925`; `M2 · :937`; `M3 · :936`; `M4 · :934`; `M5 · :955`; `M6 morreu · bin/forge-testes:816`.
- Cobertura da lista contra o diff: as 6 linhas de guarda (`--medir`: existência, erros, completude, sinal, argumentos; ordem do `--vermelho`) têm mutante. A guarda `len(argv) == 2` está coberta por M5. Sem guarda mudada sem mutante.
- O check-run `bateria` do mesmo sha fica para o CI do PR.

## Revalidação no head afcc49b4 (delta de `forge-check parecer delta`: só `tests/test_suite_paralela.py`, +11 linhas)
- Teste novo `test_medir_verde_nao_grava_o_carimbo_da_suite_verde` (commit 124f2f6a). `forge-testes --vermelho 0c47762a6a9d4453adfe0b8e244604a265c6bde3 --modulos test_suite_paralela --prazo 280`: `vermelho: base=0c47762a6a9d head=afcc49b47c01`; `...test_medir_verde_nao_grava_o_carimbo_da_suite_verde · H=ok · B=falha · prova (asserção)`; rc 2 só pelo A1 (`test_medir_modulo_que_nao_existe...` B=erro, sem veredito), inalterado.
- Mutante M7 (manual, cópia descartável de `scripts/suite-paralela.py`): `--medir` verde chama `gravar_carimbo(RAIZ, hash_calculado_antes)` após `gravar_pesos`: o teste falha com `--medir gravou o carimbo` (morreu). Nota: o mutante ingênuo `gravar_carimbo(RAIZ, hash_da_arvore(RAIZ))` depois de `gravar_pesos` sobrevive, mas é equivalente (a árvore já está suja pelo `pesos-d4.json`, o hash é `None` e `gravar_carimbo` não grava).
- O teste isola a causa: afirma que não há carimbo e que, sem marcas, a suíte roda `a, b, c` sem reuso. Sem outro achado; o A1 segue recomendado.
- Execução local: `python3 -I -m unittest discover -s tests -p test_suite_paralela.py -k test_medir_verde_nao_grava`: 1 teste, OK. Suíte inteira: check-run `bateria` do CI do PR.

## Revalidação no head 95c7fc2f (E18.12)
O delta (`forge-check parecer delta`) é só `bin/forge-testes`: o merge da develop trouxe `test_promocao_por_marca`, `test_fc_pr_parecer_forjado` e `test_filtros_l08_g2_ancora` para a tupla `FORGE_CHECK`, com o conflito de `tests/test_testes_tocados.py` resolvido. Os três módulos existem e rodaram com `TMPDIR`: 7, 4 e 6 testes, `rc=0` nos três. Nada no domínio do QA mudou além disso; o parecer segue aprovado e a suíte inteira fica para o check-run `bateria` do CI do PR.
