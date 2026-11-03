---
tipo: revisao-seguranca
contrato: 1
pedido: lote-unico-032
branch: melhoria/lote-unico-032
commit: 0c90721c86b15d89ea0aec0befa1850b45948698
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-03
---
# Review de segurança: lote-unico-032 (E2.1 do pedido lote-unico-032-REV)

Segurança única do lote (fases 0+A, B, D e F: L00 a L18, L31 a L37, L49 a L51), diff `b2580c6...0c90721`, contra o modelo de ameaças `docs/security/ameacas/lote-unico-032.md` (C-G, T-G, T-B1, C-n e T-n por item). Análise estática e testes dos módulos tocados (D-5); a suíte inteira é do QA. Veredito: **aprovado**, sem bloqueante; quatro recomendações.

## Gatilhos
`R-SEGURANCA`: controles do Forge (`bin/forge-check`, `bin/forge-fechar`, `bin/forge-mutante`, `scripts/suite-paralela.py`, `tests/config.json`, texto dos agentes) e pipeline (`.github/workflows/ci.yml`, L01). O lote não toca `hooks/`, `.githooks/`, `tests/catraca.py` nem `tests/neutralidade.py` (C-G2 conferido no diffstat): não há classe de `hooks/` neste PR, logo nenhum parecer por classe nem corpus de hook (a fase C saiu do lote, decisão 4 = B).

## Achados
- A1 (recomendado) bin/forge-check:1941 · `fila` (L18) executa `.githooks/pre-push --status` da árvore da raiz; um comando só de leitura passa a rodar código da branch checada. Ler a trava em Python (flock LOCK_NB, como a suíte) sem executar o hook.
- A2 (recomendado) bin/forge-check:553 · `gatilhos` casa o `gatilhos_seguranca` do plano técnico só pelo pedido exato; com o id trocado pelo slug (L08, :697, e o caminho do brief) o plano com `pedido: <id>` some. Casar pelo id e pelo slug.
- A3 (recomendado) bin/forge-mutante:649 · `--processos K` (L33) respeita o teto 4, mas a vez da trava da suíte (C-33b) só está no texto de `skills/qa-testing/SKILL.md:89`; nada no código a confere.
- A4 (recomendado) bin/forge-check:2050 · o `custo total` (L16) soma `custo do trecho: N tokens` lido do motivo livre do histórico; um `--motivo` com esse texto infla a medida. Ler só o sufixo que o próprio `movimento` grava.

## Detalhe dos achados
**A1.** Evidência: `bin/forge-check:1933-1950` (`ocupacao_da_trava`). Caminho: quem escreve na branch checada na raiz (o autor, ou um PR de fork checado localmente num projeto) põe código no `.githooks/pre-push`; o Jarvis roda `forge-check fila` e o executa sem push. No Forge é o mesmo usuário da mesma máquina, sem ganho de privilégio, e o `--status` atual só testa a trava (`.githooks/pre-push:106-108`); por isso não bloqueia. Contraria o "não executa nada dos documentos" do cabeçalho do `forge-check` e a classe AR-10 (texto isento executado por outro caminho). Severidade baixa. Correção mínima: abrir o arquivo da trava e testar `fcntl.flock(LOCK_EX|LOCK_NB)` e soltar, com a recusa de link e de dono que a `suite-paralela.py` já usa. Esforço P. Dono: tech-lead (dev do lote).

**A2.** Evidência: `bin/forge-check:553` compara `campos.get("pedido") == pedido`; `pedido_do_pr` (`:680-707`) troca o id pelo slug antes de `gatilhos`. Caminho: num projeto em que a mudança sensível não casa nenhum padrão de diff (só o plano a marca) e o plano técnico leva `pedido: <id>`, `forge-check pr <id>` vira `pr <slug>` e não exige `revisao-seguranca`. Não é regressão provada: `pr <slug>` já se comportava assim em b2580c6, e id e slug hoje dão o mesmo conjunto (C-08a cumprido à letra); o caminho novo (branch sem brief) só amplia quando a troca acontece. Severidade baixa. Correção mínima: `gatilhos` aceitar o plano cujo `pedido` é o argumento original ou o slug. Esforço P. Dono: tech-lead.

**A3.** Evidência: `bin/forge-mutante:180-182`, `:649`. Caminho: não há atacante; é disputa de CPU (R-TETO) se o QA usa `--processos 4` enquanto outra suíte roda. Teto fixo existe (C-33b, primeira metade). Severidade informativa. Correção mínima: com K > 1, recusar ou cair para 1 quando a trava da suíte está ocupada (a mesma leitura de A1). Esforço P. Dono: tech-lead.

