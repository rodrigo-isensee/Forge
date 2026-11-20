---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-b3-pre-push
commit: 081067f06a28a5bea555e81f69e9cbb35d8c05b2
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E57.40, PR-VERDE B3, patch do `.githooks/pre-push`, head 081067f0)

Escopo lido: `git diff 20bbbd8d..081067f0` (1 commit: o patch `docs/engineering/v0479-pv-b3-pre-push.patch`, a nota `docs/engineering/v0479-pv-b3-pre-push.md` e o fragmento do changelog). O hook em vigor não muda nesta branch: o patch é para o dono aplicar (D6), e este review não o aplica.

## Ferramentas citadas (sem refazer)
- Suíte: só no CI do PR (`R-REVIEW`); não rerrodada aqui.
- `git apply --check` do patch sobre o `.githooks/pre-push` da base (blob f9443600): aplica; `bash -n` do hook com o patch: ok.
- `bin/forge-changelog conferir --base 20bbbd8d`: ok, 1 fragmento novo.
- `shellcheck`: fora do PATH nesta estação (o CI confere quando o patch entrar).
- Tamanho (H1): 35 linhas de shell acrescentadas, um comportamento: dentro do teto.

## Leitura
- Faz o que o B3 pede: soma uma recusa depois das checagens que já existem, sem tocar nelas; mesma condição do changelog (HEAD é a ponta de uma branch enviada); `R-VERIFY` preservado, sem opção de pular.
- Falha fechada conferida por sonda: qualquer saída fora de 0 recusa o envio. O `timeout` do GNU sinaliza o grupo de processos, então os `unittest` filhos não ficam órfãos no estouro.
- Saída sanitizada (`tr -d` dos caracteres de controle) como nas checagens vizinhas; `env -u BASH_ENV -u ENV` e `python3 -I` como no resto do hook.

## Achados
- A1 (recomendado) docs/engineering/v0479-pv-b3-pre-push.patch:29 · Erro do intérprete (exceção não tratada) sai com 1 e cai em "registro desatualizado", não em "sem veredito"; a recusa vale, a mensagem engana. A tabela da nota (v0479-pv-b3-pre-push.md:23) diz o contrário. Ver sonda abaixo.
- A2 (recomendado) docs/engineering/v0479-pv-b3-pre-push.patch:10 · O comentário diz "em segundos", mas a nota mede 34 a 45 s, acima da meta R3 (p95 < 20 s) e do espírito do ENVIO-LEVE; cartão para cortar ou paralelizar o grupo mais lento de REGISTROS, como a própria nota sugere.
- A3 (recomendado) docs/engineering/v0479-pv-b3-pre-push.patch:16 · As guardas novas não trazem teste de comportamento nem spec em tests/mutantes/; o PR de aplicação do dono deve levar os 5 casos medidos da nota como teste do pre-push (ramo de recusa 1, outra saída, ausente, prazo).

## Sondas

## Parecer
Aprovado. O patch aplica limpo, é aditivo e falha fechado, que é o que o B3 e o caso de abuso pedem. Sonda do A1 (registro, não bloqueante): cópia com o patch aplicado, `bin/forge_apoio_testes.py` removido, origem sem rede, `.githooks/pre-push` com ambiente limpo; espera "não deu veredito"; obtido: `FileNotFoundError`, "pre-push: registro desatualizado (o CI reprova igual)" e rc 1. Sugestão para A1: no patch, conferir também `[ -f bin/forge_apoio_testes.py ]` na guarda de ausência e citar, na mensagem de rc 1, que a causa pode ser erro da conferência (ver o tail impresso). A1 a A3 viram cartão depois do merge.
