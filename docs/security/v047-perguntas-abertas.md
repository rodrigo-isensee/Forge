---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-perguntas-abertas
commit: 3da5f24a4bb8aacb7fbf314e12f48ff955b93aba
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: v047 (E1.165, perguntas-abertas, volta 1 da E1.135, por delta)

Intervalo revisado: `2511f48b..3da5f24a` (`4b945876`, `a7beb9b6`, `3da5f24a`; os demais são pareceres e merges). Lido pelo `forge-check parecer delta`: no domínio, só `bin/forge_dono.py`. As specs de mutantes e `tests/test_forge_dono.py` ficam fora do domínio. O parecer anterior (E1.146, head `2511f48b`, aprovado) está no histórico do git.

Veredito: **aprovado**. A1 e A2 foram corrigidos e as sondas confirmam. O A3 continua aberto e recomendado, porque não fazia parte desta volta. A mudança de regra (cada decisão fecha no máximo uma pergunta) é mais estreita que a anterior, em que a última decisão fechava todas. Ela erra para o lado de mostrar mais, e por isso não esconde pergunta. Surgiu um custo quadrático novo em `_respondida` (A4). Ele é recomendado, pelo mesmo motivo do A2: só nega o serviço de uma ferramenta local, e só com milhares de perguntas abertas num mesmo pedido.

## Gatilhos
`R-SEGURANCA`: a ferramenta do Forge lê arquivos do projeto. Pontos conferidos: pasta por link simbólico (A1), regex sobre texto livre (A2 e as regex novas `DATA_DO_CORPO`, `CITACAO` e `RESPONDIDA_NA_LINHA`) e arquivo ilegível (`KANBAN.md`). Não há segredo, rede, workflow nem escrita.

## Achados
- A3 (recomendado) bin/forge_dono.py:501 · `_limpo` tira C0, DEL e `|`, mas deixa passar C1 (U+0080 a U+009F, ex.: U+009B, o CSI de 8 bits) e formato Cf (U+202E); filtrar pela categoria Cc e Cf, como `recusa_da_forja` já faz com Cf
- A4 (recomendado) bin/forge_dono.py:541 · `_respondida` varre todos os instantes a cada decisão (`any(...)`) e `abertas.remove` é linear: 8 mil perguntas e 8 mil decisões num pedido levam 30 s (4 mil: 6,6 s); usar `bisect` sobre `instantes`, que já está ordenado

## Sondas

## Detalhe dos achados
Método: as sondas importaram o `bin/forge_dono.py` do head `3da5f24a` (`python3 -I`, raízes temporárias). Também rodei `python3 -m unittest tests.test_forge_dono` no head: 79 testes, OK. A suíte inteira roda no CI do PR, que a branch ainda não tem (a E1.3 abre o PR depois dos pareceres).

**A1 (fechado).** `:583` recusa `docs/pedidos` ou `docs` como link, seguindo a convenção de `_gravar_novo` (`:56`). Sonda com cada um dos dois links apontando para uma pasta fora da raiz que tem `y.md`: `cmd_abertas` devolveu `(['abertas: erro: docs/pedidos ou docs é link simbólico; recusado'], 1)`, e o texto de fora não apareceu. O caso do FIFO local continua apenas teórico: o git não guarda FIFO.

**A2 (fechado).** O trecho depois da data agora é `[^):\n]{0,80}`. Tempos de `LINHA_DO_REGISTRO.match` na linha `PERGUNTA AO DONO (2026-11-03` seguida de n espaços: 8 mil em 0,04 s (antes 1,8 s), 32 mil em 0,16 s (antes 31 s), 128 mil em 0,56 s e 1 milhão em 4,5 s, ou seja, linear. As regex novas também ficaram lineares até 8 mil repetições: `DATA_DO_CORPO` (`(dono, 2026-11-03` e espaços), `CITACAO` (`pergunta ` repetido e `pergunta ao dono 1a de` e espaços), `RESPONDIDA_NA_LINHA` (`resposta ` repetido) e a alternativa `[A-Z…]{2,20} DO DONO` (`AB DO DONO` repetido). Todas ficaram em até 5 ms.

**KANBAN.md ilegível.** O `OSError` agora vira aviso (`:594-597`). Rodando como root, não consegui provocar o erro por permissão. O ponto é de robustez e fica com o QA.

**A4.** Evidência: `:541` faz `any(abertas[-1][0] < outro < instante for outro in instantes)` para cada decisão enquanto há pergunta aberta, e `:556` faz `abertas.remove(fechada)`, que é O(n). Tempos com n perguntas abertas (`PERGUNTA AO DONO (2026-11-03 10:MM): q`) seguidas de n `DECISÃO DO DONO (2026-11-04 10:00): d`: 1 mil em 0,26 s, 2 mil em 1,2 s, 4 mil em 6,6 s e 8 mil em 30 s. Com uma pergunta só e milhares de decisões, o custo é desprezível (4 mil em 0,07 s), porque a lista esvazia logo. O maior pedido real tem 933 linhas e 93 falas do dono. Caminho de ataque: texto colado num pedido, vindo de fonte externa ou de um agente induzido, com milhares de pares pergunta e decisão, trava `abertas` para quem o roda. O efeito se limita a negar o serviço de uma ferramenta local. Severidade: baixa. Correção mínima: com `instantes` já ordenado, trocar o `any` por `bisect.bisect_right(instantes, abertas[-1][0]) < bisect.bisect_left(instantes, instante)` e somar um teste de orçamento de tempo. Esforço P. Dono: `tech-lead`.

**A3.** Continua como estava no parecer da E1.146: `_limpo` (`:501`) troca só `[\x00-\x1f\x7f|]`. Correção mínima: trocar por espaço todo caractere com `unicodedata.category(c) in ("Cc", "Cf")`. Severidade: informativa a baixa. Esforço P. Dono: `tech-lead`.

## Riscos aceitos e ferramentas
Sem riscos aceitos. As sondas foram locais e passivas, com a biblioteca padrão. Varredura de segredos e SAST não se aplicam a este delta: não há segredo, dependência nem workflow novos. Nenhuma ferramenta foi instalada.
