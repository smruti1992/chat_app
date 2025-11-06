import { useState, useRef, useEffect } from "react";

const API_BASE = import.meta?.env?.VITE_API_BASE || "http://localhost:8000";

function Message({ role, text }) {
  const isUser = role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[80%] rounded-2xl p-3 shadow ${
          isUser ? "bg-blue-600 text-white" : "bg-gray-100"
        }`}
      >
        <div className="whitespace-pre-wrap break-words">{text}</div>
      </div>
    </div>
  );
}

export default function App() {
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Hi! Ask me a question about your knowledge base." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scroller = useRef(null);

  useEffect(() => {
    if (scroller.current) {
      scroller.current.scrollTo({
        top: scroller.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [messages, loading]);

  const ask = async () => {
    const q = input.trim();
    if (!q || loading) return;
    setMessages((m) => [...m, { role: "user", text: q }]);
    setInput("");
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: q, topk: 3 }),
      });
      const data = await res.json();
      if (data?.best) {
        const top = data.best;
        const reply = `Matched Problem (score ${top.score}):\n${top.problem}\n\nSolution:\n${top.solution}`;
        setMessages((m) => [...m, { role: "assistant", text: reply }]);
      } else {
        setMessages((m) => [...m, { role: "assistant", text: "No good match found." }]);
      }
    } catch (e) {
      setMessages((m) => [...m, { role: "assistant", text: `Error: ${e}` }]);
    } finally {
      setLoading(false);
    }
  };

  const onKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      ask();
    }
  };

  return (
    <div className="min-h-screen w-full bg-gradient-to-b from-white to-gray-50 flex flex-col items-center p-4">
      <div className="w-full max-w-3xl flex flex-col gap-3">
        <header className="flex items-center justify-between p-3">
          <h1 className="text-2xl font-semibold">Excel Q&amp;A Chat</h1>
          <a className="text-sm underline" href={`${API_BASE}/healthz`} target="_blank" rel="noreferrer">
            health
          </a>
        </header>

        <div
          ref={scroller}
          className="border rounded-2xl bg-white shadow-inner p-4 h-[60vh] overflow-auto flex flex-col gap-3"
        >
          {messages.map((m, i) => (
            <Message key={i} role={m.role} text={m.text} />
          ))}
          {loading && <div className="text-sm text-gray-500">Thinking…</div>}
        </div>

        <div className="flex gap-2 items-end">
          <textarea
            className="flex-1 border rounded-2xl p-3 shadow-sm focus:outline-none focus:ring w-full"
            rows={2}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKey}
            placeholder="Type your question and press Enter…"
          />
          <button
            onClick={ask}
            disabled={loading}
            className="px-4 py-2 rounded-2xl bg-blue-600 text-white shadow disabled:opacity-40"
          >
            Send
          </button>
        </div>

        <footer className="text-xs text-gray-500 p-2">
          Answers are matched via TF-IDF similarity on your Excel's Problem column.
        </footer>
      </div>
    </div>
  );
}
