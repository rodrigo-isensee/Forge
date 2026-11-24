---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-d2-portao-entrega
commit: d64a506b4a01f13be0798ce2af2123cb3013a5bd
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0478 (E173.11, PR #864)

Escopo: diff `8a6f5907..d64a506b` (E173.2): `patches/d2-portao-entrega.patch` (patch do `.githooks/pre-push` para o dono aplicar), `tests/test_pre_push_d2.py`, `tests/pesos-d4.json` (peso) e o fragmento do changelog. O hook vivo não muda neste PR.

## Gatilhos
Gatilhos: hook de envio (portão local do pre-push, controle do Forge), chamada ao `gh` com corpo de PR vindo da rede

## Achados

## Sondas

## Detalhe dos achados
Conclusão por escrito: o patch **só aperta**; nenhuma checagem existente é afrouxada, e a falha aberta sem rede é avisada.

- **Só aperta.** O patch só acrescenta linhas: nenhuma linha `-` além do cabeçalho (`patches/d2-portao-entrega.patch:2`); 65 linhas `+`. Os dois blocos novos só levam `falhas=1` (`:63`, `:75`) ou aviso com saída 0; nada desliga, pula nem troca checagem anterior. A neutralidade segue barrando no hook remendado (`test_stack_no_nucleo_segue_barrando_no_remendado`). `git apply --check` no head: aplica limpo. Sem `--no-verify`, sem `--force`, sem teste local acrescentado (ENVIO-LEVE; `test_patch_nao_acrescenta_teste_local_ao_envio`).
- **Falha aberta avisada.** Sem `gh`, sem rede, `gh` acima de 10 s ou resposta ilegível: `pr_da_branch` devolve motivo e o hook imprime `aviso: PR de <branch> não verificável (...)` e sai 0 (`patches/d2-portao-entrega.patch:30-33`; `test_sem_rede_avisa_e_segue`). Erro ao carregar `bin/forge-check`, `git diff --numstat` ilegível, `indice-forge.py` ou `pr-texto` com saída diferente de 0 e 1: aviso e saída 0 (`:20-26`, `:46-47`, `:64-65`). O CI do PR continua sendo o portão que vale (mesmo `pr-texto` e mesmo índice). Saídas sem aviso: sem `origin/develop` local ou `merge-base` falho (`:69`, `:74`), o mesmo padrão dos blocos vizinhos do hook (`.githooks/pre-push:280`, `:380`); sem efeito de segurança, porque o CI confere.
- **Entrada da rede (corpo do PR).** O corpo vai ao `pr-texto` por variável de ambiente (`PR_BODY`), nunca por linha de comando nem pelo shell (`:40-41`); o `python3 -I` não lê o diretório corrente como caminho de módulo, e o `bin/` inserido é a árvore do próprio envio, já confiada pelo hook. O que volta ao terminal são textos fixos e caminhos do repositório (`tests/catraca.py:1693-1697` e o T1), não o corpo; a saída do índice passa por filtro de caracteres de controle (`:61`). Sem caminho de injeção.
- **PR de outro dono com o mesmo nome de branch.** `gh pr view <branch>` com o nome sem `dono:` casa pelo rótulo da cabeça do PR (PR de fork leva o dono na frente; não provado nesta sessão sem rede), e o pior efeito de um PR casado por engano seria barrar o envio local do autor (aperta), nunca liberar; o CI confere o PR real. Sem caminho que afrouxe: sem achado.
- **Execução de código da árvore.** O patch roda `bin/forge-check`, `bin/forge_tamanho.py`, `tests/catraca.py` e `scripts/indice-forge.py` do clone, com recusa de link simbólico nos três que o shell chama; é a mesma fronteira de confiança do hook atual (que já roda `scripts/verificar-contribuicao.sh` e `bin/forge-changelog` da árvore). Nenhuma fronteira nova.
- **Disponibilidade.** O `gh` tem teto de 10 s (`TETO_DO_GH_S`) e `stdin` fechado; o `pr-texto` não chama rede no modo `pr-texto`.
- **Testes dos arquivos tocados:** `python3 -m unittest tests.test_pre_push_d2` no head d64a506b: 15 testes, OK (13,2 s). Suíte inteira: só no CI do PR #864 (não conferível daqui: o `gh` não tem credencial no sandbox).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, `git apply --check`, testes do arquivo tocado; segredo não se aplica (sem credencial no diff). Lacuna: o analisador de shell e os varredores de segredo e de workflow não estão no PATH deste ambiente (o CI roda o analisador de shell).
