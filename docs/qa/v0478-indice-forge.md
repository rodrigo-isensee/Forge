---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0478-indice-forge
commit: 35a78d7408bc3940e034e94e3b6983d3adc3e1da
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0478 (índice do Forge, H7, E8.1)

Passada única no head 7bd4913e, só os testes dos arquivos tocados (`R-QA`); a suíte inteira é do check-run `bateria` do CI do PR, não rodada aqui.

## Critério → teste → resultado
| Critério (obrigação) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Índice gerado em dia com `bin/`, `hooks/`, `scripts/` e o mapa | `test_indice_esta_em_dia`, `test_conferir_da_rc_0_em_dia`; `indice-forge.py --conferir` | arquivo desatualizado | passou |
| Toda entrada versionada tem linha (guarda de suíte vazia, mínimo 60) | `test_toda_entrada_versionada_tem_linha` | lista vazia | passou |
| `--conferir`: rc 1 desatualizado ou sem arquivo, rc 0 em dia; sem argumento grava; argumento inválido rc 2 sem gravar | `Main.*` (5) | arquivo ausente, argumento extra | passou |
| Primeira linha de doc: Python, shell, sem doc, `\|` escapado, corte em 160 | `PrimeiraLinhaDeDoc.*` (4) | exatamente 160 e 161 caracteres | passou |
| Testes por arquivo: ordem, corte em 6 com "e mais N", sem oráculo, modo completo | `TestesDoArquivo.*` (3) | 6 e 7 módulos, lista só de oráculo | passou |
| Só versionados, um nível, sem `GIT_*` herdado (AR-7) | `Arquivos.*` (2) | não versionado, subpasta | passou |
| Mapa: `docs/indice-forge.md` aciona `test_indice_forge`; o índice não é portão | `test_testes_tocados` (162 testes, 1 skip herdado da base) | lista fechada `AVISOS` | passou |

## Cenários e resultado real
- `python3 scripts/indice-forge.py --conferir`: `docs/indice-forge.md: em dia`.
- `python3 -m unittest tests.test_indice_forge`: 18 testes, OK (16,6 s). `test_testes_tocados.py` via discover: 162 testes, OK, 1 skip existente na base (não adicionado por este diff).
- Vermelho antes do verde, `bin/forge-testes --vermelho 4182a6b9 --modulos test_indice_forge`:
  `vermelho: base=4182a6b95a12 head=7bd4913edcb3 módulos=test_indice_forge (restrito por --modulos)`; revertidos à base: `bin/forge-testes`, `changelog.d/v0478-indice-forge.md`, `docs/indice-forge.md`, `scripts/indice-forge.py`; `contagem: prova (API ausente)=18`, rc 0.
- Mutação, `bin/forge-mutante` nas 3 specs (`--processos 2`), `rev=7bd4913edcb3`: M1 a M22 `morreu`, nenhum sobrevivente, nenhum equivalente (M1 morreu por erro do teste declarado, que passa sem o mutante, aceito).
- `forge-mutante --cobertura --base 4182a6b9`: só linhas `coberta`, nenhuma condição do arquivo novo sem mutante; `base=4182a6b9… mb=4182a6b9…`.
- Observação: `-I` com `-m unittest tests.test_indice_forge` não importa o pacote `tests` (o módulo usa `from tests.ambiente_git`); era defeito, não forma do comando: o módulo importava `from tests.ambiente_git`, que falha no modo `discover -s tests -t tests` do CI, e o CI pegou. Corrigido no head 35a78d74 (ver revalidação E8.14); a observação anterior estava errada.
- Acessibilidade e E2E: não se aplicam (ferramenta de linha de comando e documento gerado).

