---
tipo: review
contrato: 1
pedido: v046
branch: melhoria/conformidade-caminho-git
commit: 3b3d7a67387c4c61bfd51692513a03bec916d492
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-12
---
# Review: v046 (E20.30, conformidade-caminho-git, revalidação por delta da volta 3)

## Escopo lido
Delta lido por `forge-check parecer delta docs/reviews/v046-conformidade-caminho-git.md`: intervalo cddc8915..3b3d7a67 (volta E20.29, commits 143c9ae4, 7491b5ff, 3b3d7a67, mais o merge limpo da develop 4f74842c, que a ferramenta tira do escopo), 16 arquivos no domínio: `hooks/conformidade.py` (`origens_do_rev_parse` nova, `link_em_protegido` e `segmento_lido` mudados), `bin/forge-testes` (`test_hook_git_comum` no `FORGE_CHECK`), `tests/test_testes_tocados.py` (78 → 79), `tests/test_hook_git_comum.py` (mínimo 58 → 64), 6 fixtures `gitcomum-v3-*`, a spec `tests/mutantes/v046-conformidade-caminho-git-4.json` (G20 a G26), `docs/hooks-fixtures.md` e o fragmento. M14 da branch inteira contra a base a1318e88: 142 linhas de código e teste (`hooks/conformidade.py` 98+6, `tests/test_hook_git_comum.py` 34+0, `bin/forge-testes` 1+1, `tests/test_testes_tocados.py` 1+1), abaixo da orientação de 150; uma classe de comportamento em `hooks/` com corpus próprio. Instância que não fez a entrega, numa worktree destacada minha no head 3b3d7a67.

Rodados um por vez (ambiente limpo, `python3 -I`): `tests/test_conformidade_verde.py` 11 testes OK (69 s); `tests/test_hooks_volta_lancador.py` 22 testes OK, 25 pulados (241 s); `tests/test_hook_git_comum.py` 1 teste OK, 64 fixtures (15 s). São os três vermelhos da E20.24 (A1, A3) mais o módulo do corpus.

CI do PR #507 (run 43289298967, head 3b3d7a67): vermelho só no passo "Parecer de review (e de QA para a homolog)": `R-REVIEW` com review e segurança desatualizados (`bin/forge-testes mudou depois do parecer`), que é o que esta revalidação e a E20.31 resolvem; as partes da suíte, as verificações longas e o teto de pulados ficaram `skipping` atrás dele, então a bateria completa ainda não rodou neste head. Catraca, instalação e "árvore já provada na develop" verdes. O merge (E20.33) espera o CI de novo com os pareceres no head.

## Achados
- A4 (recomendado) hooks/conformidade.py:954 · A4 a A8 da segurança (E20.8, E20.13) seguem nomeados como cartões no Histórico (12:38), sem linha no KANBAN.md; pendente: do Jarvis, não do autor
- A5 (recomendado) hooks/conformidade.py:1076 · o corte `caminhos[:-1]` (destino nunca livre) não tem mutante nem fixture: trocado por `caminhos`, o `test_hook_git_comum` fica verde (S8); sugestão: fixture `ln h <rev-parse>/HEAD` (rc 2) e mutante G27

