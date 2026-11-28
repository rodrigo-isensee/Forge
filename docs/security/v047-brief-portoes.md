---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-brief-portoes
commit: 21edf48a63d7351585725752aace5501fc71f970
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: v047 (desenho do BRIEF-NAO-SEGURA-VAGAS, revalidação da volta 2)

Revalidação por delta (etapa E1.246) da volta E1.244 do desenho. Intervalo `0979cb63..21edf48a`: só `docs/propostas/brief-portoes-por-ferramenta.md`. O `forge-check parecer delta` diz "nenhum arquivo do domínio mudou" (a proposta é documentação), mas o desenho é de controle do Forge (hook `conformidade`), então a releitura foi da parte 0 da seção 10, do item "Programa opaco e interpretador" da 3.4, das sondas S10 a S12, do corpus 11 x 9, dos mutantes da parte 0 e do limite da cópia renomeada, conferidos contra `hooks/conformidade.py` no mesmo clone (`args_do_forge_check` `:97-108`, o ponto de chamada `:1492` e `:1514`, `forge_check_grava` `:1590-1607`).

## Gatilhos
`R-SEGURANCA`: o desenho muda as guardas do hook `conformidade` (o programa opaco e o interpretador do `forge-check`) e corrige, na parte 0, uma fronteira aberta na `develop`. Classe C quando implementado. Sem código nesta entrega: o parecer é de desenho e não há suíte a rodar.

## Achados
- A8 (recomendado) docs/propostas/brief-portoes-por-ferramenta.md:120 · Corpus 11x9: `rodar`, `meta` e `medida` dão rc 0 pela forma direta no papel de autor de stack; o rc esperado pelo opaco deve ser o da forma direta no mesmo papel, não rc 2 fixo (27 dos 99 casos falham com a regra certa).
- A9 (recomendado) docs/propostas/brief-portoes-por-ferramenta.md:98 · Crase: o ponto de chamada tira a crase do nome (hooks/conformidade.py:1492) e o args_do_forge_check recebe `command`; o critério do opaco tem de olhar a palavra original, senão as 8 escritas recusadas pela forma direta seguem rc 0 pela crase.

## Sondas

## Detalhe dos achados

**A7 (rodada anterior, bloqueante): resolvido.** A 3.4 (linhas 97-102) e a parte 0 (linha 197) trocam a lista à parte pelo predicado inteiro do `forge_check_grava`: o opaco devolve sempre os argumentos, o interpretador confere cada fatia que começa numa palavra opaca, e quem decide é a política de destinos, que só confere destino nos subcomandos de escrita (`grava_no_pedido`, `pausa` sem `--retomar`, `FORGE_CHECK_ESCRITAS`, `recado` sem `--confirmar`, `transcricao anonimizar`; conferido em `hooks/conformidade.py:1590-1607`). Os mutantes da parte 0 (linha 189) cobrem os três ramos (opaco, interpretador, cada palavra opaca). O falso positivo aceito (`"$editor" pausa`) é falha fechada, proporcional.

Conferência do desenho por execução: copiei o plugin para `$TMPDIR` e troquei só o `args_do_forge_check` e o ponto de chamada pelo texto da 3.4 (opaco sempre; no interpretador, uma fatia por palavra opaca ou de nome `forge-check`), e rodei o corpus das linhas 120 e 121 (11 escritas x 9 formas, 10 leituras x 9 formas, 3 casos da sessão principal, um script comum do usuário com `pausa` como argumento, um `-c` com código literal e um `-c "$code"` antes do script opaco) no papel de autor de stack, num repositório temporário, ambiente limpo. Resultado: as 90 leituras, os 3 da sessão principal e os 2 legítimos passam (rc 0); as escritas pelo `$(...)`, `"$(which ...)"`, `"$f"`, interpretador (com `-I` e `-W ignore`), `env` e `eval` são recusadas (rc 2), salvo as duas classes abaixo (35 casos: 27 de A8 e 8 de A9). A mesma bateria na `develop` deixa 90 dos 100 casos de recusa abertos (rc 0; os 10 fechados são `anotar --tipo` e `brief --gravar` pelas formas com `$`, já cobertas hoje), o que confirma S6 a S11; S12 e o limite da cópia renomeada também se reproduzem (rc 0). A regra está certa; os dois achados são de precisão do texto para quem implementa.

**A8 (informativa, recomendado; linha 120).** Evidência: `forge-check rodar x`, `forge-check meta x` e `forge-check medida x`, forma direta, papel de autor de stack, dão rc 0 no hook em `21edf48a` (a política do papel permite os destinos deles); o corpus pede rc 2 para as três em todas as formas. Origem: a lista veio da correção mínima do meu A7, que as pôs entre as escritas abertas sem conferir a forma direta; o erro é deste revisor. Caminho de ataque: nenhum (o opaco não dá mais que a forma direta); o risco é de processo: com a regra certa, 27 dos 99 casos reprovam, e quem implementa pode "corrigir" apertando a política do papel em `hooks/conformidade.json`, fora do escopo da parte 0. Correção mínima: o rc esperado de cada escrita pelo opaco é o da forma direta no mesmo papel (o teste roda as duas e compara), ou tirar `rodar`, `meta` e `medida` da lista de recusa e pô-las na de equivalência; o mínimo de casos (checklist 11) passa a contar o produto inteiro. Esforço P. Dono: `tech-lead` (autor do desenho).

**A9 (baixa, recomendado; linha 98).** Evidência: no ponto de chamada (`hooks/conformidade.py:1492`), `prog = Path(palavras[0].lstrip("`")).name`; para `` `command -v forge-check` pausa ``, as palavras são `` ['`command', '-v', 'forge-check`', 'pausa'] `` e o `prog` que chega ao `args_do_forge_check` (`:1514`) é `command`, sem crase. Implementado ao pé da letra ("o nome com `$` ou crase" no `prog`), o opaco não pega a crase: na bateria acima, as 8 escritas que a forma direta recusa seguem rc 0 pela crase (as outras 3 são as de A8). Caminho de ataque: o de A7 (agente de autor pausa a fábrica ou escreve na caixa da sessão principal pela crase). Não é bloqueante porque o corpus da parte 0 já tem a crase entre as 9 formas e reprova a implementação que esquecer; o texto deve dizer onde olhar. Correção mínima: na 3.4, "o critério do opaco olha a palavra original (`palavras[0]`, antes do `lstrip` da `:1492`), não o `prog`"; mutante: "opaco pelo `prog` sem crase" (a crase do corpus reprova). Esforço P. Dono: `tech-lead`.

**Limite registrado (cópia renomeada).** Aceito como fora da parte 0. A mesma classe vale para o link simbólico (`ln -s "$(command -v forge-check)" fc; ./fc pausa`, rc 0 na sonda desta rodada): a sugestão própria ao Forge deve citar as duas formas.

**Sem achado novo** em S10 a S12, nos mutantes da parte 0 e na ordem da seção 10.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do desenho e de `hooks/conformidade.py` no clone; o hook em subprocesso com ambiente limpo num repositório temporário, na versão do clone e numa cópia em `$TMPDIR` com a regra da 3.4 (nada gravado no clone). Sem varredura de segredo nem de dependência: a entrega é só texto, sem dependência nova.
