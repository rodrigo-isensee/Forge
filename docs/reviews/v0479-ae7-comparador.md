---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae7-comparador
commit: 5961e2f3a30a4209a940a9745fe02a1b3a24f39c
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E58.32, AE7.1 `forge-check comparar`)

Diff `821db42e..5961e2f3` lido contra o AE7 de `docs/propostas/v0479-melhorias-anti-erro.md` (seção AE7 e linha AE7.1 da tabela).

## Conferido
- Desenho (a): extrai os dois shas por `git archive`, roda o corpus nos dois lados, saída `so-aperta: medido base= head= corpus=<sha256> casos= aceites-novos=` mais uma linha por transição; corpus da base somado aos casos novos do head, caso tirado ou mudado no head sai `corpus-removido` e roda como a base o escreveu. Limite do corpus finito declarado no módulo e no changelog.
- Riscos da linha AE7.1: caso removido (testes `Corpus`), hook que detecta o comparador (`ComoOClaudeCode`), sha fora do repositório e ref com opção ou intervalo (`Refs`).
- Medida real: `bin/forge-check comparar 821db42e 5961e2f3` deu rc 0, `casos=215 aceites-novos=0`. O corpus exercita os hooks de verdade: na árvore da base, 174 dos 215 casos saem `recusa` e 41 `aceite` (rodado caso a caso pelo `rodar_caso`).
- Teste novo: `python3 -I tests/test_comparar.py`, 30 testes OK em 5,2 s.
- Mutantes (R-REVIEW, V2): `bin/forge-mutante --processos 1` nas 4 specs, 31 de 31 morreram (CMP31 por erro do teste sob o mutante); `--cobertura --base 821db42e` sem guarda descoberta (a linha 138, teto do pool, isenta com motivo).
- Nomes repetidos: `grep -oE '^def [a-zA-Z_0-9]+' bin/forge-check | sort | uniq -d` vazio no head (538 funções) e na base.
- Tamanho (H1): 143 linhas no módulo mais 5 no `bin/forge-check`, dentro do teto.
- `filter="data"` do `tarfile` existe nas versões do CI (3.12 e 3.14); changelog no fragmento da branch; `forge-testes` e `pesos-d4.json` listam o `test_comparar`.
- `praticas.md` sem regra "decidida por: leitura"; suíte inteira fica com o CI (R-CUSTO), não rerrodada aqui.

## Achados
- A1 (recomendado) bin/forge_comparar.py:101 · `permissionDecision: allow` e "sem decisão" viram o mesmo ACEITE; um head que passe a emitir `allow` (pula o pedido de permissão ao usuário) não aparece como aceite-novo. Separar `allow` num quarto nível acima de ACEITE.
- A2 (recomendado) bin/forge_comparar.py:137 · base e head rodam intercalados no mesmo pool e na mesma pasta temporária: um hook do head pode reescrever a árvore da base antes dos casos seguintes. Rodar todos os casos da base antes do primeiro hook do head (ou a árvore da base só leitura).
- A3 (recomendado) bin/forge_comparar.py:114 · os hooks rodam com o HOME real: leem `~/.forge-contrib` e `~/.forge/maquina` da máquina (veredito depende dela) e um caso pesado futuro pegaria a trava real sem o PostToolUse que a solta. HOME temporário igual nos dois lados.

## Sondas

## Parecer
Aprovado. O AE7.1 entrega o que o desenho pede, com os três riscos da linha AE7.1 cobertos por teste de comportamento e todos os mutantes mortos; a medida real no par base/head deste item dá zero com 174 recusas exercitadas. Os três achados são recomendados (R-REVIEW): endurecem a medida contra um head adversário e contra o estado da máquina, sem defeito provado no uso descrito; viram cartão depois do merge. A2 e A3 tocam o parecer do `security-engineer` (R-SEGURANCA), que os decide.