**A4.** Evidência: `bin/forge-check:2039-2056`; `cmd_movimento` grava o motivo livre e o custo na mesma célula. Caminho: o autor do movimento escreve `--motivo "custo do trecho: 999999 tokens"`; o Pronto soma. É só medida (nenhum portão lê), severidade informativa. Correção mínima: ler só o último segmento ` · custo do trecho: ...` que o próprio `movimento` acrescenta, ou gravar o custo numa coluna própria. Esforço P. Dono: tech-lead.

## Por item (contra o modelo de ameaças)
- **Gerais.** C-G1: um commit por item (`git log b2580c6..0c90721`, 50 commits com o Lnn na mensagem). C-G2: só `ci.yml` em `.github/`; nada em `hooks/`, `.githooks/`, `tests/catraca.py`, `tests/neutralidade.py`, `scripts/conferir-release.py`. C-G3: texto novo impresso passa por `sem_controle`/`nome_seguro` (Cc, Cf/bidi, Zl, Zp: `bin/forge-check:1269-1277`). C-G4: sem rede nos testes novos. T-G1: nenhum `--no-verify`, `--force`, `paths-ignore`, `continue-on-error` no diff. **T-B1:** os subcomandos novos (`proximo`, `decisoes`, `transcricao vereditos|recusas`) só imprimem; a única opção nova de CLI é `--pedido` (só leitura) e `--processos` no `forge-mutante`; a única gravação nova vai pelo `movimento` (C-16a). Cumprido.
- **L00.** ADRs 0014 e 0015 com `Estado: proposta` e o PR que as destrava; emendas das 0003 e 0009 marcadas proposta ("nenhum papel ganha poder novo por este texto"). C-00 e T-00 cumpridos.
- **L01 (CI).** As 5 condições do pulo intactas (`ci.yml:104-112`); lista nova ancorada em `^docs/(reviews|qa|security|devops|ux)/`, com `_*` e `docs/security/(ameacas|aceites)/` rodando tudo; falha de leitura segue em `pesada=true`; nenhuma permissão nova; passos sem gate intactos. Casos de abuso conferidos pela mesma expressão com GNU grep: `aceites/x.md`, `docs/qa/x.md`+`bin/forge-check`, `docs/qa/_modelo.md`, `ameacas/x.md`, lista vazia e `?` dão completa; `docs/security/x.md` e `docs/devops/x.md` pulam. `homolog`, `opened`/`reopened` e anterior sem `bateria` verde seguem pela condição de `:104`/`:110`. `actionlint`/`zizmor`: lacuna (fora do PATH).
- **L02.** Reuso do rascunho só com um PR aberto, sem fork, base = alvo e head = `remoto_sha` (`bin/forge-fechar:712-722`); `pr ready` só no passo 6, depois de reler base, fork, head e o número pelo nome (`:831-846`), e `--match-head-commit`. C-02a a C-02c cumpridos.
- **L03 a L07.** L03 Etapa/Cobre por `sem_controle`; L04 coluna fora do quadro recusa sem gravar; L05 a linha `pr: veredito` só com a lista de violações vazia, calculada pela mesma `exigidos_do_pr` e `base_do_delta` do `cmd_pr`; assinatura e retorno de `cmd_pr` iguais (T-05). L06 o Histórico pelo `forge-check anotar` (T-06 cumprido). L07 só muda o argumento `--pedido` e a raiz do conferente.
- **L08.** O commit de um pai só sai do escopo se for ancestral de `origin/<base>` e por arquivo de conteúdo igual ao da base (`bin/forge-check:1111-1113`): por conteúdo, nunca por mensagem, autor ou nome (C-08b; T-08a não ocorre). Ambiguidade de slug segue no `uso:` (`:695`). Recomendação A2.
- **L09.** O brief de `merge-integracao` manda o `forge-fechar --dry-run` (que roda `forge-check pr --ref --base` e `--match-head-commit`); as `DECISÃO DO DONO` continuam na seção de decisões. C-09 cumprido.
- **L10 a L13.** Só `aviso:` e contagens; nenhuma recusa vira aviso (T-10); `transcricao vereditos` não imprime trecho.
- **L14.** Só papel (`sem_controle`) e contagem; comando recusado nunca sai (T-14).
- **L15.** Só `docs/pedidos/` via `ler_registro`, só stdout, nenhum portão o lê (C-15a a C-15c).
- **L16.** Gravação só pelo `movimento`, só acrescentando, com a recusa de link de sempre; o valor é número ou `lacuna`, nunca 0 sem medida (C-16a, C-16b). Recomendação A4.
- **L17.** Toda linha por `sem_controle`, largura 160 e teto 40; o veredito vem do frontmatter validado e só conta commitado; o passo vem das Etapas, não do Histórico; sem registro, `não verificável` (C-17a, C-17b).
- **L18.** A leitura não toma a trava (o `--status` só testa); recomendação A1 sobre a forma.
- **L31.** O teto de produção (`PRAZO_DO_CLAUDE_CODE_S`, vigia de 3 s) não mudou; a parede do hook segue medida, só sem a subida do interpretador, e a CPU é asserção a mais. Nada em `hooks/`. C-31 cumprido; os mutantes lentos são do QA.
- **L32.** O registro só roda depois do veredito impresso e num `try` que não muda o rc (`scripts/suite-paralela.py:587-589`); pasta `~/.forge-contrib` exigida existente, sem link, do usuário e sem escrita de grupo/outros; arquivo aberto com `O_APPEND|O_NOFOLLOW`, modo 600; grava só id (truncado, imprimível), carga e taxa, nunca a mensagem; fora do CI. C-32a, C-32b cumpridos.
- **L33.** Cópia por mutante (`trabalho/<id>`, ids únicos validados); o controle por conjunto de testes calculado uma vez sob trava; erro ou sinal mata o grupo de cada processo ativo, impede novos e propaga; `git status` da árvore real e a limpeza no pai depois do pool; o veredito é o máximo dos códigos (independe da ordem); processo que falha é `sem veredito` (2). C-33a cumprido; C-33b na parte do teto (A3).
- **L34, L35.** `tests/config.json`: só `invariantes` mudou, nenhuma chave saiu, `termos_proibidos_hash` igual; dos trechos da base, os 22 que saíram de `agents/jarvis.md` estão iguais nas três skills novas e casam nelas; os mínimos sobem (23→48 arquivos, 95→410 trechos) e entra `invariantes_motivo`. C-35 cumprido.
- **L36.** Casos sintéticos anonimizados (`<branch>`, datas de 2026-01-01); `scripts/verificar-contribuicao.sh b2580c6`: "nenhum segredo nem caminho pessoal"; varredura própria de e-mail, `/home/`, tokens e nomes: nada. `gitleaks`: lacuna.
- **L37.** Só em `melhoria/*` (main, develop, homolog e a branch de integração recusadas antes); base relida do servidor e igual à local; `git merge-tree --write-tree` limpo, commit com a árvore dele e pais (conferido, base do servidor), conferido de novo; `update-ref` com o valor antigo (ou ff-only na worktree limpa); `git push origin <ref>:<ref>` normal, com pre-push; a cadeia recomeça no head novo e o `--trazida` impede um segundo merge; conflito e falha de leitura param. C-37a a C-37c cumpridos; T-37a a T-37c não ocorrem (nada em `hooks/`, sem `--no-verify`/`--force`).
- **L49.** Só leitura do histórico já carregado (C-49).
- **L50.** A suíte inteira segue no QA, no pre-push e no CI; o texto da segurança diz "roda mais quando houver dúvida (nada aqui proíbe)" (`agents/security-engineer.md`). C-50 cumprido.
- **L51.** Todos os IDs de regra da base seguem citados no núcleo (R-MAIN, R-VERIFY, R-CONFORMIDADE, R-DECISAO, R-SEGURANCA, R-REVIEW, R-QA, R-CUSTO e os demais, cada um ao menos uma vez); o núcleo manda ler cada skill nova no passo dela (`agents/jarvis.md:44`, `:61`, `:105`); nenhum invariante saiu (L35). C-51a a C-51c cumpridos.
- **Risco 4.** Ferramentas usadas por este portão, por `command -v`: `forge-check`, `forge-fechar`, `forge-mutante` e `forge-testes` em `~/.local/share/forge/vigente/bin/` (0.31.0); nenhuma ferramenta da branch serviu de evidência. O rótulo `afrouxa-regra` depois do último push fica com o integrador (E1.8).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, `scripts/verificar-contribuicao.sh`, varredura com GNU grep e os testes dos módulos tocados (D-5): `tests.test_fechar_base_andou`, `test_fechar_rascunho`, `test_forge_mutante`, `test_suite_paralela`, `test_jarvis_nucleo`, `test_proximo`, `test_decisoes`, `test_fila_ocupacao`, `test_volta_por_delta`, `test_catraca`: 513 testes, OK (rc 0). Lacunas: `gitleaks`, `actionlint`, `zizmor`, `semgrep` e `osv-scanner` não estão no PATH; o CI cobre o passo de segredos.
