---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-meta-notas-reconta
commit: c947a0634110a0006d4ca4f6d63e446a2c2445d5
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-23
---
# Review de segurança: v0478 (E137.1, PR #822)

Escopo: `hooks/meta.py` (pré-filtro do resultado de ferramenta em `notas_da_rodada` e marca por transcrito em `vistas_anteriores`/`notas_em_outro_idioma`), `tests/test_meta.py`, `tests/mutantes/v0478-meta-notas-3.json`, `tests/mutantes/v0480-meta-notas-reconta.json` e o fragmento do changelog, de `0e59c446` a `c947a063`.

**Veredito: neutro.** O item não afrouxa nem aperta controle: mexe só na medida S6, que nunca bloqueia (docstring em `hooks/meta.py:10`), roda depois da decisão do objetivo S4 e não toca nela. A escrita continua por `gravar_json` (`hooks/_comum.py:2561`, `O_EXCL|O_NOFOLLOW` e troca atômica), sem mudança.

## Gatilhos
Gatilhos: hook do Forge (controle da fábrica), leitura de arquivo de estado comum às sessões (`.forge/run/notas.json`)

## Detalhe dos achados
Sem achado. Análise da entrada (o `notas.json` em `.forge/run`, pasta comum às sessões do projeto, gravável por qualquer sessão ou agente do mesmo projeto):

- **Entrada forjada na forma.** `hooks/meta.py:317` descarta a raiz que não é objeto e a entrada que não é objeto; `marca` e `final` de tipo errado só são comparados por igualdade (`hooks/meta.py:295`, `hooks/meta.py:302`) e não levantam. Sonda local: raiz `[]`, `null`, `1`, `"x"`, `{quebrado` e entrada própria com `marca` objeto e `final` nulo: a medida devolve 0 e o arquivo é regravado só com a entrada do transcrito corrente. Testes: `test_marca_do_transcrito_fora_da_forma_e_ignorada`, `test_marca_ilegivel_ou_fora_da_forma_e_ignorada` (mutantes M2 e M20/M21).
- **Entrada grande.** A leitura é a de antes (`ler_json`, sem teto de tamanho, igual à versão anterior); o arquivo regravado fica limitado a `MARCAS_GUARDADAS` entradas (`hooks/meta.py:271`, `hooks/meta.py:330`). Sonda: 200 mil entradas forjadas lidas em 0,36 s e regravadas em 8 entradas (706 bytes). Teste: `test_marcas_guardadas_param_no_teto_e_sai_a_mais_velha`.
- **Resíduo, sem caminho de ataque (não é achado).** As até 7 entradas de outras sessões são regravadas como vieram, então conteúdo plantado nelas (sonda: 5 MB numa chave) persiste até sair pela idade, onde antes era sobrescrito no Stop seguinte. Quem planta já grava a pasta e já podia, antes e agora, forjar a própria marca para a medida contar menos; o ganho é nulo (a medida não bloqueia) e o custo é ler e regravar o arquivo no Stop. Endurecimento opcional, se o autor quiser: regravar cada entrada só com `marca` (texto) e `final` (64 hex).
- **Pré-filtro (`hooks/meta.py:285`).** Agora decodifica a linha com o par `"type":"tool_result"` quando ela traz também `"type":"assistant"`. Custo limitado por `LEITURA_MAXIMA` (`hooks/meta.py:42`), como antes. Sonda: registro de usuário com resultado de ferramenta e `toolUseResult` que imita um assistente com texto em inglês, seguido de nota de subagente com o par no input: nenhuma nota contada e nenhuma parada antecipada como fala do dono (`texto_do_dono` recusa o bloco `tool_result`, `hooks/vigia.py:337`). Teste: `test_nota_cuja_entrada_traz_o_par_type_tool_result_ainda_conta` (mutante M1).
- **Dado gravado.** Continua sem texto de mensagem: o uuid, o sha256 da final e, como chave, o caminho do transcrito (até 8 caminhos, antes 1); caminho local de sessão, sem segredo.

Suíte: `tests/test_meta.py` rodado localmente no head (54 testes, OK); a suíte inteira é do CI do PR #822, que no momento da revisão tinha bateria, instalação e "árvore já provada" verdes e as partes da suíte em andamento. O merge segue preso ao CI verde.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do diff e sondas locais com a biblioteca padrão. Varredor de segredos e SAST ausentes do PATH (lacuna registrada; o diff não traz credencial nem configuração).
