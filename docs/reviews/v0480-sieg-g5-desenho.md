---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-sieg-g5-desenho
commit: dc706f6d923a9c9ee4f24fd56dc4a4417b926982
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 · desenho do SIEG-G5 (decisão ao dono em formato fixo), revalidação E135.7

Revalidação por delta da volta E135.5, no head dc706f6d, desde acf0b227 (parecer anterior: 2b4a4453, reprovado por A1 e A2). Delta lido: `forge-check parecer delta docs/reviews/v0480-sieg-g5-desenho.md`, intervalo acf0b227..dc706f6d, no domínio só `docs/propostas/sieg-g5-decisao-formato-fixo.md`. Só texto: sem código, guarda nem mutante; sem suíte local (o CI do PR a roda).

## Achados
- A5 (recomendado) docs/propostas/sieg-g5-decisao-formato-fixo.md:46 · a DECISÃO DO DONO 21/11 20:54 está na linha 719 de `docs/pedidos/v0478.md`, não na 717; e esse arquivo, como o insumo da linha 48, vive em `~/.forge-contrib/docs`, fora do repositório: cite o caminho fora da árvore ou o texto.
- A6 (recomendado) docs/propostas/sieg-g5-decisao-formato-fixo.md:49 · `hooks/conformidade.py:1954` no head é `checar_remocao`, não a gramática de leitura (o insumo foi lido noutra versão); a chamada de `fora_da_gramatica_de_leitura` está em `:2217`. O brief do T3 deve citar o lugar atual.

## Revalidação de A1 a A4 (parecer 2b4a4453)
- A1 resolvido: linhas 5-6 e 46-55 declaram "Trava nova: sim (F1 a F4 e F6)" e nomeiam a que sai, a T3 do insumo de corte (conferida: seção T3, risco baixo, primeira da ordem sugerida). A troca afrouxa e vai ao dono (linha 96), com PR próprio e rótulo `afrouxa-regra`; o C1 fica preso ao merge do T3 (linhas 54-55 e 77). O "regra 3 vale mesmo assim" (linha 53) é a saída que o parecer anterior aceitou.
- A2 resolvido: a régua passa a ser `fora_do_formato` do C3 (linha 73), que vê `A)` e `Na)` e tem caso com o texto da sonda S1; C0 usa essa régua e vem depois do C3 (linhas 74 e 77); a reversão (linhas 92-93) mede com a mesma régua.
- A3 resolvido: linhas 57-62 dizem a direção (o hook importa de `bin/forge_dono.py` pelo caminho `PLUGIN / "bin"`, o bin não importa do hook), com o precedente `hooks/doutor.py:106` (conferido: `sys.path.insert(0, str(PLUGIN / "bin"))` e `import forge_versoes`) e o oráculo do teto único; o import vai ao security-engineer (linha 79).
- A4 resolvido: o pronto do C2 (linha 76) traz a frase exata, os arquivos e as linhas, e o `grep -cF` que dá 1 em cada.

## Leitura
- Provas novas do delta conferidas no head: `bin/forge_transcricao.py:255` é o `RE_OPCAO` com `[A-F]`; `hooks/_comum.py:689` é `fora_da_gramatica_de_leitura`; `hooks/meta.py:40` é `TETO_DA_MENSAGEM = 1200`. O `\b1200\b` do oráculo não casa hoje em `bin/forge-check` (só `120000` e `5 << 20`), então o teste nasce verde só se o C1 não duplicar o número.
- A linha "`decisoes --resposta`" saiu da tabela do existente; a porta segue citada na linha 44. Sem perda.
- Changelog: o delta não toca o fragmento em `changelog.d/`; nada no `CHANGELOG.md`.
- Afrouxa: a proposta não; a troca T3 sim, declarada e levada ao dono. Neutralidade sem termo de projeto.

## Parecer
Aprovado. A1 a A4 resolvidos no texto. A5 e A6 são citações a acertar e viram cartão depois do merge (ou entram no brief do T3).
