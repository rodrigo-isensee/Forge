# Comandos prontos para colar (QA no Forge)

Parte da skill `qa-testing`, num arquivo próprio porque o texto inteiro não cabe no teto de caracteres da `SKILL.md`
(diretriz 25 do dono: regra existente não se apaga nem se resume; o que não cabe muda de arquivo, com ponteiro). Cada
comando roda da raiz do repositório; troque só o que está entre `<>`. Rodados numa cópia na v0478 E96.1.

## Um módulo de teste com `-I`
- O módulo inteiro: `python3 -I -m unittest discover -s tests -p test_x.py`.
- Uma classe: `python3 -I tests/test_x.py <Classe>` (vale para o módulo que põe a própria pasta no `sys.path`, como os
  do Forge que importam um vizinho).
- `python3 -I -m unittest tests.test_x` falha: sob `-I` a raiz sai do `sys.path` e `tests.test_x` não importa.

## Pasta temporária e comando longo
A pasta temporária nasce no mesmo comando, fora de `~/.forge-contrib` (o `mktemp -d` usa o `TMPDIR` da sessão). O
primeiro plano da ferramenta Bash corta entre 180 e 600 s: comando longo vai com o `run_in_background`, log de caminho
literal e a linha `rc=` no fim, e a espera segue o laço do log da skill `esperar-estado`:

`TMPDIR=$(mktemp -d) <comando> > <log> 2>&1; echo "rc=$?" >> <log>`

O `rc=` guarda o código: no vermelho e na rodada de mutantes, 2 é sem veredito, que não vale como prova.

## Vermelho antes do verde
Com a árvore limpa (commite antes):

`TMPDIR=$(mktemp -d) bin/forge-testes --vermelho <Base-sha> --modulos test_x`

Sem `--modulos`, ele roda os módulos de teste do diff mais o plano dos outros caminhos, e o plano pode ser a suíte
toda. Vários módulos: `--modulos test_x,test_y`.

## Mutantes declarados
- Autor, antes do push: `bin/forge-mutante --cobertura --base <Base-sha>`.
- Rodada, depois do commit: `TMPDIR=$(mktemp -d) bin/forge-mutante tests/mutantes/<pedido>.json`. Uma chamada por
  pedido: as specs do mesmo pedido (`tests/mutantes/<pedido>-2.json`) vão juntas na mesma chamada; specs de pedidos
  diferentes na mesma chamada saem 2. Com a árvore suja, a spec que difere da do commit, ou que ele não tem, sai 2.
- Revalidação: `bin/forge-mutante tests/mutantes/<pedido>.json --base <head-aprovado>`.

## Simulação de merge (a base certa)
Simule o merge sobre a base de integração fora da árvore de trabalho:
1. Use um clone ou uma worktree **com as refs remotas** e rode `git fetch origin <base>`.
2. Faça `git merge --no-ff refs/remotes/origin/<base>` na cópia descartável.
3. Rode a checagem **contra essa base** (a mesma da validação), nunca contra a base local.

Sem as refs remotas, a checagem compara com a base errada e sai com rc 0: confira que
`git rev-parse refs/remotes/origin/<base>` responde.

Prontos para colar, em duas chamadas (o hook `parecer` recusa o merge em pasta com variável; a segunda leva a pasta
literal que a primeira imprime):

```bash
u=$(git remote get-url origin) && d=$(mktemp -d) && git clone -q --no-hardlinks . "$d/c" && git -C "$d/c" remote set-url origin "$u" && git -C "$d/c" fetch -q origin <base> && git -C "$d/c" rev-parse refs/remotes/origin/<base> && echo "$d/c"
```

```bash
cd <pasta impressa> && git merge --no-ff --no-edit refs/remotes/origin/<base>
```
