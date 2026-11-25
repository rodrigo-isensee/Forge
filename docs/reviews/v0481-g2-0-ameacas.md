---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-g2-0-ameacas
commit: bfd788efbbf839d5afa539ec806977f503903b69
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0481 (E6.9, PR #876, modelo de ameaças do G2; classe T)

Lido: `git diff 30dde218..bfd788ef` (`docs/security/ameacas/g2-parecer-status.md` e o fragmento `changelog.d/v0481-g2-0-ameacas.md`), contra a ADR 0019 (`origin/melhoria/v0481-g2-0-adr-status`, #872) e a seção 3 de `docs/propostas/g1-g3-fluxo-rapido.md` (Riscos R1 a R5) e a tabela do corte (seção 5). Sem parecer anterior na branch. Classe T, só documentação: o review é o único portão; a suíte é do CI do PR (no head bfd788ef: catraca, bateria (passos), bateria (pareceres) e instalação verdes; partes da suíte ainda em andamento na leitura), sem rerrodar aqui (R-REVIEW).

## Achados
- A1 (bloqueante) docs/security/ameacas/g2-parecer-status.md:72 · M4.1 exige o registro do `publicar` em `.forge/run/` na cópia que integra, mas cada clone tem o seu (`raiz_principal`, bin/forge-check:2340; S1): o portão publica no clone -rev e o forge-fechar roda em outro, e o parecer legítimo (corpus, :156) seria recusado. Diga onde o registro mora.
- A2 (recomendado) docs/security/ameacas/g2-parecer-status.md:105 · M3.2 é código do Forge (hook `parecer`) e é a única mitigação de código sem teste nomeado; cite o teste (por exemplo em tests/test_hooks_parecer_repo.py) que prova o merge decidido pelo resultado gravado do `pr`.
- A3 (recomendado) docs/security/ameacas/g2-parecer-status.md:74 · M10.2 fala do "blob de comparação" do desenho (R3: comparar bin/ com a origin/develop), mas M10.1 trocou a comparação pelo forge-check do PATH ou extração; diga a que leitura M10.2 serve (M1.4 e a extração de M10.1).
- A4 (recomendado) docs/security/ameacas/g2-parecer-status.md:10 · a tabela da seção 0 omite C22 (T16) na linha de R2 e C23 (T18) na linha de R3 (:11), embora as ameaças estejam listadas nelas.

## Sondas
- S1 · bash sonda_m41.sh (raiz_principal do bin/forge-check em /root/.forge-contrib/wt/v0481-g2-0-ameacas-rev e em /root/.forge-contrib/wt/v0481-g2-0-ameacas) · espera: o mesmo .forge/run para o portão e para quem integra · obtido: mesmo .forge/run: False (um .forge/run por clone)

## Parecer
Reprovado por um bloqueante, só de texto.

O que está bom e foi conferido:
- Linhas citadas do código, conferidas no 30dde218: `hooks/conformidade.py:3956-3973` e `:3965` (normalização com `strip`), `bin/forge-check:158-160`, `:904` (`commit_vale`), `:1389-1395` (`autorias`), `:1828` (`exigidos_do_pr`), `hooks/parecer.py:836` (`verificar`), `tests/catraca.py:47` (`PROTEGIDOS` com `.github/workflows/`), `hooks/conformidade.json:38` e `:77`, e as permissões de `ci.yml:27-28`, `catraca.yml:10-11` e `:22-25`, `release.yml:11` e `:52-53`. Nenhum workflow pede `statuses: write` nem usa `secrets.`, como o texto diz.
- Teste nomeado e item: toda mitigação com código no Forge tem teste nomeado e item G2.1 a G2.4, salvo M3.2 (A2). M3.3 e M17.1/M17.2 ficam com o G4 e são provadas pela leitura do dono, com o comando, o que a seção 3 permite.
- C19 a C23 estão nos casos de abuso, cada um ligado à sua mitigação e ao seu teste.
- Emendas E-1 a E-3 (seção 5) estão claras: cada uma cita a mitigação, o ponto da ADR 0019 que muda (E-1 troca o "creator igual à conta da sessão" da seção 3 pela lista vinda da base; E-2 prende o sha256 ao corpo devolvido pela API; E-3 dá corpo ao "a leitura descarta o que não veio da ferramenta") e o caminho se o arquiteto não acolher (ADR com as duas posições). O que já está acolhido na ADR bate com as seções citadas (seções 1.4, 2 e 3).
- Critério de reversão, medida e lacunas estão ligados aos da ADR 0019, sem regra nova.

A1, explicado: M4.1 pede que `pr` e `forge-fechar` recusem status sem registro do `publicar` em `.forge/run/` "na máquina que integra". Mas `.forge/run/` é por cópia: a raiz principal de um clone separado é ele mesmo (S1), e os portões trabalham em clones próprios (`<branch>-rev`, `-qa`, `-sec`), separados da cópia em que o `tech-lead` roda o `forge-fechar`. Escrito assim, o G2.2 recusaria todo parecer legítimo publicado de outro clone, o que contradiz o corpus da linha 156. Sugestão: dizer onde o registro fica para valer entre as cópias da mesma máquina (por exemplo, a raiz dos pedidos `~/.forge-contrib`, ou o `.forge/run/` da cópia principal com o clone do portão apontando para ela), com um caso no corpus de legítimos (publicado num clone, lido noutro) e o teste correspondente na seção 3. O mesmo texto vai para a emenda E-3. Severidade: bloqueia, porque a seção 2 faz de cada mitigação requisito dos itens G2.1 a G2.4.

A2 a A4 não bloqueiam; podem entrar na mesma volta.
