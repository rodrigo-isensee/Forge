---
tipo: review
contrato: 1
pedido: lote-cilista
branch: melhoria/lote-cilista
commit: 009668b935cc2ed2692d199ef56807f657019af2
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-26
---
# Review: lote-cilista

Escopo: E1 do pedido LOTE-CILISTA (CI-LINT-LISTA-ABERTA), diff `b6eb84f...009668b` (um commit, `tests/test_ci_local.py` e `changelog.d/lote-cilista.md`). Primeira rodada, sem delta.

## Achados
- A1 (recomendado) tests/test_ci_local.py:28 · a alternativa `\b(...|\.github)/` nunca casa `.github/` precedido de espaço ou aspas (`\b` antes de `.` pede caractere de palavra); sonda: gate ou download com `. .github/x` passa. Sugestão: `(?<![\w.-])\.github/` ou tirar o `\b` dessa alternativa.
- A2 (recomendado) tests/test_ci_local.py:61 · gate e download são aceitos pelo nome sem olhar `shell:` nem `env:`; sonda: gate com `shell: ./scripts/x {0}`, com `env: BASH_ENV: scripts/x.sh` ou com `perl scripts.pl` passa. Sugestão: exigir `shell` vazio e nenhum `BASH_ENV`/`ENV` no env desses dois passos.
- A3 (recomendado) tests/test_ci_local.py:78 · o ramo "condição do actionlint ou do zizmor fora da esperada" não tem subcaso no teste novo (a sonda prova que funciona com `if: ${{ always() }}`). Sugestão: um subTest que troca a condição do actionlint.

## Parecer
**Aprovado.** Faz o que o cartão pede: a lista passou a ser positiva (checkout e setups `actions/checkout|setup-python|setup-node` fixados por SHA de 40 hex e sem `run`, gate com `id: gate` e sem código da branch, download com `curl` em número igual ao de `sha256sum -c`), e qualquer outro passo antes do actionlint e do zizmor reprova (`passos_antes_do_lint_fora_da_lista` percorre `passos[:max(lint, ziz)]`, menos o próprio actionlint). A exceção do passo "Testes que leem pareceres" vale só com a condição exata `!cancelled() && steps.gate.outputs.pesada != 'true'`, que é a negação da do lint (também conferida: `SO_COM_LINT` nos dois passos de lint), então ele nunca roda no mesmo job antes do lint; está no commit e no fragmento. O teste lê o `ci.yml` real (`RAIZ / ".github" / "workflows" / "ci.yml"`, nas duas funções) e injeta as variantes nele, com contraprova depois do zizmor.

Leitura: `passos_da_bateria` repete o laço do `ler_jobs` só para pegar `uses` e `id`, e o `assert` do total de passos (linha 49) amarra os dois parsers, falhando alto se divergirem. Os três recomendados são do heurístico do gate e do download, que já são passos nomeados da lista; nenhum deixa um passo de outro nome passar antes do lint nem afeta o `ci.yml` atual, por isso não bloqueiam. A2 tem sabor de segurança (execução antes do lint pelo `BASH_ENV`/`shell`): fica para o `security-engineer` decidir no parecer dele (E2.1), sem refazer aqui.

Testes do lote: `python3 -m unittest tests.test_ci_local` → `Ran 53 tests ... OK` no head revisado. Sondas em `$TMPDIR/tech-lead-lote-cilista/sonda.py`.

Teto M14: 110 linhas de código e teste (`tests/test_ci_local.py` 97+13; o fragmento fica fora), abaixo de 400; não toca `hooks/` nem `PROTEGIDOS`. Fragmento novo em `changelog.d/` presente. Commit em Conventional Commits em português, com o motivo no corpo. `R-NEUTRO` e `R-CUSTO`: sem termo de projeto nem serviço pago. Achados recorrentes (PA-7): lista vazia, nada a conferir. O projeto não tem `docs/engineering/praticas.md`, sem regra "ferramenta" a citar.
