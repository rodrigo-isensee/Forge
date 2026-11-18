---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-indice-forge
commit: 7bd4913edcb31af54510071cb86fe53a07087174
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478 (E8.4, índice do Forge)

Escopo lido: o diff `4182a6b9..7bd4913e` inteiro (9 arquivos): `scripts/indice-forge.py`, `docs/indice-forge.md`, `bin/forge-testes` (1 linha do mapa), `tests/test_indice_forge.py`, `tests/test_testes_tocados.py` (lista `AVISOS`), os três `tests/mutantes/v0478-indice-forge*.json` e o fragmento do changelog.

## Gatilhos
Gatilhos: nenhum da lista da R-SEGURANCA (sem auth, dado pessoal, segredo, dependência nova, endpoint, banco, CI, IaC nem controle protegido); toca `bin/` e `scripts/`, que estão em `SENSIVEIS` de `tests/catraca.py`, e nenhum caminho de `PROTEGIDOS`.

## Achados

## Sondas

## Detalhe dos achados
Sem achado. O que foi conferido:

- **Execução e entrada.** `scripts/indice-forge.py` só lê arquivos versionados do próprio repositório (`git ls-files -z`, lista em argumentos, sem shell, `scripts/indice-forge.py:46`) e grava um caminho fixo (`docs/indice-forge.md`, `:115`); `argv` fora de `[]`/`["--conferir"]` sai com rc 2 (`:106`). As variáveis `GIT_*` herdadas são removidas antes do git (`:45`), o que evita que um ambiente de hook aponte o `ls-files` para outro repositório. Sem rede, sem dependência nova (só biblioteca padrão).
- **Código carregado.** O script carrega `bin/forge-testes` como módulo (`:35-38`); o arquivo tem guarda `if __name__ == "__main__"` (`bin/forge-testes:988`), então a carga não executa o `main`, e o mutante do E8.1 guarda isso. A fonte é o próprio repositório, mesma fronteira de confiança de quem roda o script. `ast.parse` só analisa, não executa.
- **Saída Markdown.** Texto de doc vai a uma célula com quebras normalizadas e `|` escapado (`:28-30`) e cortado em 160 caracteres; o conteúdo é a primeira linha de doc de arquivos públicos do repositório, sem segredo. Sem caminho de ataque: quem controla os nomes e docstrings já controla o repositório.
- **Controle de testes.** A linha nova do mapa (`bin/forge-testes:194`) só acrescenta `test_indice_forge` ao plano de `docs/indice-forge.md`; não tira teste de plano nenhum. A lista fechada `AVISOS` (`tests/test_testes_tocados.py:822`) ganha `scripts/indice-forge.py`, justificada: o script chama `planejar` para documentar, não roda teste nem decide portão (conferido no código, `:78-85`). Não afrouxa a guarda: script novo que cite o `forge-testes` sem estar na lista continua reprovando.
- **Prova executada.** `python3 -m unittest tests.test_indice_forge`: 18 testes OK; `scripts/indice-forge.py --conferir`: em dia, rc 0. Suíte inteira: no CI do PR (não rodada aqui, por regra).

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: leitura estática do diff e o teste novo. Lacuna: varredor de segredos e SAST não estão no PATH deste ambiente (não instalados, `R-CUSTO`); o diff não traz credencial nem configuração.
