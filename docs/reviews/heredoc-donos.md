---
tipo: review
contrato: 1
pedido: heredoc-donos
branch: melhoria/heredoc-donos
commit: f16b60eb3d9045948fc1fef7e16cb74e7607a103
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-03
---
# Review: heredoc-donos (E1.1, revisão E1.2)

Revisor: forge:tech-lead, outra instância que não é o autor (D-ETAPAS-INST = A). Base `032b4cbf691719c356676ab2b7ed717afbaa6335`, head revisado `f16b60e`, 6 commits. Fonte do desenho: seção (b) de `docs/propostas/heredoc-donos.md` (E1.0); decisão do dono P-HEREDOC-DONOS-C4 = A.

## Achados
- A1 (recomendado) tests/test_hooks.py:1986 · o oráculo lê o lado novo com o `corpo_so_lido` em cache global: um texto igual visto antes (outro teste, outro texto) responde do cache e não passa pelo ramo das partes; limpar `corpo_so_lido`, `_leitura_do_dono` e `interpretado` antes de cada texto
- A2 (recomendado) tests/test_hooks.py:1864 · o `print` dos tempos no teste do orçamento suja a saída da suíte; a prova do CI (PQ-1 do pedido) já é a asserção; levar a medida para a mensagem da asserção ou tirar
- A3 (recomendado) hooks/conformidade.py:747 · o C-4 conta os corpos só depois do `tirar_heredocs`: o prazo vencido durante a própria extração, sem marcador, ainda libera; hoje a extração é linear (sonda abaixo), então fica como observação para a segurança (E2.1) e o C-6 do QA, não como defeito provado
- A4 (recomendado) tests/test_hooks.py:2003 · o C-4 se prova por unidade (`KeyboardInterrupt` simulado e `prazo_vencido` direto); a cadeia `executar` → `PrazoVencido` → recusa com o vigia de produção e o `lento`, prevista em (e) da proposta, fica para a fixture do QA (C-6)

## Parecer
**Aprovado.** Faz o que a seção (b) da proposta pede, sem nada além disso.

