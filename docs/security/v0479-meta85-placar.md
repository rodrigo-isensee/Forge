---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-meta85-placar
commit: f74d6dd71cdc9ae8c458509cf6ed7674b55bc83f
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-19
---
# Review de segurança: v0479-meta85-placar, revalidação pós-junção (v0478 E36.11)

Volta por delta (R-REVIEW): `forge-check parecer delta docs/security/v0479-meta85-placar.md`, intervalo 97ef4fd1..f74d6dd7. No domínio, só `bin/forge-placar` (junção com a develop: `fundo_demais`, teto 64, :208-231 e :240-245); fora, `changelog.d`, `tests/evals/test_placar.py` e dois mutantes. Rodadas anteriores (87aff761, 97ef4fd1) ficam no git: A1 (PARADA com data impossível) segue resolvido.

Gatilhos: nenhum (ferramenta local de leitura; sem autenticação, segredo, dependência, CI, rede nem controle do Forge).

## Achados
- A2 (recomendado) bin/forge-placar:714 · `paradas_do_ci` (META85, `fases --ci`) lê JSON sem `fundo_demais`: só capta `RecursionError`; a guarda da develop vale só para `--prs` (:240)

## Sondas
- S8 · `fases --raiz R --ci ARQ` com `[`x100000 e `]`x100000, e com `[{"conclusion":"x","a":[`...`]}]` aninhado igual · espera: sai 2 com mensagem · obtido (py 3.12.3): rc 2, `--ci ... não é uma lista de runs legível`, nos dois
- S9 · `--prs ARQ` com os 100000 `[` · espera: sai 2 pela guarda · obtido: `não é JSON legível (aninhado acima de 64 níveis)`
- S10 · `--ci ARQ` (caminho da develop, `ci_vermelha` :199) com os 100000 `[` · espera: sai 2 · obtido: traceback `RecursionError`, rc 1; idêntico na develop (fora do delta)

## Detalhe
- Ponto 1 (mesma guarda de aninhamento): **parcial**. `--prs` passa por `fundo_demais` (teto 64, passe linear, sem regex; sai 2 em qualquer versão). A leitura de JSON da META85 (`paradas_do_ci`, :712-715) não a chama; segue o mecanismo antigo (captar `RecursionError`), que funciona no 3.12 (S8) mas, pelo comentário da própria develop, não dispara no 3.14. Sem Python 3.14 no PATH, não sondei. Caminho de ataque: quem controla o arquivo `--ci` (saída de `gh run list`, gerada localmente pelo operador) é o próprio operador; no pior caso o JSON fundo é aceito no 3.14, analisado em tempo linear, sem travar nem vazar (elemento aninhado sem `.get` cai em `AttributeError`, captado). Sem ganho para atacante: inconsistência de comportamento, daí `recomendado`. Correção mínima: chamar `fundo_demais(texto)` antes do `json.loads` em :712, com a mensagem de `--prs` (dono: o autor de `bin/forge-placar`). O `ci_vermelha` (:199, S10) já era assim na develop e fica fora deste delta.
- Ponto 2 (PARADA com data impossível): **continua tratado**. `paradas_do_historico` (:688-703) tem o `try/except ValueError` por linha, aviso fixo só com o nome do pedido, demais linhas seguem, sem intervalo legível devolve None (`-`); a junção não tocou esse trecho (S5 e S7 da rodada anterior valem).
- `fundo_demais` e o teto 64 vindos da develop, lidos no delta: contagem de nível fora de strings, escape tratado, retorno cedo ao passar do teto; sem backtracking.

## Riscos aceitos e ferramentas
Sem risco aceito. Ferramentas: leitura do delta e sondas locais em `$TMPDIR` com `python3 -I`. Suíte: não rodada localmente (brief: sem suíte local); a suíte inteira fica com o CI do PR. Varredor de segredos e SAST não estão no PATH: lacuna registrada; o delta não traz credencial.
