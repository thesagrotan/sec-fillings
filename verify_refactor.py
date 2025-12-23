import sys
import os

# Add the current directory to sys.path so we can import backend modules
sys.path.append(os.getcwd())

try:
    print("Testing imports...")
    from backend import config
    print(f"Config loaded. Excluded industries: {len(config.EXCLUDED_INDUSTRIES)}")
    
    from backend import main
    print("Main module loaded.")
    
    from backend import ingestion
    print("Ingestion module loaded.")
    
    print("ALL TESTS PASSED")
except Exception as e:
    print(f"TEST FAILED: {e}")
    sys.exit(1)
