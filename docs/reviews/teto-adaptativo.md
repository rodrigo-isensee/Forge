---
tipo: review
contrato: 1
pedido: teto-adaptativo
branch: melhoria/teto-adaptativo
commit: 54852d4e5bde991de5a2691dc4fa979d9ce01d4e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-19
---
# Code review: TETO-ADAPTATIVO, revalidação por delta da volta 2

Substitui o parecer anterior (reprovado em 119bc50, por A1). Diff revisado: `da15a88..54852d4` (cinco arquivos: `bin/forge-check`, `docs/hooks.md`, `docs/regras/R-TETO.md`, `hooks/agentes.py`, `tests/test_hooks.py`). O resto do parecer anterior (escopo, modelo dos projetos, volta 1, R-CUSTO, R-NEUTRO, changelog) não foi tocado pelo delta e continua valendo.

Ferramentas, rodadas só no recorte (a suíte inteira é prova do autor, 871 OK, e o pre-push a roda; R-TETO):
- `python3 -m unittest tests.test_hooks`: 24 testes, OK.
- `python3 -m unittest tests.test_forge -k kanban -k instancias -k limites -k invariante -k regra`: 8 testes, OK.

## Achados anteriores
- A1 (bloqueante), resolvido: `docs/hooks.md` (linha da tabela e a seção de config) descreve o teto adaptativo de R-TETO sem os números antigos; sem leitura, "3 ou nproc, o menor". Bate com R-TETO e com o hook.
- A2, resolvido: `teto_maximo` é aplicado dentro de `agentes.calcular_teto`, sobre o fixo e o adaptativo; `forge-check` (`teto_calculado`) só chama a função e perdeu o `min` próprio. Fórmula num lugar só. Teste `test_teto_maximo_vale_igual_sobre_o_fixo_e_o_adaptativo` (8 com máximo 5 dá 5; 4 dá 4; adaptativo 16 com máximo 5 dá 5). Documentado em `docs/hooks.md:79` e R-TETO.
- A3, resolvido: sem leitura, `min(3, nproc)` quando nproc é conhecido; `test_teto_sem_leitura_nunca_passa_de_nproc` (nproc 1, 2, 3, 8, None).
- A4, resolvido: `nucleos()` usa `os.sched_getaffinity(0)` com `os.cpu_count()` de reserva e trata `OSError`; teste cobre afinidade, falha e ausência da função. R-TETO descreve a leitura.
- R1 da segurança, resolvido: `FORGE_NPROC` e `FORGE_PROC` definidos ficam registrados no `erros.log` (`registrar_escape`); teste `test_variaveis_de_substituicao_ficam_no_erros_log`. O ajuste da asserção de `erros.log` nos testes aceita só as linhas "Aviso: FORGE_", e qualquer outro erro interno ainda falha o teste.

## Conferências pedidas
- Hardware (1, 8, 16 núcleos): `test_faixas_do_teto_segue_o_hardware` e as fixtures `nproc-*` do parecer anterior seguem verdes; o delta soma 1, 2, 3, 8 e sem leitura (sem leitura) e 16 núcleos com `teto_maximo`. Kanban: 4, 6 e 16 núcleos, 1, 3, 6, 7 e 16 nos limites de coluna, verdes.
- Fórmula num lugar só: `agentes.calcular_teto` é a única; hook e `forge-check` a usam. O fator de coluna (`teto // 3`) é a regra de R-WIP, não cópia da fórmula.
- Invariantes: `tests/config.json` não aparece no delta; a lista continua com as mesmas três trocas do parecer anterior (R-TETO: "2 agentes com load acima de 6" por "menor que 0,8 × nproc"; R-WIP: as duas frases de "2 worktrees" e o novo "teto ÷ 3"), todas pela decisão do dono, e nenhum outro invariante saiu. O PR precisa do destaque no título.
- Escopo: nenhum arquivo fora dos permitidos; sem custo (R-CUSTO), sem termo de projeto (R-NEUTRO).

## Achados
- A5 (recomendado): `hooks/agentes.py:5` (docstring do módulo) ainda diz "`teto_maximo` limita o adaptativo"; agora limita também o fixo. Texto só, pode entrar na próxima mudança do arquivo (ou na do cartão TETO-RAJADA).
