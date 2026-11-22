---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-g1-1-uma-volta
commit: 4d2c53330343163b7027e417db7090acf3bd9bfc
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-22
---
# Review de segurança: v0478 E100.11 (G1.1, revalidação da segunda volta)

Revalidação por delta (DECISÃO DO DONO 22/11 05:21, mais uma volta). A rodada anterior (E100.7, `f930fc45`, A2 parcial) fica no git.

Delta lido: `forge-check parecer delta docs/security/v0480-g1-1-uma-volta.md`, intervalo `8522e8fe..4d2c5333`. No domínio só `bin/forge-check`: `VOLTA_NA_DECISAO` (`:4247`), `branch_do_anterior_diferente` nova (`:4278`) e as chamadas em `gerar_volta` (`:4317`) e `conferir_volta` (`:4453`). Fora: `changelog.d/`, fixture, specs de mutantes e testes. Já lido e não relido: o resto do `bin/forge-check`.

Gatilhos: código de controle do Forge (`bin/forge-check`).

Suíte: não rodada aqui (só no CI; o PR ainda não existe). Rodei a classe `BriefDeVolta` (32 testes, com `test_s7_*` e `test_s8_*`): OK.

## Achados
- A1 (bloqueante) bin/forge-check:4247 · corrigido na rodada anterior; a âncora no fim da linha (A4 do review) mantém S1 a S4 em 1 e fecha "mais uma volta para <branch> recusada" (S9)
- A2 (bloqueante) bin/forge-check:4278 · corrigido: gerar_volta (:4317) e conferir_volta (:4453) recusam o anterior sem Branch: ou com Branch: diferente da do brief novo; S7 e S8 dão rc 1 nos dois
- A3 (recomendado) bin/forge-check:4255 · aberto, sem mudança no delta: a autorização segue sendo uma linha que o Jarvis escreve (ADR 0018); falta declarar o limite no R-QA e na skill antes do merge

## Sondas
- S7 · anterior sem Branch: (ato-1.md), já existe volta 1 do item; gerar(--branch melhoria/x, volta=anterior) e conferir(-3.md) · espera: recusa · obtido: gerar rc 1 "não tem `Branch:`", conferir rc 1 (test_s7_anterior_sem_branch_nao_gera_outra_volta_um)
- S8 · como S7, anterior com Branch: melhoria/y · espera: recusa · obtido: gerar rc 1 "é de melhoria/y, não de melhoria/x", conferir rc 1 (test_s8_anterior_de_outro_item_nao_gera_outra_volta_um)
- S9 · voltas_autorizadas(fontes=["- 2026-11-22 09:00: DECISÃO DO DONO: mais uma volta para melhoria/x recusada"], "melhoria/x") · espera: 1 · obtido: 1
- S10 · branch_do_anterior_diferente("melhoria/x", None) · espera: recusa (brief novo sem Branch:) · obtido: 'é de "melhoria/x", não de "<branch>"'

## Detalhe dos achados

**A2, corrigido.** A correção mínima pedida veio inteira: `branch_do_anterior_diferente` recusa `do_item` vazio e `do_item != branch`; em `gerar_volta` compara com o `--branch` efetivo antes de contar, em `conferir_volta` com a `Branch:` do brief novo (que, ausente, também recusa, S10). O `caminho_de_brief` segue prendendo o anterior a `docs/briefs/`, então a contagem por pasta não foge para outro diretório. Os nomes na mensagem passam por `nome_seguro(sem_controle(...))`.

**A1 e A4.** `\.?\s*$` em `canonica.match`: texto depois da branch na mesma linha não autoriza (S9; "e para melhoria/y" também dá 1); ponto final e espaço no fim seguem valendo, o que a forma canônica admite.

**A3, aberto (recomendado).** Mesma correção mínima da rodada anterior: uma linha no `R-QA` e na skill `briefs-e-conferencia` dizendo que a autorização da volta é uma linha que o Jarvis escreve com a leitura dele (ADR 0018), ou o ato `volta-extra` nas concessões. Esforço P. Dono: autor da E100.9. Não é falha explorável por terceiro: quem escreve a linha é o próprio orquestrador, sob o limite já aceito na ADR 0018.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: o diff do delta, os testes S7 e S8 da classe `BriefDeVolta` e sondas pela biblioteca padrão (`voltas_autorizadas`, `branch_do_anterior_diferente`, módulo carregado de `$TMPDIR`). `gitleaks` e `semgrep` não estão no PATH (lacuna); o delta não tem segredo nem dependência.
