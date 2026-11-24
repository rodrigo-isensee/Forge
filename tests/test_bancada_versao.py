"""Bench de versões com agentes (BENCH-VERSAO, E175.3): o roteiro tests/bancada/versao.py com `claude` e `gh` falsos,
Forge e remoto locais e testes escondidos de mentira; nunca chama o modelo nem a rede."""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import remoto_sem_manutencao, sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("bancada_versao", RAIZ / "tests" / "bancada" / "versao.py")
v = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v)

MARCA = "zqmarcadeteste0000"
LIMPO = {"PATH": "/usr/bin:/bin"}
# A lista fica aqui, e não lida de v.AMBIENTE_PROIBIDO: tirar um nome de lá tem de derrubar o teste (R-CUSTO).
PROIBIDAS = ("CI", "GITHUB_ACTIONS", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL",
             "CLAUDE_CODE_USE_BEDROCK", "CLAUDE_CODE_USE_VERTEX", "CLAUDE_CODE_USE_FOUNDRY")
DE_AGENTE = ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT")

# claude falso: grava o argv e o ambiente pago que recebeu, emite o stream-json do cenário e, conforme o cenário, abre
# o "PR" (commit e pr.json), troca o teste escondido ou ignora o SIGTERM
CLAUDE = r'''#!{py}
import json, os, signal, subprocess, sys, time
from pathlib import Path
base = Path(os.environ["FALSO_DIR"])
cen = json.loads((base / "cenario.json").read_text())
if cen.get("ignora_term"):
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
chamadas = base / "chamadas.jsonl"
n = sum(1 for _ in open(chamadas)) if chamadas.exists() else 0
with open(chamadas, "a") as f:
    f.write(json.dumps(sys.argv[1:]) + "\n")
with open(base / "ambiente.jsonl", "a") as f:
    f.write(json.dumps(sorted(os.environ)) + "\n")
plugin = sys.argv[sys.argv.index("--plugin-dir") + 1]
def emite(ev):
    print(json.dumps(ev), flush=True)
emite({{"type": "system", "subtype": "init", "session_id": "s1", "apiKeySource": cen.get("api", "none"),
       "plugins": [{{"name": "forge", "path": plugin}}]}})
if cen.get("vivo"):
    time.sleep(cen["vivo"])
    (base / "vivo").touch()
uso = {{"input_tokens": 10, "output_tokens": 5, "cache_creation_input_tokens": 2, "cache_read_input_tokens": 100}}
for i in range(cen.get("agentes", 1)):
    emite({{"type": "assistant", "session_id": "s1", "message": {{"id": f"m{{n}}-{{i}}", "usage": uso,
          "content": [{{"type": "tool_use", "id": f"t{{n}}-{{i}}", "name": "Task", "input": {{}}}}]}}}})
    emite({{"type": "assistant", "session_id": "s1", "message": {{"id": f"m{{n}}-{{i}}", "usage": uso, "content": []}}}})
if cen.get("marca"):
    Path("anotacao.txt").write_text("copiei " + cen["marca"])
if cen.get("troca"):
    Path(cen["troca"]).write_text('print("resultado: 2/2")\n')
time.sleep(cen.get("dorme", 0))
if n >= cen.get("pr_na_chamada", 99):
    g = ["git", "-c", "user.name=t", "-c", "user.email=t@t"]
    Path("src").mkdir(exist_ok=True)
    Path("src/entregue.txt").write_text("ok")
    subprocess.run(g + ["switch", "-q", "-c", "feat/romanos"], check=True)
    subprocess.run(g + ["add", "-A"], check=True)
    subprocess.run(g + ["commit", "-q", "-m", "feat: romanos"], check=True)
    subprocess.run(g + ["push", "-q", "origin", "feat/romanos"], check=True)
    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    (base / "pr.json").write_text(json.dumps([{{"number": 7, "state": "OPEN", "isDraft": True, "headRefOid": sha}}]))
emite({{"type": "result", "session_id": "s1", "is_error": False}})
'''
# gh falso: `repo view` lê repo.json (padrão: público, vazio, do dono), `api user` responde o dono, `pr list` lê pr.json
GH = r'''#!{py}
import json, os, sys
from pathlib import Path
base = Path(os.environ["FALSO_DIR"])
if sys.argv[1:3] == ["repo", "view"]:
    repo = base / "repo.json"
    print(repo.read_text() if repo.exists() else json.dumps({{"visibility": "PUBLIC", "isEmpty": True, "owner": {{"login": "dono"}}}}))
elif sys.argv[1:3] == ["api", "user"]:
    print("dono")
else:
    pr = base / "pr.json"
    print(pr.read_text() if pr.exists() else "[]")
'''
ESCONDIDO = r'''import os, sys
from pathlib import Path
# marca: {marca}
ok = (Path(os.environ["ROMANOS_PROJETO"]) / "src" / "entregue.txt").is_file()
print("resultado: %d/2" % (2 if ok else 0))
'''
FORGE_INIT = """#!/bin/bash
mkdir -p "${@: -1}/.claude"
printf '{"enabledPlugins": {"forge@forge": true}, "permissions": {}}' > "${@: -1}/.claude/settings.json"
"""


