---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-g2-1-publicar
commit: 0048e0c4160e62e66f5a166b068911e58c9ce848
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0481 (E6.14, #878, G2.1: forge-check parecer publicar; classe C)

Diff revisado: `30dde218..0048e0c4` (12 arquivos; código: `bin/forge_pareceres.py` novo, `bin/forge-check` +47, `hooks/conformidade.json` +4, `tests/catraca.py` +1, `bin/forge-testes`). Conferido contra a ADR 0019 (seções 1.2, 2, 3 e 8) e o modelo de ameaças `docs/security/ameacas/g2-parecer-status.md` (#876, na `develop` d49accf8).

## Achados
- A1 (bloqueante) bin/forge_pareceres.py:49 · R-QA: a catraca do CI (run 45520012052) e `forge-mutante --cobertura --base 30dde218` acusam 7 guardas sem mutante declarado: forge-check:3751, 3754 (2) e forge_pareceres.py:38, 49, 58, 69. Declare um mutante por linha com teste do ramo de falha.
- A2 (recomendado) bin/forge_pareceres.py:1 · O modelo de ameaças põe M1.4, M4.1, M4.2, M9.2, M9.3, M10.1 e M18.1 no G2.1; o corte só está no PR. Registre etapa ou cartão e a condição "o G2.2 não entra sem eles", e a emenda da coluna Item no modelo pela segurança.
- A3 (recomendado) bin/forge-check:3783 · Se o agregado falha depois do `gravar_status` do papel (forge_pareceres.py:91), o comando imprime só "recusado" e sai 1, com o status do papel já gravado. Diga o que ficou gravado, para quem roda não supor "nada gravado".
- A4 (recomendado) bin/forge-testes:153 · Falta o espaço depois da vírgula em `"test_forge_pareceres","test_conferida_por_branch"`; ajuste de formato.

## Leitura
- **ADR 0019, seção 2:** contextos fechados e sem barra (`CONTEXTOS`), estados `success`/`failure` como a tabela, descrição `<veredito> · sha256 <64> · <n> bloqueantes · <n> recomendados` com o sha256 inteiro e falha fechada acima de 140 antes de gravar qualquer coisa (M7.1); a troca de 12 por 64 hex segue a ADR, que prevalece sobre o desenho e o brief. Agregado sobre `exigidos_do_pr` (M13.1), lendo todas as páginas (`--paginate --slurp`, M19.1), com o filtro de conta antes do mais novo (M1.2).
- **ADR 0019, seção 3:** o `publicar` confere `validar_documento` estrito, `fora_do_delta` (G1.2), autoria do papel com o sha256 do texto e recusa sem `autoria.jsonl` (M9.1, sem a folga do `pr`), aceite do dono no `riscos-aceitos` (M14.1), o `commit:` como head do único PR aberto da `branch:` por nome exato (o falso do `gh` filtra pelo nome exato, item 12 do checklist), e o corpo relido pela API antes do status (M5.3), com o `html_url` preso ao PR. Toda recusa da conferência local sai antes da primeira chamada ao `gh` (os testes afirmam zero chamadas).
- **Autoria pelo sha256 sem o caminho:** o hook `autoria` grava o hash com a mesma normalização (`strip`, `hooks/conformidade.py:3965`); casar pelo hash e pelo papel, sem o caminho, prova que o mesmo papel escreveu o mesmo texto: mesma força de hoje. Até o M9.2, o arquivo em `.forge/pareceres/` sozinho não gera registro, e o `publicar` recusa: falha fechada.
- **Entrar agora é seguro (pergunta do brief):** o G2.1 só escreve; nenhum leitor (`pr`, hook `parecer`, `forge-fechar`, `entrega`) lê status de parecer até o G2.2, e o job `pareceres` e o parecer commitado seguem decidindo. Um status forjado, publicado pela cópia da branch (M10.1) ou com outra conta (M1.4), não libera nada hoje. Sem a permissão do token (D3 b), o `gh` falha e o comando recusa (`test_c17_gh_com_erro_ou_ausente`). O corte é aceitável desde que o G2.2 não entre sem as mitigações cortadas (A2).
- **Nada que barra hoje deixa de barrar:** `bin/forge-check` ganha só um subcomando; `PROTEGIDOS` só ganha `bin/forge_pareceres.py`; as 4 entradas de `conformidade.json` têm `quem` com papel: em `caminho_barrado` a entrada que casa com o papel só faz `continue` e não libera o que outra regra barra, e `.forge/pareceres/` não colide com `.forge/run/`. O `casa` com `*` cobre o caminho (`test_caminho_por_papel_em_forge_pareceres`). Limite igual ao das pastas `docs/`: a regra com papel casa só relativa à raiz da sessão, e não aos clones em `~/.forge-contrib/wt/`.
- **Segurança (leitura; parecer próprio do `security-engineer`, E6.16):** sem shell, argv em lista; corpo em JSON por `--input -`; sha validado em 40 hex antes de entrar no caminho da API; `id` do comentário em `int`. Sem segredo nem custo (R-CUSTO: só `gh` da sessão; testes com `gh` falso, sem rede).
- **Tamanho (H1):** 149 linhas de código, um comportamento (a escrita).
- **Testes:** os testes de subprocesso limpam o ambiente e chamam o Python com `-I`; `test_nenhum_workflow_usa_secrets` afirma pelo menos 3 workflows (item 11 do checklist).

## Verificações
- Teste novo, rodado aqui no 0048e0c4: `python3 -m unittest tests.test_forge_pareceres`: 29 testes, OK.
- Mutantes declarados, rodados aqui (`bin/forge-mutante --processos 1` nas 4 specs): M1 a M23 morreram (M21 por erro do teste sob o mutante).
- CI do PR no 0048e0c4: `catraca` vermelha por R-QA (A1) e pelo rótulo do dono (`bin/forge-check` e `tests/catraca.py` em `PROTEGIDOS`, esperado); `bateria (pareceres)` vermelha por falta de pareceres (esperado); suíte em andamento na leitura. Não rerrodei a suíte.

## Sondas

## Parecer
Reprovado só pelo A1: a catraca do CI está vermelha por R-QA além do rótulo do dono. Para a volta: declarar os 7 mutantes, com teste do ramo de falha onde faltar, e rodar `forge-mutante --cobertura --base 30dde218` sem nenhum `sem mutante`. No mérito, o publicar segue a ADR 0019 e o modelo nas mitigações que traz, falha fechado sem a permissão do token (D3 b) e não tira nenhuma barreira de hoje, porque nada lê status de parecer antes do G2.2. A2 a A4 são recomendados.
