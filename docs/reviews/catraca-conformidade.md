---
tipo: review
contrato: 1
pedido: catraca-conformidade
branch: melhoria/catraca-conformidade
commit: cae76b9
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Code review: catraca confere hooks/conformidade.json

Escopo: `origin/develop..0d34f53` (1 commit): `tests/catraca.py`, `tests/test_catraca.py`, `CHANGELOG.md`. Referências: ADR 0008, R-CONFORMIDADE.

## Checklist
- Faz o pedido: acusa remoção de caminho, ampliação de `quem`/`acoes`/`papeis`, perda ou troca de `so_forge`/`branch` e verbo de instalação removido; acrescentar ou restringir não acusa. Nada mais.
- Nenhuma checagem existente foi alterada; a nova entra só como soma em `violacoes_das_regras`. Violação é R-CONFORMIDADE (não R-CUSTO), então o rótulo do dono libera.
- Política ausente na base não acusa (arquivo novo); ausente no head acusa tudo (base com conteúdo, head vazio).
- Testes: 13 casos novos; vermelho antes (9 falhas sem a mudança), verde depois (238 OK). Cobrem remoção, ampliação, branch, acréscimo e rótulo.
- Só biblioteca padrão; sem custo; neutro.

## Observações (não bloqueiam)
- `papel_padrao`/`sem_agent_type` acusam em qualquer mudança (conservador).
- Como `tests/catraca.py` é protegido, este PR exige o rótulo `afrouxa-regra` do dono.

Parecer: **aprovado**.

## Review independente

Segunda leitura (outra instância do `forge:tech-lead`) sobre `origin/develop..fb376cd`. Testes no checkout do PR: `python3 -m unittest discover -s tests`, 238 OK. Os desvios foram conferidos chamando `afrouxamentos_da_politica` com a política real alterada, e a semântica de cada chave foi lida em `hooks/conformidade.py`.

### Desvios (afrouxa e a checagem não acusa)
1. `tests/catraca.py` (`CAMPOS_DE_ESCOPO`) · **bloqueia** · Acrescentar `so_forge: true` a uma entrada que não tinha a chave não acusa. No hook, `so_forge` faz a entrada ser pulada fora de um clone do Forge; em `.claude/`, por exemplo, a proteção some em todos os projetos. O teste `test_restringir_nao_acusa` trata isso como aperto e está errado. Sugestão: acusar quando `so_forge` passa a ser verdadeiro no head (`not c.get("so_forge") and novo.get("so_forge")`) e corrigir o teste.
2. `tests/catraca.py` (bloco `pacotes`) · **bloqueia** · Os campos que decidem o que conta como instalação congelada não são conferidos: `flags_congeladas` global, `pacotes.<x>.congelados`, `pacotes.<x>.flags_congeladas` e `pacotes.<x>.so_arquivo`. Com `"--save"` em `flags_congeladas` ou `"install"` em `npm.congelados`, `npm install <pacote>` vira `instalar_congelado`, que `qa` e `tech-lead` podem executar. Nenhum desses casos acusa. Sugestão: acusar quando qualquer uma dessas listas ganha itens.
3. `tests/catraca.py` (bloco `papeis`) · **bloqueia** · Duas mudanças rebaixam um agente para `papel_padrao` (`dev`), que ganha `instalar_pacote`, e nenhuma acusa: tirar um agent_type de um papel (por exemplo, `forge:qa-engineer` sai de `qa`) ou remover o papel inteiro. Também não acusa criar um papel novo chamado como o `papel_padrao` (`"dev": ["forge:qa-engineer"]`). Sugestão: comparar o mapeamento resolvido agent_type -> papel entre base e head (pela regra de `papel_de`, em que vale o primeiro papel que casa) e acusar qualquer agent_type que mude de papel ou desapareça.
4. Quebra de esquema · **recomendado** · Renomear `papeis`, remover `quem` de uma entrada ou remover `flags_congeladas` não acusa. No hook isso vira `KeyError`, e a falha fechada é seletiva (`CRITICO`): `npm install`, `.claude-plugin/`, `.github/` e `tests/neutralidade.py` não casam com `CRITICO`, então essas ações passam a ser liberadas. Sugestão: acusar quando uma chave de topo da base ou o `quem` de uma entrada some no head.
5. `hooks/conformidade.py` fora de `PROTEGIDOS` · **recomendado (PR próprio)** · Afrouxar o código passa sem o rótulo do dono. `SENSIVEIS` só exige parecer de review; trocar `casa`, `papel_de` ou o `continue` de `caminho_barrado` anula a política inteira. Pôr `hooks/conformidade.py` em `PROTEGIDOS` resolve o próprio arquivo, mas não basta: a decisão também depende de `parecer.e_clone_do_forge` (`so_forge`) e de `_comum.executar`/`falhar_fechado`, que precisariam do mesmo tratamento, ou ser isolados num módulo protegido. É lacuna anterior a este PR.

