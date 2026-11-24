---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-vigia-trava-critica
commit: aa0f55f8ae0829ad1e958c543e259d5ff6cb6b92
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0478 (E169.9, PR #853), revalidação por delta

Escopo: delta `cf8b8f69..aa0f55f8` (`forge-check parecer delta`), sem o que veio da develop. Commit próprio da branch no intervalo: `160ab342` (E169.6). O resto (`hooks/ordens.py`, `hooks/hooks.json`, ADR 0003 item "ordens", `tests/test_hooks.py` ramo `contexto` e `reason`) vem da develop pelo merge de `fde1e76b` (PR #805, com parecer próprio) e fica fora deste parecer; o merge `aa0f55f8` só resolve conflito em `docs/hooks-fixtures.md` (gerado).

## Gatilhos
Gatilhos: controle de hook que decide recusar ou liberar (falha fechada por prazo, ADR 0009 seção 7)

## Detalhe dos achados
Conclusão por escrito: o delta é **neutro** no código (nenhuma linha de `hooks/`, `bin/`, `scripts/`, `.githooks/` ou `.github/` da branch muda desde `cf8b8f69`) e **só aperta** nos testes: um teste que aceitava a liberação sem marcador passa a exigir a recusa.

- **Delta lido.** `tests/test_hooks_volta_propriedades.py:224-228`: o caso "sem marcador" de `test_t_vigia_de_prazo_recusa_com_marcador_e_libera_sem` esperava `(0, "")`; agora espera código 2 e `^<regra>: o hook não decidiu`, nos dois hooks (`conformidade`, `parecer`). É o que `hooks/_comum.py:2860` já faz desde `cf8b8f69` (aprovado na rodada anterior); o teste antigo é que estava desalinhado. Nenhuma asserção de recusa foi afrouxada.
- **Mutantes realinhados.** `tests/mutantes/heredoc-donos.json` D11 passa a reinserir a isenção antiga (`hook.marcado is False`) no retorno antecipado de `hooks/_comum.py:2860`; D12 força o texto genérico em `:2863`. As duas âncoras casam uma vez só no arquivo. `bin/forge-mutante tests/mutantes/heredoc-donos.json --ids D11,D12` no head: os dois morreram. A guarda nova de D11 é mais forte que a antiga: mata a volta da isenção inteira, não só a do corpo pendente.
- **`docs/hooks-fixtures.md`:** índice gerado, sem efeito de segurança.
- **Já lido na rodada anterior (estado):** retorno antecipado, saídas que ainda liberam (`critico is None`, `PostToolUse`, sessão não vigiada) e disponibilidade: sem mudança no delta, a conclusão de `cf8b8f69` segue.
- **Provas.** `python3 -m unittest` de `test_t_vigia_de_prazo_recusa_com_marcador_e_libera_sem` e `test_prazo_vencido_com_corpo_de_heredoc_pendente_recusa` no head: 2 testes, OK. Suíte inteira: no CI do PR #853 (em andamento quando este parecer foi escrito; o merge depende dele verde).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, `forge-check parecer delta`, testes e mutantes do próprio PR. Varreduras de segredo e SAST fora do escopo do delta (só testes e índice); as ferramentas não estão no PATH deste ambiente (lacuna registrada, sem efeito aqui).
