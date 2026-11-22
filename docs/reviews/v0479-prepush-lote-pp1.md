---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-prepush-lote-pp1
commit: ce1dc90c2fd20b2a6049b11ac8b9afdcecfbede2
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E94.6, melhoria/v0479-prepush-lote-pp1)

Escopo: revalidação (H3, `R-REVIEW`) do delta `51648bfe..ce1dc90c`, lido só por `forge-check parecer delta docs/reviews/v0479-prepush-lote-pp1.md`. No domínio: `bin/forge-testes`, `changelog.d/v0479-prepush-lote-pp1.md`, `tests/test_prepush_lote_pp1.py` e `tests/test_testes_tocados.py`. A rodada anterior (E94.2, head 51648bfe) reprovou pelo A1. A suíte inteira fica com o CI do PR e não foi rerrodada.

## Achados
- A2 (recomendado) docs/propostas/prepush-lote-pp1.md:67 · O comentário fala em "envio de código", mas a condição avisa em qualquer envio com a base e a lista vazia. Ajuste o texto ou a condição. Vira cartão depois do merge.

## Parecer
Aprovado. O A1 está resolvido.

- **A1 (fechado):** a variável `MUTANTE` saiu. O teste agora usa o caminho literal `bin/forge-mutante`, tanto na cópia quanto nos dois falsos. O MAPA do `bin/forge-testes` ganhou uma linha com a regra `bin/forge-mutante` → `test_forge_mutante`, `test_forge`, `test_prepush_lote_pp1` e `test_pre_push_patch`.
- **Mapa:** `bin/forge-testes --listar bin/forge-mutante` no ce1dc90c devolve `dirigido (test_forge, test_forge_mutante, test_indice_forge, test_oraculo_sempre_atual, test_oraculo_v047, test_pre_push_patch, test_prepush_lote_pp1)`. Os dois módulos que rodam a cópia estão na lista.
- **Sonda S1 refeita:** com o literal, `MapaCobreOQueOsTestesLeem` passa, então o mapa cobre o que o teste executa.
- **Ajustes em `test_testes_tocados`:** os dois testes acompanham a regra nova. `bin/forge-mutante` sai da lista de caminhos sem regra, e o teste de renomeação cria os três módulos que o mapa cita. A regra é uma exceção real à convenção, e `Convencao` passa.
- **Registros:** `bin/forge-testes --registros --base fb3b670b` (o Base-sha, e não a origin/develop, que já está na 0.47.14) termina com `registros rc=0 em 19 s (9 conferências e o peso dos módulos de teste novos)`.
- **Testes tocados:** `MapaCobreOQueOsTestesLeem`, `Convencao`, `Execucao.test_arquivo_mapeado_renomeado_inclui_os_modulos_do_caminho_antigo` e `test_prepush_lote_pp1.CoberturaDaCatraca` rodaram 19 testes, todos OK.
- **Fragmento:** a linha nova descreve a regra do mapa e o literal, dentro do pedido.
- **Fora do delta:** o resto da rodada E94.2 continua valendo, porque a volta não tocou a proposta nem as specs de mutante.
