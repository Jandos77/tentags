import tentags
from pathlib import Path
import re
from demo_paths import demo_output_path

try:
    import tomllib
except ModuleNotFoundError:
    tomllib = None


def load_pyproject():
    pyproject_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    if tomllib is not None:
        with pyproject_path.open("rb") as f:
            return tomllib.load(f)

    pyproject = {"project": {}}
    section = None
    for raw_line in pyproject_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("[") and line.endswith("]"):
            section = line.strip("[]")
            continue
        if "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if section == "project":
                if value.startswith("["):
                    pyproject["project"][key] = [
                        item.strip().strip('"')
                        for item in value.strip("[]").split(",")
                        if item.strip()
                    ]
                else:
                    pyproject["project"][key] = value.strip('"')
    return pyproject


def test_metadata_features():
    print("=== Testing Metadata and Helper API ===")
    pyproject = load_pyproject()
    
    # 1. Check meta constants
    print(f"Version: {tentags.__version__}")
    print(f"Author: {tentags.__author__}")
    print(f"License: {tentags.__license__}")
    print(f"Homepage: {tentags.__homepage__}")
    print(f"Version Info: {tentags.version_info}")
    
    print(f"Copyright: {tentags.__copyright__}")
    print(f"URL: {tentags.__url__}")
    
    project_version = pyproject["project"]["version"]
    assert re.fullmatch(r"\d+\.\d+\.\d+", project_version)
    assert tentags.__version__ == project_version
    assert tentags.version_info == tuple(int(part) for part in project_version.split("."))
    assert tentags.__license__ == pyproject["project"]["license"]
    assert tentags.__copyright__ == "Copyright (c) 2026 Zhandos Mambetali"
    assert tentags.__url__ == "https://tentags.org"
    assert "get_promt" in tentags.__all__
    
    # 2. Check info()
    print("\n--- Running tentags.info() ---")
    tentags.info()
    
    # 3. Check features()
    print("\n--- Running tentags.features() ---")
    feats = tentags.features()
    print(feats)
    assert isinstance(feats, dict)
    assert "html" in feats
    assert "pdf" in feats
    assert "xlsx" in feats
    
    # 4. Check validate()
    print("\n--- Running tentags.validate() ---")
    good_formula = '3,3,1,"black","solid",0, data(A,B,C;D,E,F;G,H,I)'
    bad_formula = '3,3,1,"black","solid",0, data(<b>A,B,C;D,E,F;G,H,I)'  # missing </b>
    
    good_res = tentags.validate(good_formula)
    bad_res = tentags.validate(bad_formula)
    
    print(f"Good formula validation: {good_res}")
    print(f"Bad formula validation: {bad_res}")
    
    assert good_res["status"] == "ok"
    assert bad_res["status"] == "error"
    assert "Missing closing tag </b>" in bad_res["message"]
    
    # 5. Check demo()
    print("\n--- Running tentags.demo() ---")
    demo_prefix = str(demo_output_path("test_demo"))
    tentags.demo("dashboard", filepath_prefix=demo_prefix)
    tentags.demo("invoice", filepath_prefix=demo_prefix)
    tentags.demo("table", filepath_prefix=demo_prefix)
    
    print("\nAll metadata & diagnostic helper tests passed successfully!")


def test_get_promt_returns_bundled_llm_bootstrap_prompt(capsys):
    prompt = tentags.get_promt()

    assert isinstance(prompt, str)
    assert "TenTags LLM Bootstrap Prompt" in prompt
    assert "TenTags is currently 2.1.0" in prompt
    assert prompt == tentags.get_prompt()

    printed_prompt = tentags.get_promt(print_output=True)
    captured = capsys.readouterr()

    assert printed_prompt == prompt
    assert captured.out == prompt + "\n"

if __name__ == "__main__":
    test_metadata_features()
