---
tipo: review
contrato: 1
pedido: maq-lote-a
branch: melhoria/maq-lote-a
commit: 8e8acf0a457d7b1a3810fcaa6cbad873b99751e1
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-24
---
# Review: maq-lote-a

## Achados
- A1 (recomendado) tests/test_forge.py:4862 · o teste de pesos só falha acima de 20% sem peso (13 de 64); um módulo novo sem peso passa; é o pedido (C5), só vale saber.

## Parecer
Aprovado. Diff lido inteiro (4 arquivos, 96 adições e 26 remoções; código e teste contados: 31 linhas, abaixo do teto M14).

- C5: `tests/pesos-d4.json` cobre os 64 módulos `tests/test*.py` (conferido por script: 64 de 64, nenhum peso órfão, soma 715 s); oito pesos 0.0 são aceitos por `ler_pesos` (`v >= 0`). `PesosDaSuite` calcula o mesmo conjunto de módulos do `suite-paralela` e falha acima de 20% sem peso, com mensagem que diz como regravar.
- A3 e A4: as frases em `agents/tech-lead.md:21-22` dizem o que as propostas A3 e A4 de `docs/propostas/estudo-maquina-aq.md` pedem (push em `run_in_background`, espera da notificação, só leitura até lá; mutação no diff do item, módulos do `bin/forge-testes --listar`, 1 processo, pela fila, suíte completa uma vez no push). Não contradizem o item 3 (teto do Bash) nem o resto do papel. O brief-padrão e o brief da V2 não são arquivos do repositório; o texto do repositório que existe é o do tech-lead.
- Testes de frase: `assertIn` com trechos literais das duas frases; se a frase some ou muda, o teste falha.
- Fragmento `changelog.d/maq-lote-a.md` presente; sem dependência nova; sem mexida em `hooks/`; `R-NEUTRO` e `R-CUSTO` preservadas. Segurança e QA são pareceres próprios, não refeitos aqui. Itens de `achados-recorrentes.md` sem ocorrência a conferir.
