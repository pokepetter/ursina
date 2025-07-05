import subprocess
import glob
import os
import sys

def main():
    test_files = sorted(glob.glob("*.py"))
    this_script = os.path.basename(__file__)
    for file in test_files:
        if file == this_script:
            continue
        print(f"\n=== Running {file} ===")
        try:
            result = subprocess.run(
                [sys.executable, file],
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"\n[ERROR] {file} exited with code {e.returncode}")
            continue
        except KeyboardInterrupt:
            print("\n[INTERRUPTED] Stopping.")
            break

if __name__ == "__main__":
    main()