def git(*args, cwd=None):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd, check=True,
                   capture_output=True, env=sem_manutencao())


class Versao(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        d = self.d = Path(tmp.name)
        self.falso, self.bin = d / "falso", d / "bin"
        self.falso.mkdir()
        self.bin.mkdir()
        for nome, fonte in (("claude", CLAUDE), ("gh", GH)):
            (self.bin / nome).write_text(fonte.format(py=sys.executable), encoding="utf-8")
            (self.bin / nome).chmod(0o755)
        esc = self.escondidos = d / "bench" / "escondidos" / v.VERSAO_ESCONDIDOS
        esc.mkdir(parents=True)
        (esc / "test_escondido.py").write_text(ESCONDIDO.format(marca=MARCA), encoding="utf-8")
        (esc / "marca.txt").write_text(MARCA + "\n", encoding="utf-8")
        amb = mock.patch.dict(os.environ, sem_manutencao({
            "PATH": f"{self.bin}:{os.environ.get('PATH', '/usr/bin:/bin')}", "HOME": str(d / "casa"),
            "FALSO_DIR": str(self.falso)}))
        amb.start()
        self.addCleanup(amb.stop)
        self.forge = d / "forge"
        (self.forge / "bin").mkdir(parents=True)
        (self.forge / "bin" / "forge-init").write_text(FORGE_INIT, encoding="utf-8")
        git("init", "-q", "-b", "main", str(self.forge))
        git("add", "-A", cwd=self.forge)
        git("commit", "-q", "-m", "x", cwd=self.forge)
        git("tag", "v9.9.9", cwd=self.forge)
        self.remoto = d / "remoto.git"
        git("init", "-q", "--bare", str(self.remoto))
        remoto_sem_manutencao(self.remoto)
        config = d / "config.json"
        sha_marca = hashlib.sha256(MARCA.encode()).hexdigest()
        config.write_text(json.dumps({"termos_proibidos_hash": [{"tipo": "trecho", "n": len(MARCA), "sha256": sha_marca}]}))
        self.quadro = d / "quadro" / "bench-versao.md"
        congelados = {n: hashlib.sha256((esc / n).read_bytes()).hexdigest() for n in ("test_escondido.py", "marca.txt")}
        for alvo, valor in (("CONGELADOS", congelados), ("MARCA_SHA256", sha_marca), ("CONFIG", config), ("INTERVALO", 0.05)):
            p = mock.patch.object(v, alvo, valor)
            p.start()
            self.addCleanup(p.stop)

    def cenario(self, **c):
        (self.falso / "cenario.json").write_text(json.dumps(c), encoding="utf-8")

    def chamadas(self, arquivo="chamadas.jsonl"):
        arq = self.falso / arquivo
        return [json.loads(x) for x in arq.read_text().splitlines()] if arq.exists() else []

    def rodar(self, *extra, env=LIMPO, executar=True):
        argv = ["--tag", "v9.9.9", "--repo", "dono/bench-teste", "--bench", str(self.d / "bench"), "--quadro",
                str(self.quadro), "--forge", str(self.forge), "--remoto-url", str(self.remoto), *extra]
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = v.principal(argv + (["--executar"] if executar else []), env)
        return rc, out.getvalue(), err.getvalue()

    def registro(self):
        (arq,) = (self.d / "bench" / "rodadas").glob("*/rodada.json")
        return json.loads(arq.read_text(encoding="utf-8"))

    def test_sem_executar_so_valida_e_estima_sem_chamar(self):
        self.cenario()
        rc, saida, _ = self.rodar(executar=False)
        self.assertEqual(rc, 0)
        self.assertIn("simulação", saida)
        self.assertIn("1,0 M", saida)
        self.assertEqual(self.chamadas(), [])
        self.assertFalse((self.d / "bench" / "rodadas").exists())

    def test_recusa_com_ci_ou_credencial_paga(self):
        self.cenario(pr_na_chamada=0)
        self.assertEqual(set(v.AMBIENTE_PROIBIDO), set(PROIBIDAS))
        for nome in PROIBIDAS:
            with self.subTest(nome=nome):
                rc, _, err = self.rodar(env={**LIMPO, nome: ""})
                self.assertEqual(rc, 2)
                self.assertIn(nome, err)
                rc, _, _ = self.rodar(env={**LIMPO, nome: "1"}, executar=False)
                self.assertEqual(rc, 2)
        self.assertEqual(self.chamadas(), [])

    def test_executar_numa_sessao_de_agente_recusa_e_a_simulacao_passa(self):
        self.cenario(pr_na_chamada=0)
        for nome in DE_AGENTE:
            with self.subTest(nome=nome):
                rc, _, err = self.rodar(env={**LIMPO, nome: "1"})
                self.assertEqual((rc, nome in err), (2, True))
                self.assertEqual(self.rodar(env={**LIMPO, nome: "1"}, executar=False)[0], 0)
        self.assertEqual(self.chamadas(), [])

    def test_sessao_nao_herda_credencial_paga_nem_marca_de_agente(self):
        self.cenario(pr_na_chamada=0)
        herdadas = {n: "1" for n in PROIBIDAS + DE_AGENTE}
        with mock.patch.dict(os.environ, herdadas):
            self.assertEqual(self.rodar()[0], 0)
        (ambiente,) = self.chamadas("ambiente.jsonl")
        self.assertIn("FALSO_DIR", ambiente)  # o resto do ambiente do dono chega
        self.assertEqual(set(ambiente) & set(herdadas), set())

    def test_init_com_api_paga_encerra_a_sessao_sem_retomar(self):
        self.cenario(api="ANTHROPIC_API_KEY", dorme=30)
        inicio = time.monotonic()
        self.assertEqual(self.rodar()[0], 0)
        self.assertLess(time.monotonic() - inicio, 20)
        r = self.registro()
        self.assertEqual((r["limite"], r["api_key_source"], len(self.chamadas())), ("api-paga", "ANTHROPIC_API_KEY", 1))

    def test_api_paga_mata_a_sessao_sem_esperar_o_intervalo(self):
        self.cenario(api="apiKeyHelper", vivo=1)
        with mock.patch.object(v, "INTERVALO", 3):
            self.assertEqual(self.rodar()[0], 0)
        self.assertFalse((self.falso / "vivo").exists())  # morta antes de 1 s, não na conferência de 3 s
        self.assertEqual(self.registro()["limite"], "api-paga")

    def test_repo_que_nao_e_publico_vazio_e_do_dono_recusa(self):
        for nome, dados in (("privado", {"visibility": "PRIVATE", "isEmpty": True, "owner": {"login": "dono"}}),
                            ("com conteúdo", {"visibility": "PUBLIC", "isEmpty": False, "owner": {"login": "dono"}}),
                            ("de outro", {"visibility": "PUBLIC", "isEmpty": True, "owner": {"login": "outro"}})):
            with self.subTest(nome):
                (self.falso / "repo.json").write_text(json.dumps(dados))
                self.cenario(pr_na_chamada=0)
                rc, _, err = self.rodar()
                self.assertEqual((rc, "público, vazio" in err), (1, True))
        self.assertEqual(self.chamadas(), [])

    def test_remoto_url_que_nao_e_pasta_local_recusa(self):
        rc, _, err = self.rodar("--remoto-url", "https://exemplo.invalid/x.git", executar=False)
        self.assertEqual((rc, "--remoto-url" in err), (1, True))

    def test_claude_fora_do_path_recusa(self):
        self.cenario(pr_na_chamada=0)
        with mock.patch.object(v.shutil, "which", return_value=None):
            rc, _, err = self.rodar()
        self.assertEqual((rc, "não está no PATH" in err), (1, True))
        self.assertFalse((self.d / "bench" / "rodadas").exists())

    def test_teste_escondido_alterado_ou_ausente_recusa(self):
        arq = self.escondidos / "test_escondido.py"
        arq.write_text(arq.read_text() + "\n", encoding="utf-8")
        rc, _, err = self.rodar(executar=False)
        self.assertEqual((rc, "alterado" in err), (1, True))
        arq.unlink()
        rc, _, err = self.rodar(executar=False)
        self.assertEqual((rc, "ausente" in err), (1, True))

    def test_escondido_trocado_pela_sessao_nao_da_nota(self):
        self.cenario(troca=str(self.escondidos / "test_escondido.py"))
        self.assertEqual(self.rodar()[0], 0)
        r = self.registro()
        self.assertEqual((r["pr"], r["avaliacao"]["resultado"]), (None, "escondido alterado"))

    def test_marca_fora_do_config_ou_que_nao_bate_recusa(self):
        v.CONFIG.write_text(json.dumps({"termos_proibidos_hash": []}))
        rc, _, err = self.rodar(executar=False)
        self.assertEqual((rc, "termos_proibidos_hash" in err), (1, True))
        with mock.patch.object(v, "MARCA_SHA256", "0" * 64):
            self.assertIn("não bate", self.rodar(executar=False)[2])

    def test_marca_na_arvore_da_tag_recusa(self):
        (self.forge / "vazou.md").write_text(f"copiado: {MARCA.upper()}\n")
        git("add", "-A", cwd=self.forge)
        git("commit", "-q", "-m", "vazou", cwd=self.forge)
        git("tag", "-f", "v9.9.9", cwd=self.forge)
        rc, _, err = self.rodar(executar=False)
        self.assertEqual((rc, "vazaram" in err), (1, True))

    def test_tag_inexistente_e_repo_malformado_recusam(self):
        rc, _, err = self.rodar("--tag", "v0.0.0", executar=False)
        self.assertEqual((rc, "não existe" in err), (1, True))
        rc, _, err = self.rodar("--repo", "sem-barra", executar=False)
        self.assertEqual((rc, "--repo" in err), (1, True))

    def test_rodada_retoma_com_a_resposta_fixa_avalia_o_pr_e_grava_a_linha(self):
        self.cenario(pr_na_chamada=1, agentes=2)
        rc, saida, err = self.rodar()
        self.assertEqual(rc, 0, err)
        primeira, segunda = self.chamadas()
        for cmd in (primeira, segunda):
            self.assertEqual(cmd[cmd.index("--permission-mode") + 1], "auto")
            self.assertEqual(cmd[cmd.index("--agent") + 1], "forge:jarvis")
            self.assertFalse([a for a in cmd if "bypass" in a.lower() or "dangerously" in a])
        self.assertEqual(primeira[1], v.PEDIDO.read_text(encoding="utf-8"))
        self.assertNotIn("--resume", primeira)
        self.assertEqual(segunda[1], v.RESPOSTA.read_text(encoding="utf-8"))
        self.assertEqual(segunda[segunda.index("--resume") + 1], "s1")
        r = self.registro()
        self.assertTrue(r["plugin_forge"][0]["path"].endswith("/forge"))
        self.assertEqual((r["voltas"], r["agentes"], r["limite"], r["marca"]), (1, 4, None, None))
        self.assertEqual(r["tokens"], {"novos": 68, "processados": 468})  # 4 mensagens (repetidas não contam)
        self.assertEqual((r["avaliacao"]["resultado"], r["pr"]["number"]), ("2/2", 7))
        self.assertEqual(set(r["carga"]), {"inicio", "max", "fim"})
        texto = self.quadro.read_text(encoding="utf-8")
        self.assertEqual(texto.count("| Data |"), 1)
        self.assertIn("| v9.9.9 (", texto)
        self.assertIn("| 2/2 | #7 open | 68 | 468 | 4 | 1 |", texto)
        self.assertIn("Fontes:", texto)
        projeto = Path(r["registro"]).parent / "projeto"
        settings = json.loads(subprocess.run(["git", "-C", str(projeto), "show", "main:.claude/settings.json"],
                                             capture_output=True, text=True, env=sem_manutencao()).stdout)
        escondidos = str(self.escondidos.parent.resolve())
        # o forge instalado sai (só a árvore da tag carrega) e a sessão não lê nem escreve os testes escondidos
        self.assertEqual(settings, {
            "permissions": {"deny": [f"Read(/{escondidos}/**)", f"Edit(/{escondidos}/**)", f"Write(/{escondidos}/**)"]},
            "sandbox": {"filesystem": {"denyRead": [escondidos], "denyWrite": [escondidos]}}})
        self.assertIn("refs/heads/develop", subprocess.run(["git", "ls-remote", str(self.remoto)],
                                                           capture_output=True, text=True,
                                                           env=sem_manutencao()).stdout)

    def test_segunda_rodada_acrescenta_linha_sem_repetir_cabecalho(self):
        self.quadro.parent.mkdir(parents=True)
        self.quadro.write_text("cabeçalho já existe\n", encoding="utf-8")
        self.cenario(pr_na_chamada=0)
        self.assertEqual(self.rodar()[0], 0)
        texto = self.quadro.read_text(encoding="utf-8")
        self.assertTrue(texto.startswith("cabeçalho já existe\n| "))
        self.assertNotIn("| Data |", texto)

    def test_sem_pr_para_nas_3_voltas_e_avalia_o_head(self):
        self.cenario()
        self.assertEqual(self.rodar()[0], 0)
        self.assertEqual(len(self.chamadas()), 1 + v.LIMITES["voltas"])
        r = self.registro()
        self.assertEqual((r["limite"], r["pr"], r["voltas"], r["avaliacao"]["resultado"]), ("voltas", None, 3, "0/2"))
        self.assertIn("| sem PR |", self.quadro.read_text(encoding="utf-8"))

    def test_mais_de_20_agentes_encerra_sem_retomar(self):
        self.cenario(agentes=v.LIMITES["agentes"] + 1)
        self.assertEqual(self.rodar()[0], 0)
        self.assertEqual(len(self.chamadas()), 1)
        self.assertEqual(self.registro()["limite"], "agentes")

    def test_20_agentes_ainda_cabem(self):
        self.cenario(agentes=v.LIMITES["agentes"], pr_na_chamada=0)
        self.assertEqual(self.rodar()[0], 0)
        self.assertEqual(self.registro()["limite"], None)

    def test_tokens_acima_do_limite_encerram(self):
        self.cenario()
        with mock.patch.dict(v.LIMITES, {"tokens": 116}):
            self.assertEqual(self.rodar()[0], 0)
        self.assertEqual((self.registro()["limite"], len(self.chamadas())), ("tokens", 1))

    def test_prazo_vencido_encerra_a_sessao_em_curso(self):
        self.cenario(dorme=60)
        inicio = time.monotonic()
        with mock.patch.dict(v.LIMITES, {"segundos": 1}):
            self.assertEqual(self.rodar()[0], 0)
        self.assertLess(time.monotonic() - inicio, 30)
        self.assertEqual(self.registro()["limite"], "tempo")

    def test_sessao_que_ignora_o_sigterm_morre_pelo_kill(self):
        self.cenario(dorme=20, ignora_term=True)
        inicio = time.monotonic()
        with mock.patch.dict(v.LIMITES, {"segundos": 1}), mock.patch.object(v, "ESPERA_KILL", 0.5):
            self.assertEqual(self.rodar()[0], 0)
        self.assertLess(time.monotonic() - inicio, 12)
        self.assertEqual(self.registro()["limite"], "tempo")

    def test_marca_no_projeto_aparece_na_linha(self):
        self.cenario(marca=MARCA, pr_na_chamada=0)
        self.assertEqual(self.rodar()[0], 0)
        self.assertTrue(self.registro()["marca"].endswith("anotacao.txt"))

    def test_remoto_nao_vazio_recusa_antes_da_sessao(self):
        git("push", "-q", str(self.remoto), "main", cwd=self.forge)
        self.cenario(pr_na_chamada=0)
        rc, _, err = self.rodar()
        self.assertEqual((rc, "não está vazio" in err), (1, True))
        self.assertEqual(self.chamadas(), [])

    def test_trava_de_outra_rodada_recusa(self):
        (self.d / "bench" / "rodadas").mkdir(parents=True)
        (self.d / "bench" / "rodadas" / ".trava").touch()
        self.cenario(pr_na_chamada=0)
        self.assertEqual(self.rodar()[0], 2)
        self.assertEqual(self.chamadas(), [])

    def test_tokens_das_transcricoes_somam_subagentes_sem_repetir(self):
        cwd = self.d / "proj eto"
        # a regra do Claude Code: todo caractere não alfanumérico vira "-" (o nome do tempfile pode ter "_")
        pasta = self.d / "casa" / ".claude" / "projects" / re.sub(r"[^A-Za-z0-9]", "-", str(cwd))
        self.assertIn("proj-eto", pasta.name)
        (pasta / "s1" / "subagents").mkdir(parents=True)
        uso = {"input_tokens": 1, "output_tokens": 2, "cache_creation_input_tokens": 3, "cache_read_input_tokens": 4}
        linha = lambda i: json.dumps({"message": {"id": i, "usage": uso}})  # noqa: E731
        (pasta / "s1.jsonl").write_text("\n".join([linha("a"), linha("a"), "lixo", "[]"]))
        (pasta / "s1" / "subagents" / "agent-1.jsonl").write_text(linha("b"))
        self.assertEqual(v.tokens_das_transcricoes(cwd), {"novos": 12, "processados": 20})
        self.assertIsNone(v.tokens_das_transcricoes(self.d / "outro"))


if __name__ == "__main__":
    unittest.main()