## Sondas
- S1 · ln -s "$(git rev-parse --git-dir)"/hooks h · espera: rc 2 R-CONFORMIDADE · obtido: rc 2
- S2 · ln "$(git rev-parse --git-dir)"/hooks/pre-push h · espera: rc 2 R-CONFORMIDADE · obtido: rc 2
- S3 · ln "$(git rev-parse --git-dir)"/forge/x h · espera: rc 2 R-CONFORMIDADE · obtido: rc 2
- S4 · ln -- "$(git rev-parse --git-dir)"/HEAD h · espera: rc 2 R-CONFORMIDADE · obtido: rc 2
- S5 · ln --symbolic "$(git rev-parse --git-dir)"/HEAD h · espera: rc 2 R-CONFORMIDADE · obtido: rc 2
- S6 · ln -t docs "$(git rev-parse --git-dir)"/HEAD · espera: rc 2 R-CONFORMIDADE · obtido: rc 2
- S7 · ln "$(git rev-parse --git-dir)"/HEAD .git/x · espera: rc 2 R-CONFORMIDADE · obtido: rc 2
- S8 · ln h "$(git rev-parse --git-dir)"/HEAD · espera: rc 2 R-CONFORMIDADE · obtido: rc 2 (com o mutante `caminhos[:-1]` → `caminhos`, o corpus segue verde: A5)
- S9 · ln -s "$(git rev-parse --git-dir)" h · espera: rc 2 R-CONFORMIDADE · obtido: rc 2 (o `.git` inteiro casa a regra do `.git`, não a genérica `.git/`)
- S10 · ln -s "$(git rev-parse --git-dir)"/hooks/ h · espera: rc 2 R-CONFORMIDADE · obtido: rc 2
- S11 · d=$(git rev-parse --git-dir); ln -s $d/config h · espera: rc 2 R-CONFORMIDADE · obtido: rc 2
- S12 · cp -s "$(git rev-parse --git-dir)"/HEAD h · espera: rc 0 · obtido: rc 0
- S13 · builtin -iu X d=$(git rev-parse --git-dir); cp x $d/hooks/pre-push · espera: rc 2 R-CONFORMIDADE · obtido: rc 2
- S14 · ln -sS "$(git rev-parse --git-dir)"/HEAD h · espera: rc 2 R-CONFORMIDADE · obtido: rc 2
- S15 · ln -s "$(git rev-parse --git-path hooks)" h · espera: rc 2 R-CONFORMIDADE · obtido: rc 2
- S16 · ln -s "$(git rev-parse --git-dir)/hooks" h · espera: rc 2 R-CONFORMIDADE · obtido: rc 2
- S17 · ln -s "$(git rev-parse --git-dir)/hooks" h; cp x h/pre-push · espera: rc 2 R-CONFORMIDADE · obtido: rc 2
- S18 · ln "$(git rev-parse --git-dir)"/HEAD docs/h · espera: rc 0 · obtido: rc 0

## Parecer
**Aprovado** no head 3b3d7a67.

A1 (E20.24) resolvido: `origens_do_rev_parse` devolve só os índices das origens (nunca a última palavra) cujo texto, com a variável da linha expandida, traz o `DIR_DO_GIT`; `link_em_protegido` dispensa nelas só o achado igual ao da regra genérica `.git/`, e os derivados de pasta (índices depois de `caminhos`) nunca entram. Falha fechada com `-S`, `-t`, opção longa, `--` e `-` sozinho (a regex `-[^-St=]+` exige letras sem valor). S1 a S18 refeitas como fixtures temporárias na minha worktree, pela máquina do `tests/test_hooks.py`, e apagadas depois: as regras específicas (`.git/hooks/`, `.git/forge/`, `.git/config`) e o destino seguem barrando; só `HEAD` e afins, lidos do `.git` para fora, liberam, como na develop. S12 e S18 (rc 0) provam que as sondas distinguem.

A3 resolvido: em `segmento_lido`, a leitura a mais do lançador descarta o ambiente, menos as variáveis cujo valor traz o `DIR_DO_GIT`, que seguem na linha; só soma restrição para escrita (S13). A2 resolvido: `test_hook_git_comum` no `FORGE_CHECK` e a contagem do `test_testes_tocados` com o comentário da etapa.

Leitura: função nova pequena, com docstring do contrato e da falha fechada; nomes claros. Guardas novas com um mutante por linha (G20 e G21 :1074, G22 :1077, G23 e G24 :1060, G25 :1416, G26 :1056); cada `de` das specs -1 a -4 aparece uma vez na fonte (conferido, AR-12). A execução dos mutantes e da cobertura é do QA (E20.32); cito sem refazer. A5 é lacuna de teste num corte que hoje está certo (S8), não defeito provado: recomendado. A classe dele é a do AR-1 (lista de mutantes incompleta), que volta neste pedido; a linha do AR fica para o Jarvis, porque este brief limita a entrega ao parecer.

Cito e não refaço (`R-SEGURANCA`): a segurança revalida o mesmo delta na E20.31 e o QA na E20.32.
