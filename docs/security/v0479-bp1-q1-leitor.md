---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp1-q1-leitor
commit: d0619ab2ca768b802cc9731ea5792c56447da461
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: BP1 Q1, leitor da quarentena (v0478, E37.45)

Escopo: `bin/forge_quarentena.py`, `tests/test_forge_quarentena.py`, `tests/quarentena.json`, os três specs de mutante e o fragmento de changelog (diff `004ce869..d0619ab2`). Requisitos: modelo de ameaças Q0 (`docs/security/ameacas/bp1-quarentena.md`, branch `melhoria/v0479-bp1-q0-ameacas`), casos C5, C6 e C12 com caminho "leitor" e as mitigações M4.1, M4.2, M5.1, M10.1 e M13.1. O leitor é a fonte única de runner e catraca (M4.1, S10): o que ele aceita, as duas camadas aceitam.

Gatilhos: autorizacao, ci-cd, controles-do-forge.

Atendido: M4.1 em parte (arquivo ausente, JSON inválido e tipo errado dão `([], [motivo])`, `bin/forge_quarentena.py:21`; qualquer erro zera `ativas` e `vencidas`, `:85` e `:92`; teste `test_com_erro_nao_exclui_nada_de_ativas_nem_de_vencidas`); M15.1 no leitor (sem relógio; `hoje` obrigatório, `test_o_leitor_nao_tem_padrao_de_data`); M16.1 (`vencidas`, `test_vencida_sai_sozinha_e_aparece_nas_vencidas`); prazo de 7 dias e prorrogação única com `A-<n>` novo (parte de M13.1 e M14.1; o `pr:<N>` da prorrogação fica para a Q3); teto de 3 ativas (C8 no leitor).

## Achados
- A1 (bloqueante) bin/forge_quarentena.py:56 · `desde` no futuro passa (M13.1, C12): `desde` 2026-12-30 e `prazo` 2027-01-06 com hoje 2026-11-21 dão 0 erro e a entrada fica ativa por 46 dias, sem prorrogação nem OK novo (sonda S1). Validar `desde <= hoje` e testar.
- A2 (bloqueante) bin/forge_quarentena.py:50 · `teste` sem formato (M5.1, C6): `tests.*`, `tests`, `tests.test_a.A`, lista, inteiro e texto com espaço passam com 0 erro (S2). Exigir texto `modulo.Classe.metodo` literal (identificadores separados por ponto, ao menos 3 partes, sem curinga nem espaço).
- A3 (bloqueante) bin/forge_quarentena.py:24 · chave duplicada aceita em silêncio, vale a última (C5, M4.1): `autorizacao` A-10 e depois A-99 na mesma entrada carrega A-99 sem erro (S3); o diff mostra um valor e o controle usa outro. Recusar duplicata com `object_pairs_hook` e testar.
- A4 (bloqueante) bin/forge_quarentena.py:24 · link simbólico e tamanho sem teto (M4.2, C5): `carregar` segue o link e lê o alvo, 1 entrada e 0 erro (S4); editar o alvo não toca `tests/quarentena.json` e escapa dos vigiados do rótulo (M2.1). Recusar link e arquivo acima de um teto fixo, com teste.
- A5 (recomendado) bin/forge_quarentena.py:77 · id repetido passa e conta 2 ativas para 1 teste (M10.1, S5): o runner que some ao pulado uma unidade por entrada abre folga no `teto_pulados`. Recusar `teste` repetido no `validar`.

## Sondas
- S1 · `validar([entrada(desde="2026-12-30", prazo="2027-01-06")], date(2026,11,21))` e `ativas(..., date(2027,1,6))` · espera: erro de `desde` no futuro e nenhuma ativa · obtido: `[]` e ativa em 2026-11-21 e em 2027-01-06
- S2 · `validar([entrada(teste=t)], hoje)` para t em `"tests.*"`, `"tests"`, `"tests.test_a"`, `"tests.test_a.A"`, `["tests.test_a.A.test_x"]`, `1`, `"tests.test_a.A.test_x tests.test_b"` · espera: erro de formato em cada um · obtido: `[]` nos sete
- S3 · `carregar` de `{"entradas":[{..., "autorizacao":"A-10", "autorizacao":"A-99"}]}` · espera: `([], [motivo])` · obtido: entrada com `A-99` e erros `[]`
- S4 · `carregar(link.json)` com `link.json` link simbólico para `outro.json` válido · espera: `([], [motivo])` · obtido: 1 entrada e erros `[]`

