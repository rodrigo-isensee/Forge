---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-perguntas-abertas
commit: 2511f48b990a871fd4700a67ddd00942174edcba
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: v047 (E1.146, perguntas-abertas, FOCO-NAS-DECISOES)

Intervalo revisado: `origin/develop` (`e60183d0`) até `2511f48b`, em 2 commits (`ca4acfb6` e `2511f48b`). No domínio: `bin/forge_dono.py` (`cmd_abertas`, `perguntas_do_pedido`, `pendencias_do_quadro`, `_limpo`, `peso`, `recomendada`, `LINHA_DO_REGISTRO`) e a classe `PerguntasAbertas` de `tests/test_forge_dono.py`. As specs de mutantes e o fragmento do changelog não pedem leitura de segurança.

Veredito: **aprovado**, com três recomendações. A função só lê e não escreve nada. Hoje ela não tem entrada pela linha de comando: o registro em `forge-check decisoes --abertas` vem em outra entrega. Também não abre fronteira de confiança nova. Ela lê, com o mesmo usuário, arquivos do repositório que esse usuário já lê, e a saída vai só para ele. Nenhum dos achados dá ganho a quem escreve no repositório, porque essa pessoa já controla o texto de `docs/pedidos/` e do `KANBAN.md`. Mesmo assim, o A1 desmente a docstring ("link simbólico não é lido"), e o A1 e o A2 devem ser fechados antes do registro na CLI.

## Gatilhos
`R-SEGURANCA`: leitura de arquivos do projeto por ferramenta do Forge, com estes pontos a conferir: link simbólico, arquivo ilegível e caminho fora da raiz. Não há segredo, rede, workflow nem escrita.

## Achados
- A1 (recomendado) bin/forge_dono.py:545 · `docs/pedidos` ou `docs` como link simbólico de pasta é seguido: os `*.md` do alvo, fora da raiz, entram na lista (S1, S2), contra a docstring; recusar como `_gravar_novo` (:56) ou exigir `resolve()` dentro da raiz real
- A2 (recomendado) bin/forge_dono.py:473 · `LINHA_DO_REGISTRO` é quadrática: linha `PERGUNTA AO DONO (2026-11-03` seguida de 32 mil espaços leva 31 s, e 8 mil levam 1,8 s; limitar `[^):\n]*` (ex.: `{0,80}`) ou pular linha acima de um teto antes do `match`
- A3 (recomendado) bin/forge_dono.py:486 · `_limpo` tira C0, DEL e `|`, mas deixa passar C1 (U+0080 a U+009F, ex.: U+009B, o CSI de 8 bits) e formato Cf (U+202E); filtrar pela categoria Cc e Cf, como `recusa_da_forja` já faz com Cf

## Sondas

## Detalhe dos achados
Método: as sondas importaram o `bin/forge_dono.py` do head `2511f48b` (`python3 -I`, raízes temporárias) e chamaram `cmd_abertas` e `perguntas_do_pedido`. Rodei também `tests.test_forge_dono` no head: 73 testes, OK. Contra a raiz real de pedidos, `cmd_abertas` levou 0,2 s e listou 4 perguntas. A suíte inteira roda no CI do PR; a branch ainda não tem PR (a regra da E1.3 abre o PR depois dos pareceres). A entrega foi conferida às 08:46 (Histórico do pedido, 14/11 08:49).

Pontos pedidos pela etapa:
- **Link de arquivo:** `docs/pedidos/<x>.md` e `KANBAN.md` como link ficam fora da lista. O teste `test_link_e_arquivo_ilegivel_ficam_fora` cobre os dois casos.
- **Arquivo ilegível:** `ruim.md`, que não é UTF-8, e uma pasta chamada `d.md` (sonda: `IsADirectoryError`) viram aviso e o comando segue. O `KANBAN.md` usa `errors="replace"`. O `OSError` na leitura do `KANBAN.md` (`:555`) fica com o parecer de QA (E1.147). Rodando como root, não consegui provocá-lo por permissão, e o defeito é de robustez, não de segurança.
- **Caminho fora da raiz:** é o A1.