### Conferidos sem desvio
- Renomear `caminhos` ou `acoes`, remover ou encurtar um `caminho`, JSON inválido e arquivo apagado ou movido: acusam (o head vira `{}`; o hook lê o caminho fixo).
- Ordem das entradas: não importa para `caminhos`. Em `papeis`, só importa com agent_type duplicado, e acrescentar um agent_type a um papel existente já acusa.
- Entrada duplicada com `quem` mais largo: não afrouxa, porque o hook exige que todas as entradas que casam permitam (`continue` quando permitem; a primeira que barra decide).
- Trocar `motivo`: só muda o texto da mensagem.

### Falsos positivos (não bloqueiam)
- Apertos que acusam: `so_forge` de `true` para `false`, `branch` mais longo (`melhoria/x`) e qualquer mudança em `sem_agent_type`/`papel_padrao`. Postura conservadora aceitável; o rótulo do dono libera.

### Regressão
- Nenhuma: o diff só soma `regra_politica` em `violacoes_das_regras`; as demais checagens e os testes existentes não mudaram.

Parecer independente: **ajustes necessários** (desvios 1 a 3 bloqueiam; 4 e 5 recomendados). Frontmatter atualizado para `reprovado` no commit `fb376cd`.

## Re-review independente

Terceira leitura (outra instância do `forge:tech-lead`) sobre `cca8c18..cae76b9`, a troca da checagem por lista branca (`mudancas_da_politica`). Testes no checkout do PR: `python3 -m unittest discover -s tests`, 248 OK. Os desvios foram conferidos chamando `mudancas_da_politica` com a política real alterada, e o desvio novo também rodando o hook real (`hooks/conformidade.py`) sobre uma cópia com a política alterada.

### Desvios do review anterior
- 1 (`so_forge` acrescentado), 2 (`flags_congeladas`, `pacotes.<x>.congelados` e `so_arquivo`), 3 (papel perde agent_type, papel removido, papel `dev` novo) e 4 (renomear `papeis`, tirar `quem` de uma entrada, tirar `flags_congeladas`, arquivo removido): **todos acusam agora**.
- 5: resolvido para o próprio arquivo (`hooks/conformidade.py` entrou em `PROTEGIDOS`). `parecer.e_clone_do_forge` e `_comum.executar`/`falhar_fechado` continuam só em `SENSIVEIS`; segue como recomendação para PR próprio.

### Como o hook escolhe a entrada
`caminho_barrado` percorre todas as entradas: a que permite dá `continue`, a primeira que barra decide. Não há "primeira que casa" nem "mais específica": uma entrada nova bem formada só pode acrescentar bloqueio. Por isso entrada mais larga, entrada mais específica dentro de um caminho existente (`.claude/settings.json` com `quem: ["jarvis"]`), `quem` amplo como `jarvis` e reordenar a lista não afrouxam. Caminho vazio acusa; espaço ou Unicode no caminho só criam um bloqueio inócuo.

### Desvio novo (afrouxa e a checagem não acusa)
1. `tests/catraca.py` (`_entrada_nova_invalida`) · **bloqueia** · A entrada nova só tem `caminho` e `quem` validados. Sem `motivo` (ou com `branch` que não seja texto), o hook lança `KeyError`/`TypeError` ao barrar, e a falha fechada é seletiva (`CRITICO`). Como a lista branca ignora a ordem (`Counter`), a entrada pode ser inserida no início. Reproduzido: `{"caminho": ".github/workflows/ci.yml", "quem": []}` no índice 0 passa na catraca, e as fixtures `protegido-github-dev-bloqueia` e `protegido-github-fora-de-melhoria-bloqueia` passam a sair com código 0 (`erros.log`: `KeyError: 'motivo'`). Na prática, a proteção de `.github/` some sem o rótulo do dono. O mesmo vale para `.claude-plugin/` e `tests/neutralidade.py`, que também ficam fora de `CRITICO`. Sugestão: validar o esquema completo da entrada nova (`motivo` texto não vazio; `so_forge`, se houver, booleano; `branch`, se houver, texto não vazio; nenhuma chave fora de `caminho`, `quem`, `motivo`, `so_forge` e `branch`) e acrescentar um teste para cada caso.

### Falsos positivos (não bloqueiam)
- Duplicar uma entrada existente, acrescentar entrada mais larga que um caminho existente (`docs/`) e trocar o texto de `motivo` acusam. Postura conservadora aceitável; o rótulo do dono libera.

### Regressão
- Nenhuma: as demais regras da catraca não mudaram; `PROTEGIDOS` só ganhou um item.

Parecer da re-review: **ajustes necessários** (desvio novo 1 bloqueia; item 5 anterior segue recomendado). Frontmatter mantido em `reprovado`, commit `cae76b9`.
