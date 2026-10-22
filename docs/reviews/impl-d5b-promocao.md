---
tipo: review
contrato: 1
pedido: impl-d5b-promocao
branch: melhoria/impl-d5b-promocao
commit: ffa8b00957735dd90ac7e318379a6a084766063d
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-22
---
# Review: impl-d5b-promocao

Escopo lido: `git diff c092f1b..ffa8b00` (6 arquivos: `scripts/promover-homolog.py`, `tests/test_promover_homolog.py`, `tests/test_forge.py` classe `GuiaDaPromocao`, `docs/promocao-integrador.md`, `docs/fechamento-integrador.md`, `changelog.d/impl-d5b-promocao.md`), contra o item 22 (PA-5) do refinamento da 0.29.0, a decisão PA-5 "A" do dono (2026-10-19) e a ação 1 da retrospectiva da 0.28.0.

## Achados

## Parecer
Aprovado. O script faz o que o E1 pede e nada além: confere refs (só `develop` → `homolog`; a `main` e qualquer outro par são recusados), pareceres lidos da ref (só os que a promoção traz, modelos `_` e subpastas fora), versão e CHANGELOG com a mesma regra do CI (`scripts/conferir-release.py --so-se-versao-mudou`), abre ou reusa o PR, lê os checks uma vez e só imprime o comando de merge, preso ao head com `--match-head-commit`. Não mescla, não aplica rótulo, não usa `--force` nem `--no-verify` (`R-MAIN`, `R-VERIFY`, `R-FLUXO`). `--dry-run` não faz fetch nem chama o `gh` (provado por teste com remoto à frente). O `gh` falso só vale com `FORGE_PROMOVER_TESTE=1`. Guia com reversão e "Por que o existente não basta", com a evidência medida (50,9 min no #276).

Conferido à parte:
- Leitura dos checks igual à do `bin/forge-fechar` (colunas por tab, estado na 2ª; `catraca` vermelha como pedido de rótulo).
- Promoção não contorna o hook `parecer`: `develop` está em `INTEGRACAO` no `hooks/parecer.py`, então o `gh pr create` de dentro do script cai no mesmo caso isento do comando direto.
- Valores reais: na `develop` (c092f1b) todos os pareceres de `docs/{reviews,qa,security,devops}/` têm `parecer:`; os 4 reprovados que existem já estão iguais na `homolog`, fora do intervalo.

Ferramentas (citadas, não refeitas): numa cópia limpa em `$TMPDIR` do ffa8b00, `python3 -m unittest tests.test_promover_homolog` deu `Ran 25 tests ... OK`; `tests.test_forge.GuiaDaPromocao` e `tests.test_forge.Neutralidade` deram `Ran 3 tests ... OK`; `-k regra_so_na_fonte` deu OK. A suíte inteira roda no `pre-push` deste envio. O Forge não tem `docs/engineering/praticas.md` com regras "ferramenta"; nada a pendurar. Segurança: parecer próprio em `docs/security/impl-d5b-promocao.md` (aprovado, mesmo SHA), não refeito aqui.

Recomendações (não bloqueiam):
- `scripts/promover-homolog.py:227` · o `subprocess.run` do `gh pr create` não tem `timeout`, ao contrário do `git` e das leituras (120 s); um `gh` travado prende o script · sugestão: `timeout=120` com mensagem de "confira no GitHub antes de rodar de novo" (a criação não se repete) · recomendado.
- `scripts/promover-homolog.py:105` · um parecer antigo reprovado que for regravado no intervalo sem virar aprovado trava a promoção (falso vermelho possível, há 4 reprovados históricos na develop) · o fluxo manual segue valendo e o guia já diz que vale o da ref; acompanhar pelo critério de reversão · recomendado.
- Commits: `ada4b61` e `fc545a8` não se revertem sozinhos sobre o HEAD (as voltas `dc33689`, `62f74bc` e `ffa8b00` mexem nos mesmos arquivos; sonda com `git revert --no-commit` num clone em `$TMPDIR`). O item é um só e a `develop` mescla por squash, então vira um commit; o teto da P3 (lote de 6) não se aplica · recomendado.
- `tests/test_promover_homolog.py` ainda fora do mapa do `bin/forge-testes` (cartão D5B-MAPA, já registrado no pedido) · recomendado.
- `tests/test_forge.py:4779` · três linhas em branco antes da classe (o resto do arquivo usa duas) · recomendado.
