import { StrictMode, useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  authenticate,
  createChat,
  deleteChat,
  getChat,
  listChats,
  listDocuments,
  logout,
  streamMessage,
  uploadDocument,
} from "./services/api";
import "./styles.css";

function AuthScreen({ onAuthenticated }) {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event) {
    event.preventDefault();
    setError("");
    setBusy(true);
    try {
      const result = await authenticate(mode, email, password);
      if (mode === "register") {
        setMode("login");
        setError("Account created. Sign in to continue.");
      } else {
        onAuthenticated(result);
      }
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="auth-shell">
      <section className="auth-panel">
        <div className="brand-mark">PA</div>
        <p className="eyebrow">Production AI workspace</p>
        <h1>Think with your documents.</h1>
        <p className="muted">One assistant for private knowledge, current research, and clear answers.</p>
        <form onSubmit={submit} className="auth-form">
          <label>Email<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required /></label>
          <label>Password<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} minLength="8" required /></label>
          {error && <p className="form-message">{error}</p>}
          <button className="primary-button" disabled={busy}>{busy ? "Working..." : mode === "login" ? "Sign in" : "Create account"}</button>
        </form>
        <button className="text-button" onClick={() => { setMode(mode === "login" ? "register" : "login"); setError(""); }}>
          {mode === "login" ? "Create a new account" : "I already have an account"}
        </button>
      </section>
      <aside className="auth-aside"><span>01</span><h2>Private by default.</h2><p>Your conversations and uploaded documents stay scoped to your account.</p></aside>
    </main>
  );
}

function Dashboard({ onLogout }) {
  const [chats, setChats] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [activeChat, setActiveChat] = useState(null);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const fileInput = useRef(null);

  async function refreshChats() {
    const items = await listChats();
    setChats(items);
    if (!activeChat && items.length) setActiveChat(await getChat(items[0].id));
  }

  useEffect(() => {
    Promise.all([listChats(), listDocuments()]).then(([chatItems, documentItems]) => {
      setChats(chatItems);
      setDocuments(documentItems);
      if (chatItems.length) getChat(chatItems[0].id).then(setActiveChat);
    }).catch((requestError) => setError(requestError.message)).finally(() => setLoading(false));
  }, []);

  async function newConversation() {
    try {
      const chat = await createChat();
      setChats((items) => [chat, ...items]);
      setActiveChat(chat);
    } catch (requestError) { setError(requestError.message); }
  }

  async function selectChat(id) {
    try { setActiveChat(await getChat(id)); } catch (requestError) { setError(requestError.message); }
  }

  async function removeChat(id) {
    try {
      await deleteChat(id);
      const remaining = chats.filter((chat) => chat.id !== id);
      setChats(remaining);
      setActiveChat(remaining.length ? await getChat(remaining[0].id) : null);
    } catch (requestError) { setError(requestError.message); }
  }

  async function sendMessage(event) {
    event.preventDefault();
    const content = input.trim();
    if (!content || !activeChat || busy) return;
    setInput(""); setBusy(true); setError("");
    const userMessage = { id: `local-user-${Date.now()}`, role: "user", content };
    const assistantMessage = { id: `local-assistant-${Date.now()}`, role: "assistant", content: "" };
    setActiveChat((chat) => ({ ...chat, messages: [...(chat.messages || []), userMessage, assistantMessage] }));
    try {
      await streamMessage(activeChat.id, content, (token) => {
        setActiveChat((chat) => ({ ...chat, messages: chat.messages.map((message) => message.id === assistantMessage.id ? { ...message, content: message.content + token } : message) }));
      }, (message) => setError(message));
      await refreshChats();
    } catch (requestError) { setError(requestError.message); }
    finally { setBusy(false); }
  }

  async function handleUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    setError("");
    try {
      const document = await uploadDocument(file);
      setDocuments((items) => [document, ...items]);
    } catch (requestError) { setError(requestError.message); }
    event.target.value = "";
  }

  if (loading) return <div className="loading-screen">Preparing your workspace...</div>;

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-top"><div className="brand-mark small">PA</div><div><strong>Private AI</strong><span>Workspace</span></div></div>
        <button className="new-chat" onClick={newConversation}>+ New conversation</button>
        <p className="section-label">Conversations</p>
        <div className="chat-list">{chats.map((chat) => <div className={`chat-row ${activeChat?.id === chat.id ? "selected" : ""}`} key={chat.id}><button onClick={() => selectChat(chat.id)}>{chat.title}</button><button className="delete-button" onClick={() => removeChat(chat.id)} aria-label="Delete conversation">x</button></div>)}</div>
        <div className="sidebar-bottom"><p className="section-label">Documents <span>{documents.length}</span></p><div className="document-list">{documents.map((document) => <div className="document-item" key={document.id}>{document.filename}</div>)}</div><button className="upload-button" onClick={() => fileInput.current.click()}>Upload document</button><input ref={fileInput} type="file" accept=".pdf,.docx,.txt,.csv" onChange={handleUpload} hidden /><button className="logout-button" onClick={() => { logout(); onLogout(); }}>Log out</button></div>
      </aside>
      <section className="chat-panel">
        <header className="chat-header"><div><p className="eyebrow">Conversation</p><h1>{activeChat?.title || "Start a new conversation"}</h1></div><div className="status-dot">Assistant online</div></header>
        <div className="message-area">{!activeChat && <div className="empty-state"><span className="empty-number">00</span><h2>What are you working on?</h2><p>Create a conversation, upload a document, or ask a question.</p></div>}{activeChat?.messages?.map((message) => <article className={`message ${message.role}`} key={message.id}><span className="message-role">{message.role === "user" ? "You" : "Assistant"}</span><p>{message.content || (busy ? "Thinking..." : "")}</p></article>)}</div>
        {error && <div className="error-bar">{error}</div>}
        <form className="composer" onSubmit={sendMessage}><textarea value={input} onChange={(event) => setInput(event.target.value)} placeholder={activeChat ? "Ask about your documents or anything else..." : "Create a conversation to begin"} disabled={!activeChat || busy} rows="1" /><button className="send-button" disabled={!activeChat || busy || !input.trim()} aria-label="Send message">Send</button></form>
      </section>
    </main>
  );
}

function App() {
  const [authenticated, setAuthenticated] = useState(Boolean(localStorage.getItem("agent_token")));
  return authenticated ? <Dashboard onLogout={() => setAuthenticated(false)} /> : <AuthScreen onAuthenticated={() => setAuthenticated(true)} />;
}

createRoot(document.getElementById("root")).render(<StrictMode><App /></StrictMode>);
