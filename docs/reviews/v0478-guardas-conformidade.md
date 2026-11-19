---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-conformidade
commit: 40dc5f4f1c305481e7b7657626aaadac513fd100
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-19
---
# Review: v0478 E1.20 (revalidação no head 40dc5f4f, A6 da segurança)

Escopo lido: só o delta de `forge-check parecer delta` (bdbdc257..40dc5f4f): changelog.d, docs/hooks.md, hooks/conformidade.py (1 linha), spec -10 dos mutantes (M72), tests/test_conformidade_verde.py (classe `AtualizacaoAtrasDoBusybox`). Fora do domínio, nada relido.

## Achados
- A1 (recomendado) tests/test_conformidade_verde.py:463 · segue do head bdbdc257: o pulo sem GNU tar também pula no CI; siga o `tests/apoio_sandbox.py`. Vira cartão.
- A2 (recomendado) hooks/conformidade.py:2293 · H1: o item soma 299 linhas em hooks/ desde a base 4182a6b9 (+1 nesta volta), acima de 150; o PR leva `teto: excedido, <n> linhas, <motivo>`. Vira cartão.

## Sondas
- S1 · M72 aplicado à mão (`self.atualizacao(palavras)` → `pass`), `busybox chroot / forge-atualizar` (tech-lead, projeto temporário) · espera: teste falha · obtido: `AssertionError: 0 != 2`, FAILED; fonte restaurada (`git status` limpo)
- S2 · head 40dc5f4f, as 54 formas de applet × 3 cargas × 2 papéis e os 5 usos legítimos · espera: rc 2 nas cargas, rc 0 nos legítimos · obtido: `AtualizacaoAtrasDoBusybox`, 2 testes OK

## Revalidação
- A6 da segurança: fechado no domínio do review. A varredura `atualizacao(palavras)` roda antes da troca pelo applet, com a linha inteira, como a do `busybox` em ENVOLVEDORES na base; o recorte fica igual ao da base (sem recusa nova fora dela). O aceite do A6 é da segurança (E1.19).
- A1 e A2: seguem recomendados, sem mudança no código deles.

## Verificação
- Testes do delta: `python3 -m unittest tests.test_conformidade_verde.AtualizacaoAtrasDoBusybox`: 2 testes, OK (20 s).
- Mutantes: `bin/forge-mutante --cobertura --base bdbdc257`: rc 0, spec -10 editada, 7 mutantes (até 8); M72 morto (S1). Teste roda subprocesso com `-I` e ambiente do `CloneDoForge`.
- Suíte inteira: não rodada (brief); sem PR, CI do head não citável.

## Parecer
Aprovado. A guarda nova de uma linha devolve ao `busybox`/`toybox` com applet a varredura de atualização que a base tinha; teste de comportamento do ramo de falha e mutante declarado e morto.
