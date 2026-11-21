---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae5-retro-pendentes
commit: 600bbecf622bd734806ae351276e844f9a55cc10
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0479-ae5-retro-pendentes (pedido v0478, etapa E58.64)

Escopo: `821db42e..600bbecf` (AE5.1). Subcomando novo `forge-check retro --pendentes` (bin/forge-check:5813-5879, parser em 10257-10263, despacho em 10577-10578), os modelos `docs/retrospectivas/_modelo.md` e `templates/projeto/docs/retrospectivas/_modelo.md`, o mapa do `bin/forge-testes`, mutantes e `tests/test_retro_pendentes.py`.

## Gatilhos
Gatilhos: ferramenta de controle do Forge (bin/forge-check) que lê a pasta de controle e o git.

## Só aperta (confirmação escrita para o rótulo afrouxa-regra)
Confirmo: a mudança **não afrouxa** nenhuma regra, guarda nem portão. Ela só acrescenta um subcomando de leitura e um campo de cabeçalho (`Cobre:`) no modelo de retrospectiva:
- Nenhum hook, workflow, regra de `docs/regras/`, `invariantes` nem lista de proteção é tocado (diff: só `bin/forge-check`, `bin/forge-testes`, os dois `_modelo.md`, changelog, mutantes, `tests/pesos-d4.json` e o teste novo).
- O `retro --pedido` antigo segue igual (bin/forge-check:10579-10580, `cmd_retro` sem mudança); `--pedido` deixa de ser `required` só porque passou a um grupo mutuamente exclusivo e obrigatório com `--pendentes` (bin/forge-check:10258): um dos dois continua obrigatório e os dois juntos são recusados (sonda S5).
- O subcomando não escreve em lugar nenhum (só `for-each-ref` e leitura de `*.md`), e nenhum hook nem portão consome o rc dele hoje (grep em `hooks/`, `.github/` e `bin/`: só o despacho e o mapa de testes).
- `bin/forge-testes` só ganha `test_retro_pendentes` em duas tuplas (mais teste roda, nenhum sai).

## Achados
- A1 (recomendado) bin/forge-check:5829 · Leitura da retro por read_text após is_symlink/is_file/stat: troca entre a checagem e a leitura (link ou FIFO) é seguida, e a leitura não tem teto. Reusar o padrão de _tabela_segura (bin/forge-check:5651): os.open com O_NOFOLLOW e read(TETO_DA_RETRO + 1).

## Sondas

## Detalhe dos achados
**A1** · evidência: bin/forge-check:5826 checa `is_symlink()`, `is_file()` e `stat().st_size`; bin/forge-check:5829 abre de novo pelo caminho com `read_text` e lê tudo. · caminho de ataque: quem escreve em `docs/retrospectivas/` da pasta de controle troca o arquivo, entre a checagem e a leitura, por um link para arquivo grande ou um FIFO; o FIFO trava o `forge-check` sem prazo, o link faz ler fora da pasta. Quem escreve ali já é confiável e a janela é estreita: sem ganho realista além de travar a própria execução. · severidade: baixa. · correção mínima: abrir uma vez com `os.open(arq, os.O_RDONLY | os.O_NOFOLLOW)` (e `O_NONBLOCK` ou `fstat` + `S_ISREG` no descritor), ler `TETO_DA_RETRO + 1` bytes e recusar acima do teto, como `_tabela_segura` já faz; a mesma observação vale para a pasta `docs/` mãe, que é seguida se for link (só `retrospectivas` é conferida em bin/forge-check:5867). · esforço: P. · dono: o autor da branch (AE5.1).

Pontos conferidos sem achado:
- Injeção de opção no git: `--main` passa por `REF_DA_MAIN` (início alfanumérico, bin/forge-check:5816 e 5854) e vai como valor de `--merged`; `--main=--output=...` dá rc 2 e não cria arquivo (S2). Ref com `..` cai no erro do git, rc 2 (S6). `git()` remove as `GIT_*` herdadas e tem prazo (bin/forge-check:580-590).
- Saída: só sai nome de tag que casa `v\d+\.\d+\.\d+` inteiro; nome de arquivo e valor de `Cobre:` saem por `nome_seguro` (ESC e aspas escapados, S1). Sem caractere de controle na saída.
- Entrada da pasta de controle: link, pasta, FIFO, arquivo acima de 1 MB e `_*.md` não cobrem e geram aviso (S1); `--desde` e `--agora` inválidos dão rc 2 (S3, S4). Regex sem retrocesso catastrófico (`Cobre:(.*)` e grupos fixos).
- Relógio é argumento (`--agora`), sem leitura do relógio do sistema; `_hora` devolve sempre hora com fuso, sem erro de comparação.

Sondas executadas (TMPDIR em /root/.forge-contrib/wt/sondas-E5864; nenhuma prova bloqueante, por isso fora do bloco `## Sondas`):
- S1 · pasta com `link.md` (link), `_x.md`, `grande.md` (>1 MB), `fifo.md` e `esc.md` com ESC no `Cobre:` · espera: nada cobre, avisos escapados, rc 1 · obtido: 4 avisos, ESC como `\u001b`, `pendentes=2`, rc 1.
- S2 · `--main=--output=<sondas>/pwn` · espera: rc 2 sem arquivo · obtido: rc 2, arquivo ausente.
- S3 · `--desde v1.0` · obtido: rc 2. S4 · sem `--agora` · obtido: rc 2. S5 · `--pendentes --pedido x` · obtido: erro do parser de argumentos "not allowed with". S6 · `--main main..main` · obtido: rc 2. S7 · `--desde v1.1.0` · obtido: só v1.1.0 pendente, rc 1.
- `tests/test_retro_pendentes.py`: 18 testes OK no head.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Suíte inteira: não rodada aqui (brief: sem suíte local); vale o CI do PR para o merge, ainda não aberto. Ferramenta ausente no ambiente: o varredor de segredos (lacuna; diff de 556 linhas lido à mão, sem segredo).
