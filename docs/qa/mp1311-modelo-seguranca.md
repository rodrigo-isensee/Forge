---
tipo: qa
contrato: 1
pedido: mp1311-modelo-seguranca
branch: melhoria/mp1311-modelo-seguranca
commit: c734a22a012c8564c2c65e354e3401aa5394ae39
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-13
---
# QA: mp1311-modelo-seguranca

Parecer: aprovado na revalidação por delta até c734a22a (A1 e A2 da primeira rodada resolvidos, bug mp1311-01 fechado). A rodada anterior (head 4b78a54b) está preservada abaixo.

Item 9 do pedido melhorias-de-projeto-1311 (E1.9): a migração `migrations/0.47.1/migrar` cria `docs/security/_modelo.md` em projeto existente. Head testado 4b78a54b (o diff até a base efe7c9e8 é a migração, o LEIA, o fragmento de changelog e a classe `ModeloDeSegurancaNoProjeto`). Não há PR, então não há check-run `bateria` para citar: rodei só os meus cenários (carga da máquina alta).

## Achados
- A3 (recomendado) migrations/0.47.1/migrar:27 · as flags O_EXCL|O_NOFOLLOW da abertura não têm mutante (só uma corrida entre a checagem e a abertura as exerce); aceitável como defesa em profundidade, sem teste determinístico.


## Rodada anterior (histórico)
- A1 da rodada anterior (bloqueante, resolvido): migrations/0.47.1/migrar:13 · reproduzido: com docs/security como link simbólico para pasta de fora, a migração cria _modelo.md fora do projeto (R-SEGURANCA, bug em docs/qa/bugs/mp1311-01-migracao-segue-link.md); usar lstat e recusar link.
- A2 da rodada anterior (recomendado, resolvido): tests/mutantes/mp1311-modelo-seguranca.json:1 · a spec de mutantes da migração não está versionada na branch (o review já apontou); rodei a minha, de seis mutantes, e todos morreram; vale o autor versionar a spec ou a minha.

## Critério → teste → resultado
O pedido não traz `CA-n` numerados para o item 9; as obrigações vêm do escopo do item: o modelo chega ao projeto novo e ao existente, sem sobrescrever e idempotente.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| projeto novo recebe o modelo (init) | `test_projeto_novo_recebe_o_modelo` | bytes iguais ao template | passou (já passava na base: o init já copiava) |
| projeto existente sem o modelo recebe pela atualização, com commit e árvore limpa | `test_projeto_existente_recebe_o_modelo_pela_atualizacao` | pasta `docs/security` ausente | passou; vermelho na base (ERROR) |
| modelo do projeto não é sobrescrito | `test_atualizacao_nao_sobrescreve_o_modelo_do_projeto` | arquivo já existente | passou; mutante M1 mata |
| repetir a migração não muda nada (saída vazia, bytes iguais) | `test_migracao_repetida_nao_muda_nada` | segunda rodada | passou; vermelho na base (FAIL) |
| LEIA resume o efeito para o `forge-upgrade` | `test_leia_resume_para_o_forge_upgrade` | linha 3 do LEIA | passou; vermelho na base (ERROR) |

## Cenários e resultado real
- Cinco testes da classe passam no head (`Ran 5 tests ... OK`).
- Vermelho: com os três arquivos da migração revertidos à base e o teste mantido, 3 dos 5 caem (2 ERROR, 1 FAIL). Os outros dois passam na base por natureza: o do init (o init já copiava) e o de não sobrescrever (sem migração nada sobrescreve); este segundo é provado pelo mutante M1. A rodada `forge-testes --vermelho` com `--modulos tests.test_forge` estourou o meu prazo de 520 s sob carga (rc 124, sem veredito, nunca vale como vermelho); `-k` não combina com `--vermelho`, por isso a prova acima é a manual, em cópia do head com a migração removida.
- Mutação (seis mutantes, um por linha de guarda mudada: `if not alvo.exists()` duas trocas, `mkdir`, `copy`, `print` dentro do if, LEIA): todos morreram; em M2 o teste dá erro em vez de falha (o arquivo não existe), e a ferramenta o conta como morto com o aviso.
- Ponta a ponta: o `forge-upgrade --ate 0.47.1` sobre repositório git de projeto em 0.46.0 cria o modelo, commita `chore(forge): migração 0.47.1` e deixa a árvore limpa. Sem `--ate`, com o plugin ainda em 0.46.0, o upgrade diz "nada a fazer": a migração só vale quando a release subir a versão para 0.47.1 (o fragmento de changelog já marca "requer migração"); não é defeito, é dependência da release.
- Sonda de abuso (confirma o A1 da segurança): `mkdir proj/docs; ln -s $TMPDIR/s/fora proj/docs/security; migrar proj` imprime `criado docs/security/_modelo.md` e `ls fora` mostra `_modelo.md`. `alvo.exists()` segue o link e `shutil.copy` escreve através dele. Os testes do autor não cobrem link; falta teste de link para pasta de fora e de link pendurado no arquivo.
- Bordas: modelo existente com conteúdo próprio preservado; pasta `docs/security` ausente criada; execução repetida idempotente. Sem interface, então acessibilidade e teclado não se aplicam.

## Provas
```
vermelho (manual, base efe7c9e8): ERROR test_leia_resume_para_o_forge_upgrade; ERROR test_projeto_existente_recebe_o_modelo_pela_atualizacao; FAIL test_migracao_repetida_nao_muda_nada; Ran 5 tests, FAILED (failures=1, errors=2)
head 4b78a54b: Ran 5 tests in 5.488s OK
forge-mutante: pedido=mp1311-modelo-seguranca rev=4b78a54b4ebb spec=f321877d... M1 morreu · M2 morreu (erro) · M3 morreu · M4 morreu · M5 morreu · M6 morreu; rc=0
sonda: migrar proj (docs/security -> link para fora) => criado docs/security/_modelo.md; ls fora => _modelo.md
```

## Revalidação por delta (c734a22a)
`forge-check parecer delta` listou no meu domínio: `migrations/0.47.1/migrar`, `tests/mutantes/mp1311-modelo-seguranca.json` e `tests/test_forge.py`. Sondas de link reproduzidas (todas recusadas, rc 1, nada fora do projeto): docs/security como link para pasta de fora, link pendurado no `_modelo.md`, link existente para pasta de fora, docs como link. Caminhos felizes mantidos: projeto novo cria o modelo; segunda rodada rc 0 sem saída; projeto passado como link para diretório funciona (o `resolve()` o segue de propósito). Testes novos: link pendurado e pasta como link (7 testes da classe, OK). Não recebi o texto do relatório do autor com os dois desvios; julguei os que o diff mostra: (1) a spec usa um mutante (M1) para as duas pastas, porque é uma só linha de guarda (`islink(pasta)` no laço), aceito; (2) a numeração pula M4 (sem equivalente), inofensivo. Sem PR, sem check-run `bateria`: rodei só a classe afetada e os mutantes.

```
head c734a22a: Ran 7 tests in 3.517s OK
forge-mutante: pedido=mp1311-modelo-seguranca rev=c734a22a012c spec=5997810b... M1 morreu · M2 morreu · M3 morreu · M5 morreu; rc=0
sondas: p1/p2/p3/p4 => recusado ..., rc=1 cada; ls das pastas de fora vazio
```
