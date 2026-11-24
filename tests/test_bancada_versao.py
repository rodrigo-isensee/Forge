"""Bench de versões com agentes (BENCH-VERSAO, E175.3): o roteiro tests/bancada/versao.py com `claude` e `gh` falsos,
Forge e remoto locais e testes escondidos de mentira; nunca chama o modelo nem a rede."""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("bancada_versao", RAIZ / "tests" / "bancada" / "versao.py")
v = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v)

MARCA = "zqmarcadeteste0000"
LIMPO = {"PATH": "/usr/bin:/bin"}

# claude falso: grava o argv, emite o stream-json do cenário e, conforme o cenário, abre o "PR" (commit e pr.json)
CLAUDE = r'''#!{py}
import json, os, subprocess, sys, time
from pathlib import Path
base = Path(os.environ["FALSO_DIR"])
cen = json.loads((base / "cenario.json").read_text())
chamadas = base / "chamadas.jsonl"
n = sum(1 for _ in open(chamadas)) if chamadas.exists() else 0
with open(chamadas, "a") as f:
    f.write(json.dumps(sys.argv[1:]) + "\n")
plugin = sys.argv[sys.argv.index("--plugin-dir") + 1]
def emite(ev):
    print(json.dumps(ev), flush=True)
emite({{"type": "system", "subtype": "init", "session_id": "s1", "plugins": [{{"name": "forge", "path": plugin}}]}})
uso = {{"input_tokens": 10, "output_tokens": 5, "cache_creation_input_tokens": 2, "cache_read_input_tokens": 100}}
for i in range(cen.get("agentes", 1)):
    emite({{"type": "assistant", "session_id": "s1", "message": {{"id": f"m{{n}}-{{i}}", "usage": uso,
          "content": [{{"type": "tool_use", "id": f"t{{n}}-{{i}}", "name": "Task", "input": {{}}}}]}}}})
    emite({{"type": "assistant", "session_id": "s1", "message": {{"id": f"m{{n}}-{{i}}", "usage": uso, "content": []}}}})
if cen.get("marca"):
    Path("anotacao.txt").write_text("copiei " + cen["marca"])
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
GH = r'''#!{py}
import os, sys
from pathlib import Path
pr = Path(os.environ["FALSO_DIR"]) / "pr.json"
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
                   capture_output=True)


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
        esc = d / "bench" / "escondidos" / v.VERSAO_ESCONDIDOS
        esc.mkdir(parents=True)
        (esc / "test_escondido.py").write_text(ESCONDIDO.format(marca=MARCA), encoding="utf-8")
        (esc / "marca.txt").write_text(MARCA + "\n", encoding="utf-8")
        self.forge = d / "forge"
        (self.forge / "bin").mkdir(parents=True)
        (self.forge / "bin" / "forge-init").write_text(FORGE_INIT, encoding="utf-8")
        git("init", "-q", "-b", "main", str(self.forge))
        git("add", "-A", cwd=self.forge)
        git("commit", "-q", "-m", "x", cwd=self.forge)
        git("tag", "v9.9.9", cwd=self.forge)
        self.remoto = d / "remoto.git"
        git("init", "-q", "--bare", str(self.remoto))
        config = d / "config.json"
        sha_marca = hashlib.sha256(MARCA.encode()).hexdigest()
        config.write_text(json.dumps({"termos_proibidos_hash": [{"tipo": "trecho", "n": len(MARCA), "sha256": sha_marca}]}))
        self.quadro = d / "quadro" / "bench-versao.md"
        congelados = {n: hashlib.sha256((esc / n).read_bytes()).hexdigest() for n in ("test_escondido.py", "marca.txt")}
        for alvo, valor in (("CONGELADOS", congelados), ("MARCA_SHA256", sha_marca), ("CONFIG", config), ("INTERVALO", 0.05)):
            p = mock.patch.object(v, alvo, valor)
            p.start()
            self.addCleanup(p.stop)
        amb = mock.patch.dict(os.environ, {"PATH": f"{self.bin}:{os.environ.get('PATH', '/usr/bin:/bin')}",
                                           "HOME": str(d / "casa"), "FALSO_DIR": str(self.falso)})
        amb.start()
        self.addCleanup(amb.stop)

    def cenario(self, **c):
        (self.falso / "cenario.json").write_text(json.dumps(c), encoding="utf-8")

    def chamadas(self):
        arq = self.falso / "chamadas.jsonl"
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

    def test_recusa_com_ci_github_actions_ou_chave_da_api(self):
        self.cenario(pr_na_chamada=0)
        for nome in v.AMBIENTE_PROIBIDO:
            with self.subTest(nome=nome):
                rc, _, err = self.rodar(env={**LIMPO, nome: ""})
                self.assertEqual(rc, 2)
                self.assertIn(nome, err)
                rc, _, _ = self.rodar(env={**LIMPO, nome: "1"}, executar=False)
                self.assertEqual(rc, 2)
        self.assertEqual(self.chamadas(), [])

    def test_teste_escondido_alterado_ou_ausente_recusa(self):
        arq = self.d / "bench" / "escondidos" / v.VERSAO_ESCONDIDOS / "test_escondido.py"
        arq.write_text(arq.read_text() + "\n", encoding="utf-8")
        rc, _, err = self.rodar(executar=False)
        self.assertEqual((rc, "alterado" in err), (1, True))
        arq.unlink()
        rc, _, err = self.rodar(executar=False)
        self.assertEqual((rc, "ausente" in err), (1, True))

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
                                             capture_output=True, text=True).stdout)
        self.assertEqual(settings, {"permissions": {}})  # o forge instalado sai; só a árvore da tag carrega
        self.assertIn("refs/heads/develop", subprocess.run(["git", "ls-remote", str(self.remoto)],
                                                           capture_output=True, text=True).stdout)

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
        pasta = self.d / "casa" / ".claude" / "projects" / ("-" + str(cwd)[1:].replace("/", "-").replace(" ", "-"))
        (pasta / "s1" / "subagents").mkdir(parents=True)
        uso = {"input_tokens": 1, "output_tokens": 2, "cache_creation_input_tokens": 3, "cache_read_input_tokens": 4}
        linha = lambda i: json.dumps({"message": {"id": i, "usage": uso}})  # noqa: E731
        (pasta / "s1.jsonl").write_text("\n".join([linha("a"), linha("a"), "lixo", "[]"]))
        (pasta / "s1" / "subagents" / "agent-1.jsonl").write_text(linha("b"))
        self.assertEqual(v.tokens_das_transcricoes(cwd), {"novos": 12, "processados": 20})
        self.assertIsNone(v.tokens_das_transcricoes(self.d / "outro"))


if __name__ == "__main__":
    unittest.main()
