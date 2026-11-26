---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-release-04719-anexo-2
commit: 17395e4d905fdbf24bbe21451050873b77261ba6
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (segundo anexo da 0.47.19, E12.43, #911), 1ª rodada completa

Diff lido: `53e879cf..17395e4d` (merge-base com a develop), um commit, dois arquivos. `CHANGELOG.md` ganha 2 linhas e troca 1: a linha do anexo (`CHANGELOG.md:24`) e a linha do #908 (`CHANGELOG.md:26`). O fragmento `changelog.d/v0481-fixtures-gerada.md` é apagado.

Gatilhos: nenhum no diff, que é só nota de versão. A versão inteira, com gatilho, está em `docs/security/release-0.47.19.md`, renovado neste head para 19 itens.

## Detalhe
- **Junção:** a linha nova `CHANGELOG.md:26` é idêntica à linha 2 do fragmento apagado. `git diff 53e879cf 17395e4d -- CHANGELOG.md` não tem nenhuma linha `-` fora da troca da linha do anexo, então nenhuma linha da marca nem do 1º anexo sai.
- **Linha do anexo** (`CHANGELOG.md:24`): diz "os 9 itens", lista #875, #878, #888, #901, #902, #903, #904, #906 e #908 e cita E12.26, E12.27 e E12.40. Bate com os 9 fragmentos juntados nos dois anexos.
- **Versão igual:** `0.47.19` em `.claude-plugin/plugin.json:3` e em `dev/.claude-plugin/plugin.json:3`, igual a `CHANGELOG.md:7`. `bin/forge-changelog conferir-release` dá `ok: changelog.d/ sem fragmentos pendentes` (só o `README.md` fica na pasta).
- **Segredos:** os padrões de token do GitHub, chave da Anthropic, chave da AWS, chave privada e token do Slack dão 0 nas linhas novas.

## O que aperta, o neutro e o que afrouxa
- **Aperta:** nada.
- **Neutro:** o diff inteiro. É texto de nota de versão e não mexe em controle, hook, teste, invariante nem manifesto. Ele também tira a pendência que fazia `scripts/promover-homolog.py --conferir-ref` recusar o `53e879cf`.
- **Afrouxa:** nada.

A classificação dos 19 itens da versão, inclusive o #908 que este anexo leva às notas, está em `docs/security/release-0.47.19.md`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. gitleaks, osv-scanner, semgrep, zizmor, actionlint e trivy estão fora do PATH (lacuna). O diff são três linhas de texto, lidas por inteiro, e a busca de segredos foi feita por padrões.

Rodei no head só o que foi tocado: `python3 -m unittest tests.test_changelog tests.test_indice_fixtures` (101 testes, OK) e `conferir-release`. A suíte inteira vale pelo CI.

- ci: 17395e4d905fdbf24bbe21451050873b77261ba6 verde

CI no head `17395e4d` (runs 45834666619 e 45834666443): as 10 partes da suíte (3.12 e 3.14), `bateria`, `bateria (pareceres)`, `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, os dois `teto de pulados`, `instalação`, `árvore já provada` e a `catraca` estão verdes, sem vermelho.
