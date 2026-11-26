---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-s1-status
commit: 154a36f1283ebb81be649cf08e1235f4636ba6a6
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (E20.9, #910, volta por delta)

Gatilhos: controle do Forge (bin/forge-check, despacho novo; bin/forge-testes), leitura do gh e de docs/pedidos, saída lida pelo Jarvis.

Delta lido: `git diff 0b412b4a..154a36f1` e `forge-check parecer delta`: no domínio só bin/forge_estado.py:100 (`fromisoformat` trocado por `instante`); fora do domínio, conferidos para a prova: tests/test_forge_status_estado.py (+5 testes), tests/mutantes/v0481-s1-status-5.json (M33, M34), docs/indice-forge.md (+1 linha). O resto do diff são os pareceres.

## Estado dos achados anteriores
- A1 (bloqueante) resolvido: bin/forge_estado.py:100 passa por `instante` (:21-26), que converte o ValueError em NaoVerificavel; `executar` (:131-133) já o apanha. A sonda S1 virou teste literal (`test_pergunta_com_mes_13_pela_raiz_de_pedidos_nao_verificavel_e_rc_0`, mesma entrada e mesmos argumentos) e há o caso 2026-02-30 na unidade e pelo forge-check: seis linhas, rc 0, sem traceback. Data inválida que não é a mais antiga na ordenação não afeta a linha (só `horas[0]` é lida).
- A2 (recomendado) resolvido: `test_titulo_com_esc_e_u2028_sai_limpo_pelo_forge_check` usa a limpeza real (`sem_controle`) com o gh falso devolvendo ESC e U+2028 no título; `test_linha_impressa_passa_pela_limpeza_do_contexto` cobre a unidade. M34 (tirar `ctx["seguro"]`) morre nos dois.

## Aperta, neutro, afrouxa
- **Aperta:** data fora do calendário num pedido não derruba mais o comando (disponibilidade do controle que impede o Jarvis de afirmar estado de memória); a limpeza de caracteres de controle da saída passa a ter teste e mutante.
- **Neutro:** a linha nova em docs/indice-forge.md (resolve o vermelho da parte 3/5 da 1ª rodada); os testes e a spec de mutantes.
- **Afrouxa:** nada. Nenhuma guarda mexida no delta; a catraca segue pedindo o rótulo `afrouxa-regra` só por bin/forge-check tocado na 1ª rodada (decisão do dono, R-CONFORMIDADE, R-DECISAO).

## Provas
- ci: 154a36f1283ebb81be649cf08e1235f4636ba6a6 verde
- CI do head (runs 45829599149 e 45829598981, headSha conferido): as dez partes da suíte (3.12 e 3.14), teto de pulados, passos, verificações longas, instalação e árvore já provada verdes. Vermelhos, pelo log: `bateria (pareceres)` por falta dos pareceres aprovados desta volta (R-REVIEW, R-QA; este parecer é um deles); `bateria` é o agregador e cai só por `pareceres: failure`; `catraca` por bin/forge-check sem o rótulo `afrouxa-regra` do dono (R-CONFORMIDADE). Nenhum é defeito do código.
- `python3 -m unittest tests.test_forge_status_estado`: 24 testes OK.
- M33 e M34 aplicados à mão numa cópia (`git archive` do head; o `bin/forge-mutante` ficou barrado pelo R-TETO por tarefa pesada de outra sessão): M33 FAILED (failures=2, errors=2) nos três testes da data; M34 FAILED (failures=2) nos dois da limpeza. Os dois morrem.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: git, unittest, `gh pr checks` e logs dos jobs pela API (só leitura). gitleaks e zizmor não se aplicam ao delta (sem segredo nem workflow).
