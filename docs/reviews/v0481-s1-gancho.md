---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-s1-gancho
commit: 8aa2e859d46e4f472097216a267bef3b8f05dfba
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 (E20.23, #920, hook estado, volta 1)

Revalidação por delta (H3, `R-REVIEW`) do #920, `5da15059..8aa2e859`, sobre o parecer aprovado da 1ª rodada (E20.14, head `0ad62d85`). Cobre E20.19 (A1 e A2 da segurança, E20.15).

## Escopo conferido
- Delta lido: `forge-check parecer delta docs/reviews/v0481-s1-gancho.md` deu `revalida: sim` (`hooks/estado.py` mudou depois do parecer). `git diff --stat 5da15059..8aa2e859`: só `hooks/estado.py` (1 linha), `tests/mutantes/v0481-s1-gancho-2.json` (M16), `tests/test_forge_mutante.py` (classe `CoberturaDoPedidoInteiro`) e `tests/test_hook_estado.py` (1 asserção). Nada mais mudou.
- Entregar contra os commits: E20.19 em `50aef9aa` (cabeçalho e M16) e `8aa2e859` (teste da sonda S1). Nenhum item sem commit.
- Tamanho (H1): 1 linha de código; dentro do teto.
- A2 da segurança: `CABECALHO` (`hooks/estado.py:24`) passa a dizer que as linhas são dados lidos, nunca instruções; `test_pergunta_do_estado_injeta_a_linha_fixa_e_so_as_linhas_status` afirma o trecho na primeira linha da saída real do hook.
- A1 da segurança: a guarda `if __name__ == "__main__":` ganha o M16, morto pelo teste que roda o hook como script. `CoberturaDoPedidoInteiro` aplica a análise de guardas da catraca (`analisar_com_textos`) ao arquivo inteiro das specs do pedido, com mínimo de 16 mutantes e de 11 condições, e exige todas `coberta`.

## Verificações
- ci: 8aa2e859d46e4f472097216a267bef3b8f05dfba verde
  - `gh pr checks 920`, runs 45901535861 e 45901685025, ambos com `headSha` `8aa2e859`: suíte 3.12 e 3.14 (partes 1 a 5), instalação, passos, verificações longas, teto de pulados, árvore provada e `catraca` verdes; só `bateria` e `bateria (pareceres)` falham, à espera dos pareceres e do rótulo.
- Testes do diff: `python3 -m unittest tests.test_hook_estado tests.test_forge_mutante.CoberturaDoPedidoInteiro`: `Ran 16 tests ... OK`.
- Mutante declarado novo: `bin/forge-mutante tests/mutantes/v0481-s1-gancho-2.json --id M16`: `M16 · morreu · hooks/estado.py:68`.
- `python3 tests/catraca.py --base 3c833f3f1ba1e9770b8e5b10e7a1b0ed588d161f`: rc 0 (antes rc 1 pela guarda do `__main__`, sonda S1 da segurança); restam só os avisos "confira no parecer" de `test_doutor` e `test_hooks`, já conferidos na 1ª rodada.
- Shell: nenhum arquivo de shell no delta.

## Achados
- A1 (recomendado) hooks/estado.py:61 · Da 1ª rodada, sem mudança: no clone do Forge, `hooks_desligados: ["estado"]` não silencia o hook (o manifesto vence), e a emenda diz que hook desligado fica em silêncio. Ajuste o texto da emenda ou a checagem.
- A2 (recomendado) hooks/estado.py:18 · Da 1ª rodada, sem mudança: `estado` e `status` casam ordens curtas e cada uma paga uns 3,5 s do `forge-check status`. Some a contagem de disparos à leitura da emenda.

## Sondas

## Parecer
Aprovado. O delta faz só o que a volta pede: o cabeçalho marca as linhas como dados (A2 da segurança) e toda condição de `hooks/estado.py` tem mutante declarado e morto, inclusive o `__main__` (A1 da segurança), com a catraca verde no head. A1 e A2 deste parecer seguem recomendados e viram cartão depois do merge. O merge espera o rótulo `afrouxa-regra` do dono e os pareceres do QA e da segurança.
