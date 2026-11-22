---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-g1-1-uma-volta
commit: 8522e8fe58bcfd9240228b875f1314237bee1f27
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478 E100.7 (G1.1, revalidação da volta)

Revalidação por delta (ORDEM DO DONO 21/11 22:13). A rodada anterior (E100.3, `57c0cbff`, A1 e A2 bloqueantes) fica no git.

Delta lido: `forge-check parecer delta docs/security/v0480-g1-1-uma-volta.md`, intervalo `57c0cbff..8522e8fe`. No domínio: `bin/forge-check` (`VOLTA_NA_DECISAO`, `voltas_autorizadas`, `voltas_da_branch` nova, `gerar_volta`, `conferir_volta`, `avaliar_brief`), `agents/jarvis.md` (passo 6), `skills/briefs-e-conferencia/autor-ate-o-merge.md`. Fora: `changelog.d/`, specs de mutantes, `tests/test_volta_por_delta.py`. Já lido na rodada anterior e não relido: o resto do `bin/forge-check`, `hooks/conformidade.py`, ADR 0018.

Gatilhos: código de controle do Forge (`bin/forge-check`).

Suíte: não rodada aqui (só no CI; o PR ainda não existe). Rodei a classe `BriefDeVolta` (31 testes, com os 7 novos do G1.1): OK.

## Achados
- A1 (bloqueante) bin/forge-check:4247 · corrigido: só a forma canônica ancorada autoriza; S1 a S4 dão 1 no head novo
- A2 (bloqueante) bin/forge-check:4305 · parcial: a contagem usa a Branch: do anterior, mas o brief gerado usa o --branch; com anterior sem Branch: ou de outro item e --branch do item, sai outra "volta 1" e a conferência (:4439) passa com rc 0 (S7, S8)
- A3 (recomendado) bin/forge-check:4255 · aberto: a autorização segue sendo uma linha que o Jarvis escreve (limite da ADR 0018), e o delta não declara esse limite no R-QA nem na skill

## Sondas
- S1 · voltas_autorizadas(fontes=["- 2026-11-21 23:00: DECISÃO DO DONO: sem nova volta para melhoria/v1-x; cortar e reabrir menor"], "melhoria/v1-x") · espera: 1 · obtido: 1
- S2 · voltas_autorizadas(fontes=["DECISÃO DO DONO (2026-11-21 23:00): melhoria/v1-x aceita com cartão, nada de voltas"], "melhoria/v1-x") · espera: 1 · obtido: 1
- S3 · voltas_autorizadas(fontes=["DECISÃO DO DONO (2026-11-21 23:00): melhoria/v0480-g1-1-uma-volta entra antes do G1.2"], "melhoria/v0480-g1-1-uma-volta") · espera: 1 · obtido: 1
- S4 · voltas_autorizadas(fontes=["DECISÃO DO DONO (2026-11-21 23:00): o dono volta na segunda; melhoria/v1-x espera"], "melhoria/v1-x") · espera: 1 · obtido: 1
- S5 · BriefDeVolta: gerar() -> volta 1 gravada em -2.md; gerar() de novo com --volta no brief original; conferir(saida, nome=-3.md) · espera: recusa · obtido: gerar rc 1 "já tem volta"; conferir rc 1 "o anterior ... já tem volta"
- S7 · gerar(--branch melhoria/x) -> -2.md; anterior sem Branch: (com_branch(..., branch=None)); gerar(--branch melhoria/x, volta=anterior); conferir(-3.md) · espera: recusa (volta 2 sem decisão) · obtido: gerar rc 0 "(volta 1)" com Branch: melhoria/x; conferir rc 0
- S8 · como S7, anterior com Branch: melhoria/y · espera: recusa · obtido: gerar rc 0 "(volta 1)" com Branch: melhoria/x; conferir rc 0

## Detalhe dos achados

**A1, corrigido.** `VOLTA_NA_DECISAO` (`:4247`) agora exige a frase canônica logo depois de `ABRE_A_DECISAO`, com a branch delimitada (`(?=\s|$)`), e `voltas_autorizadas` (`:4261`) conta linhas distintas. S1 a S4 dão 1. O texto depois da branch segue livre (`mais uma volta para melhoria/x recusada` dá 2), como a correção mínima da rodada anterior pedia; a recusa (`:4285`) prescreve a forma exata, então isso fica sem achado.

**A2, parcial.** O que ficou corrigido: a volta gerada de novo a partir do original (S5), o anterior com sucessor e o `(volta N)` sem `Volta-de:` (`:8731`). O que segue aberto: a contagem e a autorização usam `do_item`, a `Branch:` do anterior (`:4305`, `:4439`), mas o brief gerado grava `branch = a.branch or ...` (`:4304`), e a conferência não compara a `Branch:` do brief novo com a do anterior. Caminho: o Jarvis passa em `--volta` qualquer brief do pedido sem `Branch:` (ato, por exemplo) ou de outro item, junto com `--branch <item>`. `do_item` sai vazio ou de outro item, a conta dá 0 e sai mais uma "volta 1" para o item, que passa na conferência (S7, S8). O teto do `R-QA` cai com um comando, que é o mesmo caminho e a mesma severidade (média) do A2 original. Correção mínima, nos dois lugares (`gerar_volta` e `conferir_volta`):
- recusar quando a `Branch:` do brief novo (ou o `--branch`) é diferente da `Branch:` do anterior;
- recusar a volta cujo anterior não tem `Branch:`. Hoje o comentário de `:4439` diz "falha fechada", mas para n=1 a volta passa.

Testes: S7 e S8 como recusa no `gerar` e no `conferir`. Esforço P. Dono: autor da E100.5.

**A3, aberto (recomendado).** Sem mudança no delta. A correção mínima é a da rodada anterior: uma linha no `R-QA` e na skill dizendo que a autorização da volta é uma linha que o Jarvis escreve com a leitura dele (ADR 0018), ou o ato `volta-extra` nas concessões. Esforço P. Dono: autor da E100.5.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas usadas: o diff do delta e sondas pela biblioteca padrão (`voltas_autorizadas` e a classe `BriefDeVolta` subclassificada fora da cópia, em `$TMPDIR`). `gitleaks` e `semgrep` não estão no PATH (lacuna); o delta não tem segredo nem dependência.
