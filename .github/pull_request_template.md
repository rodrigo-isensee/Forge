## Projeto de origem
<!-- OBRIGATÓRIA (a catraca barra o PR sem ela): mínimo de 20 caracteres fora de comentários. Tipo/identificador genérico do projeto; sem nomes, regras de negócio ou código dele. -->

## Situação observada
<!-- O problema na fábrica, descrito sem dados do projeto. -->

## O que muda
<!-- Arquivos e comportamento, em poucas linhas. -->

## Como medir
<!-- OBRIGATÓRIA (a catraca barra o PR sem ela): mínimo de 20 caracteres fora de comentários. Como saber se melhorou (ver docs/melhoria-continua.md). -->

## Sem teste
<!-- Só quando o `forge-check pr` dá `sem teste:` (T1): por que o código mudou sem teste mudado ou novo; o review confere. Sem o aviso, apague a seção. -->

## Checklist
- [ ] `python3 -m unittest discover -s tests -v` verde
- [ ] `claude plugin validate . --strict` verde
- [ ] `scripts/verificar-contribuicao.sh` sem achados
- [ ] Fragmento novo em `changelog.d/` (`bin/forge-changelog novo`; versão não alterada, `CHANGELOG.md` intocado)
- [ ] Neutralidade: nada do projeto de origem; sem afrouxar `tests/config.json` (ou destacado no título)
- [ ] Rótulo `afrouxa-regra` pedido ao dono (marque só se a mudança afrouxa regra protegida; o dono aplica o rótulo)

Rótulo: <linha DECISÃO DO DONO que cobre o afrouxamento | sem afrouxamento real (catraca)>
<!-- Na promoção, a catraca lista os PRs rotulados da leva com esta linha como "decisão declarada no corpo": ela confere só o rótulo do dono, não a decisão (ADR 0008). -->
