### Corrigido
- Hooks: `git rm|mv|checkout|restore` de caminho em vigor passam pela conferência de escrita e remoção, e a falta de `.forge/versao` numa sessão marcada como projeto falha fechado nas ações críticas (o vigia avisa), em vez de desligar os hooks (BP-1).
