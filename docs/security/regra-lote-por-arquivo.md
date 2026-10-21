---
tipo: revisao-seguranca
contrato: 1
pedido: regra-lote-por-arquivo
branch: melhoria/regra-lote-por-arquivo
commit: 6f61294442b6753b27725d1725b88bfbe056a558
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-21
---
# Review de segurança: regra-lote-por-arquivo

## Gatilhos
Toca o gatilho de controles do Forge (texto de regra do Jarvis e invariantes em `tests/config.json`). Não toca segredo, pipeline, dependência nem dado pessoal.

## Achados

## Detalhe dos achados
Escopo lido: o diff entre a base 26f7189 e 6f61294 (`agents/jarvis.md`, `tests/config.json`, fragmento de changelog).

- Lote por arquivo (`agents/jarvis.md:48`): o texto mantém review, segurança e QA sobre o lote inteiro, um commit por item (reversível por revert) e fecha com a frase de que nenhum portão cai. Bate com a decisão do dono de 08:26. O gatilho de segurança (`R-SEGURANCA`) de qualquer item continua exigindo o parecer, que cobre o HEAD final do lote. Nenhum portão é afrouxado.
- Passo 1 (`agents/jarvis.md:33`): agrupa só itens no mesmo estágio de discovery e proíbe item sem discovery com item já descoberto, o que bate com a decisão das 09:30; vale para o Forge e para os projetos. Não contorna `R-DISCOVERY`.
- Exceção a uma melhoria por PR (`agents/jarvis.md:96`): restrita ao lote definido na regra; o lote exclui item que depende de decisão do dono ainda não tomada (`R-DECISAO`). Sem brecha para `R-MAIN` nem `R-FLUXO`.
- `tests/config.json:270-272`: dois invariantes adicionados, nenhum removido nem afrouxado.

Recomendações (não bloqueantes):
- Explicitar que o lote com item de gatilho de segurança recebe um único parecer no HEAD final e que o revert de um item exige nova revalidação desse parecer, pois o commit muda.
- O invariante da exceção ao PR único poderia travar também a frase da exceção em `agents/jarvis.md`, para ela não sumir sem o teste notar.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão estática manual; nenhuma ferramenta de varredura necessária, nada faltou.
