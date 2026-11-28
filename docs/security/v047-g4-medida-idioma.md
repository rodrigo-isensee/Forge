---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-g4-medida-idioma
commit: bdbb45cd5235d601649e3bbdd889bb8b4aaae4cb
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v047 (SIEG-G4, medida de idioma no hook meta)

Etapa E2.699. Diff revisado: `5b1aacd5..675cf7a1` (hooks/meta.py, tests/test_meta.py, tests/mutantes/v047-g4-medida-idioma.json, changelog.d/v047-g4-medida-idioma.md).

Revalidação por delta: `675cf7a1..bdbb45cd` só mudou `tests/mutantes/v047-jargao-medida-4.json` (`de` do M27 realinhado à linha nova de hooks/meta.py), fora do domínio; nenhum arquivo do domínio mudou, achados anteriores: nenhum, parecer segue aprovado.

## Gatilhos
Gatilhos: hook do Forge (`R-SEGURANCA`): grava em `.forge/run/mensagens.jsonl` dado derivado da mensagem ao dono e lê `.forge/config.json` do projeto.

## Achados

## Sondas

## Detalhe dos achados
Verificado sem achado:
- Texto da mensagem não vai ao disco: a linha gravada (hooks/meta.py:228-231) só ganha `idioma` (uma das chaves fixas de `PALAVRAS_DO_IDIOMA` ou nulo, hooks/meta.py:195-202), `idioma_do_dono` e `outro_idioma` (booleano). Sonda de ponta a ponta (evento Stop num projeto marcado, mensagem com uma marca única): a marca não aparece em `mensagens.jsonl` nem em arquivo algum do projeto, nem no erros.log.
- Valor da configuração não vai ao disco cru: `idioma_do_dono` (hooks/meta.py:205-212) só devolve `IDIOMA_PADRAO`, uma chave da lista ou nulo; `isinstance(valor, str)` vem antes do `in`, então objeto ou lista na chave não quebra por não ser hasheável. Sondas: `{"a":1}`, `"pt\u0000\n"` e sequência de escape de terminal gravam `idioma_do_dono: null`, `outro_idioma: false`, rc 0.
- Config ruim não derruba o hook: JSON inválido, raiz que não é objeto e bytes fora de UTF-8 saem com rc 0 e uma linha no erros.log (só o tipo e a posição do erro, sem conteúdo). A falha já acontece antes, em `hook.projeto()` (leitura de `config()` em hooks/_comum.py:2589, inalterada); a nova leitura não cria modo de falha novo e, se falhasse, cai no `except` da medida (hooks/meta.py:245-248).
- Nada bloqueia: a medida continua no `finally` depois de `avaliar_meta`, com `except Exception` que só registra; o `meta` não passa `critico` ao `executar`, então erro interno libera (ADR 0003). O teste ajustado (tests/test_meta.py, chamada com `raiz` e `sys.exit(2)`) prova que a decisão do Stop não muda.
- Tempo limitado: a detecção roda sobre `TETO_DA_MEDIDA` (20000) caracteres; sonda com mensagem de 3,8 MB: 3,6 ms.
- Neutralidade: o idioma do dono vem do projeto (`.forge/config.json`), não fixo no hook.
- Leitura da config sem conferir link simbólico: mesma postura da leitura já existente em `config()`; sem superfície nova (informativo).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do diff e sondas locais do hook como processo (evento Stop por stdin); testes do item rodados no clone: `python3 -m unittest tests.test_meta` (20 OK). Suíte inteira: só no CI, que ainda não rodou para esta branch (sem PR); o portão de merge a exige. Faltaram no ambiente: gitleaks e Semgrep (nenhum workflow mudou).
