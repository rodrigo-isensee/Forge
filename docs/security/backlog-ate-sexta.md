---
tipo: revisao-seguranca
contrato: 1
pedido: backlog-ate-sexta
branch: melhoria/backlog-lote-1111
commit: b0cf649d31e65f3342b1fd1666241bcd27a28a8a
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-11
---
# Review de segurança: backlog-ate-sexta (E1.16/E1.17, junção melhoria/backlog-lote-1111)

Head revisado: `b0cf649d31e65f3342b1fd1666241bcd27a28a8a`, base `36d976dfc01247a1e9c1652904bf36f2e7d07496` (origin/develop do brief). Leitura sem escrita na branch (Z10), numa worktree destacada em `~/.forge-contrib/wt/sec-lote-1111`. Diff da junção contra a base: 35 arquivos, +577 −21. Nenhum workflow, hook de `hooks/` nem dependência mudou.

## Gatilhos
`R-SEGURANCA`: analisador de contribuição (`scripts/verificar-contribuicao.sh`, caminho pessoal), script do integrador que lê log do CI e escreve o corpo do PR (`bin/forge-fechar --medir`), conferente de reversão (`scripts/conferir-reversao.py`), fila de pesadas de pacote de stack (`R-TETO`) e texto de regra de portão (`R-QA`, `agents/tech-lead.md`, `agents/qa-engineer.md`, `skills/engineering-practices/SKILL.md`: afrouxamento TEMPO-A A11/A13).

## Junção: merges, conflitos e o que mudou desde as frentes
- Merge-base de cada frente com a develop: `8eb9893f` (as nove). Toda frente é ancestral do head; nenhuma tem commit depois do que entrou.
- Remerge (`git merge-tree --write-tree p1 p2` comparado à árvore gravada) dos dez merges da branch: nove limpos, sem resolução manual; o único resolvido é `53a953a5` (varredura-caminho-pessoal sobre tm17-dado-neutro), conflito só em `tests/test_forge.py`, anotado na mensagem. `git show --cc 53a953a5`: a resolução mantém o teste da TM-17 e os seis da varredura, um depois do outro, sem tirar linha de nenhum lado.
- Último merge `b0cf649d` (1º pai `0eb79b49`, 2º pai a base `36d976df`, 23 commits da develop desde `8eb9893f`): remerge dá a mesma árvore (`e9a632b6`), sem resolução manual.
- Presença de cada frente no head (`git diff <merge-base> melhoria/<frente>` aplicado ao contrário com `git apply --cached --reverse --check` num índice com `b0cf649d`): inteiras maq-i9-refazer-1, tm25-pesados-stack, orcamento-tempo-no-log, fechar-medir-do-log, fechamento-540s, revisor-sem-rerrodar e diretrizes-jarvis-12-14. As duas do conflito não aplicam ao contrário só por contexto; arquivo a arquivo, todas as linhas acrescentadas estão no head (tm17: 24 de 24; varredura: 82 de 82, inclusive `scripts/verificar-contribuicao.sh` e o mutante) e nenhuma linha removida voltou.
- Único commit próprio da junção: `0eb79b49` (`tests/test_reval_delta.py`, contagem 13→14, consequência do teste novo do MAQ-I9); sem efeito de segurança.

## Leitura de segurança por frente
- **Varredura de caminho pessoal** (`scripts/verificar-contribuicao.sh:26`): endurece. Sondas na regex, em `LC_ALL=C` e `C.UTF-8`: pega `/home/<nome>/` com minúscula, maiúscula, ponto, hífen, acento, `/Users/<nome>/`, `/mnt/c/Users/<nome>/` e `/var/home/<nome>/`; deixa passar pasta que começa com ponto, o marcador `<nome>`, `/home/<nome>` sem barra final, nome com espaço, `C:\Users\...` e `/HOME/` (todos já passavam antes; não é regressão). A varredura do head contra a base sai `ok`.
- **`forge-fechar --medir`** (`bin/forge-fechar:180`-`204`, `:319`): o número da execução é validado (`^[0-9]{1,20}$`) antes do `gh run view` (só leitura); arquivo só com `-f`/`-r` e `cat --`; texto livre, marca ausente e linha fora do formato param antes do passo 1; o dry-run não chama o `gh`; a leitura é linha a linha, então não injeta nova linha no corpo. Ver A1 (o campo `forma` aceita qualquer coisa).
- **conferir-reversao** (`scripts/conferir-reversao.py:79`): endurece; o revert que pede a suíte inteira sai `sem-veredito` em vez de rodar.
- **Fila de pesadas** (`stacks/node-react/pesados.json`): só acrescenta comandos (mais restrito); projeto antigo mantém a lista, como dizem o `pronto.md` e o fragmento.
- **Revisor sem rerrodar** (`docs/regras/R-QA.md:12`, agentes e skill): afrouxamento declarado (`afrouxa-regra`, decisão do dono no pedido). O portão continua: a prova é o check-run do CI no mesmo sha ou o PQ do autor. O texto do `security-engineer` e da skill `cyber-security` não muda nesta junção. Ver A3.
- **Diretrizes 12 a 14** (`agents/jarvis.md:15`-`16`, `docs/economia-de-tokens.md`): política de tokens; nenhuma toca regra de segurança. O Jarvis perde "sobre falhas" e "o scratchpad é temporário"; a regra de gravar a decisão no mesmo turno fica.
- **fechamento-540s** (`docs/fechamento-integrador.md`): só texto de espera; sem efeito de segurança.

