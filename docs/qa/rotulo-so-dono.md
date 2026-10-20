---
tipo: qa
contrato: 1
pedido: rotulo-so-dono
branch: melhoria/rotulo-so-dono
commit: 6ec509586c79014203222d65760177ab1be9674e
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-20
---
# QA - rotulo-so-dono (R-CONTRIB: o rótulo afrouxa-regra só do dono)

Sem UX nem API. Diff `976a159...6ec5095` em `hooks/`, `tests/` e `docs/regras/R-CONTRIB.md`. Não escrevi o diff. Review (`aee3305`) e segurança (`fd69fab`) aprovaram `6ec5095`; HEAD testado `fd69fab` (só pareceres depois de `6ec5095`). Fora do escopo, por decisão do Jarvis: R7 e R8 (cartão ROTULO-VARIAVEL).

## Obrigação -> teste -> resultado
| ID | Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|---|
| E1 | Texto único da regra em `R-CONTRIB` | `tests/config.json` (invariante) e testes de regras com ID na suíte | texto da regra não some | passa |
| E2a | Conta dona aplica e remove `afrouxa-regra` (`gh pr edit`, REST, GraphQL) | fixtures `rotulo-so-dono-pr-edit-conta-do-dono-libera`, `-api-labels-conta-do-dono-libera`; `formas_alternativas` e `volta_2_...remocao` com conta do dono (código 0) | permissão (dono) | passa |
| E2b | Outra conta barrada em cada forma: `pr edit`/`issue edit`/`pr create`, REST (`?`, `#`, `/` final, URL), GraphQL (`/graphql`, URL, `addLabelsToLabelable`), `bash -c`, `eval`, crase, crase escapada, comentário com aspa, `gh label create|edit|clone`, `--remove-label`, DELETE REST | fixtures `*-outra-conta-bloqueia`, `-remover-rotulo-exige-dono`, `-bash-c-aninhado-...`; `formas_alternativas` (20 barram) e `volta_2_crase_escapada_comentario_clone_e_remocao` (11 barram) | permissão (outra conta) | passa |
| E2c | Erro ou timeout de `gh api user` barra | fixture `pr-edit-erro-na-conta-bloqueia`; `gh_pendurado_decide_antes_do_timeout_do_hook`; `erro_inesperado_falha_fechado`; guarda de timeout dos subprocessos de rede | falha fechado, timeout < hooks.json | passa |
| E2d | Comando sem o rótulo passa e não chama `gh api user` | casos `passam` (outro rótulo, corpo que cita o rótulo, `gh label list`, crase sem o rótulo); sonda manual abaixo | sem rótulo, sem custo de rede | passa |
| E2e | Sessão de projeto continua barrada (R-CONTRIB), inclusive crase escapada e comentário | `volta_2_sessao_de_projeto` (5 barram, 2 passam) | sessão de projeto | passa |
| E3 | Fragmento `changelog.d/rotulo-so-dono.md` | testes de changelog da suíte | n/a | passa |

## Execução (HEAD `fd69fab`, gh falso, sem rede)
- `python3 -m unittest discover -s tests -q`: `Ran 877 tests in 422.091s`, `OK`.
- `scripts/validar-plugin.sh`: `Validation passed` (as duas validações). Chamadas de rede negadas pelo sandbox (api.anthropic.com, datadog) não afetam o resultado.
- Sonda manual (hook direto, gh falso que registra chamadas e responde `outra-pessoa`, sessão do Forge): `gh pr list`, `git status` e `gh pr edit 70 --add-label bug` -> `rc=0`, nenhuma chamada ao gh; `gh pr edit 70 --add-label afrouxa-regra` -> `rc=2`, uma chamada, `R-CONTRIB: só o dono do Forge aplica ou delega o rótulo afrouxa-regra (conta do gh: outra-pessoa)`.

## Vermelho antes do verde
Comando: `git show 976a159:hooks/conformidade.py > hooks/conformidade.py && python3 -m unittest discover -s tests -q -k rotulo_so_dono -k fixtures`, depois restaurei o hook novo (árvore limpa).
- Com o hook da `develop`: `FAILED (failures=45)`: 8 fixtures novas, 20 em `formas_alternativas`, 11 em `volta_2_crase_escapada_comentario_clone_e_remocao`, 3 em `volta_2_sessao_de_projeto`, 2 em `erro_inesperado_falha_fechado`, 1 em `gh_pendurado_decide_antes_do_timeout_do_hook`.
- Só `-k rotulo_so_dono` com o hook antigo: `Ran 5 tests`, `FAILED (failures=37)`; com o hook novo: `Ran 5 tests`, `OK`.

## Mutação
Sem ferramenta de mutação gratuita para Python na stack; o vermelho com o hook da `develop` mostra que cada forma nova é guardada por caso que falha sem a implementação.

## Achados
