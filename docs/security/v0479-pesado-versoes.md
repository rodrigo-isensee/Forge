---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-pesado-versoes
commit: 4d3f76d441f1c276b554497e69c4330556dc3433
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-pesado-versoes (v0478 E64.4, revalidado na E64.9)

Head revisado `f8210fe5`, base `develop` `8ee73d15`. Mudança: `hooks/pesado.py:292-310` troca a lista aberta de opções pesadas do `bin/forge-testes` (`--completa`, `--vermelho`) pela lista fechada das leves (`LEVES_DO_FORGE_TESTES` mais `-k` e `--`); é a recomendação do parecer do PR-VERDE D1 (`--versoes` fora da fila do R-TETO).

## Gatilhos
Gatilhos: hook de controle (R-TETO, classificação pesado/leve do `hooks/pesado.py`).

## Só aperta (confirmação escrita)
Confirmo por escrito: a mudança **só aperta**. Todo comando que o head classifica como leve já era leve na base; nenhum comando que pesava passa a ser leve. O rótulo afrouxa-regra, se a catraca o pedir por ser mudança de hook, pode ser aplicado pelo time com esta confirmação.

Prova lógica (`hooks/pesado.py:298-310`): no head, leve exige que toda palavra iniciada por `-` seja `--`, `-k`/`-k=…` ou prefixo (mais de 2 caracteres) de uma opção de `LEVES_DO_FORGE_TESTES`. Na base, pesava a palavra em que `pede_opcao` casa `--completa` ou `--vermelho`, o que exige nome com mais de 2 caracteres começando por `--c` ou `--v`. Palavra sem `-` nunca casava na base; `--` (2 caracteres) e `-k` não casam; e nenhuma opção leve começa por `--c` nem `--v` (teste `test_nenhuma_opcao_leve_abrevia_completa_vermelho_nem_versoes`). Logo leve(head) implica leve(base). O ramo do `bin/forge-mutante` (`hooks/pesado.py:311`) não muda.

Prova diferencial executada: as duas funções (a da base reconstruída e a do head) sobre 186392 linhas, todas as sequências de 0 a 3 palavras de um alfabeto de 45 (opções reais do `bin/forge-testes:1143-1159` inteiras, abreviadas e com `=`, `-`, `--`, `-kx`, `-h`, `---c`, `--C`, `--=x`, caminhos), nos dois moldes do teste dirigido: 0 linhas em que o head libera e a base pesava.

Passam a pesar (aperto, sem perda de uso legítimo): `--versoes`, `--modulos`, `--prazo` (só valem com `--vermelho`, já pesado; `bin/forge-testes:1176,1184`), `--executar`, `-h`, `-kx`, a opção desconhecida e opção escrita depois do `--`. A troca em `tests/test_hooks.py:3212` (`--dirigida`, opção inexistente que era leve, sai da lista de leves) é consequência do aperto, não afrouxa teste.

Observação, sem achado: `--registro` (opção interna oculta) segue leve por ser prefixo de `--registros`; sozinha não executa nada pesado (o executor só roda com `--executar`, que pesa; `bin/forge-testes:1161-1162`) e já era leve na base.

## Custo do corpus (teto em `tests/apoio_volta_unica.py:199-200`)
O aumento fica **abaixo de 0,1%** do teto. O teto de 0,1% é 5897 passos do interpretador (de 5897219). O corpus contado por `MEDIDA_DO_CORPUS` (`test_corpus_nos_dois_hooks`, `tests/test_hooks_volta_corpus.py:217`) roda só os hooks `conformidade` e `parecer` (`modelos` de `tests/fixtures/heredoc-volta-unica.json`); nenhum deles importa `hooks/pesado.py` (só `hooks/agentes.py:75` o importa, e ele não está no corpus), e o commit não toca o corpus nem `apoio_volta_unica.py` (execuções seguem 557). O efeito no teto é zero passos; mesmo contadas as +7 chamadas de `pede_opcao` que o autor mediu no corpus diferencial (função sem laço), ficam ordens de grandeza abaixo de 5897. As +3 fixtures entram em `tests/hooks/pesado/` (`test_fixtures` do `tests/test_hooks.py`), fora desse teto.

## Verificação
- `python3 -m unittest tests.test_forge_pesado`: 18 testes OK (inclui a classe nova `FormasLevesDoForgeTestes`).
- As 27 fixtures de `tests/hooks/pesado/` pelo executor do `tests/test_hooks.py` (`executar_em_lote`): OK, 0 puladas.
- Mutantes M1 a M3 (`tests/mutantes/v0478-pesado-versoes.json`) cobrem `-k`, a lista fechada e a leitura da opção curta.
- Suíte inteira: só no CI do PR (ainda sem PR nem execução na branch); este parecer não a substitui.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão estática e sondas locais com a biblioteca padrão; nenhuma ferramenta externa usada nem instalada.

## Revalidação no head 4d3f76d4 (v0478 E64.9)
Delta lido: `forge-check parecer delta docs/security/v0479-pesado-versoes.md`, intervalo `f8210fe5..4d3f76d4`: nenhum arquivo do domínio mudou; fora do domínio só `tests/mutantes/v0451-a1b.json` (além dos pareceres de review, QA e este). `hooks/`, `bin/`, `tests/test_forge_pesado.py` e `tests/test_hooks.py` sem mudança (`git diff --quiet`). O que já foi lido acima segue valendo para o código, que é o mesmo.

Na spec `v0451-a1b`: M5 e A1-separador passam a mutar a fonte nova (`all(opcao_leve(a) for a in argumentos[:1] if`, tupla `("-k",)` sem `--`), e A1-prefixo, A1-igual e A1-separador ganham o teste `test_formas_da_lista_seguem_leves` além do anterior. Nenhum teste saiu, nenhuma guarda foi removida: a spec segue só apertando. Rodei `bin/forge-mutante tests/mutantes/v0451-a1b.json --processos 1` no head: os 10 (M1 a M7, A1-prefixo, A1-igual, A1-separador) morreram.

Achados anteriores: nenhum. Confirmação escrita mantida: a mudança **só aperta**.
