---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-prepush-lote-pp1
commit: ce1dc90c2fd20b2a6049b11ac8b9afdcecfbede2
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478 (E94.7, revalidação do lote PP1 do pre-push do Forge)

Gatilhos: hook de envio do Forge (controle, arquivo travado; a entrega é proposta de diff que o dono aplica), R-VERIFY.

## Volta por delta
A rodada anterior (E94.3, head `51648bfe`, aprovado sem achados) está no git e não é recopiada aqui. Os pontos dela (só aperta, lista vazia com aviso, trava por `/proc/self/fd/9`, intervalo da fila) não foram tocados pelo delta.

Delta lido (`forge-check parecer delta`, `51648bfe..ce1dc90c`): no domínio, `bin/forge-testes` e `tests/test_prepush_lote_pp1.py`. Fora do domínio: `tests/test_testes_tocados.py` e `changelog.d/v0479-prepush-lote-pp1.md`.
- `bin/forge-testes:207`: uma regra nova no `MAPA`, `bin/forge-mutante` → `test_forge_mutante`, `test_forge`, `test_prepush_lote_pp1`, `test_pre_push_patch`. O casamento é por `re.fullmatch`, e a regra só pega o caminho exato. O efeito é só acrescentar testes à seleção do envio local. Nada sai da seleção, nenhuma checagem é pulada, e o CI do PR continua rodando a suíte inteira. Sem caminho de ataque.
- `tests/test_prepush_lote_pp1.py:225-293`: a constante `MUTANTE` dá lugar ao caminho literal `bin/forge-mutante`. Não há mudança de comportamento, e o falso continua gravado só no repositório de brinquedo.

Achados anteriores: nenhum.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum.

Ferramentas e evidência:
- `bin/forge-testes --listar bin/forge-mutante`: a seleção dirigida inclui os quatro módulos da regra (mais os da convenção).
- `python3 -m unittest tests.test_prepush_lote_pp1 tests.test_testes_tocados`: 229 testes OK (1 skip), no head `ce1dc90c`.
- Suíte inteira: só no CI do PR, que não foi citado no brief. O merge depende do CI verde.
