---
tipo: revisao-seguranca
contrato: 1
pedido: impl-furo-hook-a
branch: melhoria/impl-furo-hook-a-a1
commit: badc53798232589ad4e893c195b90b1a4e9e8ff4
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-31
---
# Review de segurança: impl-furo-hook-a, branch a1

Etapa E1.3 do pedido `impl-furo-hook-a` (brief `impl-furo-hook-a-security-engineer-2`). Diff lido: `234dbe0..badc537`. Modelo de ameaças: `~/.forge-contrib/docs/security/ameacas/furo-hook.md`, §4.1. Não sou o autor.

## Item entregue e M14
- **Item:** E1, A1 TESTE-MATRIZ-CRITICO. Só teste: `tests/test_hooks.py` e `tests/mutantes/impl-furo-hook-a.json`, mais o fragmento de changelog e o parecer do review.
- **M14 (decisão M14, `agents/tech-lead.md:19` na develop):** conta só `tests/test_hooks.py`, com 26 adições e 1 remoção, 27 linhas, abaixo de 150. `tests/mutantes/`, `changelog.d/` e o parecer ficam fora. Um comportamento só, a régua T6. A branch não toca `hooks/` nem caminho de `PROTEGIDOS`. **Cumpre.**

## Gatilhos
R-SEGURANCA, controles do Forge: o teste é a régua que mede a leitura dos hooks `conformidade` e `parecer`.

## Achados

## Detalhe dos achados
Sem achado. Conferência contra os controles do modelo (§4.1):
- **C-A1-1:** `test_t6_a_leitura_ve_a_acao_sem_marcador_com_cada_variante` (`tests/test_hooks.py:1850-1871`) roda pelo hook real (`executar_em_lote`) as ações do corpus sem marcador `CRITICO`, cruzadas com `VARIANTES_QUE_O_BASH_IGNORA`. Exige saída 2, e a nova chave `stderr_sem` (`:638-639`) exige que o motivo não seja o da rede da ADR 0011.
- **C-A1-2:** o merge reprovado do `parecer` entra na mesma matriz, com o texto da rede do `parecer`.
- **C-A1-3:** `MECANISMOS_DO_COMENTARIO ⊆ VARIANTES_QUE_O_BASH_IGNORA` (`:1856`) e pelo menos 2 ações sem marcador (`:1860`). Não há lista de pendentes que tire caso da matriz. Uma ação ausente do mapa levanta `KeyError` e o teste falha, em vez de pular o caso.
- **C-A1-4:** os mutantes m1 (laço da crase) e m2 (`atribuicoes +`) estão em `tests/mutantes/impl-furo-hook-a.json`, os dois apontando para o T6.
- **Execução:** rodei o T6 na worktree, no HEAD revisado: `Ran 1 test in 18.755s`, `OK`.
- **Observação, sem achado:** `stderr: "R-"` aceita qualquer recusa que não seja a da rede, inclusive a da linha ilegível. É o que o desenho pede (§2.4): a leitura recusou, porque viu a ação ou porque não conseguiu ler.

Sem superfície nova: a branch não muda código de hook. O C-A1-5 (tempo do T6 no corpo do PR) é do autor e do PR, fora deste parecer.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff e execução local do teste. `gitleaks`, `semgrep`, `osv-scanner`, `zizmor` e `actionlint` não estão no PATH (lacuna registrada; o diff não traz segredo, dependência nem workflow).