## Achados
- A1 (recomendado) bin/forge-fechar:180 · o grupo forma=(.+) aceita caractere de controle e marcação; a sonda S1 com ESC, menção, link e caixa marcada saiu igual no terminal e no corpo do PR. Restringir forma a imprimíveis sem @ [ ] ( ) ou pôr a medida em bloco de código.
- A2 (recomendado) agents/jarvis.md:14 · a develop andou para 11ba4fa6 (#491, R-DECISAO uma a uma) e o merge-tree com o head dá conflito em agents/jarvis.md; a resolução precisa manter as duas mudanças e o delta dela volta à revalidação.
- A3 (recomendado) changelog.d/revisor-sem-rerrodar.md:2 · o título do PR da junção precisa destacar o afrouxamento de R-QA (TEMPO-A A11/A13) com o motivo, como pede a regra de invariantes, já que ele chega à develop dentro de um lote.

## Sondas
- S1 · `forge-fechar p1 --ref melhoria/x --medir <log>` (ambiente de tests/test_fechar_medir.py), log com `ORCAMENTO-TEMPO ... forma=x <ESC>[2J @dono [ok](http://x) - [x]` · espera: recusa ou texto neutro · obtido: rc 0, a linha crua no stdout e em "## Como medir"
- S2 · `git merge-tree --write-tree --name-only origin/develop b0cf649d` (origin/develop `11ba4fa6`) · espera: limpo · obtido: `CONFLICT (content): Merge conflict in agents/jarvis.md`

## Detalhe dos achados
- **A1.** Evidência: `bin/forge-fechar:180` (regex `forma=(.+)`), `:217` (corpo "Como medir"), `:319` (impressão no terminal); sonda S1. Caminho de ataque: quem controla a saída do CI da execução escolhida (o autor do PR) imprime uma linha no formato com sequência de terminal, menção (notifica alguém) ou link; ela vai ao terminal do integrador e ao corpo do PR. Ganho pequeno: o mesmo autor já escreve o PR, os números seguem conferidos pela regex e não há quebra de linha. Severidade baixa. Correção mínima: trocar `forma=(.+)` por uma classe de imprimíveis sem `@`, `[`, `]`, `(`, `)` nas duas regex que precisam continuar iguais (`FORMATO_DO_ORCAMENTO` de `tests/test_hooks.py` e `bin/forge-fechar:180`), ou cercar a medida no corpo com bloco de código. Esforço P. Dono: `tech-lead`.
- **A2.** Evidência: S2. O lado da develop diz "as perguntas vão uma a uma" (R-DECISAO, #491); o lado da junção mantém "vão em lote ... prazo" na mesma linha 14 e muda as linhas 15-16 (diretrizes 12-14). Caminho: uma resolução que fica com o lado da junção devolve o texto antigo de R-DECISAO. Severidade baixa (controle de processo; os invariantes de `tests/config.json` tendem a pegar). Correção mínima: na atualização da develop, linha 14 da develop e linhas 15-16 da junção; o delta de `agents/jarvis.md` volta à revalidação. Esforço P. Dono: `tech-lead`.
- **A3.** Evidência: `changelog.d/revisor-sem-rerrodar.md:2` declara o afrouxamento. Caminho: o lote leva nove frentes; um título genérico esconde do dono que uma regra de portão afrouxou. Severidade informativa. Correção mínima: título do PR com o destaque e o rótulo `afrouxa-regra` pedido ao dono. Esforço P. Dono: `tech-lead`.

## Testes dos arquivos tocados (no head, worktree destacada)
- `python3 -m unittest tests.test_fechar_medir`: Ran 8, OK.
- `python3 -m unittest tests.test_conferir_reversao`: Ran 13, OK.
- `python3 -m unittest tests.test_forge.VerificarContribuicao`: Ran 14, OK.
- `python3 -m unittest tests.test_reval_delta`: Ran 10, OK.
- `python3 -m unittest tests.test_sugerir`: Ran 37, OK.
- `python3 -m unittest tests.test_hooks.Hooks.test_orcamento_sai_numa_linha_de_formato_fixo tests.test_hooks.Hooks.test_fixtures_do_tm25` (os dois testes novos da junção no arquivo): Ran 2, OK. O `tests.test_hooks` inteiro passou de 800 s no sandbox e foi cortado sem resultado; ele fica com o CI do PR (os 4 fixtures `agentes/*` falham também na develop, por ambiente, e não bloqueiam, conforme o brief).
- `scripts/verificar-contribuicao.sh 36d976df`: `ok: nenhum segredo nem caminho pessoal no diff contra 36d976df.`
- `shellcheck bin/forge-fechar scripts/verificar-contribuicao.sh`: sem aviso.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `git`, `shellcheck`, `grep -E` (sondas da regex), os testes dos arquivos tocados. Ausentes no PATH (lacuna, não instaladas): `gitleaks`, `osv-scanner`, `semgrep`, `zizmor`, `actionlint`, `trivy`; a varredura de segredos ficou com `scripts/verificar-contribuicao.sh` e o secret scanning do CI. Sem dependência nem workflow mudado, a falta das varreduras de dependência e de workflow não deixa superfície sem leitura.
