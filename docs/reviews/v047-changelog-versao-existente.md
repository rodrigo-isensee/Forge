---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-changelog-versao-existente
commit: 665ddd3279ad383032f47b2ff706c59e7bb54d9a
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047, lote CH1 (CHANGELOG-RELEASE-VERSAO-EXISTENTE, E2.93)

Code review da classe C no head `9bf1fa1c`, base `bf475209`, por instância que não fez a entrega (E2.77). Parecer completo: não havia parecer anterior.

## Escopo lido
- `bin/forge-changelog:186-191`: a recusa de versão repetida já existia; o diff só troca a mensagem (o quê, por quê, como destravar) e mantém a saída antes de qualquer gravação.
- `tests/test_changelog.py:290-308`: recusa com rc=1, texto das três partes, `CHANGELOG.md`, fragmento e `plugin.json` intactos; versão vizinha (0.1.1) passa.
- `tests/mutantes/v047-changelog-versao-existente.json`: CV-M1 (guarda) e CV-M2 (texto da recusa).
- `changelog.d/v047-changelog-versao-existente.md`: tipo `Corrigido`, coerente com o `fix`.

## Verificadores
- `bin/forge-mutante --processos 1 tests/mutantes/v047-changelog-versao-existente.json`: CV-M1 morreu (`bin/forge-changelog:186`), CV-M2 morreu (`:187`).
- `bin/forge-mutante --cobertura --base bf475209`: nenhuma condição mudada sem mutante.
- `python3 -m unittest tests.test_changelog.Release`: 24 testes, OK. A suíte inteira fica para o CI do PR.
- Tamanho (M14): 26 linhas de código e teste (fora o JSON de mutantes e o fragmento), um comportamento só.

## Achados
- A1 (recomendado) bin/forge-changelog:190 · A mensagem manda usar `release --anexar`, que só existe em melhoria/v047-changelog-anexar (sem PR); neste head a sonda dá rc=2 (unrecognized arguments). Mesclar só depois dela (plano CH1) ou trocar o texto se ela cair.
- A2 (recomendado) tests/test_changelog.py:303 · O teste da versão vizinha usa 0.1.1 contra 0.1.0 e não pega a perda do `\]` no padrão; 0.1.1 contra uma entrada 0.1.10 pegaria. A guarda não mudou no diff; fica como reforço.

## Sondas

## Parecer
Aprovado. O cartão pede a recusa com o quê, por quê e como destravar, sem gravar nada, e é isso que o diff faz; os dois mutantes declarados morrem e o teste cobre o ramo de falha com o estado dos três arquivos.

Condição de integração (não é achado bloqueante porque a ordem já está decidida no plano da noite, linha CH1: "merge depois de melhoria/v047-changelog-anexar", e no brief da E2.77): este item entra na `develop` só depois da `melhoria/v047-changelog-anexar`, trazendo a `develop` antes do PR. Sonda feita no head revisado: `forge-changelog release --anexar 0.1.0 2026-01-02` recusa com `unrecognized arguments: --anexar`, rc=2. Se a melhoria do `--anexar` for retirada, A1 vira defeito e a mensagem precisa mudar antes do merge.

## Revalidação (head 665ddd32, E2.534)
Delta lido (`forge-check parecer delta`): 9bf1fa1c..665ddd32 em `bin/forge-changelog` e `tests/test_changelog.py` é só a entrada da develop (86ac0fcb) com o `release --anexar` (E1.256), não código deste item; o diff do item contra a develop segue em 26 linhas (6 em `bin/`, 20 em teste).
- A1 resolvido: o `--anexar` está na base; sonda `forge-changelog release --anexar 0.1.0` num CHANGELOG com a 0.1.0 devolveu rc=0 ("1 fragmento(s) anexado(s)"). A condição de ordem de integração está cumprida.
- A2 segue recomendado, sem mudança.
- `python3 -m unittest tests.test_changelog`: 89 testes, OK.
- `bin/forge-mutante --processos 1 tests/mutantes/v047-changelog-versao-existente.json`: CV-M1 morreu (`bin/forge-changelog:195`), CV-M2 morreu (`:196`).
Parecer mantido: aprovado, agora no head 665ddd32.
