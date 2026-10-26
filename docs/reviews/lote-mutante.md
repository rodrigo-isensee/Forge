---
tipo: review
contrato: 1
pedido: lote-mutante
branch: melhoria/lote-mutante
commit: 786505960a19cb0ec3ba4ae30f454031625e75c7
parecer: aprovado
revisor: forge:tech-lead (instância de review, não a autora)
data: 2026-10-26
---
# Review: LOTE-MUTANTE (E1.1 do LOTE-MUTANTE-REV)

Base `b6eb84fed86e3b5289f3950b33d43a86f34343c2`, head `786505960a19cb0ec3ba4ae30f454031625e75c7`. Três commits: `e6f3f34` feat (MUTANTE-TETO), `6f7b6ef` fix (MUTANTE-ID-ASCII) e `7865059` test (spec de mutantes do lote). São um commit por cartão, com os testes de cada um, em Conventional Commits em português.

## Achados
- A1 (recomendado) skills/qa-testing/SKILL.md:85 · o texto ainda fala de uma spec só ("3 a 8 mutantes") e não cita que o pedido com mais de 8 divide em `<pedido>-<n>.json` e passa todas numa rodada. Sugestão: uma frase com o uso novo.
- A2 (recomendado) bin/forge-mutante:215 · `isidentifier` aceita parte fora da NFKC (`c` + U+0327, letra de largura cheia). O Python normaliza o nome do `def` e o loader não acha o teste; o resultado é "controle vermelho", nunca "morreu" (sondado). Sugestão: recusar a parte com `unicodedata.normalize("NFKC", p) != p`.

## Escopo e requisitos
- **Várias specs (E1):** `spec` passou a `nargs="*"`. A lista vazia continua caindo em `falta a SPEC`. `validar_specs` (linha 218) valida cada spec com o `validar_spec` de antes, então o teto de 8 continua por spec (`MAXIMO_DE_MUTANTES` não mudou). Depois confere o mesmo `pedido` em todas e recusa id de mutante repetido no conjunto. Isso é necessário porque a cópia de cada mutante tem o nome do id. Uma spec ilegível ou inválida sai 2 antes de `principal` e nada roda (`test_segunda_spec_invalida_barra_tudo_antes_de_rodar`). A mesma spec passada duas vezes cai em id repetido. A checagem do `executor` passou a `any(...)`, que é o correto para um conjunto.
- **Cabeçalho:** a linha 295 imprime um `spec=<sha256>` por spec, na ordem da linha de comando, e `pedido=` vem da primeira (as outras têm o mesmo pedido, já validado). O teste confere o hash de cada arquivo.
- **Id de teste (E2):** `id_de_teste_valido` (linha 209) parte por `.`, exige `tests` na primeira parte e pelo menos uma parte depois dela, e cada parte precisa passar em `str.isidentifier`. Ponto vazio, ponto final, espaço, hífen, NBSP, `\n`, U+2024 e metacaracteres de shell são recusados (testes e sonda). Como não há shell, o id vai em argv.
- **Mudança de contrato:** agora é recusada a parte que começa por dígito (`tests.x.1a`), que o `ID_DE_TESTE` antigo aceitava. Não há perda real: o arquivo de teste precisa casar `test_[a-z0-9_]+\.py` (`TESTE`), e classe e método não começam por dígito. As quatro specs de `tests/mutantes/` validam no código novo. A mudança está no fragmento `changelog.d/lote-mutante.md`, em `### Corrigido`.

## Checklist (leitura)
- Arquitetura e regras: só biblioteca padrão, sem shell, não é portão (nenhum hook nem CI o chama). `R-NEUTRO` e `R-CUSTO` estão preservadas. Tem fragmento em `changelog.d/`, e o `CHANGELOG.md` não foi editado.
- Legibilidade: as funções novas são pequenas, têm docstring de contrato e o cabeçalho do script foi atualizado (uso e "uma spec inválida barra todas").
- Erros: a mensagem de spec ilegível agora diz qual caminho falhou.
- Testes: 5 testes novos cobrem o caminho feliz, o teto por spec, pedido diferente, id repetido, lista vazia, a segunda spec inválida e a execução real com nome não ASCII. Não há teste de ausência cujo alvo tenha mudado.
- Teto por PR (M14): `git diff --numstat --no-renames` dá 52+23 em `bin/forge-mutante` e 49+2 em `tests/test_forge_mutante.py`, 126 linhas no total, abaixo de 400. A spec em `tests/mutantes/` e o changelog ficam fora da conta. Não mexe em `hooks/` nem em `PROTEGIDOS`.
- Segurança: não encontrei achado com gatilho. O total de mutantes por rodada cresce com o número de specs, mas o prazo por mutante continua valendo e a ferramenta não é portão. O parecer próprio é o do `security-engineer` (E2.1).

## Ferramenta (citada)
- `python3 -m unittest tests.test_forge_mutante` neste head: `Ran 35 tests`, `OK`.
- Sonda num repositório de brinquedo (`$TMPDIR/tech-lead-lote-mutante/toy`) com `def test_borda_ação`. O id em NFC deu `M1 · morreu · lib.py:2`. O id em NFD e o de largura cheia deram `M1 · controle vermelho · lib.py`. É a base do A2.
- A rodada da spec do lote (`tests/mutantes/lote-mutante.json`, 7 mutantes) é evidência do QA (E3.1) e não a refiz.

## Parecer
Aprovado, sem bloqueante. Os dois cartões fazem o que o pedido pede, nem mais nem menos. O teto de 8 continua por spec, uma spec inválida barra todas e o contrato do id ficou mais estrito sem quebrar nenhuma spec existente. A1 e A2 são recomendações e não devolvem a entrega.
