import os
import sys
import subprocess

def build():
    print("Iniciando build do executável...")
    
    command = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--icon=NONE",
        "--name=AssistenteOrganizacao",
        "--hidden-import=pystray",
        "--hidden-import=PIL",
        "--hidden-import=plyer",
        "--hidden-import=plyer.platforms.win.notification",
        "--hidden-import=scikit-learn",
        "--hidden-import=customtkinter",
        "--collect-all=organizador",
        "main.py"
    ]
    
    try:
        subprocess.run(command, check=True)
        print("\nBuild concluído com sucesso!")
        print("O executável está na pasta 'dist/AssistenteOrganizacao'")
    except subprocess.CalledProcessError as e:
        print(f"\nErro durante o build: {e}")

if __name__ == "__main__":
    build()
