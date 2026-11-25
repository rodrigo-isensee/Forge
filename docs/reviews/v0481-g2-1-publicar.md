---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-g2-1-publicar
commit: c78bfe22110b57436b64bcc2866af1c03542938e
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0481 (E6.18, #878, G2.1: forge-check parecer publicar; classe C), volta por delta

Revalidação por delta da rodada que reprovou em 0048e0c4 (E6.14; texto no git). Delta lido: `forge-check parecer delta` deste arquivo (16 arquivos no domínio) e `git diff 0048e0c4..c78bfe22` (código: `bin/forge_pareceres.py`, `bin/forge-check`, `bin/forge-testes`, `hooks/conformidade.py`; testes, 5 fixtures `contrib-publicar-*` e as specs `-4` a `-6`).

## Achados
- A1 (bloqueante) hooks/conformidade.py:2566 · A trava R-CONTRIB lê a primeira `--raiz` (`parecer.opcao`), e o argparse do forge-check usa a última: com duas `--raiz`, a última no clone do Forge, o publicar libera na sessão de projeto (S1, S2). Use a última `--raiz`, com fixture das duas formas.
- A2 (recomendado) hooks/conformidade.py:113 · Com o programa opaco (`python3 $(command -v forge-check)`), `args_do_forge_check` só reconhece o `anotar` e o `--gravar`, e o publicar com `GH_REPO=<forge>` libera na sessão de projeto (S3). Fora do delta (G1.2): vira cartão; inclua `parecer publicar` na forma opaca.

## Sondas
- S1 · sessão de projeto, `forge-check --raiz=. --raiz ~/.forge-contrib/proj parecer publicar .forge/pareceres/v1/review.md` · espera: código 2, R-CONTRIB · obtido: código 0, sem saída
- S2 · sessão de projeto, `forge-check --raiz . parecer publicar --raiz ~/.forge-contrib/proj .forge/pareceres/v1/review.md` · espera: código 2, R-CONTRIB · obtido: código 0, sem saída
- S3 · sessão de projeto, `GH_REPO=<forge> python3 $(command -v forge-check) parecer publicar .forge/pareceres/v1/review.md` · espera: código 2, R-CONTRIB · obtido: código 0, sem saída

## Achados anteriores
- A1 (bloqueante): corrigido. `bin/forge-mutante --cobertura --base 30dde218` no c78bfe22 não aponta nenhuma condição sem mutante (só `hooks/conformidade.json` e `tests/pesos-d4.json`, que não são código de guarda). As 7 guardas do A1 têm M24 a M28; o M21 foi refeito para o `""`.
- A2 (recomendado): segue como cartão, sem mudança neste delta. O parecer de segurança E6.20 repete a condição de que o G2.2 não entra sem M1.4, M4.1, M4.2, M9.2, M9.3, M10.1 e M18.1.
- A3 (recomendado): corrigido. A recusa depois do PR diz o que já ficou gravado (`já gravado: ...`, `bin/forge_pareceres.py:102`, M30) e o comando a imprime (`bin/forge-check:3784`).
- A4 (recomendado): corrigido (`bin/forge-testes:153`).

## Leitura do delta
- **Como as sondas rodaram:** pela máquina de fixtures de `tests/test_hooks.py` (`Fixture` e `executar_em_lote`), com o `gh` ausente e sem chamada ao GitHub. Que o forge-check usa a última `--raiz` nas duas formas, provei com o mesmo par de parsers de `bin/forge-check:10727-10735` (`parents=[comum]`, `default=SUPPRESS`): `parse_args` dá a última nos dois casos. Barram, como deviam (código 2, R-CONTRIB): `cd ~/.forge-contrib/proj && forge-check parecer publicar`, `export GH_REPO=<forge>; forge-check parecer publicar`, `env GH_REPO=<forge> forge-check parecer publicar` e `forge-check parecer publicar --raiz=~/.forge-contrib/proj`.
- **Agregado em `pending` antes do papel** (`bin/forge_pareceres.py:78-103`): o agregado vai a `pending` antes do status do papel, que só é gravado depois, e o agregado é recalculado no fim. Uma falha em qualquer ponto deixa o mais novo do `pareceres` em `pending` e nunca um `success` velho: falha fechada. Os testes `test_falha_entre_o_papel_e_o_agregado_nao_deixa_success` e `test_falha_antes_do_status_diz_o_que_ficou` usam o `gh` falso com `falha_em` por argumento exato. O `except` só troca o tipo do erro e o relança como `Recusa`, sem engolir nada. O `pending` do agregado sai sem `target_url`, e o teste confere isso (M26).
- **`recusa_do_publicar`** (`bin/forge-check:3751-3754`): a troca de `Path(arquivo) if is_absolute() else raiz / arquivo` por `raiz / arquivo` é equivalente, porque o pathlib descarta a raiz quando `arquivo` é absoluto, e o comentário da linha diz isso. A mudança de `None` para `""` faz o arquivo ausente e o arquivo sem frontmatter caírem na mesma recusa pelo caminho (M21, M28).
- **Trava do hook** (`hooks/conformidade.py:2465`, `2560-2568`): usa a mesma `alvo_do_forge` do `gh_contrib`, com `GH_REPO` da linha ou do `export`, e não afrouxa nada. O defeito está na leitura da `--raiz` (A1); a forma opaca (A2) é anterior ao delta. Do resto, as 5 fixtures e `test_fixtures_do_publicar` (mínimo de 5 e os dois lados, item 11 do checklist) estão corretos.
- **Tamanho (H1):** `teto: excedido, 169 linhas` está declarado no corpo do PR, com o motivo. Aceito: cortar mais deixa um portão vermelho. A correção de A1 e A2 cabe em poucas linhas.
- **Mensagens dos commits:** Conventional Commits em português, com o pedido e a etapa.

## Verificações
- Rodados aqui no c78bfe22: `python3 -m unittest tests.test_forge_pareceres` (35 testes, OK) e `tests.test_hooks.Hooks.test_fixtures_do_publicar` (OK).
- Mutantes: `bin/forge-mutante --processos 1` nas specs `-4`, `-5` e `-6`. M21 a M33 morreram. M21, M24, M25, M27 e M28 morreram por erro do teste sob o mutante, que passa sem ele.
- CI do #878 em andamento na leitura (`catraca` pendente). A suíte inteira não foi rerrodada aqui.

## Parecer
Reprovado por A1: a trava R-CONTRIB que esta volta acrescentou tem um contorno provado, com um só comando na sessão de projeto. Para a volta:
- ler a última `--raiz` da linha;
- uma fixture para S1 e S2 e um mutante por linha de guarda mudada.

O A2 (forma opaca) é anterior ao delta e vira cartão depois do merge.

O resto do delta fecha os achados anteriores e falha fechado.
