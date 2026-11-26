---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-g2-publicar-caminho
commit: 0cdf17c362c8ecb59196d5234a7db013ea334e71
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-26
---
# QA: v0481 G2 publicar confere caminho (#916)

## Achados
- A1 (recomendado) bin/forge-check:3883 · PARECER_A_PUBLICAR duplica a constante de hooks/conformidade.py:4069 (com grupos); nenhum teste confere que as duas aceitam o mesmo conjunto de caminhos, e a deriva reabre a divergência hook x publicar.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Obrigação: texto copiado de fora da raiz não publica (S1) | test_s1_texto_de_docs_reviews_publicado_de_fora_do_projeto; M41 | caminho fora da raiz | passou |
| Obrigação: registro de outro caminho (docs/reviews/) não vale (S1) | test_s1_texto_de_docs_reviews_copiado_para_o_parecer_a_publicar; M38 | caminho do registro | passou |
| Obrigação: só o último registro do caminho vale (S2) | test_s2_veredito_superado_nao_volta_a_publicar; M39 | registro superado | passou |
| Obrigação: sem autoria.jsonl ou sem registro, recusa (M9.1) | test_c11_sem_autoria_jsonl_recusa; M40, M42 | arquivo ausente, vazio | passou |
| Obrigação: papel e sha256 do último registro (M9.1) | test_c11_papel_autor_publica, test_texto_mudado_depois_da_autoria; M17, M18 | papel errado, texto mudado | passou |

## Cenários e resultado real
- Diff lido contra o merge-base 3c833f3f: guarda mudada em bin/forge-check (caminho relativo à raiz via realpath, fullmatch, último registro do caminho); cada condição mudada tem mutante (M38 a M42, M17, M18).
- Módulos tocados, local: unittest de tests.test_conformidade_pareceres e tests.test_forge_pareceres: Ran 44 tests, OK.
- Vermelho: bin/forge-testes --vermelho 3c833f3f... --modulos test_conformidade_pareceres: `vermelho: base=3c833f3f1ba1 head=0cdf17c362c8`; revertidos à base: bin/forge-check; os 3 testes (S1, S1, S2) H=ok, B=falha, "prova (asserção)"; contagem: não prova (passa na base)=6; prova=3.
- Mutantes: bin/forge-mutante nas specs v0481-g2-publicar-caminho.json e v0481-g2-1-publicar-3.json: M38, M39, M40, M41, M42, M17, M18, M19, M20 todos "morreu", nenhum sobrevivente (M40 e M42 morrem por erro do teste sob o mutante, com controle verde).
- O registro do hook usa o caminho relativo à raiz (hooks/conformidade.py:4083), o mesmo que o publicar passa a calcular.
- CI do PR no head exato: "bateria (pareceres)" e "catraca" em falha (esperam parecer, conforme o brief); as 10 partes "suíte (python 3.12 e 3.14, partes 1 a 5)" estavam pending na leitura, as demais verdes. Por isso não gravo a linha ci verde: reler gh pr checks 916 quando a suíte concluir e, estando verde, gravá-la na volta.
