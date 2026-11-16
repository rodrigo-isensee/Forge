---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-jargao-id-duas-letras
commit: cf59506c11d7ff03caa4418ef9e984e7f5f9ed82
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047-jargao-id-duas-letras

Parecer completo (não havia parecer anterior) da etapa E2.373, sobre o head cf59506c, base 1b88640e. O diff toca quatro arquivos: `hooks/meta.py:144` (o padrão da classe `regra` passa de três para duas ou mais letras), `tests/test_meta.py:195-198` (fixture nova), `tests/mutantes/v047-jargao-id-duas-letras.json` (M1 e M2) e o fragmento `changelog.d/v047-jargao-id-duas-letras.md`.

## Gatilhos
`R-SEGURANCA`: a entrega toca um hook (o de fim de resposta, `hooks/meta.py`). O trecho mudado é uma medida que só conta e grava em `mensagens.jsonl` do diretório da execução; não decide, não bloqueia e não executa nada (`hooks/meta.py:190-198`). Nenhum controle de acesso, segredo, CI, envio ou escrita fora da pasta da execução muda.

Análise pela matriz de dimensões (analisador de texto livre):
- Mecanismo e posição: expressão regular de um quantificador só, `R-[A-Z]{2,}`, entre lookbehind e lookahead fixos de um caractere; sem aninhamento nem alternância, logo sem retrocesso catastrófico.
- Tamanho: a entrada já vem cortada no `TETO_DA_MEDIDA` antes da conta (`hooks/meta.py:192`); sondas abaixo mostram custo linear mesmo acima do teto.
- Fronteiras: `xR-QA`, `R-QA-X`, `R-QA_` não contam; `R-QA.` e `(R-QA)` contam; `R-QÁ` e `R-Qa` não contam; `R-X` (uma letra) não conta. Corresponde ao pedido (E2.351).
- Sobreposição com outras classes: a classe `cartao` exige duas maiúsculas antes do hífen, então `R-QA` não é contado duas vezes.
- Saída: o registro guarda só a contagem por classe, nunca o termo (`hooks/meta.py:175`), então a mudança não passa a gravar texto da mensagem.
- Pior caso de abuso: quem escreve a mensagem é o próprio agente; inflar ou esconder a contagem só altera um aviso, sem efeito em portão. Sem caminho de ataque realista.

PA-7 conferido: AR-5 (sem novo caminho que decide), AR-12 (as specs M1 e M2 citam o texto do head, `R-[A-Z]{2,}(?![\w-])`, presente uma vez em `hooks/meta.py:144`), AR-1 (as duas mutações relevantes do quantificador, para 3 e para 1, estão listadas); os demais não se aplicam ao diff.

## Achados

## Sondas

## Detalhe dos achados
Sem achados. Sondas executadas (não provam bloqueante, por isso fora do bloco `## Sondas`): entrada de 200.002 caracteres `R-` seguido de maiúsculas, 0,0 s; 50.000 ocorrências de `R-QA `, 0,08 s, 50.000 contagens; 100.003 caracteres terminados em hífen, 0,02 s, 0 contagens. Testes do módulo do item no clone: 16 testes, OK.

## Riscos aceitos e ferramentas
Sem riscos aceitos. Ferramentas: leitura do diff, o executor de testes da stack no módulo `tests.test_meta` e sondas locais do padrão. A suíte inteira roda no CI do PR (não citado aqui por não existir ainda no head); o portão de merge confere o CI verde. Varredura de segredos, de dependências e de workflow não se aplicam ao diff (nenhum segredo, dependência ou workflow tocado).
