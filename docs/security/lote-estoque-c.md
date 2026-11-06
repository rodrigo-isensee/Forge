---
tipo: revisao-seguranca
contrato: 1
pedido: versao-034
branch: melhoria/lote-estoque-c
commit: f11234dffd10cdf566a5a22d43210edf595229ad
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-05
---
# Review de segurança: lote-estoque-c (junção do lote C do E7)

Escopo (E2.3): a junção em `melhoria/lote-estoque-c` de d9b26bb a f11234d, isto é, a resolução de conflitos e o que a soma dos 7 itens muda nos gatilhos. Cada item segue com o próprio parecer; aqui não se revê de novo o que ele já teve aprovado.

## Gatilhos
R-SEGURANCA: hooks (`hooks/parecer.py`, `hooks/doutor.py`) e controles do Forge (`bin/forge-testes`, de que o `.githooks/pre-push` tira o plano dirigido; `bin/forge-doutor`). Sem mudança em `.github/`, `.githooks/` nem `tests/config.json`.

Junção: os 7 merges (a93a38e, def197c, 0e0a91d, dc5f542, 289da2d, e6fd0fb, 14c5dea) têm `git show --remerge-diff` vazio, ou seja, nenhum conflito resolvido à mão. Os dois commits que não são merge: e17d07a (mapa FORGE_CHECK de `bin/forge-testes` ganha `test_qa_doutor_034`, contagem em `tests/test_testes_tocados.py` passa a 40; só amplia o que roda) e f11234d (fragmentos de `changelog.d/` juntados num só; só texto).

Por item que toca a área:
- forge-testes-filtro-k: `-k` só vale por linha de comando; o pre-push chama `bin/forge-testes --base` sem `-k`, então o plano do pre-push não muda.
- forge-testes-aviso-mapa: avisos vão a stderr, que o pre-push descarta no `--listar` (só lê a primeira linha de stdout); exceção fora de RuntimeError faz o script falhar, e o pre-push cai na suíte inteira ou recusa (falha fechada).
- forge-testes-sem-mapa: o atalho só vale com CAMINHO explícito; o pre-push não passa caminho.
- Soma dos três em `bin/forge-testes`: a branch que muda `bin/forge-testes` não se autojulga, o pre-push confere o diff (`.githooks/pre-push:312`) e roda a suíte inteira; este lote, portanto, sobe com a suíte inteira.
- doutor-034 (`hooks/doutor.py`): aviso de versão uma vez por versão e `OSError` do relógio contido; aviso consultivo, nenhuma recusa afrouxada.
- doutor-f8-caminho (`bin/forge-doutor`): só o texto do aviso de proteção de branch muda (cita o guia que existe); a conferência da proteção é a mesma.
- lote-fechar2-guardas-v2: só testes e spec de mutantes, sem código de produção.
- hook-parecer-034 (`hooks/parecer.py`): muda o texto das recusas e acrescenta uma recusa mais específica antes da existente no ramo do `ValueError`; as duas saem por `bloquear` (saída 2), nenhum caminho que recusava passou a liberar. Os corpus `atualiza-*` só fixam em teste o comportamento que já existia.

## Achados
- A1 (recomendado) bin/forge-testes:627 · `-k` filtra o comando, mas `anotar` grava em `.forge/run/testes.log` o modo e os módulos sem o filtro; hoje nenhum portão lê o log, então é só clareza: anotar os filtros na linha.

## Detalhe dos achados
A1: evidência `bin/forge-testes:627` (filtro somado ao comando) e `bin/forge-testes:247` (linha do log sem os filtros). Caminho de ataque: nenhum hoje, porque o log só é escrito (`bin/forge-testes`, `bin/forge-mutante`) e não é lido por portão; se um portão futuro tomar a linha `modo=completo saida=0` como prova, uma rodada com `-k` passaria por suíte inteira. Severidade: informativa. Correção mínima: acrescentar `filtros=` à linha de `anotar`. Esforço: P. Dono: forge:tech-lead (autor da junção), em item próprio; não devolve esta junção.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Análise estática do diff da junção e do `--remerge-diff` de cada merge; testes dos 8 módulos tocados rodados localmente em árvore igual a f11234d fora de docs/reviews: 256 testes, OK. Faltam no PATH: gitleaks, semgrep, osv-scanner, zizmor, actionlint, trivy (lacuna registrada; o diff não traz dependência nem workflow, e não traz segredo à leitura).
