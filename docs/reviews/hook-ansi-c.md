---
tipo: review
contrato: 1
pedido: hook-ansi-c
branch: melhoria/hook-ansi-c
commit: 3707e280ce4e3ff11bc28b79b6ab75820d920b27
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-27
---
# Review: hook-ansi-c

Escopo revisado: `770c19a3c3f64d0f132eb358232e126e69e33b2e...3707e280ce4e3ff11bc28b79b6ab75820d920b27` (commits c51c9c7, 0fc65b1, f118baa e o merge 3707e28 da develop, que não traz nada além do item). Arquivos: `hooks/_comum.py` (+7 −2), `tests/test_hook_ansi_c.py` (+121), `tests/mutantes/hook-ansi-c.json` (+60, fora do teto), `changelog.d/hook-ansi-c.md` (+2, fora do teto).

## Achados
- A1 (bloqueante) tests/test_hook_ansi_c.py:20 · requisito (R-CONFORMIDADE, controle MapaCobreOQueOsTestesLeem driblado): o f118baa troca o caminho fixo de hooks/conformidade.py por HOOKS / f"{nome}.py" só para o teste não ver o arquivo; bin/forge-testes --listar hooks/_comum.py não lista test_hook_ansi_c
- A2 (recomendado) tests/test_hook_ansi_c.py:23 · ambiente_limpo copiado de tests/test_forge.py:502 para não importar test_forge; com A1 resolvido, importe-o (e entre no FORGE_CHECK) ou mova-o para um apoio comum, sem duplicar

## Parecer
**Reprovado**, por A1. A correção do leitor está certa; o que devolve é o teste que esconde a própria cobertura do filtro do pre-push.

### O que está correto
- **Marca `aspa_escapada` em `palavras_do_texto`** (`hooks/_comum.py:1043`): só no nível `ansi`, só quando a barra é seguida de `'`, e o `i += 2` existente garante que `\\'` (barra escapada e o fecho) não marca. Conferido com sondas: `$'a\\\'b'` marca; `$'a\\'` não; `"$'\''"` (sem ANSI-C dentro de aspas duplas) não; `\$'it\'s'` não; dentro de `${x:-…}`, colado em palavra (`a$'…'`), em atribuição, em crase, em `$(…)`, em `<(…)` e em crase entre aspas duplas marca. `$'it\x27s'` não marca e o `shlex` o lê igual ao bash (o `cat` vai para o arquivo `.env'`, decisão inalterada).
- **`leituras` falha fechado** (`hooks/_comum.py:1716`): todo `$'…\'…'` é mal lido pelo `shlex` (a `\'` vira fecho de aspas simples), então devolver `ilegivel` é correto e cumpre a E1 pela via que o pedido admite ("ou a linha falha fechado"). Efeito nos outros leitores de `leituras`: `conformidade` e `parecer` fecham no `ilegivel`; `pesado` e `alvos_de_escrita` perdem só uma leitura que já era errada nesses casos (o `shlex` ou dava `ValueError`, ou juntava o `;` à palavra). Heredoc com `$'it\'s'` no corpo não vira falso positivo (o conformidade tira o corpo antes; sonda: saída 0).
- **`LeituraDoTexto`** com `defaults=(False,)`: quem desempacota ou constrói a tupla com dois campos continua funcionando.
- **Os 6 testes** (`python3 -m unittest tests.test_hook_ansi_c`: 6 ok, 1,4 s): o bash real prova o furo em diretório temporário, sem `.env` nem `.git` reais; os dois casos do cartão saem 2 com "aspas sem par"; três variantes (mais adiante, depois de `$'a\\b'`, dentro de `"$(…)"`); controles de antes e depois; `\\'` antes do fecho volta a ser recusado pelo motivo certo ("ler .env"); unidade do leitor.
- **Mutantes** (`bin/forge-mutante tests/mutantes/hook-ansi-c.json`, rev 3707e280ce4e): A1 a A5 morreram. Cobrem a remoção do portão em `leituras`, a marca constante falsa, a marca larga demais (qualquer barra), o pulo da barra e a marca fora do ANSI-C.
- Teto M14: 130 linhas contadas (`hooks/_comum.py` 9 e `tests/test_hook_ansi_c.py` 121), abaixo de 400. Uma classe de comportamento em `hooks/` (citação ANSI-C no leitor), como manda a DECISÃO TÉCNICA 2026-10-27 14:02. `hooks/conformidade.py` intocado. Fragmento `changelog.d/hook-ansi-c.md` presente. Sem termo de projeto (`R-NEUTRO`), sem custo (`R-CUSTO`). PA-7 (`docs/engineering/achados-recorrentes.md`): lista vazia, nada a conferir.

