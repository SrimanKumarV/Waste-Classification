import os
import sys
import uvicorn

if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")

    print("=" * 70)
    print(" [SMART WASTE] SEGREGATION ANALYTICS & AUDITING SYSTEM")
    print("=" * 70)
    print(f" * Web Dashboard:   http://{host}:{port}")
    print(f" * Mobile Client:   http://{host}:{port}/mobile")
    print(f" * Interactive API: http://{host}:{port}/docs")
    print("=" * 70)

    uvicorn.run("smart_waste.backend.app:app", host=host, port=port, reload=False)
