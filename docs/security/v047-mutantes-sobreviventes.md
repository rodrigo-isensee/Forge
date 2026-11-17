---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-mutantes-sobreviventes
commit: f39e95a6ee8b80067bcc90141c1a04802a0f0a0a
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047 (mutantes sobreviventes, E2.566)

Parecer completo (não havia parecer de segurança nesta branch), contra a develop, sobre o Revisar-sha f39e95a6 (o head 9e0f845f só acrescenta `docs/qa/` e `docs/reviews/`, sem código nem spec).

Gatilhos: guarda ou controle de conformidade tocado só por teste e spec de mutante (R-SEGURANCA); nenhum código de produção muda.

## Escopo lido
- Diff contra `origin/develop`: 5 arquivos de teste, 2 specs em `tests/mutantes/` e o fragmento do changelog. `bin/`, `hooks/`, `agents/`, `skills/` e workflows ficam intactos.
- Nenhuma guarda ficou mais fraca. Os testes só acrescentam asserções; nenhum `skip`, `expectedFailure`, variável de ambiente ou afrouxamento de asserção existente.
  - `tests/test_conformidade_verde.py`: linha ilegível passa a recusar quando cita a prova (tech-lead e sem papel) e a liberar quando não cita; endurece a guarda de leitura fora de projeto.
  - `tests/test_forge_mutante.py`: equivalente inválido com um mutante que morre ainda dá rc 2; endurece.
  - `tests/test_governanca.py`: tokens do pedido nas métricas (`=40` e `=-`); endurece.
  - `tests/test_mensagem_conferente.py`: `Desde` com commits reais; teste novo.
  - `tests/test_forge.py`: o conflito em arquivo livre agora força o merge simulado de verdade (o `src/x.txt` da base funde limpo); o teste continua afirmando o mesmo veredito e fica mais forte, pois antes o ramo podia não rodar.
- Specs: `pr-verde-lote-check.json` M8 só ganha o sufixo `; E1g; E2.252` no `de` e no `para`, e passa a casar a linha 1785 como na develop; `t6t3-mensagem.json` acrescenta um teste a duas specs (mais testes que matam, nunca menos).

## Verificação
- Testes dos arquivos tocados, no clone, sem `-I`: `test_conformidade_verde` 11 OK; `test_forge_mutante` 124 OK; `test_governanca` 50 OK; `test_mensagem_conferente` 18 OK; `test_forge.PrAposMergeDaBase` 12 OK. Suíte inteira: CI do PR (ordem do dono de 16/11: sem suíte local completa).
- `bin/forge-mutante tests/mutantes/pr-verde-lote-check.json`: M1 a M8 morreram; M8 em `bin/forge-check:1785` (a guarda D4 segue observada).
- `bin/forge-mutante tests/mutantes/t6t3-mensagem.json`: 16 de 16 morreram.
- `bin/forge-mutante --conferir --base 4068c807`: o trecho de cada spec do diff está no lugar.
- Varredura de segredo e de dependência: sem arquivo de dependência nem credencial no diff; `gitleaks` e `osv-scanner` não rodados aqui (diff só de teste e JSON; roda no CI).
- Os testes usam repositório temporário com `-c user.email=t@example.com`, sem rede e sem escrita fora do `tmp`.

## Achados

## Sondas

## Detalhe dos achados
Nenhum achado. Sem superfície nova: o item só fortalece prova de guardas existentes. A2 do review (lista de dois testes na mesma linha em `t6t3-mensagem.json`) é de estilo e pertence ao `tech-lead`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `bin/forge-mutante`, `unittest`. Lacuna: `gitleaks` e `osv-scanner` não executados localmente (CI do PR).
