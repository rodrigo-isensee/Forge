---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-k170-movimento
commit: 0000c1bfedc51ec787fc29791f385e85b33bf3e4
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0479-k170-movimento (K170, E77.3)

Escopo lido: `git diff 5e3ca873..0000c1bf` (bin/forge-check, changelog.d/v0479-k170-movimento.md, tests/mutantes/v0478-k170-movimento.json, tests/test_sobreposicao_quadro.py).

## Gatilhos
Gatilhos: controle do Forge (bin/forge-check, recusa nova no `movimento`).

Confirmação: só aperta. A mudança acrescenta uma recusa (rc 2, nada gravado) em `cmd_movimento` (bin/forge-check:5042) antes de qualquer escrita; nenhuma recusa existente sai nem afrouxa, o caminho de rc 1 dos erros de uso segue igual (bin/forge-check:10810-10812), e as origens fora de Bloqueado seguem como antes.

## Achados

## Sondas

## Detalhe dos achados
Sem achado. Pontos conferidos:
- Ordem das guardas: a recusa nova roda depois da validação da coluna contra o KANBAN.md e da recusa de link simbólico (bin/forge-check:5035-5041) e antes de abrir o arquivo para escrita; o teste `test_sem_historico_recusa_e_nao_cria_o_arquivo` prova que nada é criado.
- Leitura do histórico: `movimentos_do_cartao` usa `_ler_tabela` (abre com `O_NOFOLLOW` e teto de bytes, bin/forge-check:5779-5799); arquivo ausente, link ou acima do teto dão lista vazia e a recusa sai (falha fechada).
- Variações do `--de` (sonda local, sem gravar): `"Bloqueado "`, `BLOQUEADO` e `Bloquéado` dão rc 2; `Bloqueado` com U+200B e `Ｂloqueado` (largura cheia) dão rc 1 (coluna fora do quadro). Não há forma de dizer Bloqueado que passe pela validação da coluna e escape da recusa.
- Saída: cartão, `--de` e as colunas do último movimento saem por `nome_seguro` (bin/forge-check:4808-4810); nome com quebra de linha ou aspas não imita outra linha.
- Testes: `python3 -m unittest tests.test_sobreposicao_quadro.MovimentoDeBloqueado` com 4 testes OK neste head; os mutantes M1 a M6 cobrem cada guarda. A suíte inteira fica com o CI do PR.

Limite do controle (não é achado): quem escreve `docs/kanban/historico.md` à mão pode forjar a linha de entrada; a recusa é guarda de processo, não de integridade, e o desenho do `movimento` já é assim.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, teste da classe nova e sondas locais em pasta temporária; nenhuma varredura externa.
