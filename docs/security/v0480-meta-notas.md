---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-meta-notas
commit: 064e58ce43a4a9f25093ff826847297da1c4780d
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-22
---
# Review de segurança: v0478 (E109.5, META-NOTAS-ENTRE-FERRAMENTAS e META-NOTAS-RECONTA)

Revisão completa única do diff 900bfdfe..064e58ce (base `develop`).

Gatilhos: hook (`hooks/meta.py`, Stop) que lê o transcrito da sessão e grava estado novo em `.forge/run/notas.json`.

## Escopo lido
`hooks/meta.py` (inteiro, com `linhas_do_fim`, `texto_do_dono`/`digitado_pelo_dono` de `hooks/vigia.py`, `ler_json`/`gravar_json`/`Hook.run` de `hooks/_comum.py`), changelog, `docs/hooks-fixtures.md`, fixture `tests/hooks/meta/notas-entre-ferramentas-em-ingles-acusa.json`, `tests/test_meta.py` e os mutantes novos.

## Achados
- A1 (recomendado) hooks/meta.py:323 · gravar_json de notas.json roda antes de montar a linha (meta.py:339): falha ao gravar a marca (notas.json pasta, disco cheio, permissão) derruba a linha inteira do mensagens.jsonl, inclusive a medida da final. Proteger a gravação e seguir com a contagem.

## Detalhe
**A1.** Sonda S1: com `.forge/run/notas.json` existente como pasta, `notas_em_outro_idioma` levanta `IsADirectoryError`; `medir_mensagem` cai no `except` de `principal` (meta.py:362) e nada vai a `mensagens.jsonl`, nem a medida da final, que antes do diff seria gravada. A decisão do Stop não muda (`avaliar_meta` roda antes, meta.py:358-359), por isso não é bloqueante: é perda de disponibilidade da telemetria, sem caminho de ataque com ganho. A sobra `notas.json.<pid>.tmp` fica na pasta e sai na próxima gravação do mesmo pid. Correção mínima (dono: o autor do hook): envolver a leitura e a gravação da marca em `try/except OSError` (registrando em erros.log) e devolver a contagem mesmo sem gravar; ou montar a linha com `notas_em_outro_idioma` nulo quando a medida das notas falha.

**Dado pessoal e segredo.** `notas.json` guarda só `transcrito` (caminho local), `marca` (uuid do registro) e `final` (sha256 da final, `resumo`, meta.py:272-273); nenhum texto de nota ou da final vai a disco, e `mensagens.jsonl` ganha só a contagem. `.forge/run/` não vai ao git (`.gitignore:20` no Forge; `bin/forge-init:204` nos projetos). O sha256 de uma frase curta é adivinhável por dicionário, mas o próprio transcrito está na mesma máquina com o texto em claro: sem ganho.

**Arquivo de estado.** Gravação por `gravar_json` (tmp com `O_EXCL|O_NOFOLLOW` e `os.replace`, que troca um link plantado em vez de segui-lo). A leitura por `ler_json` segue link, mas só aproveita um dict cujo `transcrito` é igual ao da sessão (`vista_anterior`, meta.py:307-313); JSON inválido ou ilegível dá `{}`. Um agente pode escrever `notas.json` (fora do `denyWrite` de `templates/projeto/.claude/settings.json:40-41`) e apontar a `marca` para esconder notas da medida: o efeito é só baixar uma métrica de idioma que não decide nada (o único consumidor é a medida em `mensagens.jsonl`, `skills/falar-com-o-dono/toda-mensagem.md:15`); sem ganho de controle, não é achado.

**Custo e entrada livre.** Leitura limitada a `LEITURA_MAXIMA` (4 MiB, meta.py:41) do fim; texto somado limitado a `TETO_DA_MEDIDA` (meta.py:42); o pré-filtro textual pula sem decodificar as linhas com `"type":"tool_result"` e as sem `"user"`/`"assistant"`; `json.loads` com `ValueError` e `RecursionError` tratados; tipos conferidos antes de cada `.get`. O pré-filtro não esconde fala do dono: o texto digitado vai escapado no JSON (não casa com a forma literal) e `digitado_pelo_dono` já recusa registro de resultado de ferramenta. Subagente (`isSidechain`) fica fora.

## Sondas
- S1 · notas_em_outro_idioma com run/notas.json criado como pasta (transcrito de 2 linhas: fala do dono e nota em inglês) · espera: contagem devolvida e linha gravada · obtido: EXC IsADirectoryError

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodado: `python3 -m unittest tests.test_meta` (49 testes, OK) e a sonda S1. Suíte inteira: fica para o CI do PR (por brief; ainda sem PR). `gitleaks` e `semgrep` não estão no PATH: lacuna registrada.
