---
tipo: revisao-seguranca
contrato: 1
pedido: lote-mutante
branch: melhoria/lote-mutante
commit: 786505960a19cb0ec3ba4ae30f454031625e75c7
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-26
---
# Review de segurança: lote-mutante

Pedido LOTE-MUTANTE-REV, etapa E2.1. Diff revisado: `b6eb84fed86e3b5289f3950b33d43a86f34343c2...786505960a19cb0ec3ba4ae30f454031625e75c7` (`bin/forge-mutante`, `tests/test_forge_mutante.py`, `tests/mutantes/lote-mutante.json`, `changelog.d/lote-mutante.md`).

## Gatilhos
Controle do Forge (`R-SEGURANCA`): o `forge-mutante` produz a evidência de mutantes que o QA cola no parecer, e ele analisa uma entrada (a spec e os ids de teste). Não é portão: nenhum hook, pre-push, CI ou `forge-check` o chama. Sem segredo, rede, workflow nem dependência nova.

## Achados

## Detalhe dos achados
Sem bloqueante. As três perguntas do brief foram verificadas por sonda (repositório de brinquedo em `$TMPDIR`, script do commit revisado):

- **Várias specs driblam o teto?** Não por repetição: a mesma spec duas vezes e um link simbólico para ela saem 2 com `id de mutante repetido entre as specs` e nada roda (`bin/forge-mutante:230`). Specs de pedidos diferentes saem 2 (`bin/forge-mutante:228`). O teto de 8 continua por spec (`bin/forge-mutante:182`). Não há teto total: N specs com ids distintos rodam N×8 mutantes. Isso é o pedido (E1, "sem subir o teto por spec", `confirmado`), e não há atacante: quem roda é o próprio operador, na própria máquina.
- **Um id não ASCII aponta para fora de `tests/`?** Não. `id_de_teste_valido` (`bin/forge-mutante:209`) exige `tests` exato na primeira parte e `str.isidentifier` nas outras; a sonda recusou ponto de largura total, ponto ideográfico, um-ponto-guia, barra de divisão, barra de largura total, barra invertida, `/`, NBSP, U+2028, BOM, RLO, `..`, ponto final e `tests` com T cirílico. Nenhuma parte carrega separador de caminho, e os ids vão ao `unittest` por argv, sem shell (`bin/forge-mutante:137`). Homóglifo (`а` cirílico, ligadura `ﬁ`) passa na validação, mas o carregamento é por igualdade literal de nome e o veredito exige que o teste declarado rode (`bin/forge-mutante:165`): um id que não existe na cópia dá `controle vermelho` ou `inválido`, nunca `morreu` (provado na sonda).
- **Spec inválida no meio ainda roda alguma mutação?** Não. Todas as specs são lidas e validadas antes de `principal` (`bin/forge-mutante:367` a `:381`); com `s1 bad s3` a saída foi `spec 2: de 1 a 8 mutantes`, código 2, sem nenhuma linha de mutante. A spec ilegível no meio também sai 2 antes de rodar.

Recomendações, sem devolver:
- **R1 (informativa)** `bin/forge-mutante:215` · `str.isidentifier` aceita os caracteres de formato invisíveis U+200C e U+200D (categoria Cf), e o Python aceita os mesmos em nome de função. Caminho: quem escreve a spec declara um teste cujo nome difere de outro só por um caractere invisível, e o QA lê o id como se fosse o outro. A evidência continua verdadeira (o teste declarado existe, passa no controle e falha no mutante), então o ganho é só confundir a leitura humana. Correção mínima: recusar parte com caractere de categoria `Cf` (`unicodedata.category`) ou imprimir os ids com `ascii()` na saída. Esforço P. Dono: tech-lead.
- **R2 (informativa)** `bin/forge-mutante:302` · sem teto total nem orçamento de tempo do conjunto: cada mutante clona o repositório e roda até dois processos com `--prazo` de até 3600 s. Um teto do conjunto (por exemplo, 4 specs) e a lista dos caminhos das specs junto dos hashes na linha de cabeçalho deixariam a evidência mais fácil de conferir. Esforço P. Dono: tech-lead.
- **Fora do diff, sem mudança aqui:** a travessia por atributo (`tests.test_lib.os`) já era aceita pela regex antiga; com ela, o `unittest` chama um objeto chamável que não é teste. Nesta sonda deu `controle vermelho`. A entrada é a spec do próprio pedido, versionada pelo autor, que já executa código do repositório ao rodar os testes, então não há ganho para quem ataca.

Achados recorrentes (`docs/engineering/achados-recorrentes.md`, PA-7): a lista está vazia; nada a conferir nem a acrescentar.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes do lote: `python3 -m unittest tests.test_forge_mutante`, 35 testes OK. Sondas manuais com o script do commit revisado. Ferramentas ausentes no PATH (lacuna, não instaladas): gitleaks, semgrep, osv-scanner, zizmor, actionlint; o diff não toca workflow, dependência nem segredo.
