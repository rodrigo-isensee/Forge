---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-copia-nome-unico
commit: f6f1eaf1a22d1b046e953b62135e76d9419284eb
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-23
---
# QA: v0480-copia-nome-unico (CLONE-NOME-UNICO)

Delta 900bfdfe..95011540: `bin/forge-copia` (destino ocupado nunca reusado; a recusa diz a branch da cópia e sugere nome livre; `--papel`), `tests/test_forge_copia_nome.py`, specs de mutantes, `tests/pesos-d4.json`.

## Revalidação por delta (E111.11)

Delta 2f16f017..04e560fa (merge da develop f17183d; `forge-check parecer delta` lista só `tests/pesos-d4.json` no domínio). A linha `test_forge_copia_nome: 4.0` é idêntica nos dois lados; o JSON carrega (289 chaves). `python3 -m unittest tests.test_forge_copia_nome`: 9 testes, OK no head. Aprovação anterior mantida.

## Achados
- A1 (recomendado) bin/forge-copia:261 · mutante M6 de tests/mutantes/v0475-copia-pasta.json `if valor.startswith("-")` sobrevive, também na base 900bfdfe (provado em cópia); linha fora do diff, guarda redundante com check-ref-format; virar teste ou equivalente.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CLONE-NOME-UNICO: ocupado é recusado com a branch da cópia e nome sugerido | test_nome_tomado_por_outra_branch_recusa_com_o_nome_sugerido, test_mesma_branch_em_uso_tambem_recusa | cópia de outra branch / mesma branch | passou |
| nome livre cria | test_nome_livre_cria | destino livre | passou |
| nome sugerido tomado ganha -2, -3 | test_nome_sugerido_ja_tomado_ganha_sufixo_numerico | máximo: nome e arquivo ocupados | passou |
| sem --papel usa branch sem prefixo | test_sem_papel_sugere_a_branch_sem_prefixo | branch com subpasta | passou |
| pasta vazia não é tomada | test_pasta_vazia_nao_esta_tomada | vazio | passou |
| não dita a branch do repositório em volta | test_pasta_comum_dentro_de_repositorio_nao_diz_a_branch_do_repositorio | pasta comum | passou |
| papel inválido recusa sem criar | test_papel_invalido_recusa_sem_criar | `../x`, maiúscula, `-`, `/` | passou |
| nome sugerido ocupado por atalho simbólico (volta 2f16f017) | test_link_com_o_nome_sugerido_nao_e_oferecido | atalho para pasta vazia fora da pasta; nada escrito fora | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_forge_copia_nome tests.test_forge_copia` (TMPDIR): Ran 74 tests, OK.
- Vermelho (manual, em cópia de 900bfdfe com o teste novo): `python3 -m unittest tests.test_forge_copia_nome` -> Ran 8, FAILED (failures=10); só `test_pasta_vazia_nao_esta_tomada` passa na base (fronteira que já valia). O `forge-testes --vermelho` oficial rodou a suíte inteira (233 módulos, mais de 6 min) e foi interrompido: sem veredito; não vale como vermelho.
- Mutantes `bin/forge-mutante tests/mutantes/v0480-copia-nome-unico.json`: M1 a M5 morreu. Spec v0475 (editada em M5): M5 morreu, M6 sobreviveu (A1, pré-existente), demais morreram.
- `forge-mutante --cobertura --base 900bfdfe`: linhas 79, 86, 95, 97, 265 e 112 cobertas; `tests/pesos-d4.json` é dado, sem guarda.
- Suíte inteira: no CI do PR (`bateria`); não rodada local.

## Revalidação por delta (head 2f16f017, desde 950115403)
- Delta: `ocupado()` trata atalho simbólico como ocupado (`bin/forge-copia:79`), teste novo, mutante M6 da spec, fragmento de changelog.
- `python3 -m unittest tests.test_forge_copia_nome` (TMPDIR): Ran 9, OK.
- `bin/forge-mutante tests/mutantes/v0480-copia-nome-unico.json`: M1 a M6 morreu (M6 · morreu · bin/forge-copia:79); com a guarda desligada o teste novo cai: vermelho provado pelo mutante.
- A1 segue aberto como recomendado (linha fora do diff). Suíte inteira: no CI (`bateria`).

## Revalidação por delta (head f6f1eaf1, volta de CI E111.13, desde d2288045)
- Delta no domínio: só bin/forge-testes (+1 linha no MAPA: bin/forge-copia -> test_forge_copia, test_forge_copia_nome, test_forge). Dado de mapeamento, sem guarda de código; sem mutante cabível.
- python3 -m unittest tests.test_testes_tocados (da raiz, sem -I): Ran 196, OK (skipped=1, herdado do módulo).
- python3 -I -m unittest discover -s tests -p test_forge_copia_nome.py: Ran 9, OK.
- bin/forge-testes --listar bin/forge-copia: o dirigido inclui test_forge_copia_nome (o efeito da linha nova).
- Aprovação mantida; A1 segue aberto como recomendado. Suíte inteira: no CI (bateria).
