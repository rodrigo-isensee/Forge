---
tipo: revisao-seguranca
contrato: 1
pedido: impl-fechar-c
branch: melhoria/impl-fechar-c-c4
commit: 0ffbc737bc1227d11134b5214f85b56d85c021dd
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-31
---
# Review de segurança: impl-fechar-c (branch c4)

Diff lido: `234dbe0..15fbea0` (bin/forge-fechar, tests/test_fechar_corrida_rotulo.py, tests/test_fechar_espera_catraca.py, docs/fechamento-integrador.md, changelog.d/impl-fechar-c-c4.md). Relidos inteiros, no commit revisado, `estados_da_espera` e o laço dos passos 4 e 5.

**Item entregue:** E4 do pedido, FECHAR-B-REC-REVIEW item 3, pela opção B' do modelo de ameaças (`docs/security/ameacas/fechar-c.md`, SEC-FECHARC-1).

**M14 (agents/tech-lead.md:19):** um comportamento (quando a execução da Catraca vira velha); 101 linhas de código e teste, dentro do teto; nada em `hooks/` nem em `PROTEGIDOS`. Cumpre.

## Gatilhos
`R-SEGURANCA`: controles do Forge (a espera do rótulo do dono antes do merge).

## Achados

## Detalhe dos achados
Conferência dos controles:
- C4-1: as regras de `estados_da_espera` depois do rótulo e a saída do laço não mudam; só a linha do `rotulo_ok=0` passa de `run_antes` para `run_cand` (`bin/forge-fechar:345`).
- C4-2: em `:691`, com `pipefail`, a leitura que falha dá pipeline não zero e promove (conta como ausente); só a leitura que traz o rótulo descarta. Correto por leitura.
- C4-3: `run_cand` zera a cada decisão (`:696`) e não é consultada nas regras; `estados_da_espera` roda no mesmo processo (`:686`).
- C4-5: a leitura nova é `gh pr view --json labels` via `ler`; o teste de texto contra `run rerun`, `workflow run`, `-X POST` e `--method` segue verde.
- C4-6: no máximo uma leitura extra por volta, só com `esperar=1`, `rotulo_ok=0` e candidatas; a trava do head (`:675-676`) segue em cada volta.
- C4-7: em `tests/test_fechar_espera_catraca.py` só mudam o cenário (rótulo da 2ª para a 3ª leitura) e a docstring; nenhuma asserção sai.
- C4-8: `docs/fechamento-integrador.md` descreve a regra nova e o `cancel` antes do rótulo.
- Rodado aqui: `test_fechar_corrida_rotulo`, `test_fechar_espera_catraca` e `test_fechar`, 107 testes OK (1 pulado).

A1, detalhe: severidade baixa. Evidência: numa cópia descartável do commit (`git archive`), a linha `:691` trocada por uma que descarta quando `ler` falha; os 20 testes de `test_fechar_corrida_rotulo` e `test_fechar_espera_catraca` passam. Caminho: uma regressão futura que inverta o C4-2 passaria sem aviso; o efeito seria o risco informativo do modelo (§4: execução anterior ao rótulo contando como nova), que exige a Catraca passar sem rótulo no mesmo head. Correção mínima: no `gh` falso, falhar só a leitura de rótulo posterior aos checks (por exemplo, a N-ésima leitura de `labels`), com a velha em `fail` vista antes e o rótulo presente depois, e afirmar que não há merge (esforço P).

A2, detalhe: severidade baixa (cobertura). Correção mínima: dois testes no mesmo arquivo, no formato dos casos AB-C4-5 e AB-C4-7 do modelo (esforço P).

Nenhum dos dois devolve: o código está correto por leitura e o portão do merge (tudo `pass` ou `skipping`, head preso) não muda.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff e do script, testes da suíte e um mutante em cópia descartável. Faltaram no PATH: `shellcheck`, `gitleaks` e `semgrep` (lacuna).

## Revalidação (volta por delta)
`forge-check delta` de `15fbea0..0ffbc73`: `tests/test_fechar_corrida_rotulo.py` (+32, linhas 34-45 e 84-103) e `tests/mutantes/impl-fechar-c-c4.json` (+113). Delta lido inteiro. Nenhum arquivo de `bin/`, `hooks/`, `.githooks/` nem controle do Forge mudou; `bin/forge-fechar` é o mesmo do parecer anterior ("já lido").
- A1 e A2 do parecer anterior (recomendados) foram atendidos: o teste novo do AB-C4-4 falha só a leitura posterior do rótulo (a spec mapeia o mutante C4-2 a ele) e o do AB-C4-7 cobre o rótulo retirado na espera; ambos afirmam que não há merge. Os dois itens saem dos achados.
- Rodado aqui: `test_fechar_corrida_rotulo` e `test_fechar_espera_catraca`, 22 testes OK.
- A spec de mutantes só declara trocas em cópia; não executa nada no projeto.
Sem achado novo; o veredito se mantém.
