"""Одна команда для Windows, macOS і Linux: оточення, тести, звіт Allure у браузері.

    python run_tests.py                                      усі тести, 4 потоки
    python run_tests.py -m ui                                лише UI
    python run_tests.py tests/ui/test_checkout.py --headed   один файл у вікні браузера
"""
import shutil
import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"
PYTHON = VENV / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
ALLURE = "allure@3.22.1"  # Allure 3 працює на Node.js, Java не потрібна


def main():
    if not PYTHON.exists():
        venv.create(VENV, with_pip=True)
    subprocess.run([PYTHON, "-m", "pip", "install", "--quiet", "-r", ROOT / "requirements.txt"], check=True)

    tests = subprocess.run([PYTHON, "-m", "pytest", *(sys.argv[1:] or ["-n", "4"])], cwd=ROOT)

    npx = shutil.which("npx")
    if npx is None:
        print("Для звіту потрібен Node.js (LTS): https://nodejs.org. Результати вже лежать в allure-results/.")
        return tests.returncode
    try:
        subprocess.run([npx, "--yes", ALLURE, "open", "allure-results"], cwd=ROOT)
    except KeyboardInterrupt:
        pass  # Ctrl+C зупиняє сервер звіту
    return tests.returncode


if __name__ == "__main__":
    sys.exit(main())
