---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-ci-descendente-parecer
commit: 523b0065035b3e0ce068d94360966ce20ed1c4d4
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: v0481 E8.21 (2ª volta do #895 por delta, de aa26249f a 523b0065)

## Gatilhos
Gatilhos: controle do Forge (portão `forge-check pr`, PARECER-LE-O-CI), analisador de caminhos do diff

- ci: 523b0065035b3e0ce068d94360966ce20ed1c4d4 verde

## Achados

## Sondas

## Delta lido
`git diff aa26249f..523b0065`: o commit `f8839529` (E8.18) muda uma linha em `skills/engineering-practices/SKILL.md:54` e uma em `skills/qa-testing/SKILL.md:46`. Os merges `fc029f85` e `523b0065` trazem a develop até `6cc4cd5a`, sem resolução de conflito (`git show --remerge-diff` vazio nos dois). O `forge-check parecer delta` lista `bin/forge-check`, mas essa mudança vem da develop (#874). A parte da branch em `bin/forge-check`, `tests/test_forge_check_pr.py`, `tests/test_pre_envio_brief.py`, `tests/mutantes/` e no fragmento do changelog é igual, linha a linha, à que foi revisada no `aa26249f` (diff `eeb81062..aa26249f` contra `6cc4cd5a..523b0065`). Entre `aa26249f` e `523b0065`, `tests/config.json`, `tests/fixtures/metricas-texto.json`, `tests/test_metricas_texto.py` e `tests/test_orcamento_instrucao.py` não mudam.

## Achados anteriores
- A1 (bloqueante): corrigido no `aa26249f` e sem mudança desde então.
- A2 (bloqueante): corrigido no `aa26249f` e sem mudança desde então.
- A3 (bloqueante): **corrigido.** `python3 -m unittest tests.test_metricas_texto tests.test_orcamento_instrucao` deu 10 OK no `523b0065`. No CI do head, a suíte parte 1/5 passa em 3.12 e em 3.14. Nenhum teto foi mexido: os arquivos de tetos e os testes são os mesmos do `aa26249f`.

## Detalhe dos achados
Sem achado novo.

- **O que aperta:** nada novo neste delta.
- **O que é neutro:** o texto das duas skills. Os trechos de `invariantes` (`tests/config.json`) casam por regex no `aa26249f` e no `523b0065`, 10 de 10 em engineering-practices e 12 de 12 em qa-testing. Saíram de engineering-practices "o review lê o CI do head", "o merge exige todos" e "cujo diff toca apenas pareceres". A forma da linha e as três checagens de fora continuam no texto. A exigência do merge segue no `forge-check` (`bin/forge-check:2176`) e na proteção da branch, e a regra das três pastas segue no código (`PASTAS_DOS_PARECERES`, `bin/forge-check:2189-2199`) e no teste. O texto da skill não decide nada: quem barra é o portão.
- **O que afrouxa:** nada além do `via` já descrito nas rodadas anteriores e aceito pelo dono em 25/11 07:27.
- **CI do #895 no `523b0065`** (runs 45696404571 e 45696404450, `headSha` conferido): passam as dez partes da suíte (3.12 e 3.14), `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, a instalação, o teto de pulados e a árvore provada. Três checagens falham, todas por espera. `bateria (pareceres)` falha por R-REVIEW e R-QA, porque os pareceres ainda não são aprovados no head. `bateria` falha só porque `pareceres: failure` (as outras partes estão em `success`). A `catraca` falha por R-CONFORMIDADE ("mudança em bin/forge-check"), porque o rótulo `afrouxa-regra` tem de ser aplicado pelo dono depois do último push.
- **PA-7:** nenhum dos AR-1 a AR-12 se aplica a uma mudança só de texto de skill. Para o AR-9, o texto novo não cita limite numérico.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Usei git, a biblioteca padrão e o `gh`, só para ler checks e logs. Não usei gitleaks nem osv-scanner, porque o delta não traz segredo nem dependência.
