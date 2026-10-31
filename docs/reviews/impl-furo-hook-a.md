---
tipo: review
contrato: 1
pedido: impl-furo-hook-a
branch: melhoria/impl-furo-hook-a-a4
commit: 6a15c2a8098a51dc8568c34c669f06c60b5feb0f
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-31
---
# Review: impl-furo-hook-a, branch a4 (A4 FC-SUBCOMANDO-HOOK)

Escopo: `234dbe0..6a15c2a` (base 234dbe0fb90b005450d7c2eb59e6241ea9779155). Commits: `38d218a` (teste das fixtures do lote), `9c658a6` (correção, com as fixtures, o teste estrutural e a spec de mutantes) e `6a15c2a` (fragmento). O revisor é uma instância diferente da do autor (D-ETAPAS-INST = A).

## Item entregue
E4 do pedido, item A4 FC-SUBCOMANDO-HOOK, pelo desenho §2.3. A entrega tem quatro partes:
- `args_do_forge_check` acha o `forge-check` em todo papel: direto, por caminho, por interpretador, atrás de lançador e com nome opaco na forma do `anotar` ou do `--gravar`.
- `forge_check_grava` passa pela política de caminhos o destino do `anotar` (`docs/pedidos/`), do `brief --gravar` (`docs/briefs/`) e da saída do `transcricao anonimizar`, a partir da pasta da sessão e de `~/.forge-contrib`.
- O teste estrutural exige que todo subcomando cuja ajuda diz que grava esteja em `FORGE_CHECK_ESCRITAS` ou em `FORGE_CHECK_EM_CAMINHO_LIVRE`.
- O `docs/hooks.md` foi atualizado. São 20 fixtures (5 contraprovas) e a spec de mutantes.

## M14
Linhas que contam: `hooks/conformidade.py` 41 e `tests/test_hooks.py` 19, num total de 60. Ficam fora as fixtures, a spec, o `.md` e o `changelog.d/`. O total fica abaixo de 150. Há uma classe em `hooks/` (o que o `forge-check` grava passa pela política de caminhos), com corpus próprio, e nenhum caminho de `PROTEGIDOS`. Cumpre.

## Conferido
`python3 -m unittest` de `test_fixtures_do_lote_furo_hook_a` e `test_a4_todo_subcomando_do_forge_check_que_grava_esta_classificado` no HEAD revisado: `Ran 2 tests`, `OK`.

Sondas pelo hook real no HEAD revisado, com `conformidade/fc-anotar-dev-bloqueia.json` como modelo (papel `forge:node-backend`):
- saem 2:
  - `cd src &&` antes do `anotar`, `--raiz ..` e `cd /tmp && --raiz "$OLDPWD"`;
  - `bash -c "forge-check anotar ..."`, `timeout 60` antes e `xargs forge-check anotar ... < /dev/null`;
  - `python3 -I bin/forge-check anotar` e `transcricao anonimizar a.jsonl docs/pedidos/p1.md`.
- saem 0, como devem: `forge-check pr p1` e `forge-check docs`.
- saem **0**, e não deviam:
  - `python3 -X utf8 bin/forge-check anotar --pedido p1 --tipo decisao --literal sim` e o mesmo com `-W ignore` (achado A1);
  - `F=forge-check; $F anotar --pedido p1 --t decisao --literal sim` (achado A2);
  - `find . -maxdepth 0 -exec forge-check anotar ... \;` e `echo anotar | xargs forge-check` (achado A3).

No `forge-check` real, `python3 -X utf8 bin/forge-check anotar ...` e `anotar ... --t decisao` passam do argparse e chegam à busca do pedido. Com um pedido existente, gravariam. Em `args_do_forge_check`, o script do interpretador é tomado como a primeira palavra sem `-`, e o valor de `-X` ou de `-W` ocupa esse lugar. O interpretador é um dos caminhos que o desenho §2.3(a) lista como furo.

Também conferido:
- R-NEUTRO e R-CUSTO: nada a apontar. Não há shell tocado. O Forge não tem `docs/engineering/praticas.md`, então não há regra de leitura nem de ferramenta a citar.
- Commits em Conventional Commits, com os trailers.

## Achados
- A1 (bloqueante) hooks/conformidade.py:75 · `python3 -X utf8 bin/forge-check anotar ...` (e `-W ignore`) sai 0 para o dev: o valor da opção do interpretador vira o script e o forge-check some. Procure entre os argumentos a palavra cujo nome é forge-check, sem exigir a 1.ª sem `-`, e ponha a sonda como fixture.
- A2 (recomendado) hooks/conformidade.py:77 · com nome opaco, `--t decisao` sai 0: o argparse aceita prefixo de uma letra e `abreviacao_de` exige mais de 3 caracteres; conte `anotar` sozinho, ou qualquer prefixo de `--tipo`, como a forma do anotar.
- A3 (recomendado) docs/hooks.md:41 · o texto diz que vale atrás de lançador, mas `find -exec forge-check anotar` e `xargs forge-check` com o subcomando na entrada saem 0; restrinja o texto aos lançadores lidos e leve a classe ao security-engineer, como cartão.

## Parecer
Reprovado. A branch entrega o A4 e cumpre a M14. O A1, porém, é furo provado num dos caminhos que o desenho manda fechar (o interpretador), e por ele o dev forja a decisão do dono (R-DECISAO). Volta ao autor. A2 e A3 não devolvem. Na revalidação, o escopo é o delta (`forge-check delta`).
