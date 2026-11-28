---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-trava-corrida
commit: ef5bb776e3a958119834407b76ab0185932bc88e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E64.13, melhoria/v0479-trava-corrida)

Diff revisado: `8ee73d15..ef5bb776` (base `develop`), 2 arquivos: `tests/test_pre_push_trava.py` (+4/-1, só o fixture `SUITE_COM_PID`) e `changelog.d/v0479-trava-corrida.md` (fragmento novo, `### Corrigido`).

## Parecer
Aprovado (`R-REVIEW`).

- **Faz o que o cartão pede:** a corrida era o teste `test_parar_o_hook_para_so_a_propria_suite` ler `suite-pid` entre a criação do arquivo e a escrita do conteúdo (`int('')`), porque `write_text` cria e depois escreve. O fixture agora grava em `suite-pid.<pid>` e faz `os.replace` para `suite-pid`, que é atômico na mesma pasta: quando `exists()` fica verdadeiro, o conteúdo já está completo.
- **O teste não afrouxou o que prova:** nenhuma asserção mudou (código 1 da primeira, texto `kill <pid>` e `nunca pkill`, `ProcessLookupError` da suíte morta, a segunda segue e sai 0, sem `.verde`). O pid gravado continua o do processo da suíte (`os.getpid()` dentro dela). A mudança aperta a segunda espera (`read_text() != str(suite_da_primeira)`): antes, uma leitura vazia durante a regravação da segunda suíte satisfazia a condição cedo; agora só o pid novo completo a satisfaz.
- **Nome do temporário:** `suite-pid.<pid>` não coincide com `suite-pid` (o `exists()` confere o caminho exato), então o leitor não o vê; se a suíte morrer entre a escrita e a troca, sobra um arquivo no repositório descartável do `tmp`, sem efeito.
- **Guardas:** o diff não muda `if`, `||`, `&&`, `die`, `exit`, `return` de erro nem `raise` em código de controle; é fixture de teste, sem mutante a declarar.
- **Changelog:** fragmento presente, sem edição do `CHANGELOG.md`.
- **Suíte:** não rerrodada (a suíte inteira fica no CI do PR); rodei só o teste tocado, 3 vezes, `OK` nas três.
- **Commit:** Conventional Commits em português, um commit coerente.
