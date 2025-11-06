# backend/qa_matcher.py
from sklearn.metrics.pairwise import cosine_similarity




class HybridTFIDFMatcher:
"""
Robust matcher that blends word- and char-level TF-IDF to handle
phrasing differences and small typos.
"""


def __init__(self):
self.word_vect = TfidfVectorizer(
lowercase=True,
strip_accents="unicode",
stop_words="english",
ngram_range=(1, 2),
min_df=1,
)
self.char_vect = TfidfVectorizer(
analyzer="char_wb",
lowercase=True,
strip_accents="unicode",
ngram_range=(3, 5),
min_df=1,
)
self.word_matrix = None
self.char_matrix = None
self.problems: List[str] = []


def fit(self, problems: List[str]):
self.problems = problems
self.word_matrix = self.word_vect.fit_transform(problems)
self.char_matrix = self.char_vect.fit_transform(problems)


def _similarity(self, query: str) -> np.ndarray:
qw = self.word_vect.transform([query])
qc = self.char_vect.transform([query])
sim_w = cosine_similarity(qw, self.word_matrix)[0]
sim_c = cosine_similarity(qc, self.char_matrix)[0]
return np.maximum(sim_w, sim_c)


def top_k(self, query: str, k: int = 1) -> List[Tuple[int, float]]:
sims = self._similarity(query)
if k <= 0:
k = 1
k = min(k, len(sims))
top_idx = np.argpartition(-sims, k - 1)[:k]
top_sorted = top_idx[np.argsort(-sims[top_idx])]
return [(int(i), float(sims[i])) for i in top_sorted]




def load_excel(
excel_path: str,
sheet_name: str | int = 0,
problem_col: str = "Problem",
solution_col: str = "Solution",
) -> pd.DataFrame:
df = pd.read_excel(excel_path, sheet_name=sheet_name)
df = df.rename(columns={c: str(c).strip() for c in df.columns})
if problem_col not in df.columns or solution_col not in df.columns:
raise ValueError(
f"Expected columns '{problem_col}' and '{solution_col}'. Found: {list(df.columns)}"
)
df = df[[problem_col, solution_col]].copy()
df[problem_col] = df[problem_col].astype(str).fillna("")
df[solution_col] = df[solution_col].astype(str).fillna("")
df = df[df[problem_col].str.strip() != ""].reset_index(drop=True)
return df