## Revalidação E8.9 (head bf97d62a, delta desde 7bd4913e)
Delta lido por `forge-check parecer delta`: `bin/forge-testes` (`teste_do_indice` no plano dirigido e no afetados), índice sem coluna de testes nem contagem, `scripts/indice-forge.py`, specs de mutantes (M11 a M14 saem com a coluna; M23 entra), `test_indice_forge` (`SoNomeEDoc` no lugar de `TestesDoArquivo`) e `test_testes_tocados`. Fora disso nada foi relido.

| Critério (obrigação) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Índice só com arquivo e doc, sem contagem nem coluna de testes | `SoNomeEDoc.test_tabela_so_com_arquivo_e_doc_e_sem_contagem`, `test_teste_novo_nao_muda_o_indice` | módulo de teste a mais não muda o texto | passou |
| Todo arquivo do 1º nível de bin/, hooks/ e scripts/ leva `test_indice_forge` no plano dirigido (review A2); fora delas não | `SoNomeEDoc.test_o_plano_dirigido_das_pastas_roda_o_indice` | `agents/` fora; `.json` e `.sh` dentro | passou |
| Raiz sem `tests/test_indice_forge.py` segue dirigida sem pedir o módulo | `SoNomeEDoc.test_raiz_sem_o_teste_do_indice_segue_dirigida_sem_ele` | módulo ausente | passou |
| Mapa atualizado com o teste do índice | `test_testes_tocados` (162 testes, OK, 1 skip herdado da base) | contagem do `forge-check` fora do índice | passou |

Provas:
- `python3 -m unittest tests.test_indice_forge`: 19 testes, OK; `scripts/indice-forge.py --conferir`: em dia.
- Mutação, `bin/forge-mutante` nas 3 specs (`--processos 2`, `rev=bf97d62a0acb`): M1 a M10, M15 a M23 `morreu`, nenhum sobrevivente; M23 (`bin/forge-testes:314`) morreu. M1 morreu por erro do teste declarado, que passa sem o mutante (aceito, como antes). Delta com `--base 7bd4913e`: `base=7bd4913e… mb=7bd4913e… rev=bf97d62a…`, mesmos veredictos.
- `forge-mutante --cobertura --base 7bd4913e`: `coberta · bin/forge-testes:314 · M23`; as linhas `apagada` são as das condições de `testes_do_arquivo`, removidas junto com a coluna.
- Vermelho, `bin/forge-testes --vermelho 7bd4913e --modulos test_indice_forge`: `SoNomeEDoc.test_o_plano_dirigido_das_pastas_roda_o_indice`, `test_raiz_sem_o_teste_do_indice_segue_dirigida_sem_ele` e `test_tabela_so_com_arquivo_e_doc_e_sem_contagem` `H=ok B=falha · prova (asserção)`; `test_teste_novo_nao_muda_o_indice` `H=ok B=erro · sem veredito` (na base o teste erra, não falha; o comando sai rc 2 por esse caso). Três provas bastam para o risco do delta (A2 e a coluna removida); o quarto é guarda de regressão, sem bloqueio.
- Sem skip novo. Sem achado.

## Revalidação E8.14 (head 35a78d74, delta desde bf97d62a)
Delta lido por `forge-check parecer delta`: só `bin/forge-testes` (o mapa de `scripts/preparar-estacao.sh` ganha `test_ferramentas_portoes`) e `tests/test_indice_forge.py` (o import passa a `sys.path.insert(tests/)` e `from ambiente_git import sem_manutencao`, válido também no modo `tests.<módulo>`). Fora disso nada foi relido.
- Defeito de importação (corrige a linha 37 acima): `from tests.ambiente_git` quebrava sob o `discover -s tests -t tests` do CI; o import novo resolve. Defeito achado pelo CI, não por este parecer; fechado no delta.
- Prova, como no CI: `python3 -I -m unittest discover -s tests -t tests -p test_indice_forge.py`: `Ran 19 tests ... OK`.
- Mapa: a linha nova só soma um módulo ao plano de `preparar-estacao.sh`; não muda guarda de código decisório, sem mutante novo.
- Sem skip novo. Sem achado; `parecer: aprovado` mantido.
