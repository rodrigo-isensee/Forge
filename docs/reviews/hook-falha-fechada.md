---
tipo: review
contrato: 1
pedido: hook-falha-fechada
branch: melhoria/hook-falha-fechada
commit: 4a0c620
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Parecer de autor: conformidade falha fechada com a política inteira

Parecer do autor da mudança; o review independente fica a cargo de outro revisor antes do merge.

- **O que muda:** `politica()` valida a forma de toda a política (`papeis`, `sem_agent_type`, `papel_padrao`, `acoes` com as cinco ações usadas, `pacotes`, `flags_congeladas`, `caminhos`) e de JSON ilegível; qualquer desvio chama `bloquear` ("política de conformidade inválida", saída 2).
- **Vermelho antes:** 20 subcasos falhavam sem a mudança (inclui `qa` rodando `npm install x` com `pacotes` malformado); `caminhos` ausente já bloqueava.
- **Verde depois:** 271 testes passam e `scripts/validar-plugin.sh` passa; a política vigente passa na validação (teste dedicado).
- **Riscos:** política futura com ação nova só em `acoes` continua válida; remover uma das cinco ações conhecidas passa a bloquear (intencional). Altera `hooks/conformidade.py`: exige o rótulo `afrouxa-regra` do dono.

## Review independente
Revisor: forge:tech-lead (instância independente), sobre `4a0c620`. Parecer: **aprovado**, sem item que bloqueia.

- **Testes:** `python3 -m unittest discover -s tests` no checkout do PR: 271 testes, OK.
- **Política vigente:** passa (`echo oi` como `dev` sai 0; teste dedicado verde).
- **Falso positivo:** nenhum. `git status` da sessão principal e de `qa`, `npm install x` como `dev` e `npm ci` como `qa` saem 0; `npm install x` como `qa` sai 2 pela regra de pacotes, não pela validação.
- **Desvios com o hook real sobre cópia da política** (35 casos): bloqueiam com saída 2 (mensagem "política de conformidade inválida"): raiz lista, `null` ou texto; JSON vazio, truncado, com BOM, `NaN`, chave duplicada; `papeis` `null`, valor número, `null`, objeto ou lista com número; `acoes` com valor objeto ou `null`; `pacotes` com `npm` `null` ou `adicionam` com número; `quem`, `so_forge`, `caminho` e `motivo` malformados em `caminhos`; `sem_agent_type` vazio; `papel_padrao` lista ou booleano.
- **Passam por serem forma válida** (a validação trata de forma, não de conteúdo):
  - chave extra no topo, em `acoes` ou numa entrada de `caminhos`: inofensivo, o hook ignora;
  - `acoes` com papel a mais (`instalar_pacote: ["dev","qa"]`) ou papel inexistente: `qa` passa a rodar `npm install x`. É afrouxamento de política, não malformação;
  - `pacotes: {}` ou `adicionam: []`: o `qa` roda `npm install x` (o hook deixa de reconhecer o gerenciador). Mesma natureza;
  - `papel_padrao: "tech-lead"`, `papeis: {}`, `caminhos: []`, `flags_congeladas: []`, `sem_agent_type` com papel inexistente: valores legítimos de política. Nenhum libera o `qa` a instalar pacote, exceto os dois itens acima.
  Todos exigem editar `hooks/conformidade.json`, que está protegido (`melhoria/*`, tech-lead e doc) e cai no rótulo `afrouxa-regra`. Gravidade: **informativa**; fora do escopo do PR.
- **Sugestão (recomendado, não bloqueia):** num PR futuro, um teste de "política vigente" que fixe as cinco ações com seus papéis e os gerenciadores esperados em `pacotes`, para que esvaziar `pacotes` ou ampliar `acoes` apareça como teste vermelho, e não só no diff.
- **Custo:** a validação percorre uma política de poucos KB uma vez por chamada; o hook inteiro leva cerca de 0,1 s por chamada com ela. Aceitável.
- **Observação:** o hook só lê a política para sessões em projeto Forge e ferramentas Bash/arquivo; fora disso retorna antes de `politica()`, como já era.
