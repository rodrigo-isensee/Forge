---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-release-04719-anexo
commit: da7b59be13063ef51235c1e82f53bfda493cc25f
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (anexo da 0.47.19, E12.30, #907)

Escopo: `git diff --name-status 8ae4d6c6 da7b59be` (merge-base com a develop igual ao Base-sha) toca 9 arquivos, só metadado de versão: `CHANGELOG.md` (15 linhas novas na seção `[0.47.19]`, nenhuma removida) e a remoção dos 8 fragmentos `changelog.d/v0481-*.md` juntados (#875, #878, #888, #901, #902, #903, #904, #906). Os commits são `75b363ad` (E12.26, 7 itens), o merge limpo da develop `25b6e76e` e `da7b59be` (E12.27, o #906). Nenhum código, hook, `bin/`, `scripts/`, `.githooks/`, `.github/`, teste, `tests/config.json` nem manifesto; os dois `plugin.json` seguem em `0.47.19`.

Gatilhos: nenhum

## Detalhe dos achados
Sem achados de segurança.

- **Leitura.** As 14 linhas dos 8 fragmentos apagados estão idênticas na seção `[0.47.19]` (comparação por script: a única linha nova sem fragmento apagado é a do próprio anexo, `CHANGELOG.md:24`). Sem segredo: busca por padrões de token do GitHub, chave da Anthropic, chave da AWS, chave privada e token do Slack nas linhas novas dá 0. Sem comando novo.
- **O que aperta, o neutro e o que afrouxa (do anexo):** o anexo em si é neutro, porque só move texto de fragmento para o CHANGELOG e não muda nenhum controle. Os 8 itens que ele descreve têm título `[afrouxa-regra: ...]`, e a classificação de cada um, com o aceite do dono, está em `docs/security/release-0.47.19.md`. Ali está escrito, item a item, o que aperta, o que é neutro e o que afrouxa.
- **Texto, fora do meu domínio:** a linha do anexo (`CHANGELOG.md:24`) diz "os 7 itens" e não cita o #906, anexado depois em `CHANGELOG.md:36`. Isso não tem efeito de segurança, e o review já a apontou (A1 de `docs/reviews/v0481-release-04719-anexo.md`).
- **Conferência.** `bin/forge-changelog conferir-release`: `ok: changelog.d/ sem fragmentos pendentes`; `python3 -m unittest tests.test_changelog`: 91 testes, OK. A develop não andou depois de `8ae4d6c6`.

## Riscos aceitos e ferramentas
Sem riscos aceitos. Revisão estática com git e com a API do GitHub (só leitura). gitleaks, osv-scanner, semgrep, zizmor e actionlint estão fora do PATH (lacuna registrada; o diff é só texto de versão, lido por inteiro). Não rodei a suíte local: o brief pede só os testes dos arquivos tocados. O CI do PR valida.

CI no head exato:
- run 45824721639 (CI): ficou `cancelled` porque o envio do parecer de review (`80cd983c`) começou outro run;
- verdes antes do cancelamento: `bateria (pareceres)`, `bateria (passos)`, `bateria (verificações longas)`, `instalação (python 3.14)` e `árvore já provada na develop`;
- Catraca: runs 45824721537 e 45824911476 em `success`;
- as 10 partes da suíte não chegaram a concluir nesse run.