## Detalhe dos achados
- **A1** · evidência `bin/forge_quarentena.py:56` (só confere `desde <= prazo <= desde + 7`; `_erros_da_entrada`, `:48`, não recebe `hoje`) · ataque: o autor do PR de quarentena (F1) data `desde` semanas à frente; a catraca da Q3, que usa este leitor (M4.1, S10), vê prazo de 7 dias "válido", e o teste fica fora do portão por todo o intervalo até `desde`, com um OK só · severidade alta (T13) · correção mínima: passar `hoje` a `_erros_da_entrada` e reprovar `desde > hoje`; caso de teste com `desde` = hoje + 1 e mutante do ramo · esforço P · dono: `tech-lead`.
- **A2** · evidência `:50` (só confere presença) · ataque: entrada com id de módulo, classe, prefixo ou curinga exclui mais que um teste, conforme o runner da Q2 faça a exclusão; a fonte única tem de recusar antes · severidade alta (T5) · correção mínima: `teste` tem de ser `str` e casar `[A-Za-z_]\w*(\.[A-Za-z_]\w*){2,}` com `fullmatch` (sem `*`, `?`, `[`, espaço nem barra); casos com os sete valores de S2. A existência no discover continua na Q2 (M5.1, segunda metade) · esforço P · dono: `tech-lead`.
- **A3** · evidência `:24` (`json.loads` sem `object_pairs_hook`) · ataque: chave repetida (`autorizacao`, `prazo`, `prorrogacao`, `teste`) mostra no diff, ao dono e ao revisor um valor e entrega outro ao runner e à catraca · severidade média (T4) · correção mínima: `object_pairs_hook` que levanta `ValueError` com chave repetida em qualquer nível (já capturado no `except` da `:25`); caso em `test_ausente_ilegivel_e_fora_do_formato_nao_deixam_entrada` · esforço P · dono: `tech-lead`.
- **A4** · evidência `:24` (`Path(caminho).read_text` segue link e lê qualquer tamanho) · ataque: o PR troca `tests/quarentena.json` por link para outro arquivo do repositório; depois do rótulo, mudar o alvo não altera o caminho vigiado (T2, M2.1), e a entrada nova escapa da catraca. Arquivo enorme pesa no runner e na catraca · severidade média (T4) · correção mínima: recusar `Path(caminho).is_symlink()` e tamanho acima de um teto fixo (ex.: 64 KiB, com o teto em constante) antes de ler, devolvendo `([], [motivo])`; casos de link e de arquivo acima do teto. A restrição "caminho fora de `tests/`" fica para quem chama (Q2/Q3), que passa o caminho fixo · esforço P · dono: `tech-lead`.
- **A5** · evidência `:77` (`validar` não confere unicidade de `teste`) · ataque: duas entradas do mesmo teste justificam subir o `teto_pulados` em 2 e excluir 1, sobrando uma folga para outro pulo (T10) · severidade baixa (depende da contagem da Q2 e da catraca da Q3) · correção mínima: erro `teste repetido` em `validar` e caso de teste · esforço P · dono: `tech-lead`.

## Riscos aceitos e ferramentas
- Nenhum risco aceito.
- Teste novo rodado no head (`python3 -m unittest tests.test_forge_quarentena`: 20 testes, OK). A suíte inteira não foi rodada (brief: sem suíte local); o CI do head não foi consultado (credencial do `gh` fora do sandbox desta sessão): lacuna, sem efeito no veredito, que já reprova.
- Revisão estática e sondas locais em pasta temporária, com o módulo importado isolado; nada explorado fora da máquina. Varredura de segredos e SAST não aplicáveis a este diff (só dado e lógica pura, sem credencial nem rede); nenhuma ferramenta instalada.
