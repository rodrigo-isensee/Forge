---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-meta85-forge-check
commit: 6853e0ee2ac9c19305db2419ddbcfbb3f5dcf1f0
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-19
---
# Review: v0478 (E34.3, META85 na trilha do bin/forge-check)

## Achados
- A1 (recomendado) bin/forge-check:3575 · parecer `riscos-aceitos` sem o aceite do usuário sai `revalida: não`, mas o `forge-check pr` (linha 2014) o barra: a promessa de as duas respostas nunca divergirem falha nesse caso; o mesmo A1 da segurança.
- A2 (recomendado) agents/jarvis.md:29 · o passo 5 do Jarvis ainda diz que a revalidação retoma quem deu o parecer, sem o filtro `revalida: sim` que a skill autor-ate-o-merge.md:10 passou a citar como "passo 5 do Jarvis".
- A3 (recomendado) tests/test_meta85_item_arquivos.py:22 · o subprocesso herda `os.environ` e roda o Python sem `-I`; use `ambiente_limpo()` como em test_meta85_entrega. A sonda com GIT_DIR e GIT_INDEX_FILE ruins ficou verde, então não há defeito provado.

## Sondas

## Parecer
Aprovado. Revisei o diff `eca1d21b..6853e0ee`: 18 arquivos, 7 contam no teto do item, e 96 linhas de código em `bin/` (H1, dentro do teto). Os três cartões seguem o desenho em `docs/propostas/meta85-forge-check.md`, e o corte em três cartões na mesma branch veio do dono (E34 no `## Escopo`).

- **Entrega com provas:** só a forma antiga cobra as provas. A conferência (`entrega --pedido`) recusa `--mutantes` e `--pronto`, e o teste cobre isso. A leitura do log é limitada por `TETO_DA_PROVA`, e a ferramenta só lê o log, nunca o roda. O PQ do `brief gerar` e o da volta trazem os dois logs.
- **Revalida:** chama o `commit_vale` com os mesmos livres, estritos, domínio e dispensados do `cmd_pr`, e a linha sai nos dois ramos de rc 0. Há uma divergência de borda (A1).
- **Classe:** `arquivos_do_item` reusa `e_teste`, `FRAGMENTOS` e `LIVRES`, sem regra nova. Com a base ilegível, a ferramenta não conta os arquivos e a classe já sai C (decisão testada). O `--json` traz a contagem.
- **ESCOPO+ (`bin/forge-testes`):** só põe os três módulos novos no mapa. O `test_testes_tocados` foi ajustado para 105.

Provas que rodei no head 6853e0ee:
- `python3 -m unittest tests.test_meta85_entrega tests.test_meta85_revalida tests.test_meta85_item_arquivos`: 22 OK.
- `bin/forge-mutante --processos 1` com as quatro specs: M1 a M21 morreram, rc 0.
- `bin/forge-mutante --cobertura --base eca1d21b`: rc 0, sem condição sem mutante.
- `tests.test_forge.AntiDuplicacao`, `test_metricas_texto`, `test_indice_forge` e `test_testes_tocados`: 185 OK, 1 pulado pelo sandbox (proc de outro namespace).
- `test_etapa_do_brief.PqDoExecutor` e `test_volta_por_delta.BriefDeVolta`: 31 OK.
- `forge-check classe --base eca1d21b --json`: classe C, `arquivos_do_item` 7, rc 0.

A suíte inteira fica para o CI do PR. Pela regra META85 do recomendado, A1 a A3 viram cartão depois do merge, salvo o A1, que a segurança já mandou corrigir antes.
