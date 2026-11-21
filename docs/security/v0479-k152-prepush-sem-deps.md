---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-k152-prepush-sem-deps
commit: adde580693eac70bf44579bae529b20efa39a508
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: K152 (cópia nova sem dependências no pre-push do projeto), head adde5806

## Revalidação por delta (E81.8, head adde5806)
Delta lido (`forge-check parecer delta`, `ce1d79bd..adde5806`): no domínio só `tests/test_prepush_k152.py` (+24 linhas: o auxiliar `com_pronto` e os testes `test_programa_depois_de_ou_logico_tambem_e_checado` e `test_programa_depois_de_pipe_tambem_e_checado`); fora do domínio, `tests/mutantes/v0479-k152-prepush-sem-deps-2.json` (M9, M10). A proposta, o `bin/forge-init` e o `bin/forge-testes` não mudaram. Os dois testes só apertam: provam que o programa depois de `||` e de `|` no pronto rápido também é conferido e que a falta dele barra o envio sem rodar o pronto (`chamadas == []`); nada novo executa na máquina do projeto. Rodados no head: os 2 testes, OK (1,1 s). Veredito mantido: aprovado, só aperta. A 1ª rodada (abaixo) segue valendo, sem achados anteriores a revalidar.

Etapa E81.3, 1ª rodada, diff `adc52def..ce1d79bd` (8 arquivos). Veredito: a mudança só aperta; nenhum caminho novo libera envio.

Gatilhos: execução de comando no `bin/forge-init` (marcador `{{INSTALAR}}` gravado num hook do projeto), proposta de patch do pre-push do modelo de projeto (arquivo travado), lista C-2 `CITACOES_CONHECIDAS` em `tests/test_reval_delta.py`.

## Achados

## Sondas

## Detalhe dos achados
Sem achados. O que foi conferido:

- **`{{INSTALAR}}` (injeção e aspas), `bin/forge-init:67-76,171`.** A fonte é `stacks/<stack>/instalar.json` do próprio Forge (confiável, revisado por PR); `<stack>` já é validado por `^[a-z0-9-]+$` com `pronto.md` existente (`bin/forge-init:51`). Cada argv passa por `shlex.join`, que deixa sem aspas só o conjunto ASCII `[A-Za-z0-9_@%+=:,./-]` e põe entre aspas simples todo o resto (`;`, `$`, crase, `\`, `|`, `&`, espaço, quebra de linha, argumento vazio); qualquer aspa simples na saída esvazia o valor (`:72`). Logo o valor final só tem o conjunto seguro, espaços e os `&&` separadores: dentro de `instalar='...'` no hook gerado não fecha a aspa nem expande nada, e no `sed` o `&` e o `|` saem escapados por `escapar` (`:76`); `\` não chega ao `sed` porque também esvazia. JSON ilegível, sem `comandos` ou com elemento não lista: o `python3 -I` falha e o valor fica vazio (`:71`). O valor só é exibido na mensagem, nunca executado pelo hook. Provas: `test_cada_stack_grava_o_comando_do_instalar_json`, `test_stack_sem_instalar_json_fica_sem_comando_e_a_mensagem_diz_o_que_instalar`, `test_comando_com_aspa_simples_fica_vazio`; mutantes M1 a M3.
- **`{{STACK}}` dentro de `"${instalar:-...}"` (proposta, linha `+como_instalar`).** Expandido entre aspas duplas no hook, mas o nome da stack só tem `[a-z0-9-]` (validado em `bin/forge-init:51`): sem `$`, crase nem `}`.
- **Proposta do `pre-push.local` (`docs/propostas/k152-pre-push.md`, bloco `diff`): só aperta.** As saídas do script com o patch: `exit 0` só no ramo de detecção já existente (sem código da stack) e no fim, depois de `bash -c "$rapido"` aprovado; o bloco novo só acrescenta um `exit 1` (programa fora do PATH) antes do pronto rápido, que continua rodando sempre que a conferência passa. Com `set -euo pipefail`, qualquer falha inesperada do bloco novo sai com código diferente de zero, ou seja, barra. Sem variável, opção nem arquivo que pule a conferência; `command -v --` e o `case` usam o nome entre aspas (sem glob). Falso positivo possível (pronto que começa por função do shell ou `VAR=valor`) barra a mais, nunca a menos, e o critério de reversão já diz que o hook não ganha opção de pular. Provas: `PrePushLocalSemDependencias` (4 testes: nada instalado não roda o pronto; uma ferramenta faltando; tudo instalado roda o pronto; pronto reprovado barra) e `EnvioDaCopiaNova` (ponta a ponta com `git push`).
- **C-2, as duas entradas novas em `CITACOES_CONHECIDAS` (`tests/test_reval_delta.py:134-136`): aprovadas como não normativas.** (1) `("tests/test_prepush_k152.py", "docs/propostas/"): (1, "teste-le")`: uma citação literal (docstring, linha 4); o teste lê e aplica o bloco `diff` da proposta numa cópia temporária, o mesmo uso de `tests/test_forge.py` já na lista. O texto da proposta não chega a projeto algum: o modelo travado só muda quando o dono aplica o patch, e essa aplicação é diff em `templates/projeto/.githooks/` (classe código), com review e parecer próprios (decisão do dono PP1 no pedido); editar a proposta depois deste parecer não muda o que os projetos recebem, e o mapa do `bin/forge-testes` reroda o teste no CI. (2) `("bin/forge-testes", "docs/propostas/"): (1, "nome")`: uma ocorrência, a regex do caminho no `MAPA` (`bin/forge-testes:251`), que só compara o nome do arquivo do diff para escolher testes; não lê o conteúdo.
- **Resto do diff:** `bin/forge-testes` (duas linhas do `MAPA` e um teste a mais numa linha existente) só acrescenta testes à seleção; `tests/pesos-d4.json`, o fragmento do changelog e a spec de mutantes não executam nada na máquina do projeto. Nenhum segredo, workflow ou dependência nova no diff.

## Riscos aceitos e ferramentas
Nenhum risco aceito nem pendente de aceite. Rodado: `python3 -m unittest tests.test_prepush_k152` no head (8 testes, OK em 9 s); a suíte inteira é do CI do PR, obrigatório para o merge (o brief pede sem suíte local; sem CI do head para citar nesta rodada). Uma sonda extra com `instalar.json` hostil foi barrada pelo hook `R-VERIFY` do ambiente e não foi contornada; a análise acima é estática sobre o conjunto de saída do `shlex.join`. Lacuna: gitleaks, osv-scanner, semgrep, zizmor e actionlint fora do PATH; o diff não toca workflow nem dependência.
