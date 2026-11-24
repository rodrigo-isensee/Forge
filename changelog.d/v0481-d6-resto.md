### Adicionado
- Hook salvar (D6, parte a): ao parar, o agente grava num commit WIP só os arquivos do escopo do brief, na cópia citada por ele, e os envia à branch do brief, sem --force e nunca em main, develop ou homolog; sem os hooks do git da cópia, que rodariam fora do sandbox. Resultado em .forge/run/salvar.log; emenda da ADR 0003, item 2 (v0481 E11.2).
