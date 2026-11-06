---
tipo: revisao-seguranca
contrato: 1
pedido: versao-033
branch: melhoria/ci-comentario-rapida
commit: 4135cde473cb64838e0eeb8f593343adb6ddc50a
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-04
---
# Review de segurança: ci-comentario-rapida

Aprovado, sem achado. Revisão estática de `c481b78..4135cde` (código em `8bcc469`), branch empilhada em `melhoria/ci-ubuntu-26`, cujo parecer é `docs/security/ci-ubuntu-26.md`. Em `.github/workflows/ci.yml` muda só o comentário do topo (`:3-8`). Nenhuma linha executável, `if:`, `permissions:`, `uses:` ou `runs-on:` mudou. Também entram um teste novo em `tests/test_ci_local.py` e um fragmento de changelog.

## Gatilhos
`R-SEGURANCA`: mudança em `.github/workflows/` (só comentário). Não toca segredo, dado pessoal, dependência nem controle do Forge.

## Verificações
- **Fidelidade do comentário ao controle:** o texto novo diz três coisas, e as três batem com o código. O push na develop roda só o job `rapida`, porque os outros jobs têm `if:` que exclui esse evento (`ci.yml:45` e `:76`), a catraca só reage a `pull_request` e o release só à main. O `rapida` roda `scripts/suite-paralela.py` (`:37`) no Python 3.12 (`:35`). Homolog e main rodam a bateria completa. Um comentário falso sobre o que um controle cobre levaria o revisor a supor cobertura que não existe. Aqui o texto ficou mais preciso, não menos.
- **SHAs e permissions:** iguais aos de `c481b78`. As 11 ocorrências de `uses:` seguem fixadas por SHA de 40 caracteres, e nenhuma `permissions:` mudou.
- **Controles que deixaram de rodar:** nenhum. Não há mudança executável.
- **Teste novo** (`tests/test_ci_local.py:130-137`): é só leitura do arquivo, sem rede nem processo. Ele confere o comentário e confirma que um passo do `rapida` roda o script citado, o que amarra o texto ao código.

## Achados

## Detalhe dos achados
Nenhum achado. Os achados A1 a A3 de `docs/security/ci-ubuntu-26.md` (passo `env -a` no 26.04, `sha256sum` do uutils, `python3` da imagem) valem para esta branch também, porque ela contém aquela. Não se repetem aqui.

## Riscos aceitos e ferramentas
Nenhum risco aceito.
- Rodado: `python3 -I -m unittest discover -s tests -p test_ci_local.py` em `4135cde`: 54 testes, OK.
- Feito à mão: leitura do diff e grep dos `uses:` sem SHA (nenhum).
- Lacunas: `actionlint`, `zizmor` e `gitleaks` não estão no PATH desta máquina. Não foram rodados aqui, e o job `bateria` do PR roda os dois primeiros.
