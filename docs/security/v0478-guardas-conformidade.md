---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-conformidade
commit: 5118747e8d0299079713107b6fe233d0e264ff56
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-19
---
# Review de segurança: v0478 (E1.29, revalidação no head 5118747e)

Delta lido (`forge-check parecer delta`): `d67b2f4e..5118747e`, sem o que veio da `develop` (o merge `206db474` não muda `hooks/`). No domínio: `hooks/conformidade.py` (`:909`, `:1155`, `:1156`, `:1160`, `:2386`: o campo `comandos` de `Alvos` passa a `executados`, só o nome) e `docs/hooks.md` (linha do `_maquina`, texto do MP8 vindo da `develop`). Rodada anterior (E1.23) no git, em `f1cfedf8`.

Gatilhos: hook de conformidade (controle de escrita), estado do hook agentes (teto, R-TETO), falha fechada.

Leitura do delta: os quatro construtores de `Alvos` (`:1160`, `:1175`, `:1180`, `:1200`) são posicionais; o único leitor do campo é `:2386`, já trocado; nenhum `.comandos` de `Alvos` sobra em `hooks/`. Sem mudança de comportamento.

Estado dos achados anteriores: A8 segue fechado; A7 e A3 seguem recomendados, sem mudança (lacunas da base, não regressão).

## Só aperta?
**Sim, reconfirmado no head 5118747e**, com o P2 como única aceitação (DECISÃO DO DONO 2026-11-19 09:44: no clone, o limite de agentes vem só do `.forge/config.json` da raiz da sessão; o da worktree deixa de recusar). O delta é renome de campo, sem efeito no veredito: nada passa de recusa ou pergunta para liberado. As comparações base→head da E1.23 (D1 a D3, família do A6, A8, legítimos) valem para este head porque `hooks/` difere de `d67b2f4e` só nas 5 linhas do renome. Reexecutado o que o delta toca:
- Corpus da conformidade no head: as 2267 fixtures de `tests/hooks/conformidade/` (as 4 de prazo de produção à parte), pelo executor da suíte (`Hooks.test_fixtures` restrito ao hook): OK, 426 s.
- Família do tar que lê o campo renomeado (`--to-command`, `--checkpoint-action=exec=`, `-I`, `-F`, `--use-compress-program`, abreviações) e os legítimos dela: `EstadoDoAgentesNoClone` (`tests/test_conformidade_verde.py:311`), 11 OK, 111 s.

Suíte inteira: só no CI (brief sem suíte local); CI do head não citável (sem PR).

## Achados
- A7 (recomendado) hooks/conformidade.py:2295 · Lacuna anterior, não regressão: applet do busybox que roda programa e não está em LANCADORES (`chroot`, `setarch`, `nsenter`, `su -c`, `ash -c`...) esconde `git push --no-verify`, `rm -rf .githooks`, `gh pr merge --admin`: rc 0 na base e no head (D3, 1824 0→0).
- A3 (recomendado) hooks/conformidade.py:2375 · Lista negativa não fecha a família: sort -o, curl -o, wget -O, gzip, zip -m, patch -o, split, sqlite3, git -C init, dpkg-deb -x, ar x, pax -r, interpretador e destino vindo do arquivo (tar -P, 7z -spf, cpio -i absoluto, unzip -:) gravam no estado com rc 0. Saída: sandbox (dono).

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum gravado em `docs/security/aceites/`; o P2 tem a aceitação do dono no pedido (09:44), a registrar no PR. Ferramentas: executor de fixtures da suíte e `unittest`. Lacunas: busybox e toybox fora do PATH; suíte inteira não rodada localmente; CI do head não citável.