**A1.** Evidência: em `:545-547`, `Path(raiz)/"docs"/"pedidos"` é varrido por `glob`, e só o link do próprio arquivo é recusado (`arq.is_symlink()`). Sondas: com `docs/pedidos -> <pasta fora>`, `cmd_abertas` devolveu `aberta: outro | x | 2026-11-03 10:00 | segredo de fora`. Com `docs -> <pasta fora>` (que tem `pedidos/y.md`), o resultado foi o mesmo. O git guarda link simbólico, então um commit pode trazer esse link. Caminho de ataque: quem escreve um link desses na branch faz a ferramenta ler arquivos que o próprio dono já pode ler e mostrá-los a ele. Não há ganho de privilégio nem vazamento para terceiros. O link pode, porém, mostrar como pergunta pendente um texto que não está no repositório. Na mesma linha, um FIFO local chamado `*.md` em `docs/pedidos/` travaria o `read_text`. O git não guarda FIFO, então esse caso só nasce na máquina. Severidade: baixa. Correção mínima: no começo de `cmd_abertas`, recusar com aviso quando `pasta.is_symlink() or pasta.parent.is_symlink()`, que é a convenção do módulo em `_gravar_novo` (`:56`) e `_gravar_seguro` (`:74`). Alternativa: comparar `arq.resolve()` com `Path(raiz).resolve()` e exigir `arq.is_file()`, o que também afasta o FIFO. Somar dois casos ao teste: pasta `docs/pedidos` como link e pasta `docs` como link. Esforço P. Dono: `tech-lead`, na entrega do registro na CLI ou antes dela.

**A2.** Evidência: em `:473`, `(?:\(?{_DATA}[^):\n]*\)?)?` vem seguido de `(?:\s*[:,]\s*|\s+(?=\x22))`. Numa sequência longa de espaços sem `)`, `:` nem `,`, o retrocesso é O(n²). Tempos medidos em `perguntas_do_pedido` e em `LINHA_DO_REGISTRO.match`:

| espaços | tempo |
|---|---|
| 2 mil | 0,10 s |
| 8 mil | 1,8 s |
| 32 mil | 31 s |

Uma linha `PERGUNTA AO DONO (2026-11-03 10:00): ` seguida de `→"` repetido 32 mil vezes também levou 36 s. A maior linha real de pedido tem 1075 caracteres e roda em tempo desprezível. Caminho de ataque: um texto colado no pedido, vindo de conteúdo externo ou de um agente induzido, trava o comando de quem o roda. O efeito se limita a negar o serviço de uma ferramenta local. Severidade: baixa. Correção mínima: limitar o trecho ambíguo (`[^):\n]{0,80}`) ou ignorar, com aviso, linha acima de um teto (ex.: 8 KiB) antes do `match`. Somar um teste de orçamento de tempo. Esforço P. Dono: `tech-lead`.

**A3.** Evidência: `:486` troca `[\x00-\x1f\x7f|]` por espaço. Sonda: o texto `a\u009b31mVERMELHO ‮abc \x1b[2J` saiu como `a\x9b31mVERMELHO ‮abc [2J`: o ESC caiu, mas U+009B e U+202E passaram. Caminho de ataque: um terminal que interpreta C1 em UTF-8, ou a inversão bidi, desfigura a linha mostrada ao dono e pode trocar a ordem visual de "recomendada". O efeito depende do terminal e não executa nada. Severidade: informativa a baixa. Correção mínima: substituir por espaço todo caractere com `unicodedata.category(c) in ("Cc", "Cf")`, e não só a faixa ASCII. Esforço P. Dono: `tech-lead`.

## Riscos aceitos e ferramentas
Sem riscos aceitos. As sondas foram locais e passivas, com a biblioteca padrão. Varredura de segredos e SAST não se aplicam a este delta: não há segredo, dependência nem workflow novos. Nenhuma ferramenta foi instalada.
