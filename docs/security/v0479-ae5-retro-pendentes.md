---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae5-retro-pendentes
commit: e375c67ae9c02ecec5eea7baffef1bf722bd0098
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0479-ae5-retro-pendentes (pedido v0478, etapa E58.68, revalidação)

Revalidação por delta do parecer anterior (commit 13e5c18d, aprovado sobre 600bbecf com A1 recomendado; a rodada anterior fica no git).

Gatilhos: ferramenta de controle do Forge (bin/forge-check) que lê a pasta de controle e o git.

## Delta lido
`forge-check parecer delta docs/security/v0479-ae5-retro-pendentes.md`, intervalo `600bbecf..e375c67a`. No domínio: só `bin/forge-check` (função nova `_texto_da_retro`, bin/forge-check:5822-5835; `versoes_que_a_retro_cobre` passa a usá-la; `cmd_retro_pendentes` deixa de fora a `docs/` que é link, bin/forge-check:5882). Fora do domínio: changelog.d, mutantes e `tests/test_retro_pendentes.py` (rodado, 20 testes OK).

## Achados anteriores
- A1 (recomendado, 600bbecf) troca entre a checagem e a leitura, leitura sem teto e `docs/` mãe seguida se for link: **corrigido**. Abertura única com `O_RDONLY | O_NOFOLLOW | O_NONBLOCK` (bin/forge-check:5826), `S_ISREG` pelo `fstat` do descritor antes do `fdopen` (5829), leitura de no máximo `TETO_DA_RETRO + 1` bytes com recusa acima do teto (5833-5835), `docs/` ou `retrospectivas/` como link ficam de fora (5882). Mesmo padrão de bin/forge-check:4837 e 10024.

## Só aperta (confirmação escrita)
Confirmo: o delta **só aperta**. Todo caminho novo falha fechado (retro ilegível, link, FIFO, pasta, acima do teto ou `docs/` como link passa a não cobrir, o que só aumenta os pendentes); o teto é o mesmo (1 MB, exato passa, +1 recusa); nenhum hook, workflow, regra, `invariantes`, lista de proteção nem consumidor do rc é tocado; o subcomando segue só de leitura.

## Provas da revalidação
Sondas executadas com TMPDIR em /root/.forge-contrib/wt/sondas-E5868; nenhuma prova bloqueante, por isso fora do bloco `## Sondas`:
- S1 · `_texto_da_retro(fifo.md)` · espera: None sem travar · obtido: None em 0,000 s.
- S2 · `link.md` para arquivo fora da pasta · espera: None · obtido: None.
- S3 · pasta `pasta.md` · espera: None · obtido: None.
- S4 · arquivo de 1000000 bytes e outro de 1000001 · espera: o primeiro lido, o segundo None · obtido: 1000000 caracteres e None.
- S5 · troca no meio: `os.open` envolvido para, logo após abrir, apagar o caminho e pôr no lugar um link para fora e depois um FIFO · espera: lê o arquivo aberto · obtido: `'ORIGINAL\n'` nos dois casos (o descritor não segue a troca).
- S6 · troca antes da abertura (link e FIFO no caminho) · espera: None · obtido: None nos dois.
- S7 · `versoes_que_a_retro_cobre(fifo)` · espera: não cobre, com aviso · obtido: `(set(), ['"fifo.md": link, pasta ou acima de 1000000 bytes; nao cobre'])`.
- S8 · ponta a ponta, `docs` como link para pasta com retro válida de v0.1.0 · espera: não cobre · obtido: `pendente v0.1.0`, `pendentes=1`, rc 1.
- S9 · ponta a ponta, FIFO e retro válida em `docs/retrospectivas/` · espera: aviso do FIFO sem travar, v0.1.0 coberta · obtido: aviso, `pendentes=0`, rc 0 (timeout de 20 s não disparou).

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Suíte inteira: não rodada aqui (brief: sem suíte local); vale o CI do PR para o merge. Rodado: `tests.test_retro_pendentes` (20 OK). Ferramenta ausente no ambiente: o varredor de segredos (lacuna; delta de 15 linhas no domínio lido à mão, sem segredo).
