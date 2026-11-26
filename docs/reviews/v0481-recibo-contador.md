---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-recibo-contador
commit: bc9b1d1f89bfbe7157b93cecba53420292c303e8
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 (E20.16, #921, RECIBO-CONTADOR-PELO-HOOK item 4: hook `ordens_teto`), 1.ª rodada completa

Diff lido: `git diff 707fea56..bc9b1d1f` (Base-sha = merge-base com a `develop`), 2 commits do autor (068c65c6, bc9b1d1f). Código: `hooks/ordens_teto.py` (novo, 77 linhas), `hooks/hooks.json` (+17), `bin/forge-testes` (+1); 95 linhas, dentro do H1, um comportamento.

## Achados
- A1 (bloqueante) tests/test_hook_ordens_teto.py:59 · M1, M6 e M10 sobrevivem no `bin/forge-mutante` (cópia limpa): só o erros.log os mata, e o registro do erro (`_comum.git` carrega `bin/forge-check` frio) passa dos 0,5 s do vigia e some. Prove o ramo sem depender do erros.log ou aqueça o bytecode no setUpClass.
- A2 (bloqueante) hooks/ordens_teto.py:76 · A catraca do bc9b1d1f falha por guarda sem mutante (`sem mutante · hooks/ordens_teto.py:76 · __name__ == '__main__'`), não só por esperar parecer: declare o mutante (`if False:`, as recusas o matam) ou a entrada em `isentas` com motivo, como em est-m7-verificador-decisao-2.json.

## Sondas
- S1 · `bin/forge-mutante --processos 1 --ids M1,M6,M10 tests/mutantes/v0481-recibo-contador.json tests/mutantes/v0481-recibo-contador-2.json` no bc9b1d1f · espera: M1, M6 e M10 morreu · obtido: os três `sobreviveu` (rodada inteira: 12 de 15 morreram)
- S2 · cópia limpa no bc9b1d1f com o M1, Write com `file_path` 5 · espera: linha `ordens_teto TypeError` no erros.log · obtido: ausente; o registro leva 0,50 s e o vigia de 0,5 s o corta; com `bin/__pycache__` quente, 0,10 s e a linha aparece

## Leitura
- **Faz o que o cartão pede:** o item 4 da ordem do dono de 25/11 21:47 ("o arquivo de ordens recusa ao passar do tamanho, em vez de cortar calado"). Alvo pelo `fontes` do `ordens`, comparado pelo caminho real; contagem por `escapadas` e `no_teto`, fonte única, sem número duplicado. O corte com aviso do `ordens` segue como rede para a gravação pelo Bash, limite declarado no PR e na emenda da ADR 0003.
- **Semântica do Edit:** o texto montado bate com o que a ferramenta grava sempre que ela grava (trecho único, ou `replace_all`; MultiEdit em sequência). Trecho repetido sem `replace_all` falha na ferramenta; o hook conta só a primeira troca e pode recusar antes dela, sem dano.
- **ADR 0003:** o `ordens_teto` é hook próprio que recusa (saída 2); o `ordens` continua só lendo e saindo com 0 (itens 1 e 4 da emenda). Erro interno libera com linha no erros.log (item 4). Sem git, rede nem escrita.
- **R-DECISAO:** o PR traz "Por que o existente não basta" com evidência (arquivo de 2045 caracteres em 25/11), a trava que sai, a medida (linha `ordens cortadas no teto` lida pelo tech-lead 2 versões depois) e o critério de reversão (falso positivo registrado).
- **Testes:** 12 testes de ponta a ponta (hook de verdade em subprocesso, ambiente limpo, `-s -E` como o hooks.json, justificado no docstring) e 8 fixtures; cada guarda tem o par recusa e passa. O defeito é o do A1: os ramos de entrada fora da forma (M1, M6, M10) só se distinguem pelo erros.log.
- Registros em dia: `pesos-d4.json`, `changelog.d/v0481-recibo-contador.md`, `docs/indice-forge.md` e `docs/hooks-fixtures.md` regenerados, Conventional Commits com o pedido. Conflita com o #920 nos arquivos de registro; entra depois dele.

## Verificações
- Rodados aqui no bc9b1d1f: `python3 -m unittest tests.test_hook_ordens_teto` (12 testes, OK); `bin/forge-mutante --processos 1` nas duas specs (M1, M6 e M10 sobreviveram, os outros 12 morreram); `bin/forge-mutante --cobertura --base 707fea56` (todas as guardas declaradas, fora a linha 76: A2).
- CI do bc9b1d1f (run 45880744962 e Catraca 45880744827): suíte 3.12 e 3.14 (partes 1 a 5), bateria (passos), bateria (verificações longas), bateria (python 3.14), instalação, teto de pulados e árvore já provada na develop verdes. Falham `bateria (pareceres)`, `bateria` e `catraca`; a catraca por guarda sem mutante (A2).
- ci: bc9b1d1f89bfbe7157b93cecba53420292c303e8 verde

## Parecer
Reprovado. O hook faz o que o item 4 pede, com a contagem pela fonte única do `ordens` e o limite do Bash declarado, e o desenho está certo. Volta por dois pontos do portão de mutantes: A1, três mutantes declarados sobrevivem no executor oficial porque a única prova deles é a linha do erros.log, que se perde numa cópia de bytecode frio (o CI parte de checkout limpo); A2, a guarda da linha 76 sem mutante nem isenção, que deixa a catraca vermelha. Os dois se resolvem em `tests/` e no spec, sem tocar no comportamento do hook.
