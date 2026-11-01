---
tipo: revisao-seguranca
contrato: 1
pedido: heredoc-comentario
branch: melhoria/heredoc-comentario
commit: 1fa43985b6bd4fd0eb231d872800012b3b3f5fc7
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-01
---
# Review de segurança: heredoc-comentario

Etapa E1.3. Diff revisado: `e25d379..1fa4398` (4 commits). Modelo de ameaças: `docs/security/ameacas/heredoc-comentario.md` (C-1 a C-7, T1 a T6). Proposta: `docs/propostas/heredoc-comentario.md`.

## Gatilhos
R-SEGURANCA, gatilho `controles do Forge`: muda o analisador de entrada do hook (`hooks/_comum.py`, `DonosDosHeredocs`). O defeito corrigido é liberação por tempo (L1 e L2 do modelo).

## Achados
- A1 (recomendado) hooks/conformidade.py:762 · Já existe na develop e25d379, não vem desta branch: com N heredocs de donos distintos e programas fora da lista, cada dono repete `fora_do_texto` e `corpo_so_lido` fica O(N²); 1000 deles e o último corpo dado a `bash` com escrita em `.github/` liberam (rc 0, 3,3 s). Cartão novo.
- A2 (recomendado) tests/hooks/conformidade/heredoc-comentario-3000-bash-no-ultimo-push-main-no-corpo-bloqueia.json:1 · O caso C-6 (b) espera só `R-`: a linha já recusa por outros caminhos com o marcador crítico, e a fixture não prova que o `| bash` segue no dono. O teste do dono largo cobre parte; o QA pode fixar a mensagem ou somar a prova.

## Detalhe dos achados

### Conformidade com o modelo
- **M14 (agents/tech-lead.md:19):** cumpre. `git diff --numstat --no-renames e25d379 1fa4398`: `hooks/_comum.py` 40+12 e `tests/test_hooks.py` 85+3, total 140 de 150; fixtures de `tests/hooks/`, `tests/mutantes/` e `changelog.d/` ficam fora da conta. Uma classe de comportamento em `hooks/` (o custo dos donos dos heredocs), com corpus próprio (4 fixtures e 10+ mutantes). Sem linha de exceção, que não valeria em `hooks/`.
- **T1:** o legado segue nos donos (`montar` percorre todas as leituras de `trechos`, `_comum.py:952`; o largo usa todas as `lidas.partes`, `:960`). **T2:** nada se trunca nem deduplica dentro de um dono. **T3:** o cache por segmento tem `k` na chave; a chave do texto (`:953`) usa o `id` de tuplas internadas em `self.iguais` e guardadas em `self.citados` (vivas por toda a chamada, sem reuso de `id`); mesma chave implica o mesmo conteúdo, logo o mesmo texto; `lugar` não entra no ramo com `trechos`, que não o lê. **T4:** sem recorte por linha física; o `re.sub` da `MARCA` por linha equivale ao do texto inteiro (o padrão não cruza `\n`). **T5:** `None in trechos` fica (`:941`). **T6:** acima do teto, só alarga (largo = `fora_do_texto` + todas as leituras + `resto`) ou levanta `ValueError`.
- **C-1:** `test_donos_dos_heredocs_iguais_aos_da_base` compara com o `montar` da develop nas fixtures e em mais de 4200 linhas da matriz; verde aqui.
- **C-4 e o largo acima de 150 mil:** o teto conta caracteres de texto novo (`gasto`), não palavras × chaves; a diferença está declarada na proposta e é aceitável: o custo real depois do cache é o texto novo. O largo passa de 150 mil caracteres (medido: `resto` 144.494, largo 412.684, `tirar_heredocs` 1,67 s e `corpo_so_lido` 0,93 s de CPU, uma vez só, porque é um objeto para todos). Não abre liberação: `vestir` põe os programas do texto inteiro antes (`:967`), e todo programa fora da lista positiva já está lá, então uma aspa sem par de outra linha do largo não esconde o `| bash`; o teste confere `corpo_so_lido(largo) <= corpo_so_lido(base)` em 400 heredocs.
- **`ValueError` (linha ilegível):** só com `gasto` e `resto` acima de 150 mil. No `conformidade` não é alcançável no nível 0 nem abaixo: o teto de caracteres conferidos da linha (`conformidade.py:39` e `:670`) recusa antes, e o ramo ilegível recusa fora do papel só de leitura (`:733`). No `parecer`, `bloquear` (`parecer.py:584`), fechado, com a mensagem de heredoc ilegível no lugar da de tamanho (informativa: linha acima de 150 mil caracteres não é real). Em `rotulo_na_sessao_do_forge` vale o tratamento que já existia (exige o dono se cita o rótulo); em `alvos_de_escrita`, lê a mais.
- **C-5:** vigia de 3 s e `timeout: 10` sem mudança; `test_forma_com_comentario_recusa_pela_regra_com_o_vigia_de_producao` verde (R-MAIN, não a mensagem de prazo).
- **C-6:** (a), (c) e (d) com fixture e mensagem exata; (b) ver A2; (e) coberta em substância pelo teste do orçamento, que roda com o vigia de 120 s (sem prazo efetivo, como em L1) e exige recusa abaixo de 5,0 s; (f) mutantes M1 a M10 em `tests/mutantes/heredoc-comentario.json`.
- **C-7:** comentário corrigido (`_comum.py:2421`).

