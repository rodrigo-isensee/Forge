---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-indice-forge
commit: bf97d62a0acbdb143f40c4af560059ab911829c8
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478 (E8.8, índice do Forge, revalidação)

Revalidação por delta (`R-REVIEW`): `forge-check parecer delta` de `7bd4913e..bf97d62a`. No domínio: `bin/forge-testes` e `scripts/indice-forge.py`, lidos inteiros no diff. Fora do domínio (não relidos): `changelog.d/v0478-indice-forge.md`, `docs/indice-forge.md`, `tests/mutantes/v0478-indice-forge-2.json`, `tests/test_indice_forge.py`, `tests/test_testes_tocados.py`. A rodada anterior (aprovado em `7bd4913e`, sem achados) fica no git.

## Gatilhos
Gatilhos: nenhum da lista da R-SEGURANCA; o delta toca `bin/` e `scripts/` (sensíveis em `tests/catraca.py`), nenhum caminho protegido.

## Detalhe
Achados anteriores: nenhum. Sem achado novo. O que o delta muda:

- **`scripts/indice-forge.py`: superfície menor.** Saem a carga de `bin/forge-testes` como módulo (`importlib`, `SourceFileLoader`) e o cálculo da coluna de testes; o script fica com `git ls-files -z` em lista de argumentos, sem shell (`scripts/indice-forge.py:33`), `ast.parse` só de leitura e escrita no caminho fixo (`:86`). Nenhuma execução de código do repositório além do git.
- **`bin/forge-testes`: só acrescenta teste ao plano.** `teste_do_indice` (`bin/forge-testes:311-316`) devolve `{test_indice_forge}` para caminho de primeiro nível de `bin/`, `hooks/` ou `scripts/` (`fullmatch` de `(bin|hooks|scripts)/[^/]+`, `:221`), e só se o módulo existe na raiz; o resultado é unido (`update`, `|=`) ao plano em `planejar` (`:302`) e `planejar_afetados` (`:451`). Não remove módulo, não muda o desvio para a suíte completa (`casou is None` segue antes), não lê entrada externa. Sem caminho de ataque: quem controla o caminho já controla o repositório, e o efeito máximo é rodar um teste a mais.
- **Prova executada.** `python3 -m unittest tests.test_indice_forge`: 19 testes OK; `scripts/indice-forge.py --conferir`: em dia, rc 0; `bin/forge-testes --listar scripts/indice-forge.py`: dirigido com `test_indice_forge`. Suíte inteira: no CI do PR (não rodada aqui, por regra).

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: leitura estática do delta e o teste do índice. Lacuna: varredor de segredos e SAST fora do PATH (não instalados, `R-CUSTO`); o delta não traz credencial, dependência nem configuração.
