## Projeto de origem
<!-- OBRIGATÓRIA (a catraca barra o PR sem ela): mínimo de 20 caracteres fora de comentários. Tipo/identificador genérico do projeto; sem nomes, regras de negócio ou código dele. -->

## Situação observada
<!-- O problema na fábrica, descrito sem dados do projeto. -->

## O que muda
<!-- Arquivos e comportamento, em poucas linhas. -->

## Como medir
<!-- OBRIGATÓRIA (a catraca barra o PR sem ela): mínimo de 20 caracteres fora de comentários. Como saber se melhorou (ver docs/melhoria-continua.md). -->

## Checklist
- [ ] `python3 -m unittest discover -s tests -v` verde
- [ ] `claude plugin validate . --strict` verde
- [ ] `scripts/verificar-contribuicao.sh` sem achados
- [ ] Linha nova em `## [Não publicado]` do CHANGELOG (versão não alterada)
- [ ] Neutralidade: nada do projeto de origem; sem afrouxar `tests/config.json` (ou destacado no título)
