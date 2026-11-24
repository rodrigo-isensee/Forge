---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-zero-nao-medido
commit: 2cfb734c5d8e26e47cc794b4256c985a02aa7cd2
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0478 (E147.5, PR #834)

Escopo: diff `9d239dda..2cfb734c` (E147.1): `bin/forge_voltas.py`, `bin/forge_governanca.py`, ajuda do `bin/forge-check`, testes e mutantes. Ferramenta de métrica do Forge, só leitura de `docs/kanban/` e `docs/pedidos/`.

## Gatilhos
Gatilhos: nenhum (relatório de métrica sem entrada externa, sem portão, sem escrita, sem credencial)

## Achados

## Sondas

## Detalhe dos achados
Conclusão por escrito: a mudança **só aperta ou é neutra**; nenhum portão que lia 0 como aprovado passa a liberar com `nao-medido`.

- **Consumidores conferidos.** `resumo()` (`bin/forge_governanca.py:610`) é chamado só em `bin/forge_governanca.py:713` e `:725`, e o resultado vai só ao texto (`linhas_de_texto`, `:764-768`, que agora passa pelo `_n`) e ao JSON do `metricas`. O único outro leitor de `por_pedido`, `orcamento_de_tokens` (`:584-599`), lê só `tokens`, que a mudança não toca. A saída de `voltas` (`bin/forge_voltas.py:197`, `:211-213`) é só `print`. Busca em `hooks/`, `.githooks/`, `.github/`, `scripts/`, `skills/`, `agents/`, `docs/regras/`, `stacks/` e `templates/`: nenhum leitor de `voltas=`, `minutos=`, `prontos=`, `falhas=` nem de `voltas: total` como condição; `hooks/conformidade.json:111` só lista os comandos como de leitura permitidos.
- **Direção da falha.** Onde antes saía 0 (medido falso), sai `nao-medido`/`null`: um eventual consumidor futuro que compare com número cai em erro ou em "sem dado", nunca em "zero voltas, aprovado". Aperta.
- **Robustez.** Sem cartão, `voltas_do_cartao([])` não gera linha de tipo do quadro, então `contagem[tipo] += 1` só atinge `brief`, que segue inteiro (`bin/forge_voltas.py:186-188`): sem `TypeError` com a string. No `metricas`, `_n(None)` dá `nao-medido` (`bin/forge_governanca.py:740`).
- **Testes dos arquivos tocados:** `python3 -m unittest tests.test_voltas tests.test_governanca` no head: 99 testes, OK (1 skip preexistente). Suíte inteira: no CI do PR #834.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática e busca no código; segredo/SAST não se aplicam (sem gatilho) e as ferramentas de varredura não estão no PATH deste ambiente (lacuna registrada, sem efeito neste diff).
