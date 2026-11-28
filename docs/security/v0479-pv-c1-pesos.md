---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-c1-pesos
commit: a94644bcdf3a3407f4ea92ed98389050e5c644f6
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-pv-c1-pesos

Escopo: o diff `5ccac0bf..a94644bc` (PR-VERDE C1, v0478 E57.3/E57.4): `tests/test_forge.py` (classe `PesosDaSuite` e as funções `modulos_de_teste`, `violacoes_de_peso`, `base_do_pr`), uma linha no resumo de `scripts/suite-paralela.py:671`, uma asserção em `tests/test_suite_paralela.py:846`, a linha da marca de versão em `skills/trabalho-em-paralelo/ritmo-e-corte.md:49` e o fragmento do changelog. Revisão estática; nada publicado nem alterado fora deste parecer.

## Gatilhos
Gatilhos: nenhum no diff (sem `.github/`, `hooks/`, `docs/regras/`, `tests/catraca.py`, `tests/config.json`, segredo ou dependência); portão pedido pelo brief E57.35.

## Veredito
**Aprovado.** A regra trocada (limite global de 20% de módulos sem peso pela regra por PR) é de equilíbrio da divisão da suíte, não um controle de segurança: o peso só reparte os módulos entre as pernas e não decide o que roda nem o veredito.

Pontos conferidos:
- `tests/test_forge.py:7262-7281`: `git merge-base` e `git ls-tree`/`git show` com lista de argumentos e `ambiente_limpo()`, sem shell nem entrada do PR interpolada em comando. Falha fechada: sem merge-base a asserção reprova (`:7275`); `pesos-d4.json` ilegível na cabeça levanta exceção e reprova; só a ausência do arquivo na base vale `{}`, o que deixa a regra mais estrita, não mais frouxa.
- `tests/test_forge.py:7237-7250` (`modulos_de_teste`): só nomes identificadores sob `tests/`, como o `modulos()` do runner; não há caminho fora da árvore.
- `skills/trabalho-em-paralelo/ritmo-e-corte.md:49`: o comando novo usa `python3 -I scripts/pesos-do-ci.py`, script pré-existente que só lê a API (execuções `push` da `develop` do próprio repositório, anotação validada, segundos finitos com teto) e não imprime o token; o arquivo gerado é conferido e commitado por quem roda, sem escrita automática (`R-MAIN`, `R-VERIFY`).
- Caminho de abuso considerado: um PR que forja peso em `tests/pesos-d4.json` para um módulo novo passa a regra, mas o máximo que obtém é uma divisão desequilibrada (tempo de CI), sem pular teste nem mudar veredito; quem abre o PR já controla o próprio código. Sem caminho de ataque realista, sem achado.

## Achados

## Sondas

## Detalhe dos achados
Sem achados.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Suíte inteira: não rodada localmente (brief E57.35: sem suíte local; vale o CI do PR). Rodado o teste novo: `python3 -m unittest tests.test_forge.PesosDaSuite` · 3 testes, OK. Ferramenta ausente no ambiente: o varredor de segredos (não está no PATH; lacuna registrada, nada instalado); o diff não toca configuração nem credencial.
