import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    import scripts.mirror
    import scripts.filter_ru_sni_local
    assert True