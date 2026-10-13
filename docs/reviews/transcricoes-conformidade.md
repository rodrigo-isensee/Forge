---
tipo: review
contrato: 1
pedido: transcricoes-conformidade
branch: melhoria/transcricoes-conformidade
commit: ec39104
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Code review: propriedades de conformidade no verificador de transcrições (ADR 0009, seção 8)

Escopo: `bin/forge-check` (seção Transcrições), `tests/test_forge.py` (classe `Transcricoes`), `tests/transcricoes/*.jsonl` novos, `docs/transcricoes.md` e `CHANGELOG.md`, diff `origin/develop..ec39104`. Testes da classe `Transcricoes`: 15 verdes.

## Pontos verificados sem achado
- **Anonimização por lista de permissão preservada.** Todo valor novo emitido é vocabulário fechado ou id neutro: `alvo` é o texto da própria política (`classificar_caminho`, `classificar_caminho`), nunca o caminho real; `arq` é `fN` (`registrar_script`, nome do arquivo só vive em memória); `cmd` usa tokens fixos (`custo api <domínio da lista>`, `executa fN`, `pacote ...`); `ator` passa por `marcar_agente`; `causa` é `hook` ou `permissao`; `resposta` só tem números e um booleano; ramo passa por `marcar_ramo`. Texto de usuário, saída de ferramenta, prompt, caminho pessoal e nome de projeto não chegam à saída. O teste `test_anonimizador_mantem_so_o_que_as_propriedades_usam` prova isso com `Zephyrus`, `ana`, `/home` e `/tmp`.
- **Fixtures antigas continuam válidas:** `cmd` não mudou; `via`, `ator` e `c` são opcionais (`CAMPOS_OPCIONAIS`).
- **Teste antigo não foi enfraquecido:** `test_linha_malformada_vira_violacao` só teve a mensagem de `ev` estendida com os tipos novos; as demais asserções são idênticas.

## Achados

### Recomendado (corrigir neste PR ou registrar como limite conhecido)
1. **Falso positivo: `R-CONFORMIDADE.papel` ignora `so_forge` e `branch` da política** · `bin/forge-check:723-727` (`quem_pode`). `hooks/conformidade.py:161` só aplica `docs/regras/`, `tests/config.json`, `tests/catraca.py`, `tests/hooks/` e `hooks/conformidade.json` quando o repositório é o Forge. O verificador acusa qualquer papel fora de `tech-lead`/`doc` que escreva em `tests/hooks/` ou `tests/config.json` num projeto comum (ex.: `dev` gravando `tests/hooks/x.py`; confirmado: `classificar_caminho` devolve `tests/hooks/`). Sugestão: `classificar_caminho` não marcar `alvo` de itens com `so_forge` (o formato não sabe se é o Forge), ou exportar um `forge: bool` no cabeçalho; o mais simples é omitir esses itens do `alvo` e documentar que só valem no hook.
2. **Falso positivo: `pip install -r arquivo` conta como `pacote instalar`** · `bin/forge-check:~590` (`token_pacote`). `pos` inclui o valor de `-r`, então `len(pos) == 1` nunca é verdadeiro; o hook (`hooks/conformidade.py:396-408`) trata o mesmo comando como congelado. Resultado: `qa` e `tech-lead` rodando `pip install -r requirements.txt` são acusados. Sugestão: espelhar `so_arquivo` do hook (pular o valor da opção e contar só avulsos). Falta fixture.
3. **Falso positivo: `R-VERIFY` em script gravado é mais largo que o direto.** `FLAGS_PROIBIDAS["--force"]` casa `rm --force`, `npm install --force` etc.; `eh_script` aceita extensão vazia e `.py` (`bin/forge-check:~558`). Gravar um teste `.py` que cita `--no-verify` (como os do próprio Forge) e rodá-lo com `python3` dispara `R-VERIFY`. Sugestão: restringir `--force` ao ramo `git ... push` (como já fazem as outras alternativas) e exigir `#!` ou extensão de shell para `.py`/vazia, ou documentar como limite em `docs/transcricoes.md`.
4. **Contorno acusa fluxo legítimo de delegação** · `bin/forge-check:~790-800`. Bloqueio de `gh pr create` ou de escrita em `docs/reviews/` para o agente errado, seguido da mesma ação pelo papel certo (outro agente), é lido como `tentado de novo por outro agente`. A ADR 0009 (seção 8) descreve "contorno" como nova tentativa do mesmo desejo; distinguir pelo papel (só acusar quando o papel do segundo ator também não tem permissão ou é o mesmo agente por outra via) evitaria acusar o encaminhamento correto. Se a decisão for manter, registre no doc que o encaminhamento a outro agente também aparece.

### Baixo
5. **Falso negativo: heredoc detectado em `<< 2`** · `comandos_de` e `corpos_heredoc` (`bin/forge-check:~357,~392`). `python3 -c 'print(1 << 2)'` abre um "heredoc" de delimitador `2` e descarta o resto do comando, inclusive um `git push --force` posterior (confirmado). Sugestão: exigir `<<` seguido de `-?` e delimitador que não seja só dígitos, ou só tratar quando a linha não está entre aspas.
6. **`exit code 2` genérico vira bloqueio `hook`** · `BLOQUEIO_HOOK`. Qualquer comando que saia com 2 (grep, diff) e tenha alvo crítico entra como barrado. Só pesa quando há nova tentativa do mesmo alvo por outra via; aceitável, mas vale uma linha em "Limites".
7. **Cobertura:** sem fixture para `-f`/`+refspec` direto nem para `pip install -r`; incluir junto do ajuste 2.

## Parecer
**Reprovado (ajustes necessários)** (nenhum item bloqueia a segurança da anonimização; os itens 1 a 4 evitam que o verificador acuse sessões normais). Se o autor preferir aceitar 3 e 4, registre-os em "Limites" de `docs/transcricoes.md` e eu aprovo.
