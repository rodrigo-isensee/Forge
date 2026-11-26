---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-pesos-gerados
commit: cb924113ca811f1c5172f7aad569e2b22b7a4595
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (E19.5, #909, PESOS-GERADOS, 1ª rodada completa)

Lido: o diff inteiro `8ae4d6c6..cb924113` (merge-base com a `develop`): `bin/forge-testes`, `scripts/suite-paralela.py`, `tests/test_forge.py` (PesosDaSuite), `tests/test_testes_tocados.py`, `tests/test_suite_paralela.py`, as specs `tests/mutantes/v0481-pesos-gerados.json` e `v0478-pv-b1-registros.json`, o fragmento do changelog. Contexto: `ler_pesos` e `repartir` (`scripts/suite-paralela.py:143-163`) e `scripts/pesos-do-ci.py:191-194`.

Gatilhos: controle do Forge (PesosDaSuite, a conferência `--registros` e o regerador `--regerar` de `bin/forge-testes`), afrouxamento de regra (PR-VERDE C1; R-CONFORMIDADE).

- ci: cb924113ca811f1c5172f7aad569e2b22b7a4595 verde

Run 45825156631 no head exato: as 10 partes da suíte (3.12 e 3.14), `bateria (passos)`, `bateria (verificações longas)`, instalação e teto de pulados verdes. Vermelhos, pela leitura do log: `catraca` (run 45825156644) pelo rótulo `afrouxa-regra` pendente do dono (asserções que caem em `tests/test_testes_tocados.py` e PesosDaSuite, testes renomeados) e pela guarda apagada sem mutante (o A1 do review); `bateria (pareceres)` porque não havia parecer de review no head; `bateria` é o agregador e cai pela de pareceres. Nenhum vermelho de teste.

## O que aperta, o neutro e o que afrouxa
- **Afrouxa (a decisão do dono, pendente):** a PR-VERDE C1 deixa de exigir o peso do módulo de teste novo. Antes, `--registros` saía 1 e PesosDaSuite reprovava; agora o módulo novo vale a mediana até a marca regerar o arquivo. Em segurança, o impacto é nulo: o peso só ordena a divisão da suíte, e nenhum peso (ausente, corrompido ou com valor inválido) tira módulo da execução (sonda S1 abaixo). O caso de abuso "módulo novo sem medida aceito", que a proposta v0479 (linha C1) queria barrar, passa a ser comportamento aceito. O ganho dele era equilíbrio de tempo, não controle.
- **Afrouxa (menor, sem caminho de ataque):** `--registros` não lê mais os pesos. Um arquivo corrompido não dá mais "sem veredito" (saída 2), mas também nunca dá verde. O JSON inválido cai no registro "pesos da suíte" (PesosDaSuite com erro), saída 1 (sonda S2). Os testes de R4 e R6 sobre esse caminho saem com ele.
- **Aperta:** `--regerar` não roda mais o medidor (`scripts/suite-paralela.py --medir <módulo>`), que executava o módulo de teste novo do PR na máquina do autor. Isso é uma execução a menos de código do PR. Os pesos entram na fiscalização de escrita fora da lista fechada: se algo os escreve, a saída é 2 (`bin/forge-testes:989`, `tests/test_testes_tocados.py` `test_escrita_fora_da_lista_fechada_sai_2` com o alvo `tests/pesos-d4.json`, mutante PG3 morto).
- **Neutro:** PesosDaSuite continua barrando o módulo da base que perde o peso (`perdas_de_peso`, `tests/test_forge.py:7279`). A base que não resolve continua saindo 2 nos dois modos (PG1 e PG4 mortos). O registro vermelho continua saindo 1 (PG2). Nada impede um PR de editar `tests/pesos-d4.json` à mão: a ordem é de processo, sem trava, e o arquivo não é controle de segurança. PesosDaSuite aceita, como antes, um head com pesos em lista de nomes ou com valor não numérico (S3), enquanto a divisão os lê como vazios e usa a mediana. É o mesmo comportamento da base, sem efeito na cobertura.

**Arquivo de pesos corrompido sem veredito:** não sobra caminho com saída 2. `--registros` dá 1 (S2), o CI dá vermelho em PesosDaSuite (JSON inválido) e `suite-paralela.py` e `pesos-do-ci.py` toleram o arquivo como `{}` e não reprovam, como na base. Nenhum dos três dá verde falso que tire teste da execução.

**Saída de R4, R5, R6 e R7 da spec v0478-pv-b1-registros: justa.** O código que eles mutavam (`modulos_sem_peso` e a conta `or sem_peso`) foi apagado. R5 e R7 guardavam justamente a regra afrouxada. A guarda de R6 (git ilegível = 2) segue no PG1, e a de R4 (pesos que não são objeto) perdeu o objeto. O brief cita só R4, R5 e R7, mas o diff tira R6 também. A troca de R6 por PG1 cobre a mesma guarda. R1 a R3 e R8 morrem no head.

## Provas locais (sondas sem bloqueante)
Nenhuma prova bloqueante. Executadas (S1 e S3 em `sonda_pesos.py`, na pasta de rascunho da sessão, contra o clone; S2 numa cópia descartável no TMPDIR):
- S1: `ler_pesos` com `{`, `[]`, `["test_a"]`, `{"test_a": "x"}` e `{"test_a": -1}` devolve `{}`, e `repartir` cobre todos os módulos nos 5 casos.
- S2: `tests/pesos-d4.json` = `{` e `bin/forge-testes --registros --base origin/develop` dão `registro desatualizado: pesos da suíte (rc=1)` e `registros rc=1`.
- S3: `perdas_de_peso` com o head `[]` dá os dois da base; com `["test_a","test_b"]` ou valores `None`/`"x"`, dá `[]` (igual à base).

## Riscos aceitos e ferramentas
Nenhum risco aceito; o afrouxamento da C1 depende do rótulo `afrouxa-regra` do dono (R-CONFORMIDADE, R-DECISAO), que a catraca cobra. Testes: `python3 -m unittest tests.test_testes_tocados.Registros tests.test_testes_tocados.Regerar tests.test_forge.PesosDaSuite tests.test_suite_paralela` com 102 testes OK; `bin/forge-mutante` deixa PG1 a PG4 e R1, R2, R3 e R8 mortos (rev `cb924113ca81`). Ferramentas: leitura estática, as sondas locais e a leitura dos logs do CI. O varredor de segredos, o SAST e o auditor de dependências não se aplicam: o diff não traz dependência nem segredo.
