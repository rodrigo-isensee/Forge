---
tipo: revisao-seguranca
contrato: 1
pedido: impl-fechar-c
branch: melhoria/impl-fechar-c-c4
commit: 15fbea0a8d0f1b2a1bd7a83b43b6817fd7ba2be4
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
- A1 (recomendado) tests/test_fechar_corrida_rotulo.py:64 · O teste do AB-C4-4 faz falhar toda leitura do rótulo, não só a posterior: o rótulo nunca é visto e o teste passa com qualquer regra. Um mutante medido (leitura que falha descarta) passa os 20 testes. Dono: qa-engineer.
- A2 (recomendado) tests/test_fechar_corrida_rotulo.py:72 · Sem teste para AB-C4-5 (descartada em skipping com velha) e AB-C4-7 (rótulo retirado durante a espera); o código os cobre por leitura, mas nenhuma asserção os prende. Dono: qa-engineer.

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
