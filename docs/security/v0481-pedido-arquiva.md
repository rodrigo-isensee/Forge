---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-pedido-arquiva
commit: 687d97c8209f6e66cd813ce05f44423b6fb0ff87
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0481 (pedido que se arquiva sozinho, #874, E9.4)

Gatilhos: bin/forge-check (controle do Forge, R-CONFORMIDADE), bin/forge_tamanho.py (sensível da catraca), escrita automática em docs/pedidos/ pelo `brief gerar`.

Base 8d7914bc..687d97c8 (2 commits, 8 arquivos). Lido: o diff inteiro de bin/forge-check e bin/forge_tamanho.py, os consumidores de `ler_pedido_brief(...)["etapas"]` (corte, citações, apontador, decisões, etapa coberta, Fora do escopo, proximo, contradição) e o teste novo tests/test_brief_tamanho.py (`ArquivaSozinho`). Parecer anterior da branch: nenhum.

Só aperta ou neutro, por escrito: **não**.
- Neutro: bin/forge_tamanho.py:12 (margem 0,9 para 0,8) só antecipa o aviso e o arquivamento; o teto que o `brief conferir`/selar recusa (`len(texto) > TETO_DE_CARACTERES_DO_BRIEF`) não muda.
- Neutro: o `## Histórico` (selos, `entrega conferida`, `parecer conferido`) e as linhas `DECISÃO DO DONO` ficam intactos (o teste confere `etapas_conferidas`, `entregas_conferidas` e `ultimos_do_historico` iguais antes e depois); o `pr` não lê o `## Etapas`. A escrita usa a mesma trava `flock` do `gravar_no_historico`.
- Neutro por desenho: `ids_de_etapa` (citações, apontador `--cartao`, `decisoes`) aceita os ids de `## Etapas arquivadas`, que só o dono do pedido escreve, como já escreve o `## Etapas`.
- Afrouxa: A1 (etapa aberta sai do `## Etapas`) e A2 (duas recusas do corte deixam de barrar para etapa arquivada).

Suíte: CI do head 687d97c8 com a suíte pendente e a catraca vermelha à espera deste parecer (R-CONFORMIDADE); rodados aqui tests.test_brief_tamanho e tests.test_forge_tamanho (37 testes, OK) e as sondas abaixo.

## Achados
- A1 (bloqueante) bin/forge-check:8059 · Arquiva etapa aberta: `=aprovado` fecha todo id citado na mesma linha do Histórico (volta pendente, outro parecer `=reprovado`), e `entregue` (8016) idem; real no v0480: "a volta E168.5 da segurança segue". A etapa some do Etapas e o `--cobre` dela passa a falhar.
- A2 (bloqueante) bin/forge-check:7679 · O corte deixa de barrar etapa arquivada no Entregar: `etapas_citadas` só vê o `## Etapas`, então "junta delegações" (E1.1 + E20.1) e "papel errado" (E1.2 de tech-lead a node-backend) passam depois do arquivamento; o mesmo em 7748 (contradição com o Fora do escopo do pedido).
- A3 (recomendado) bin/forge-check:8085 · docs/pedidos/arquivo e o arquivo dentro dela são abertos seguindo link: um link plantado ali faz o `brief gerar` acrescentar o texto das etapas a um arquivo fora de docs/pedidos/; abrir sem seguir link (como `_ler_regular`) e recusar o que não é arquivo regular.

## Sondas
- S1 · Histórico com `- ...: docs/qa/exemplo.md=aprovado (E1.2, head abc; a volta E20.2 da segurança segue)` no pedido de test_brief_tamanho, `brief gerar --cobre E20.1` · espera: E20.2 fica no ## Etapas · obtido: etapas vivas ['E20.1'], E20.2 arquivada
- S2 · linha `docs/reviews/exemplo.md=aprovado por delta (E1.2); docs/qa/exemplo.md=reprovado por delta (E20.2, A1 bloqueante)`, depois `brief gerar --cobre E20.2 --destino forge:tech-lead` · espera: E20.2 aberta, brief gerado · obtido: arquivada; rc 2 "--cobre E20.2 não existe em ## Etapas"
- S3 · `conferir_corte` com Entregar `- a (E20.1)` e `- b (E1.1)`, destino node-backend, antes e depois do arquivamento · espera: "etapa: junta delegações E1.1, E20.1" nos dois · obtido: antes reprova, depois nenhuma recusa
- S4 · `etapas_fechadas` com Histórico `- ...: E1.1 entregue; review E1.2 despachado` · espera: só E1.1 fechada · obtido: ['E1.1', 'E1.2']
- S5 · `conferir_corte` com Entregar `- a (E1.2)` (E1.2 de tech-lead), destino node-backend, antes e depois · espera: "etapa: papel errado E1.2" nos dois · obtido: antes reprova, depois nenhuma recusa

## Detalhe dos achados
**A1.** Evidência: bin/forge-check:8059 (`aprovadas` pega todo id de qualquer linha com `=aprovado`), bin/forge-check:8016 (o `entregue` de `etapas_do_proximo`, antes só informativo no `proximo`, agora decide o que sai do pedido), bin/forge-check:8070 e 9812 (o `brief gerar` arquiva sem excluir o próprio `--cobre`). Caminho: o Jarvis registra no Histórico, como faz hoje, a aprovação de uma etapa junto com a menção da volta seguinte ou de outro parecer reprovado na mesma linha (no pedido v0480 há ao menos E168.5, E141.7, E140.18 e E168.7 nessa forma); no próximo brief perto do teto, a etapa aberta sai do `## Etapas`: o `proximo` deixa de mostrá-la, o Fora do escopo dos outros briefs deixa de listá-la e o brief da própria volta é recusado (S2), ou, se a etapa arquivada é o `--cobre` em geração, o pedido já mudou e o brief falha. É a violação direta do requisito "nenhuma etapa aberta é arquivada". Severidade: média (integridade do registro; o `pr` e os portões seguem lendo os pareceres, então não abre merge). Correção mínima: para arquivar, fechar só pelo fechamento atribuído ao id: `entrega conferida` do brief selado que o cobre, PR mesclado da `[branch]`, `=aprovado (E<id>` com o id logo após o parêntese do mesmo parecer, ou `E<id> entregue` com o id colado à palavra; nunca o `--cobre` em geração nem id citado em linha posterior sem fechamento próprio (volta, `=reprovado`, `despachad`, `segue`). Teste: S1, S2 e S4 como casos. Esforço P. Dono: autor de E9.1.

**A2.** Evidência: bin/forge-check:7679 (`etapas_citadas` sobre `pedido["etapas"]`), 7683 (papel lido de `pedido["etapas"]`), 7748 (`existentes` sem as arquivadas). Caminho: um brief (novo, ou a volta de uma etapa já fechada) que cita no Entregar uma etapa arquivada junto com a do Cobre, ou que a entrega ao papel errado, passa no `brief conferir` e é selado; antes do arquivamento, o mesmo brief era recusado (R-BRIEF). Severidade: baixa (exige erro de quem gera o brief), mas é recusa que deixa de barrar, fora do "só aperta ou neutro" pedido. Correção mínima: guardar o papel na lista arquivada (`- E1.1 (node-backend), E1.2 (tech-lead)` em `## Etapas arquivadas`, ou ler o papel de docs/pedidos/arquivo/<id>.md) e fazer `etapas_citadas`, o papel errado e `existentes` operarem sobre vivas e arquivadas. Teste: S3 e S5 como casos. Esforço P. Dono: autor de E9.1.

**A3.** Evidência: bin/forge-check:8085-8086 (`mkdir(exist_ok=True)` e `open(arquivo, "a")` seguem link). Caminho: quem já escreve em docs/pedidos/ (o Jarvis, ou um agente sob injeção com essa escrita) planta `arquivo` como link; o `brief gerar` seguinte acrescenta as linhas de etapa (texto que o mesmo escritor controla) ao alvo do link. Severidade: baixa (exige escrita local prévia na raiz dos pedidos). Correção mínima: recusar `docs/pedidos/arquivo` que não seja pasta real e abrir o arquivo com `O_NOFOLLOW` (ou conferir regular antes), sem arquivar em caso de recusa. Esforço P. Dono: autor de E9.1.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do diff e sondas locais (biblioteca padrão, fixture `ArquivaSozinho` do próprio teste); gitleaks, Semgrep e zizmor não se aplicam ao diff (sem segredo, sem workflow).
