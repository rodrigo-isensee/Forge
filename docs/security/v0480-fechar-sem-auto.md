---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-fechar-sem-auto
commit: f5143cea54012131715eeac79681695e39c23d5e
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0478 (E171.6, PR #855)

Escopo: diff `c752c227..f5143cea` (E171.1): `bin/forge-fechar` (`copia_da_develop`, `checks_do_head_verdes`, texto do `--dry-run`), `tests/test_fechar_sem_auto.py`, `tests/test_fechar.py`, mutantes `tests/mutantes/v0480-fechar-sem-auto*.json`, `tests/pesos-d4.json`, fragmento do changelog.

## Gatilhos
Gatilhos: portão de merge (FECHAR-NUNCA-AUTO, FECHAR-SEM-AUTO-MERGE), fluxo de branches (R-FLUXO), variável de ambiente que solta um controle

## Achados
- A1 (bloqueante) tests/mutantes/v0478-fechar-checks.json:49 · FCK-M5 (linha 49) e FCK-M6 (linha 59), que provam "pendente não conta como verde" e "pendente no fim do prazo para" no portão do merge, não casam mais a fonte (bin/forge-fechar:948 e :961); a guarda ficou sem prova de mutante e o CI do head está vermelho.

## Sondas
- S1 · python3 -m unittest tests.test_forge_mutante.ConferirTodas (no head f5143cea) · espera: OK · obtido: FAILED, lista com tests/mutantes/v0478-fechar-checks.json FCK-M5 e FCK-M6

## Detalhe dos achados
Conclusão por escrito sobre a direção da mudança: **só aperta ou é neutra**; nenhum caminho que antes recusava passa a mesclar. O que impede o `aprovado` é só A1 (o CI vermelho no head e a prova de mutante perdida da guarda do merge).

- **Todo check-run do head** (`bin/forge-fechar:951-958`). Corre depois do laço dos exigidos (que segue igual), lê a mesma resposta e só acrescenta motivos de parada ou de espera: terminado fora de `success` para (`neutral` também, que o GitHub trataria como aprovado: aperta); pendente espera até o `--espera` e então para; `skipped` não conta, como já valia nos exigidos. Sondas próprias, todas com recusa e sem merge: conclusão nula (`completed/-`) para; execução mais recente `skipped` não esconde a `failure` anterior do mesmo nome (o awk descarta `skipped` antes de escolher a mais recente); `neutral` para. Nome de check-run vem do `@tsv`, que escapa tabulação e quebra de linha, então não quebra o parse. Teto de `per_page=100` sem paginação: o mesmo da leitura dos exigidos (preexistente); com uns 30 check-runs no head hoje, não há caminho realista, e a correção já está pedida no A3 do tech-lead, que acompanho sem duplicar.
- **Recusa de cópia velha** (`bin/forge-fechar:329-338`). Roda antes do log e de qualquer passo, em todos os modos (`--dry-run`, `--limpar`, `--lote`, `--promover`, provado em `test_copia_velha_recusa_em_todos_os_modos_com_o_comando_da_copia_certa`). Falha fechado nos três ramos: busca que falha, develop sem o arquivo e blob diferente param com código 1 e nada feito. Confere contra a develop do servidor, não a ref local (`test_confere_contra_a_develop_do_servidor_nao_a_local`). Cópia por link simbólico para uma cópia igual segue (o `hash-object` lê o alvo): sem falso positivo. Limite conhecido e aceito pela própria decisão: a guarda vale para as cópias que a contêm; uma cópia anterior a este commit não se recusa.
- **Variável que solta a conferência** (`bin/forge-fechar:331`). Exige `FORGE_FECHAR_TESTE=1` **e** `FORGE_FECHAR_COPIA_LIVRE=1`, comparação exata com `1`. Sondas: `true`, ` 1`, `01` em qualquer das duas e `FORGE_FECHAR_TESTE` vazio com `COPIA_LIVRE=1` recusam. Não abre caminho novo fora dos testes: `FORGE_FECHAR_TESTE=1` já troca o `gh` e o `forge-check` por falsos (`bin/forge-fechar:211-216`), um poder maior que dispensar a conferência; os mutantes N1 e N2 (`tests/mutantes/v0480-fechar-sem-auto.json`) provam que cada uma das duas metades é exigida. Neutro.
- **Sem `--auto`.** `test_nenhum_gh_pr_merge_de_bin_e_scripts_usa_auto` varre `bin/` e `scripts/` com o detector provado contra o passo 6 antigo e contra a continuação de linha.
- **A1, correção mínima:** atualizar o `de` de FCK-M5 para casar uma linha só (o laço dos exigidos, `:948`, distinto do novo `:956`) e o `de`/`para` de FCK-M6 para o texto novo (`o $falta_q $falta do head`, `:961`), e conferir que os testes listados ainda matam os dois. Esforço P. Dono: o autor da branch. Severidade: média (guarda do merge sem prova de mutante; o comportamento em si está certo pelas sondas). A outra falha do CI (`test_testes_tocados`, mapa de `bin/forge-fechar` sem `test_fechar_sem_auto`, A2 do tech-lead) não é de segurança.
- **Testes dos arquivos tocados** no head: `tests.test_fechar_sem_auto` 12 testes OK; `tests.test_fechar` 111 testes OK (1 skip preexistente). Suíte inteira: CI do PR #855 no head f5143cea, execução 45408272809, vermelha (partes 1/5 e 4/5).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, sondas locais com os utilitários do teste (gh e forge-check falsos, sem rede). Varredura de segredo e SAST não se aplicam a este diff; as ferramentas de varredura não estão no PATH deste ambiente (lacuna registrada).
