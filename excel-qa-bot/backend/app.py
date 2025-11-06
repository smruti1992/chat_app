# backend/app.py
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

matcher: Optional[HybridTFIDFMatcher] = None
store = {"df": None}

class ChatRequest(BaseModel):
message: str
topk: int | None = None

@app.on_event("startup")
def startup_event():
global matcher
df = load_excel(EXCEL_PATH, SHEET_ARG, PROBLEM_COL, SOLUTION_COL)
store["df"] = df


matcher = HybridTFIDFMatcher()
matcher.fit(df[PROBLEM_COL].tolist())

@app.get("/healthz")
def healthz():
path_ok = Path(EXCEL_PATH).exists()
count = int(store["df"].shape[0]) if store.get("df") is not None else 0
return {"status": "ok", "excel_found": path_ok, "rows": count}


@app.post("/chat")
def chat(req: ChatRequest):
assert matcher is not None, "Matcher not initialized"
df = store["df"]


topk = req.topk or TOPK_DEFAULT
results = matcher.top_k(req.message, k=topk)


matches = []
for idx, score in results:
row = df.iloc[idx]
matches.append(
{
"index": int(idx),
"score": round(float(score), 6),
"problem": row[PROBLEM_COL],
"solution": row[SOLUTION_COL],
}
)

# Best match in a handy place
best = matches[0] if matches else None
return {"best": best, "matches": matches}

# For `python app.py` convenience
if __name__ == "__main__":
import uvicorn

uvicorn.run("app:app", host="172.16.16.100", port=8000, reload=True)