Leitura do diff contra a seção (b):
- `hooks/_comum.py:928`: o prefixo se monta uma vez no `__init__` e o `vestir` gera o mesmo `str` da base, byte a byte (`f"{prefixo}\n{sozinho}"`, ou só `sozinho` sem texto de fora, como o `join` de um item só). As partes só entram com `fronteira_limpa` provada (T2).
- `fronteira_limpa` (1481): sem dúvida no prefixo nem no prefixo com `\ntrue`, e os comandos simples do todo são os do prefixo mais `true` sozinho. Como `programas_e_atribuicoes` lê comando simples a comando simples, sem estado entre eles, e o `corpo_so_lido` combina com `any`/`all`, que não dependem da ordem, a leitura em partes é a do todo sempre que a fronteira vale. O oráculo diferencial confirma isso nos casos de borda (aspa, `\`, `$(`, `|`, `&&`, atribuição M4, programa só no texto de fora).
- `_leitura_do_dono` (1475): a chave do cache é o texto inteiro de cada parte (T4). O prefixo é o mesmo objeto, com o hash calculado uma vez, e fica sempre recente no LRU de 1024.
- C-5 no `gasto`: sem fronteira o dono soma também o prefixo e o dono largo assume. Isso só alarga: o dono largo tem mais programas e o `all` fica mais estrito, então nunca pula (T6).
- C-4 em `prazo_vencido` (2490): recusa com `marcado is False` só se há corpos pendentes, e só na sessão vigiada e antes da ferramenta (PreToolUse). Com marcador, a mensagem é a mesma da base, texto por texto. Contador: soma em `conformidade.py:747` e desconta depois do `bash`/`checar_texto` de cada corpo. Na linha ilegível o `return` deixa os corpos contados, e eles de fato não foram conferidos: falha fechada, coerente com a decisão A.
- `hooks/conformidade.py`, `interpreta_o_corpo`: exato sem precisar de fronteira. O `re.sub` age caractere a caractere e o `\n` entre as partes é separador do `re.split`, então os tokens do todo são a união dos tokens das partes (T3).

Testes e corpus: o teste do orçamento ganha `./x<i>`, `sh -s a<i>`, `python3 -` e `python3 - a<i>`, cada um com 1000 e com 3000 heredocs, sem o push e com a mensagem da linha curta (C-3). Somam-se o oráculo (mais de 1500 textos, com as fixtures e o `corpus_de_recusas`), a fronteira com `cat 'a`, `cat a \` e `cat $(x` mais o teto sem fronteira, e o C-4. As 4 fixtures esperam rc 2 com `.github/ (papel: dev)`; a do corpo no meio cobre o `break` (D15, T6). A spec `tests/mutantes/heredoc-donos.json` tem 16 mutantes, um por condição nova do diff, e 1 isenta justificada: o ramo rápido `partes is not None` é equivalente no oráculo e o custo dele se mede pelo orçamento. A rodada dos mutantes é do autor e do QA (`R-QA`, V2), e eu não a refiz.

Testes do item, rodados por mim no head (load 2,5): `python3 -m unittest` dos 4 testes (`test_donos_em_partes_leem_como_o_texto_inteiro`, `test_fronteira_limpa_e_o_teto_dos_donos_sem_fronteira`, `test_prazo_vencido_com_corpo_de_heredoc_pendente_recusa`, `test_muitos_heredocs_recusam_dentro_do_orcamento`) deu `Ran 4 tests in 15.794s OK`. Formas novas no hook real: de 0,23 s (`python3 -` x1000) a 0,98 s (`python3 - a<i>` x3000), contra um limite de 5,0 s.

Ressalva do vermelho: **a prova basta.** Na base, o teste do orçamento estoura o prazo do subprocesso antes de chegar à asserção de 5,0 s. O vigia dos testes é largo (120 s), então a base não libera aos 3 s como em produção e gasta de 17 s a 128 s. O que estoura é a mesma propriedade que o teste afirma: o tempo da decisão. Sonda minha, no processo, com a forma `./x<i>` + `bash` gravando `.github/`:

| donos | base 032b4cb | branch |
|---|---|---|
| 300 | 0,48 s | 0,04 s |
| 600 | 1,78 s | 0,06 s |
| 1200 | 7,89 s | 0,10 s |

Na base o tempo quadruplica quando os donos dobram (quadrático); na branch, cresce em linha. A liberação por prazo em produção (L2) fica coberta por outro caminho, o teste do C-4 (mutante D11).

Teto da decisão M14: a conta `git diff --numstat --no-renames 032b4cb...HEAD` dá 148 linhas de código e teste, dentro do teto de 150:

| arquivo | linhas (+/-) | total |
|---|---|---|
| `hooks/_comum.py` | 33/7 | 40 |
| `hooks/conformidade.py` | 16/2 | 18 |
| `tests/test_hooks.py` | 87/3 | 90 |

Não contam a spec de mutantes, as fixtures e o fragmento `changelog.d/heredoc-donos.md`. Uma classe de comportamento em `hooks/`, com corpus próprio: a parte do desempenho não muda nenhuma decisão (oráculo C-1), e a única decisão que muda é a do C-4, "o hook não libera por prazo a linha com corpo de heredoc pendente", que é a mesma classe do defeito. Sem linha de exceção, que nem é necessária. O PR mexe em `hooks/` (PROTEGIDO) e precisa do rótulo do dono no merge (E1.5).

Regras: `R-NEUTRO` sem termo de projeto. `R-CUSTO` nada pago. Invariantes intactas, sem tocar em `tests/config.json`. Fragmento em `changelog.d/` presente. Commits em Conventional Commits em português, com o comportamento no primeiro e os testes e mutantes nos seguintes. O vigia de 3 s e o `timeout: 10` não mudam. Este repositório não tem `docs/engineering/praticas.md`, então não há regra "ferramenta" para citar.

Classe dos achados, sem linha AR nesta rodada (DECISÃO TÉCNICA 2026-10-29 15:28 do T1-CONF-ESCOPO-REV). A1 é da classe "teste diferencial com cache global entre os lados", que ainda não está em `achados-recorrentes.md`. A2 a A4 são observações e não têm classe recorrente. Itens do PA-7 conferidos: AR-1 (a spec cobre cada condição nova), AR-2 (o ramo C-4 tem teste de comportamento), AR-4 (os testes novos não leem o ambiente do CI) e AR-9 (o texto cita o limite de 5,0 s vigente). Os outros não alcançam este diff.

Segurança: o parecer próprio é o da E2.1 (`docs/security/heredoc-donos.md`, `R-SEGURANCA`), e eu não o refaço. O A3 vai como observação para ele.