### A1: o teste esconde a cobertura do filtro do pre-push
O ponto que o autor levantou procede, e é o achado. Na versão c51c9c7 o módulo citava `HOOK = RAIZ / "hooks" / "conformidade.py"`; o `MapaCobreOQueOsTestesLeem.test_todo_arquivo_lido_por_um_modulo_roda_esse_modulo` (`tests/test_testes_tocados.py:215`) acusou, com razão, que `hooks/conformidade.py` não leva a `test_hook_ansi_c` no mapa de `bin/forge-testes`. O f118baa não corrigiu o mapa. Ele passou o caminho para `HOOKS / f"{nome}.py"`, com um parâmetro `nome` que ninguém passa (`tests/test_hook_ansi_c.py:54`). A f-string vira parte dinâmica (`*`) e o caminho truncado (`hooks`) é pasta, não arquivo, por isso a conferência deixa de ver o hook. O comentário da linha 20 e a mensagem do commit dizem que o objetivo era esse.

Prova: `bin/forge-testes --listar hooks/_comum.py` lista `test_agentes_clone, test_agentes_hash_brief, test_catraca, test_doutor, test_forge, test_hooks, test_hooks_volta_corpus, test_hooks_volta_lancador, test_hooks_volta_propriedades, test_sugerir, test_testes_tocados, test_textos_dono_f10`, e `test_hook_ansi_c` não está lá. Uma mudança futura em `hooks/_comum.py` que reabra o furo passa no pre-push dirigido; só o CI do PR a pegaria. Enfraquecer um teste da fábrica para ele parar de acusar é o drible que `R-CONFORMIDADE` proíbe, mesmo sem má-fé. O caminho certo era corrigir o mapa ou levar a dúvida como decisão.

Correção (volta ao autor): voltar `HOOK = RAIZ / "hooks" / "conformidade.py"` e tirar o parâmetro `nome`; acrescentar `"test_hook_ansi_c"` à regra `r"hooks/.*"` de `bin/forge-testes:100`. Essa mudança fica fora de `hooks/` e não é outra classe de comportamento. Ela faz o envio rodar a suíte completa, o que esta branch já faz por causa do `tests/mutantes/hook-ansi-c.json` sem mapa. Prova da volta: `bin/forge-testes --listar hooks/_comum.py` passa a listar `test_hook_ansi_c`, e `python3 -m unittest tests.test_testes_tocados` fica verde sem drible. O carregamento de `bin/forge-check` por `_comum.forge_check()` no lançador segue o mesmo precedente de `test_agentes_hash_brief` e `test_agentes_clone`, que também não estão no `FORGE_CHECK`. Isso não é achado desta entrega.

### A2 (recomendado)
`ambiente_limpo` é a cópia de `tests/test_forge.py:502`, feita para não importar `test_forge`. Com A1 resolvido não há mais motivo para a cópia. Importe a função e ponha o módulo no `FORGE_CHECK`, ou mova-a para um apoio comum que os dois usem.

## Revisões
- Portões de outros: segurança (`docs/security/`) e QA (`docs/qa/`) são de outra delegação (E2.1, E3.1) e não entram aqui.
