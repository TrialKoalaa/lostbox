"""
Entrypoint LostBox — Sains Data Edition
Menjalankan main.py
"""
import sys
import os

if __name__ == "__main__":
    import main
    if len(sys.argv) > 1 and sys.argv[1].lower() in ("--cli", "-c", "--demo"):
        main.run_cli_demo()
    else:
        try:
            main.run_gui()
        except Exception as e:
            print(f"[LostBox] Catatan GUI: {e}")
            print("[LostBox] Menjalankan fallback demonstrasi CLI...")
            main.run_cli_demo()
