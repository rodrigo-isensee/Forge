---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-copia-base
commit: 1571a36f79ed939ceca9979c969ef65136faa926
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0481 (E13.3), forge-copia clone com base e branch remota (#879)

Diff revisado: `d49accf8..1571a36f` (1 commit), `bin/forge-copia` (+24 linhas de código, dentro do teto H1), `tests/test_forge_copia.py`, `tests/mutantes/v0481-copia-base.json`, `changelog.d/v0481-copia-base.md`. Sem parecer de review anterior na branch.

## Achados
- A1 (recomendado) bin/forge-copia:312 · Na falha, a mensagem cita `a.base` e `origin/{a.base}` mesmo quando o ponto tentado foi `origin/<branch>` e, com a base padrão, imprime `origin/origin/develop` (sonda: `--branch develop` sobre origem na develop). Sugestão: citar `ponto` quando houver; sem ponto, as refs de fato tentadas.

## Sondas

## Parecer
**Aprovado.** Faz o que o E13.2 pede, sem mais: só o modo `clone` muda; a `worktree` fica igual.

Caminhos conferidos (a cópia nunca fica na branch padrão nem sobre ref errada):
- `git clone` que falha: sai 1 antes de procurar base (o git apaga o destino que criou); teste `test_clone_que_falha_sai_1_antes_de_procurar_a_base`.
- branch que existe no remoto: confere a ref exata `refs/remotes/origin/<branch>` (nome exato, não prefixo; checklist 12), parte dela com `--no-track`; teste confere head e ausência de `branch.<b>.remote`.
- base: tenta a dada e depois `origin/<base>`, com `rev-parse --verify -q <ref>^{commit}` (só commit vale); sem nenhuma, `rmtree` e sai 1. No clone recém-feito a `develop` local, se existe, é o head de `origin/develop`, então as duas leituras não divergem.
- `switch` que falha (branch local já existente, `--branch main`/`develop`, `HEAD`): `rmtree` e sai 1. O `rmtree` só alcança o destino já validado dentro da pasta liberada e livre (`destino_dentro`/`ocupado`), recém-criado pelo clone.
- Nada que barrava deixou de barrar: as recusas de opção, nome de branch, destino, disco e `--origem` ficam antes e intactas; o único afrouxamento é o intencional (`--base develop` passa a resolver).

Ferramentas (citadas, não refeitas): `python3 -m unittest tests.test_forge_copia` no clone, 81 testes OK; `bin/forge-mutante --processos 1 tests/mutantes/v0481-copia-base.json` em `1571a36f`: M1 a M7 morreram (linhas 127, 133, 136, 137, 307, 310, 311). Uma guarda por mutante, todas com teste de comportamento do ramo de falha. O falso de `ponto_de_partida` na classe `Disco` só cobre o clone falso sem refs e não mascara a regra (ela é exercida nos testes `Cria` com git real). Suíte inteira: CI do PR #879 ainda em andamento no momento do parecer (`bateria (passos)` pendente); cito o PQ do autor (89 testes OK com `test_forge_copia_nome`).

A1 é cosmético (só o texto do stderr de falha; o código de saída e a limpeza estão certos) e vira cartão depois do merge.
