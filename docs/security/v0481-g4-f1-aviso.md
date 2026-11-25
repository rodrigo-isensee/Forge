---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-g4-f1-aviso
commit: 3682aebaa39bbb2607e45db5d699cc5e7293a65b
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança por delta: v0481 (E7.14, #885, G4 F1: modo aviso por grupo)

Delta lido: `git diff d92b3a07..3682aeba` inteiro (`hooks/conformidade.py` em `registrar_recusa` e `Guarda.barrar`, `tests/test_hooks.py` com 4 testes novos em `ModoPorGrupo` e a classe `RecusaComFifoNoRegistro`, `tests/mutantes/v0481-g4-f1-aviso*.json` M11 a M16, `docs/hooks.md`, `changelog.d/`). Já lido na rodada anterior (no git, em `d92b3a07`): o resto da branch. Os commits depois do Revisar-sha (`c6f7cadd`, `b4ba9b8c`) só trazem pareceres de QA e review.

Gatilhos: controle do Forge (hook `conformidade`, caminho de recusa de todas as regras dele, nas sessões do projeto e do Forge).

## Conferência do delta
- **Registro (A1): corrigido.** `hooks/conformidade.py:1527` abre com `O_NOFOLLOW | O_NONBLOCK` e `:1529` só grava com `S_ISREG` no `fstat`, fechando o fd no `finally`. A pasta é achada por `diretorio_comum` (só disco; `.git` forjado ou desviado dá None e cai no `except`), não mais por `copia_principal` (git). FIFO sem leitor: `ENXIO` no `open`, `except`; com leitor: abre e não grava. Testes `test_registro_nao_espera_fifo_nem_grava_nele`, `test_registro_acha_a_pasta_pelo_disco_sem_git`.
- **Prazo vencido no registro (`:1585-1589`):** o texto da recusa é montado antes, o `registrar_recusa` roda depois, e o `PrazoVencido` dele é engolido para o `bloquear` da regra seguir. Aperta: antes, o prazo vencido ali ia ao `prazo_vencido`, que libera fora de sessão vigiada. No caminho `avisar` (ausente da política entregue) o `PrazoVencido` atravessa e recusa: falha fechada.
- **Revisão da rodada anterior (critério mudou: a sonda S1 de lá só passou pelo rótulo, que não chega ao registro).** Em `d92b3a07` o FIFO no registro **liberava** na sessão do Forge push na main, `--force` e `--no-verify` (S1 abaixo): o A1 era bloqueante, não recomendado. O `d92b3a07` não chegou à `develop`; no head está corrigido (S2).
- **Só aperta ou neutro, por escrito: aperta** no registro (liberação da sessão do Forge fechada; no projeto, a regra certa em vez do prazo) e **neutro** no resto (S4). O A2 é anterior à branch (igual na `develop` `6959cec2`), mas está na linha que o delta reescreveu (`:1585`) e é o mesmo mecanismo (FIFO, prazo vencido, liberação na sessão do Forge) que o E7.11 fecha só no registro.
- Testes: `python3 -m unittest tests.test_hooks.ModoPorGrupo tests.test_hooks.RecusaComFifoNoRegistro` → 11 testes, OK. Suíte inteira: só no CI do PR #885; ao escrever, o head do PR é `b4ba9b8c` e só a `catraca` está em andamento, sem a bateria no head: o merge depende de tudo verde.

## Achados
- A1 (bloqueante) hooks/conformidade.py:1527 · corrigido em 3682aeba: O_NONBLOCK, S_ISREG e pasta sem git; o FIFO no comandos.jsonl liberava push na main, --force e --no-verify na sessão do Forge em d92b3a07 (S1); no head recusa com a regra dela (S2).
- A2 (bloqueante) hooks/conformidade.py:1585 · o texto da recusa chama iniciante(), que lê .forge/perfil sem O_NONBLOCK e chama git (copia_principal); FIFO em .forge/perfil (mkfifo passa pelo hook) prende até o prazo e a sessão do Forge libera push na main e --force (S3).

## Sondas
- S1 · d92b3a07, sessão do Forge, FIFO em .forge/run/comandos.jsonl, `git push origin feature/x:main`, `git push --force origin feature/x`, `git commit --no-verify -m x` · espera: recusa R-MAIN, R-VERIFY, R-VERIFY · obtido: codigo=0 em ~3,1 s nos três
- S2 · 3682aeba, o mesmo de S1, nas sessões do Forge e do projeto · espera: recusa com a regra dela · obtido: codigo=2 em < 0,3 s, R-MAIN, R-VERIFY, R-VERIFY nas duas
- S3 · 3682aeba, sessão do Forge, FIFO em .forge/perfil, `git push origin feature/x:main` e `git push --force origin feature/x` · espera: recusa R-MAIN e R-VERIFY · obtido: codigo=0 em ~3,2 s nos dois (igual em 6959cec2)
- S4 · 3682aeba, sessão do Forge, FIFO em cada um dos 7 arquivos listados no detalhe do A2, `git push --force origin feature/x` · espera: recusa R-VERIFY · obtido: codigo=2 em < 0,4 s nos sete

## Detalhe dos achados
**A1.** Estado: corrigido em `3682aeba` (evidência e testes na conferência; mutantes M11 a M16). Fica no bloco como bloqueante pela revisão acima; nada a fazer.

**A2.** Evidência: `hooks/conformidade.py:1585` (`SIMPLES[simples] if simples and self.h.iniciante()`), `hooks/_comum.py:2719-2721` (`iniciante` chama `copia_principal`, que roda `git rev-parse`, e `read_text` em `.forge/perfil`, que bloqueia num FIFO). Passam por aí as recusas com `simples` (todas as chaves de `SIMPLES`, entre elas `forca` do `--force` e `main` do push na main). Caminho: na sessão do Forge (raiz e pasta corrente no clone, `sessao_vigiada` falsa), o agente roda `mkfifo .forge/perfil` (o hook deixa passar nas duas sessões) e, na chamada seguinte, `git push --force` ou `git push origin x:main`; o `read_text` espera o FIFO, o vigia vence em 3 s e `prazo_vencido` libera. Duas chamadas, sem permissão especial. No projeto a sessão é vigiada e o prazo recusa (falha fechada, com a regra errada). Severidade alta (desvio local de R-VERIFY e R-MAIN; a proteção de branch do GitHub segue valendo para a main remota, não para o `--force` em `melhoria/*`). Correção mínima: a escolha do texto em `:1585` não pode esperar nem liberar; por exemplo, ler o perfil sem git e sem esperar (cópia principal por `diretorio_comum`, como `registrar_recusa`; `os.open` com `O_RDONLY | O_NONBLOCK | O_NOFOLLOW`, ler só se `S_ISREG`, até 64 bytes) e, por cima, `try/except PrazoVencido` na escolha do texto caindo no `com_trecho` (a recusa já decidida segue). Teste: na `RecusaComFifoNoRegistro`, um FIFO em `.forge/perfil` nas duas sessões com push na main e `--force`, recusa com a regra dela e sem "não decidiu". Esforço P. Dono: o autor da branch (E7.11). Dimensão nova da matriz do hook: arquivo especial (FIFO, link, pasta) em todo arquivo que o caminho da trava lê; S4 cobriu os outros sete que achei: `.forge/config.json`, `.forge/run/agentes.json`, `.forge/run/erros.log`, `.forge/run/.trava`, `.git/forge/run/comandos.jsonl`, `~/.forge/maquina/projetos-ativos.json`, `.forge/versao`. Contexto das sondas: S1 também com FIFO em `.git/forge/run/comandos.jsonl`; S3 sem FIFO no registro, igual em `d92b3a07`, e no projeto dá codigo=2 R-CONFORMIDADE pelo prazo de 3 s.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, as 2 classes de teste e as sondas acima (scripts em pasta temporária, `git archive` dos três commits, hook rodado como em produção com `python3 -s -E` e prazo de 3 s, só clones descartáveis e projeto temporário; nada externo). Varredor de segredos, SAST e auditor de dependências: o delta não traz dependência nem segredo.
