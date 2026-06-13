from fastapi import FastAPI

app = FastAPI(title="Acme Logistics — Inbound Carrier Sales")


@app.get("/health")
def health():
    return {"status": "ok"}
