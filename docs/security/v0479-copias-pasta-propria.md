---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-copias-pasta-propria
commit: 38182111f20ad008e7db51910ef24e80f4d988c3
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478 (E78.6, revalidação das cópias do projeto em pasta própria)

Volta por delta sobre o parecer de 48a6e19b (commit 7f7d9c57). Delta lido (`forge-check parecer delta`, 48a6e19b..38182111): no domínio só `bin/forge-copia` (`ignorar_no_projeto` e a chamada em `main`); fora do domínio, `tests/test_forge_copia.py` (lido por ser a correção de A2), mutantes e changelog. A conferência da rodada anterior (limpeza presa à `raiz()`, sujeira e fim do item, detecção projeto/Forge, sandbox sem escrita nova) fica no git e não muda: o resto do arquivo não foi tocado.

## Gatilhos
Gatilhos: remoção de arquivos (limpeza de cópias), limite de escrita do sandbox, detecção de contexto Forge/projeto.

## Conferências
- **A1 (corrigido).** `bin/forge-copia:59` recusa `.gitignore` que é link (rc 2, antes de clonar) e `bin/forge-copia:62` cria com `O_CREAT|O_EXCL|O_NOFOLLOW`; um link plantado entre a checagem e o `open` cai em `FileExistsError` e nada é escrito pelo link. A pasta mãe por link (`.forge/wt` ou `.forge`) já é recusada antes, em `destino_dentro`, porque a chamada (`bin/forge-copia:247`) vem depois dela.
- **A2 (corrigido).** `tests/test_forge_copia.py:577` (S1) e `:585` (S2) cobrem os dois casos de abuso; `python3 -m unittest tests.test_forge_copia.Projeto`: 9 testes OK no head.
- **Sondas refeitas no head** (pasta temporária, `HOME` falso, sem rede): S1 `.forge/wt` link para `~/.forge-contrib/wt` → rc 2 "o destino fica fora de", pasta do home vazia. S2 `.gitignore` link solto → rc 2 "é um link simbólico", alvo não criado, cópia não criada. S2b `.gitignore` link para arquivo existente → rc 2, alvo intacto. S6 `.forge` inteiro como link → rc 2, alvo vazio. Legítimos: sem `.gitignore` → rc 0 e `*`; `.gitignore` regular existente → rc 0, conteúdo mantido.
- CI: nenhum run da branch até este parecer; a suíte inteira fica para o CI do PR (portão do merge).

## Sondas

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas de varredura de segredo, SAST e dependências ausentes do PATH nesta estação (lacuna registrada; o delta não traz dependência nem segredo).
