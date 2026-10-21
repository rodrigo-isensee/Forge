---
tipo: revisao-seguranca
contrato: 1
pedido: erros-no-brief
branch: melhoria/erros-no-brief
commit: f5d78db45fd9c57053635cf898b095b632ec69bc
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-21
---
# Review de segurança: erros-no-brief

## Gatilhos
Controle do Forge (`R-SEGURANCA`): `bin/forge-check` (registro de conferências, `brief gerar`, `brief`, `brief mensagem`) e o texto que chega ao brief aprovado e à saída lida pelo Jarvis e pelo conferente. Revisado o diff `10c838f..f5d78db` (6 arquivos) contra os 13 casos e os testes T1 a T9 do modelo de ameaças da E0.2.

## Achados

## Detalhe dos achados
Sem achado bloqueante. Conferência das mitigações obrigatórias:

- Casos 1 e 8 (nada livre do registro vai a brief ou tela): `linha_do_destino` (`bin/forge-check:1586`), `erros_do_jarvis` e `proposta_de` montam o texto só com a classe, a contagem e o texto fixo de `CLASSES_DE_FALHA`; os nomes de brief da proposta passam por `NOME_DE_REGISTRO` (sem espaço, `|` nem barra) e `quem` vem de lista fixa ou de agente conhecido. Nota e resultado nunca são lidos para saída. Teste T1 (`tests/test_erros_no_brief.py:323`).
- Casos 2 e 9 (classe forjada; Cf na nota): a gravação passa todos os campos, classe, autor e nota inclusive, por `recusa_do_campo` (cita o campo e o código U+XXXX, nunca o valor) e exige classe exatamente do catálogo; a leitura descarta célula fora do catálogo e `outra`. Testes T2 e T3 (`tests/test_erros_no_brief.py:145`, `:177`).
- Caso 3 (linha forjada ou duplicada): conta briefs distintos (pedido, brief), exige 10 células, hora no formato, rodada inteira, janela de 30 dias sem data futura; a proposta só imprime, rc inalterado, nada gravado em regra, agente ou skill. T4 (`:203`, `:210`).
- Caso 5 (destino deslocado): `agente_do_brief` usa o pedido da própria linha como prefixo exato e confere contra `agents/*.md` do plugin e das stacks. T5 (`:182`).
- Caso 6 (bloco editado à mão): `conferir_erros_do_destino` reprova com `forma:` mais de 3 linhas ou qualquer linha com o rótulo que não seja igual à gerada pelo catálogo. A isenção do rótulo na volta (`bin/forge-check:1195`, `:1231`) não abre brecha: o brief anterior aprovado já passou por essa conferência, então uma linha com o rótulo não pode carregar decisão, e as decisões do pedido seguem cobradas à parte. T6 (`:333`, `:347`).
- Caso 7 (mensagem ao conferente): `lembrar_do_jarvis` escreve só em stderr, antes de `conferencia-brief-regra:`, com prefixo `jarvis-recorrente:`; stdout de `brief mensagem` igual byte a byte e `resultado:`/rc de `brief` iguais. T7 (`:429`).
- Caso 10 (link e tamanho): `_tabela_segura` abre com `O_NOFOLLOW` e teto de 1 MiB, com aviso e sem contagem; o efeito vale também para os leitores antigos de `_ler_tabela` (mais estrito). T8 (`:233`).
- Casos 11 e 12 (arquivo vivo da PA-7): o brief recebe só o caminho, nunca o conteúdo; o arquivo traz a instrução de que é dado e não sobrepõe brief nem regra; formato e teto de 20 linhas conferidos (aviso em stderr, sem eco do texto); link simbólico não entra. O arquivo do Forge e o do modelo de projeto têm só classes e IDs (`R-NEUTRO`). T9 (`:498`, `:506`, `:513`).
- Caso 13 (proposta que afrouxa): os textos de `CLASSES_DE_FALHA` (`bin/forge-check:1404-1415`) só pedem conferência, regra ou ferramenta; nenhum sugere dispensar checagem; nada grava em `tests/config.json`, regra ou hook (`R-CONFORMIDADE`).
- Custo (`R-CUSTO`): nenhum; só biblioteca padrão.

Recomendações (baixa, não bloqueiam; dono: tech-lead, numa próxima entrega se o dono quiser):
1. PA-7 falha aberta: com o arquivo vivo fora do formato, o `brief gerar` só avisa em stderr e mantém a linha em `## Ler` (`bin/forge-check:3642`, `:1151`), e só as linhas que começam com `- AR-` são conferidas (`bin/forge-check:1640`); prosa fora do formato chega ao autor. Caminho: edição à mão do arquivo com texto citado de terceiro. Hoje o arquivo só muda por PR com review, o que contém o risco. Correção mínima: com problema, não pôr a linha em `## Ler` e conferir o arquivo inteiro contra o modelo (cabeçalho fixo mais linhas `- AR-`). Esforço P.
2. A conferência do caso 6 olha só a seção "Decisões e restrições" (`bin/forge-check:3367`); uma linha com o rótulo em outra seção não é conferida. Impacto baixo: o conferente lê o brief inteiro. Correção mínima: aplicar `conferir_erros_do_destino` a todas as seções e reprovar o rótulo fora da seção certa. Esforço P.
3. `O_NOFOLLOW` protege só o último componente (`bin/forge-check:1677`): `docs/kanban` como link ainda é seguido; e `tipo_do_brief_em_disco` abre o brief seguindo link, embora só extraia o tipo. Impacto baixo (sem atacante com disco). Esforço P.

## Riscos aceitos e ferramentas
Nenhum risco aceito neste parecer. Caso 4 do modelo (supressão de linha do registro) fica detectável e não preventivo, por decisão do dono de 2026-10-21 01:17 (docs em git local com commit a cada registro; o commit automático vai no cartão DOCS-COMMIT-AUTO). Ferramentas: `gitleaks`, `semgrep` e `osv-scanner` fora do PATH (lacuna); revisão por leitura do diff e dos testes. A suíte não foi rodada por mim: o outro revisor a rodava (`R-TETO`); a evidência dos testes é a da entrega e a do pre-push deste commit.
