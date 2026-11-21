---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-til-link
commit: 9451e78c19bbbe44b640c04ff1f6a135e0b41767
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 E80.7 (revalidação da CONFORMIDADE-TIL-EM-SUBSTITUICAO e da CONFORMIDADE-LINK-POR-COPIA)

Base `adc52def`, head `9451e78c`. Delta lido (`forge-check parecer delta`): `481d2855..9451e78c`, com `hooks/conformidade.py`, `docs/hooks.md`, `tests/test_hooks.py`, o fragmento, o índice das fixtures, 47 fixtures e 7 specs de mutantes. Código do item em `hooks/conformidade.py`: 101 linhas a mais e 9 a menos desde a base (H1 dentro do teto).

## Achados
- A1 (recomendado) hooks/conformidade.py:3893 · O comentário e docs/hooks.md:56 dizem que listar o pacote segue livre, mas `unzip -l` e `dpkg -l` numa linha com o `.claude` recusam (S1). O fechamento está certo; corrija o texto (só o `tar -t` lista livre).
- A2 (recomendado) hooks/conformidade.py:2432 · O interpretador com o texto em heredoc passa e não aparece como limite: `d=~/.claude; python3 - <<EOF` com `open("$d/settings.json","a")` dá 0, e sem o `-` também (S2). A decisão de fechar ou declarar o limite é da segurança (`R-SEGURANCA`); o sandbox já nega a escrita no `.claude`.
- A3 (recomendado) hooks/conformidade.py:3894 · `LONGA_DO_LINK` e `EXTRAI_DO_TAR` escrevem os prefixos à mão em grupos aninhados, de leitura difícil; gere-os por função (`prefixos("archive")`), montada no carregamento, sem custo. Na linha 3971, use `normalizada` no lugar do `re.sub` copiado.

## Sondas
- S1 · tech-lead, `unzip -l ~/l.zip > ~/w/a.txt; cat ~/.claude/settings.json` e `dpkg -l > ~/w/a.txt; ls ~/.claude` · espera: 0 (o texto diz que listar segue livre) · obtido: 2
- S2 · tech-lead, `d=~/.claude; python3 - <<EOF` + `open("$d/settings.json","a")` + `EOF` · espera: 2 (interpretador com texto numa linha que cita o `.claude`) · obtido: 0

## Parecer
Aprovado. A mudança só aperta (`R-CONFORMIDADE`): `normalizada` só tira caracteres antes da busca e não muda a leitura da linha; `fechado_em_vigor` e `OPACO_EM_VIGOR` só acrescentam `barrar`, e o segundo fala no fim, depois do valor calculado. A sequência das reatribuições vale só no ramo `sequencia=True`, que acrescenta alvos a `calculados`. Fora dele, a regra de antes continua: mais de uma atribuição dá None. O A1 do review anterior (docs/hooks.md:56) foi atendido.

Specs realinhadas, sem enfraquecer: CF1-D1 tira só o `atribui_como_argumento` e mantém o `and not sequencia`, então continua mirando o `declare -n`. O60 (`if False or …`) desliga a regra das várias atribuições nos dois ramos. O88 (`if True`) força o `SEM_VALOR` antes da sequência. W8 só acompanha a linha nova da regex e continua tirando o ponto como programa.

Custo do corpus: `test_corpus_nos_dois_hooks` passa sem mudar `MEDIDA_DO_CORPUS` nem `RUIDO_DO_CORPUS` (`tests/apoio_volta_unica.py` fica fora do delta). A regra nova cabe no teto. `fechado_em_vigor` só roda no ramo do interpretador com opção antes do script e no dos extratores. A regex é compilada no uso, pelo cache do `re`. O que pesa na leitura é o A3, não o custo.

Testes rodados no head, em segundo plano com log e `rc=0` e TMPDIR próprio: `test_fixtures_do_til_em_substituicao` (fixtures `tilsubst-*`), `test_fixtures_do_link_por_copia` (`linkcopia-*`), `tests.test_conformidade_verde` e `tests.test_hooks_volta_corpus`. Foram 79 testes, OK, em 311 s. As outras sondas, todas como esperado: `env python3 -c` e `python3 -I -c` com `$d` do `.claude` dão 2; `tar -tf` numa linha com o `.claude` e `python3 -c` sem arquivo em vigor dão 0. A suíte inteira fica para o CI do PR (`R-REVIEW`); este brief não tem PR.
