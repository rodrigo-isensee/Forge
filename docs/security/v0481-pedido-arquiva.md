---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-pedido-arquiva
commit: ec38cbc4121cdbf7641309bab3de4bcd30d867e2
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0481 (pedido que se arquiva sozinho, #874, E9.8, volta por delta)

Gatilhos: bin/forge-check (controle do Forge, R-CONFORMIDADE), bin/forge_tamanho.py (sensível da catraca), escrita automática em docs/pedidos/ pelo `brief gerar`.

Delta lido (`forge-check parecer delta`, 687d97c8..ec38cbc4): no domínio só bin/forge-check (`ler_pedido_brief`, `ids_de_etapa`, `papeis_das_etapas`, `conferir_corte`, `conferir_pedido_contraditorio`, `etapa_entregue_na_linha`, `etapas_fechadas`, `abrir_o_arquivo`, `arquivar_etapas_fechadas`, `cmd_brief_gerar`); fora do domínio, lidos como prova: tests/test_brief_tamanho.py, tests/test_forge_tamanho.py e os mutantes. Já lido na rodada anterior (687d97c8, no git): o resto do diff da base, sem mudança.

Só aperta ou neutro, por escrito: **sim**.
- Aperta: `etapas_fechadas` (bin/forge-check:8073) passa a fechar só pela entrega conferida do brief que cobre a etapa, PR mesclado, `=aprovado (E<id>` com o id logo após o parêntese (8060) ou `entregue` atribuído ao primeiro id da linha antes de outro id ou `;` (8063); linha de parecer (`.md=`) não entrega nada. O conjunto fechado é subconjunto do anterior.
- Aperta: o `--cobre` e todo id do Entregar do brief em geração ficam protegidos (bin/forge-check:9850) e nunca são arquivados.
- Aperta: `junta delegações`, `papel errado` e a contradição com o Fora do escopo operam sobre vivas e arquivadas (`papeis_das_etapas`, 7471; `existentes`, 7755); arquivada sem papel cai em `papel errado` (falha fechada); `conferir_corte` com pedido só de arquivadas não vira "não verificável".
- Aperta: `abrir_o_arquivo` (8084) recusa pasta `arquivo` que não é pasta real (lstat), abre com `O_NOFOLLOW|O_NONBLOCK` e exige arquivo regular; recusa não arquiva nada, e o pedido só é lido e reescrito sob a trava.
- Neutro: o `## Histórico`, as linhas `DECISÃO DO DONO` e a margem do aviso seguem como na rodada anterior.

Achados anteriores: A1 (bloqueante) corrigido, S1, S2 e S4 rodadas de novo no head (E20.2 fica viva; o brief de E20.2 sai com rc 0; `E1.1 entregue; review E1.2 despachado` fecha só E1.1) e viraram `test_linha_que_cita_outra_etapa_so_fecha_a_atribuida` e `test_cobre_entregue_fica_no_pedido_e_o_brief_sai`. A2 (bloqueante) corrigido: S3 e S5 reprovam igual antes e depois do arquivamento (`test_corte_barra_igual_antes_e_depois_do_arquivo`, `test_corte_de_pedido_so_com_arquivadas_ainda_barra`). A3 (recomendado) corrigido: pasta `arquivo` como link para fora arquiva 0 e não escreve no alvo (sonda própria e os testes de link de pasta, link de arquivo e fifo).

Resíduo aceito como neutro, sem achado: entre o `lstat` da pasta e o `os.open` do arquivo há uma janela de troca (pasta por link); exige processo local concorrente com escrita em docs/pedidos/, que já escreve o próprio pedido; abrir via `dir_fd` com `O_DIRECTORY|O_NOFOLLOW` fecharia a janela se o autor quiser.

Suíte: CI do head ec38cbc4 em andamento (a catraca espera este parecer, R-CONFORMIDADE); rodados aqui tests.test_brief_tamanho e tests.test_forge_tamanho (44 testes, OK) e as sondas S1 a S5 e a de borda abaixo, em arquivo de rascunho que herda a fixture `ArquivaSozinho`.

## Achados
- A4 (recomendado) bin/forge-check:8070 · A negação só pega "não entregue" colado: "E1.3 não foi entregue", "nunca entregue", "a ser entregue", "será entregue", "não-entregue", "sem ser entregue" e "Entregue? não" fecham a etapa e a arquivam aberta. Fechar só com `entregue` logo após o id e sem negação/futuro.

## Detalhe dos achados
**A4.** Evidência: bin/forge-check:8070 (`(?<!não )\bentregue\b` no trecho entre o primeiro id e o próximo id ou `;`). Sonda: Histórico com as nove linhas `E1.1 entregue; review E1.2 despachado`, `E1.3 não foi entregue`, `E1.4 a ser entregue amanhã`, `E1.5 entregue parcialmente, falta o teste`, `E1.6 Entregue? não, volta pendente`, `E1.7 nunca entregue`, `E1.8 será entregue na volta`, `E1.9 não-entregue`, `E1.10 sem ser entregue`; `etapas_fechadas` devolve E1.1, E1.3 a E1.10 (espera: só E1.1, e E1.5 a critério do autor). Caminho: o Jarvis escreve no Histórico uma dessas formas; no próximo `brief gerar` perto do teto a etapa aberta sai do `## Etapas` (o mesmo efeito do A1, já corrigido para a forma real). Proporcionalidade: nenhuma dessas formas aparece hoje nos pedidos de /root/.forge-contrib/docs/pedidos (grep sem ocorrência), por isso recomendado e não bloqueante; volta ao autor e é corrigido antes do merge (R-REVIEW). Correção mínima: exigir `entregue` como primeira palavra após o id (com `(papel)` opcional entre eles), ou recusar o trecho com `não`, `nunca`, `ser`, `será`, `sem` ou `?` antes ou logo depois; caso de teste com as nove linhas. Esforço P. Dono: autor de E9.5.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do delta e sondas locais (biblioteca padrão); gitleaks, Semgrep e zizmor não se aplicam ao delta (sem segredo, sem workflow).
