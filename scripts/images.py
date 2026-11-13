"""Alias da integração ComfyUI por workflow API; sem instalação ou modelo implícito.
Veja: python scripts/comfy.py --help.
"""
from comfy import main

if __name__ == "__main__":
    raise SystemExit(main())