### Medidas no hook real (vigia de teste de 120 s, WSL, load ~3)
1100 heredocs `cat a<i><110 y> <<'E' # c` (resto ~141 mil, abaixo do teto de palavras): com `git push origin main`, R-MAIN em 2,03 s; com `| bash` e push no corpo, recusa pelo prazo da linha em 3,32 s (fechado); com `true`, libera em 2,95 s (legítimo); 1300 deles, recusa em 0,09 s pelo teto da linha.

### A1 (pré-existente, fora do diff)
Evidência: `conformidade.py:762` chama `corpo_so_lido` por dono; cada `Dono` distinto carrega `fora_do_texto` inteiro (`_comum.py:968`); a reentrada com o mesmo corpo volta antes do prazo da linha (`conformidade.py:665`). Em processo: 3000 donos de 17 mil caracteres, `corpo_so_lido` 128 s na develop e 131 s nesta branch (iguais). Hook real, papel dev em `melhoria/x`, escrita em `.github/` no corpo do último heredoc lido por `bash`, 1000 heredocs: rc 0 em 3,3 s na base e na branch; com 300, recusa. Caminho: o modelo da sessão, por erro ou instrução injetada, monta a linha sem o marcador crítico, o prazo vencido libera (L2) e a regra de caminho protegido não fala. Severidade: alta (contorno de controle do Forge, sem caminho remoto). Correção mínima: conferir `fora_do_texto` uma vez por texto e o `sozinho` por dono (ou contar `len(fora_do_texto)` no `gasto` e cair no largo), com o caso no teste do orçamento. Esforço P/M. Dono: tech-lead, em pedido próprio (mesma família da regra geral do modelo). Não bloqueia esta branch: não é regressão e está fora do escopo E1.

### A2
Severidade baixa (cobertura de teste, não defeito). Correção mínima: na fixture (b), tirar o marcador crítico de fora do corpo ou fixar a mensagem esperada, para que só o dono com `| bash` decida. Dono: qa-engineer (E1.4).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Análise estática por leitura e medidas locais com os próprios hooks em pastas temporárias. `gitleaks`, `semgrep`, `zizmor` e `actionlint` não estão no PATH (lacuna; o diff não toca workflow nem segredo). Testes rodados aqui: os três novos de `tests/test_hooks.py` (C-1, C-4, C-5), verdes em 155,6 s.
