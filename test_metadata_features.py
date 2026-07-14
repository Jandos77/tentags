import tentags

def test_metadata_features():
    print("=== Testing Metadata and Helper API ===")
    
    # 1. Check meta constants
    print(f"Version: {tentags.__version__}")
    print(f"Author: {tentags.__author__}")
    print(f"License: {tentags.__license__}")
    print(f"Homepage: {tentags.__homepage__}")
    print(f"Version Info: {tentags.version_info}")
    
    assert tentags.__version__ == "1.1.3"
    assert tentags.version_info == (1, 1, 3)
    
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
    tentags.demo("dashboard", filepath_prefix="test_demo")
    tentags.demo("invoice", filepath_prefix="test_demo")
    tentags.demo("table", filepath_prefix="test_demo")
    
    print("\nAll metadata & diagnostic helper tests passed successfully!")

if __name__ == "__main__":
    test_metadata_features()
