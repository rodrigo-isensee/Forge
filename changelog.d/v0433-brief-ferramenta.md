### Adicionado
- `forge-check brief` e `brief selar` conferem o Entregar contra a fronteira de escrita do hook `conformidade` para o papel destino (VV-3): uma linha `escrita: ok|barrada|não conferida|não verificável` por caminho citado em crase ou na linha `- arquivos:`, pela função pública `conformidade.escrita_barrada` (só leitura, sem ambiente); `barrada` e `não conferida` reprovam e o brief fica sem selo antes do trabalho; caminho com `$ * ? [ <` é conferido pela pasta fixa antes da marca, e acima de 64 caminhos o excedente reprova.
- Código sem teste (T1): `forge-check pr` (no stderr) e `forge-check entrega --pedido` (etapa código) dão a linha `sem teste:` quando a entrega muda código sem mudar nem acrescentar teste (linha de comentário ou vazia não conta); a classe T fica isenta pela `classe_da_entrega` da 0.43.1, quando presente; a linha não reprova: o review confere a justificativa do PR.
- `forge-check parecer novo --tipo review|qa|seguranca|devops --pedido <p> --branch <b> --parecer aprovado|reprovado` imprime o esqueleto do parecer que o próprio `forge-check docs` aceita (frontmatter com os campos obrigatórios, `commit:`, `## Achados` e as seções do modelo) (Z7).
- AQ-5: o brief de review, segurança e QA leva `Revisar-sha:` (o código da branch sem os commits só de parecer), calculado pelo `brief gerar` e corrigido pelo `brief selar`; o `parecer novo` grava esse sha em `commit:`.

### Alterado
- `forge-check pr` recusa o parecer cujo `commit:` é um commit só de parecer (o HEAD depois dos pareceres paralelos) e dá o sha certo; o `commit não existe` ganha a mesma dica (AQ-5).

### Corrigido
- `brief gerar` num registro grande: o autorrelato lia cada pedido rodando um `git rev-parse`; agora reaproveita as raízes já calculadas (de 4 a 5 s para menos de 1 s no registro do Forge; o teste conta as chamadas ao git) (BRIEF-GERAR-TIMEOUT).
- `brief gerar --cobre` aceita a etapa escrita com o prefixo do plugin (`(forge:tech-lead)`), que antes saía como de outro papel.
