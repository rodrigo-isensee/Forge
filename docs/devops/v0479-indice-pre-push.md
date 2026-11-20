# Patch do pre-push: índice no envio leve (v0478 E45.1, INDICE-NO-PRE-PUSH)

`.githooks/pre-push` é arquivo em vigor, travado para os agentes. O patch `docs/devops/v0479-indice-pre-push.patch` é para o dono aplicar. Ele roda `scripts/indice-forge.py --conferir` e `scripts/indice-fixtures.py --conferir` nas checagens baratas do envio. Só confere, nunca grava. Roda quando o envio altera algo e a ferramenta existe na árvore. Reprovado, a mensagem diz o comando que regenera.

## Sha256 do patch
`3d3456584fadbeaef4b944396f50294416d0f0038391239cda899f1fe4710fc7`

## Aplicar (dono, a partir de uma branch `melhoria/*` em dia com a `develop`)
```
cd <clone do Forge> && echo '3d3456584fadbeaef4b944396f50294416d0f0038391239cda899f1fe4710fc7  docs/devops/v0479-indice-pre-push.patch' | sha256sum -c - && git apply docs/devops/v0479-indice-pre-push.patch && git add .githooks/pre-push && git commit -m 'fix(envio): índice no envio leve do pre-push (INDICE-NO-PRE-PUSH)'
```
Conferir antes, sem alterar nada: `git apply --check docs/devops/v0479-indice-pre-push.patch`. Aplica limpo sobre a `develop` em `0ce05485`.

## Tempo que acrescenta (cópia em `$TMPDIR`, patch aplicado)
- Isoladas, na árvore inteira: `indice-forge --conferir` 3,7 a 5,0 s; `indice-fixtures --conferir` cerca de 1,0 s. Soma de 5 a 6 s.
- Hook inteiro na árvore inteira: sem patch 2,0 s (mediana de 5); com patch 7,1 a 9,6 s (mediana 9,0 s). Acréscimo de cerca de 5 a 7 s por envio que altera algo.
- Repositório mínimo do teste: 0,72 s sem patch, 1,32 s com patch (mediana de 5).

## Prova
- Arquivo novo sem linha no índice: com o patch, o envio sai 1 com `docs/indice-forge.md: desatualizado` e `regenere com 'python3 scripts/indice-forge.py'`. Sem o patch, o hook deixa o arquivo passar nessa checagem (o CI é que reprovava).
- Índice em dia, ou regenerado depois, passa (`plano=leve rc=0`).
- Fixture novo sem linha barra com `python3 scripts/indice-fixtures.py`. Ferramenta ausente não barra.

## Teste
`tests/test_pre_push_indice.py` (6 casos). Copia o hook para `$TMPDIR`, aplica o patch na cópia se o dono ainda não aplicou e roda o hook num repositório descartável. Sem skip: passa antes e depois da aplicação.

Mapa: o teste lê o patch e as duas ferramentas; `bin/forge-testes` ganha as regras do MAPA para eles (como a do `pp1-pre-push.patch`), senão o envio dirigido pularia o teste (`MapaCobreOQueOsTestesLeem`). Fora da lista de arquivos do brief, por necessidade do teste.

Revisão do patch: `security-engineer` (o pre-push é controle). Sem PR nesta etapa.
