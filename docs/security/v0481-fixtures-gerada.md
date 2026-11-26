---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-fixtures-gerada
commit: de272439995c2476b465f8978cc9430d9c4e2a78
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (#908, HOOKS-FIXTURES-GERADA), 1ª rodada completa (E18.5)

Diff lido: `cfd83b72..de272439` (merge-base com a develop), dois commits (`ed5456ef`, `de272439`), cinco arquivos: `scripts/indice-fixtures.py`, `docs/hooks-fixtures.md` (regerado), `tests/test_indice_fixtures.py`, `tests/mutantes/v0481-fixtures-gerada.json` e o fragmento `changelog.d/v0481-fixtures-gerada.md`.

- ci: de272439995c2476b465f8978cc9430d9c4e2a78 verde via 7a98a5136a2817e852cae8ce94a705e4d2da2432

O run de `de272439` foi cancelado pelo envio do parecer de QA (`341f998a`), e o deste pelo envio do code review (`7a98a513`); o diff `de272439..7a98a513` só toca `docs/qa/` e `docs/reviews/`. No `7a98a513`, as 10 partes da suíte (3.12 e 3.14), `bateria (python 3.14)`, `passos`, `verificações longas`, `instalação`, os dois `teto de pulados`, `árvore já provada` e a `catraca` estão verdes. O único vermelho é `bateria (pareceres)` (e o agregado `bateria`, que cai por ele): o job reprova com parecer faltando (`.github/workflows/ci.yml:741`), e faltava este, de segurança. O log bruto ficou fora do alcance do sandbox (host de artefatos do Actions negado) e as anotações do job só trazem `exit code 1`: a causa vem do desenho do job, não da leitura do log.

Rodado aqui, só no que foi tocado: `tests.test_indice_fixtures` e `tests.test_prepush_unico` (30 testes, OK); `python3 -I scripts/indice-fixtures.py --conferir` dá `em dia`; `--detalhe` imprime `# Detalhe das fixtures dos hooks (3603 fixtures)` e o `git status` segue limpo (não grava); `bin/forge-mutante tests/mutantes/v0481-fixtures-gerada.json`: `M1 · morreu · scripts/indice-fixtures.py:119`. Conferi também que o arquivo gerado não casa nenhum termo de `neutralidade_nucleo` (lista vazia).

Gatilhos: script e teste da bateria do Forge (o `--conferir` roda no CI e no pre-push), teste que executa `git` em subprocesso.

## O que aperta, o que é neutro e o que afrouxa
- **Aperta:** o arquivo versionado deixa de carregar as descrições das fixtures (o exemplo por grupo) e as listas de regras e cartões; só ficam nomes de hook e prefixo, que já estavam lá. Menos texto livre no núcleo é menos superfície para termo de stack ou conteúdo de fixture vazar para a doc (R-NEUTRO); o filtro `exemplo_neutro` segue no `--detalhe`. O teste novo da junção (`tests/test_indice_fixtures.py`, `test_dois_prs_...`) roda o `git` isolado: `GIT_CONFIG_NOSYSTEM=1`, `GIT_CONFIG_GLOBAL=/dev/null`, `HOME` no temporário e `python3 -I`, então nem a configuração nem os hooks da estação entram no teste. O `--conferir` do teste existente passou a usar `-I`. Opções juntas (`--detalhe --conferir`) são recusadas com rc 2 sem gravar, agora com teste.
- **Neutro:** o `--detalhe` só lê o corpus e imprime (`scripts/indice-fixtures.py:119-121`); M1 prova que o teste o cobre. Os nomes de prefixo entram sem escape (`` f"- `{nome}-*`" ``), como já entravam na coluna da tabela antes; vêm de nomes de arquivo do próprio repositório, revisados em PR, sem caminho de ataque. Quem usava a contagem do índice como evidência (pareceres de QA antigos) passa a contar no corpus; o delta de qualquer parecer continua listando cada `tests/hooks/*.json` tocado, então fixture acrescentada ou apagada não fica invisível ao review. Limite declarado (prefixos novos vizinhos conflitam numa linha) é de fluxo, não de segurança.
- **Afrouxa:** nada de controle. O que o `--conferir` deixa de pegar (contagem desatualizada num prefixo existente) é documentação; o corpus em si continua rodando inteiro em `tests/test_hooks.py`, e a guarda dos hooks não muda.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas usadas: leitura do diff, os testes dos módulos tocados, `bin/forge-mutante` e o estado dos checks pela API do GitHub (anotações; o log bruto ficou fora do alcance do sandbox). Faltam no ambiente gitleaks, semgrep, zizmor, actionlint e osv-scanner (lacuna). O diff não traz workflow, dependência nem segredo.
