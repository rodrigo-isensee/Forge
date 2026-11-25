---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-ci-descendente-parecer
commit: aa26249f6f12bb20aa2b8d3023bd820293eaad48
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: v0481 E8.17 (volta do #895 por delta, de 2364a43b a aa26249f)

## Gatilhos
Gatilhos: controle do Forge (portão `forge-check pr`, PARECER-LE-O-CI), analisador de caminhos do diff

## Achados
- A3 (bloqueante) skills/engineering-practices/SKILL.md:54 · tests/test_metricas_texto.py:88 falha no aa26249f: engineering-practices 7113 caracteres > teto 6982 e qa-testing (skills/qa-testing/SKILL.md:46) 11774 > 11761; suíte parte 1/5 vermelha no CI nas duas versões (S3). Encurte; subir o teto é afrouxar.

## Delta lido
`git diff 2364a43b..aa26249f` (commit `aa26249f`, E8.14): `bin/forge-check:2192-2199`, `skills/engineering-practices/SKILL.md:54`, `skills/qa-testing/SKILL.md:46`, `tests/test_forge_check_pr.py:549-564` e `:595`, `tests/mutantes/v0481-ci-descendente-parecer.json` (M3, M5) e `-2.json` (M10, M11). Os outros três arquivos do intervalo são os pareceres da rodada anterior. O resto da mudança foi lido na rodada de `2364a43b` (no git) e não mudou.

## Achados anteriores
- A1 (bloqueante): **corrigido.** `bin/forge-check:2198` lê o diff com `bruto=True` e `nomes_z`, sem o `strip`. O caso está em `tests/test_forge_check_pr.py:549`, com espaço, tab e quebra de linha, e o mutante M10 o mata.
- A2 (bloqueante): **corrigido.** `python3 -m unittest tests.test_orcamento_instrucao` deu 8 OK no `aa26249f` (S2).

## Sondas
- S1 · sonda_s1.py (repos descartáveis): commit c1 sobre c0 que só cria ' docs/reviews/x.py', '\tdocs/security/x.py', '\ndocs/qa/x.py' ou '\rdocs/qa/x.py'; so_pareceres_ate(c0, c1) · espera: False · obtido: False nos quatro (no 2364a43b: True nos quatro)
- S2 · python3 -m unittest tests.test_orcamento_instrucao no aa26249f · espera: OK · obtido: OK (8 testes)
- S3 · python3 -m unittest tests.test_metricas_texto no aa26249f (no eeb81062: OK) · espera: OK · obtido: FAILED (engineering-practices caracteres 7113 > teto 6982; qa-testing caracteres 11774 > teto 11761)

## Detalhe dos achados
**A3.** A evidência está no CI do #895 no `aa26249f` (run 45589057763). `suíte (python 3.12, parte 1/5)` (job 139118556970) e `suíte (python 3.14, parte 1/5)` (job 139118557306) falham em `test_metricas_texto.MetricasDoTexto.test_nenhuma_metrica_passa_do_teto`, contra os tetos de `tests/fixtures/metricas-texto.json`. As outras partes da suíte, as baterias de passos e de verificações longas e a instalação estão verdes. O defeito já existia no `2364a43b`, com 7167 caracteres em engineering-practices e, em qa-testing, 11947 caracteres e frase média 194 acima de 192. Lá, a parte 1/5 estava cancelada pelo envio do parecer de review, e por isso a rodada anterior não o viu. O encurtamento da E8.14 cumpriu o orçamento de instrução, mas não o de métricas do texto. Isso não é achado de segurança. É defeito provado, e deixa o CI do sha revisado vermelho: sem CI verde, nenhum portão aprova (PARECER-LE-O-CI). Correção mínima: cortar pelo menos 131 caracteres da frase G3.7 em `skills/engineering-practices/SKILL.md:54` e 13 em `skills/qa-testing/SKILL.md:46`, sem tirar os invariantes das duas skills. Depois, conferir juntos `tests.test_metricas_texto` e `tests.test_orcamento_instrucao`, sem mexer em teto. O comando que tira a dúvida é `python3 -m unittest tests.test_metricas_texto tests.test_orcamento_instrucao`. Esforço P. Dono: autor da E8.14.

## Parecer
Reprovado só por A3. A parte de segurança do delta está correta e fecha A1.

- **O que aperta:** `so_pareceres_ate` (`bin/forge-check:2198`) não perde mais o branco inicial do 1º caminho (S1). Com `--ignore-submodules=none`, um gitlink fora das pastas aparece mesmo com `diff.ignoreSubmodules=all` na configuração (a sonda deu False; no `2364a43b`, True). Um nome que não é UTF-8 fora das pastas também mudou: antes, `UnicodeDecodeError` subia de `git()` em modo texto; agora o `surrogateescape` do `nomes_z` devolve False, falha fechada. O separador continua sendo só o NUL (`-z`).
- **O que é neutro:** o critério das três pastas, o `--no-renames`, o `merge-base --is-ancestor` e `leu_o_ci_via` estão iguais byte a byte. O falso de `test_erro_do_git_diff_falha_fechado` (`tests/test_forge_check_pr.py:595`) agora devolve `b""`, como o `git()` real com `bruto`. Ele não é mais frouxo que o script. No encurtamento das skills, os trechos de `invariantes` (`tests/config.json`) das duas casam no `2364a43b` e no `aa26249f`: 12 de 12 em `skills/qa-testing/SKILL.md` e 10 de 10 em `skills/engineering-practices/SKILL.md`. As frases que saíram do QA ("A suíte inteira roda no CI do PR" e "a ele e à segurança") seguem em `agents/qa-engineer.md:15`, onde "suíte inteira roda só no CI" é invariante com `R-QA`. A lista das três pastas saiu do texto ("cujo diff toca apenas pareceres"), mas a regra segue no código (`PASTAS_DOS_PARECERES`, `bin/forge-check:2190`) e no teste. Nenhum teto foi mexido.
- **O que afrouxa:** nada além do que a rodada anterior já descreveu, ou seja, o run cancelado do `commit:` vale pelo run de um descendente que mexe só em pareceres. Com A1 fechado, esse descendente não pode trazer código diferente.
- **Testes e mutantes:** `python3 -m unittest tests.test_orcamento_instrucao tests.test_forge_check_pr.LeOCiVia tests.test_forge_check_pr.LeOCiNoCmdPr` deu 28 OK. Com `bin/forge-mutante` nas duas specs, M1 a M11 morreram (M9 pelo erro do teste declarado, porque a guarda é "nem quebra"). A saída de `bin/forge-mutante --conferir --todas` no `aa26249f` é igual à da base `eeb81062` (diff vazio; rc 1 nas duas, com as mesmas 26 linhas de specs antigas).
- **CI do #895 no `aa26249f`:** a suíte parte 1/5 está vermelha (A3), e por isso `bateria` e `bateria (python 3.14)` também. `bateria (pareceres)` e `catraca` estão vermelhos por construção. O resto está verde. Sem a linha `- ci:`, o parecer não aprova.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Usei git, a biblioteca padrão e o `gh` (só leitura de checks, anotações e runs). Não usei gitleaks nem osv-scanner, porque o delta não traz segredo nem dependência.
