---
tipo: review
contrato: 1
pedido: versao-034
branch: melhoria/lote-estoque-a
commit: f99351a624c15b4956526d2b8de8d3efdef8432a
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-05
---
# Review da junção: lote-estoque-a (E2.2, versao-034, E7)

Escopo: os 12 commits de primeiro pai entre a base d9b26bb e f99351a (11 merges item a item e 1 commit de teste). Não revi de novo o que cada item já teve aprovado no próprio parecer; li a resolução dos conflitos (`git show --remerge-diff`), o commit que não é merge e o que cada item trouxe para a base.

## Itens
- achado-teto-doc (fe97010): entrou; sem conflito; security-engineer e qa-engineer dizem o teto de 300 do achado.
- invariante-gatilho (adcaec8): entrou; sem conflito; o modelo de pedido ganha a etapa de segurança para invariante novo.
- modelos-parecer-avisos-2 (cca1026): entrou; sem conflito; só os modelos de parecer e teste.
- pergunta-maior-menor (1762bb7): entrou; sem conflito na junção; mantém "a mais barata das duas com número".
- permissao-agentes-md (421ef63): entrou; sem conflito; é a redação refinada que vale.
- textos-034 (7759b69): entrou com conflito em 4 arquivos; a branch repetia a redação antiga dos três itens acima; resolvido ficando com a redação refinada, ver abaixo.
- aq1-texto-v2 (59f80f3): entrou; sem conflito.
- aq3-texto-v2 (3b2fb5c): conflito em `tests/test_forge.py` (as classes de teste das duas branches, adicionadas no mesmo ponto); resolvido mantendo as duas, com duas linhas em branco entre elas.
- pareceres-033 (42b1741): entrou; só pareceres, sem conflito.
- f22-release-v2 (ccd8fe6): entrou; sem conflito; o merge interno 871afb6 ("traz a develop") não acrescenta nada à base: o diff da base até o head não toca `bin/forge-check`, `hooks/` nem `.github/`.
- fechar-esperar-rotulo (326ad8e): entrou; sem conflito; único item que toca `bin/` (`bin/forge-fechar`, mensagem do rótulo com o gatilho e a dica); tem mutantes e parecer de segurança próprios.

## Resolução dos conflitos (textos-034)
- `agents/qa-engineer.md`: ficou a linha de teste e parecer em commits separados (da permissao-agentes-md) mais a linha de achados com o teto de 300 (da textos-034). Sem perda: as duas ideias estão no arquivo, uma vez cada.
- `skills/modo-iniciante/SKILL.md`: ficou "a mais barata das duas com número" (refinado); a versão "das três" foi descartada, e o teste de pergunta-maior-menor a afirma.
- `skills/trabalho-em-paralelo/SKILL.md`: ficou a delegação de `agents/*.md` refinada (avisa só se a regra de permissão não estiver aplicada); a antiga saiu.
- `templates/projeto/docs/pedidos/_modelo.md`: ficou a linha da etapa de segurança refinada ("no Forge, inclusive quando prevê invariante novo"); a antiga saiu.
- Sem marcador de conflito residual nos cinco arquivos tocados; busca pelas frases antigas em `agents/`, `skills/`, `templates/`, `tests/` e `docs/regras/` não acha nenhuma.
- `tests/test_textos_034.py:52` (commit f99351a, o único que não é merge): a asserção trocou a frase antiga pelo texto refinado. Troca correta: o teste passou a conferir a redação que ficou, e o trecho vizinho (a proibição de contornar por script, citada pelo ID `R-CONFORMIDADE`) segue afirmado. Uma linha de teste, sem lógica.

## Testes rodados (só os módulos tocados pela resolução e pelos itens)
test_textos_034 (6), test_permissao_agentes_md (1), test_invariante_gatilho (1), test_pergunta_maior_menor (1), test_achado_teto_doc (1), test_aq1_texto (6), test_modelos_parecer_avisos_2 (2), test_guarda_conferente (20), test_fechar (92) e, em test_forge, as classes TextosAQ3*, PrMescladoPeloHead e EntregaAtoGithub (18): todos OK. A suíte inteira fica com o QA do lote (E2.5).

## Sobreposição entre itens
- O teto de 300 do achado é afirmado em dois testes (`tests/test_achado_teto_doc.py` e `tests/test_textos_034.py:43`): duplicação inofensiva, ambos verdes.
- Nenhuma contradição de texto restante entre os itens; as redações antigas que a textos-034 trazia saíram.
- Teto por PR (M14): o lote junta itens já aprovados um a um, e o código está só em `bin/forge-fechar` (+11, -4); fora esse arquivo, o resto é texto, teste e parecer.
- A árvore de trabalho tem 12 mudanças no índice, não commitadas (remoção dos fragmentos de `changelog.d/` dos itens e `changelog.d/lote-estoque-a.md` novo): não fazem parte do commit revisado e não as toquei; o autor da junção as commita antes do envio.

## Achados
- A1 (recomendado) tests/test_textos_034.py:43 · o teto de 300 do achado já é afirmado em tests/test_achado_teto_doc.py; deixar um dos dois testes quando houver outra passada nesses arquivos.
- A2 (recomendado) changelog.d/lote-estoque-a.md:1 · consolidação dos fragmentos está só no índice da worktree; commitar no lote antes do push, em commit próprio, para o PR não sair sem fragmento.

## Parecer
Aprovado. A resolução dos quatro conflitos de texto e a do conflito de teste preservam a redação refinada de cada item, sem marcador residual e com os testes dos arquivos tocados verdes. As recomendações A1 e A2 não devolvem.
