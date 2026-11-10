---
tipo: review
contrato: 1
pedido: versao-043
branch: melhoria/uniao-043
commit: c14db03f9b41c1b4b9952a0a289bbf6de333e4cf
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-08
---
# Review do delta da junção da 0.43 (E2.2)

## uniao-043

veredito: aprovado

- Sha revisado: c14db03f9b41c1b4b9952a0a289bbf6de333e4cf, igual a `origin/melhoria/uniao-043` depois do `git fetch origin` (head conferido no Histórico de 13:32 e enviado às 14:35). Base: origin/develop f84153b3934f1c7b1af8db29024bcb81bd022409.
- Delta lido: os 20 merges do primeiro pai (`git log --first-parent origin/develop..c14db03`), cada um com `git show --remerge-diff`, e o único commit sem merge, 3d4787f (A1 do review g1). O conteúdo de cada branch não foi relido: ele é coberto pelos pareceres por branch (reviews-v043/, reviews-v075/ e os de segurança e QA).

### (1) Resoluções de conflito
`--remerge-diff` não fica vazio em 5 dos 20 merges, e todas as resoluções juntam os dois lados:
- bc37d49 (b04c3b6, EST-M11 retro): em `bin/forge-check`, o bloco D12 (medida, `TOPICO_PEQUENO`, `piora_da_release`) e o bloco EST-M11 (`MINIMO_DO_P85`, `cmd_retro`) ficam, assim como os subparsers `medida` e `retro` e os dois despachos em `executar`. Em `tests/test_voltas.py`, ficam `MedidaDoTopico`, `MedidaDaRelease` e `RetroPorGatilho` inteiras, separadas por duas linhas em branco.
- d1b456e (aa282de, EST-M12 A1): mantém `import statistics`, que `cmd_medida` (:4063) e as esperas (:5660) usam.
- 8b5100b (511c52f, E3-2a): ficam `nome_da_secao`, `cmd_kanban_gerar` (de um lado) e `erro_dos_atributos` (do outro). Só sai a assinatura antiga de `cmd_movimento`, com 5 parâmetros. Conferi que o corpo resultante é igual ao do 2.º pai e que o 1.º pai não mudou a função em relação à base bb45aac, então nada se perde. O único chamador (:8249) passa os atributos.
- b507c48 (1c7bbad, MAQ-A7): `tests/test_forge_mutante.py` mantém `PlacarDaRelease` e `MedidaDaVagaPesada`.
- d3f0c58 (57a68df, PP-4a): `tests/test_pre_push_trava.py` mantém `test_envio_dirigido_imprime_fim_e_grava_dirigida` e o bloco PREPUSH-PROVA-ARVORE. Nenhuma asserção muda.
- Pelo Histórico de 01:25, também houve conflito em `.githooks/pre-push`, `bin/forge-testes`, `tests/test_sobreposicao_quadro.py` e `tests/test_testes_tocados.py`. Nos commits gravados, porém, o `--remerge-diff` desses arquivos sai vazio: o resultado é igual à fusão automática, e não há resolução manual a revisar.
- Conferi por nome, nos 5 merges com resolução, que nenhum `def` ou `class` de qualquer dos pais falta no resultado. Também conferi, para as 20 pontas mescladas, que nada falta na árvore final. A única exceção é `uniao_de_entregas`, removida de propósito pela UN-1 (e40fc890, review g6 aprovado), que não tem mais nenhuma referência no código.

### (2) Commit do A1 (3d4787f)
Ficam uma `MARCA_DE_ATRIBUTOS` e uma `PEDIDO_DO_ATRIBUTO`, as da E3-1a, em `bin/forge-check:2948` e `:2950`. `RECUSA_DA_MARCA` e `TETOS_DO_MOVIMENTO` passam para `:2951` e `:2952`, com o texto byte a byte igual ao anterior, e por isso o valor não muda. A contagem de `^MARCA_DE_ATRIBUTOS = \|^PEDIDO_DO_ATRIBUTO = ` cai de 4 para 2 (uma de cada). As duas constantes movidas aparecem uma vez cada. O módulo carrega sem erro (`SourceFileLoader` em `python3 -I` sobre a árvore de c14db03). A mensagem segue Conventional Commits, em português.

### (3) Árvore integrada
Rodei uma varredura AST sobre os 106 arquivos alterados contra a develop, na árvore extraída de c14db03 (`git archive`):
- Nenhuma definição de topo ou de classe duplicada, o que inclui métodos de teste sombreados. A única repetição, `import importlib` / `import importlib.util`, já existe igual na develop.
- Nenhum nome global sem definição (symtable) e nenhum erro de sintaxe.
- Nos scripts shell alterados, `bash -n` passa e não há função duplicada.

Não rodei testes: a suíte do Forge estava rodando (pid 1623749 desde 14:37) e a decisão do dono de 2026-11-07 04:56 manda esperar. Para esta árvore, valem o pre-push do envio de c14db03 (rc 0, Histórico 14:35), o PQ-3 da extensão 3 (312 OK) e o QA do delta (qa-10), que cobre os testes das resoluções.

Teto M14: a junção é PR de versão sob as decisões do dono de 2026-11-08 02:43 e 13:35. O texto do PR (linha de exceção do teto) é da E2.5, não deste delta.

## Achados

## Parecer
Aprovado. As resoluções mantêm os dois lados sem perder comportamento nem teste. O A1 deixa uma definição só, sem mudar valor. A árvore integrada não tem definição duplicada, import quebrado nem nome sombreado.
