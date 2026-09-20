import { StrictMode, useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  authenticate,
  createChat,
  deleteChat,
  getCurrentUser,
  getChat,
  listChats,
  logout,
  renameChat,
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
  const [activeChat, setActiveChat] = useState(null);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [theme, setTheme] = useState(() => localStorage.getItem("agent_theme") || "dark");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [menuChatId, setMenuChatId] = useState(null);
  const [editingChat, setEditingChat] = useState(null);
  const [renameValue, setRenameValue] = useState("");
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [profile, setProfile] = useState(null);
  const [pinnedChats, setPinnedChats] = useState(() => JSON.parse(localStorage.getItem("agent_pinned_chats") || "[]"));
  const [attachedDocuments, setAttachedDocuments] = useState([]);
  const responseController = useRef(null);
  const fileInput = useRef(null);

  useEffect(() => {
    localStorage.setItem("agent_theme", theme);
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  function hydrateChat(chat) {
    const saved = JSON.parse(localStorage.getItem(`agent_attachments_${chat.id}`) || "[]");
    return {
      ...chat,
      messages: (chat.messages || []).map((message) => {
        const match = saved.find((item) => item.content === message.content);
        return match ? { ...message, attachments: match.attachments } : message;
      }),
    };
  }

  async function refreshChats() {
    const items = await listChats();
    setChats(sortChats(items));
    if (!activeChat && items.length) setActiveChat(hydrateChat(await getChat(items[0].id)));
  }

  function sortChats(items, pins = pinnedChats) {
    return [...items].sort((first, second) => {
      const firstPinned = pins.includes(first.id) ? 1 : 0;
      const secondPinned = pins.includes(second.id) ? 1 : 0;
      return secondPinned - firstPinned;
    });
  }

  useEffect(() => {
    Promise.all([listChats(), getCurrentUser()]).then(([chatItems, user]) => {
      setChats(sortChats(chatItems));
      setProfile(user);
      if (chatItems.length) getChat(chatItems[0].id).then(hydrateChat).then(setActiveChat);
    }).catch((requestError) => setError(requestError.message)).finally(() => setLoading(false));
  }, []);

  async function newConversation() {
    try {
      const chat = await createChat();
      setChats((items) => sortChats([chat, ...items]));
      setActiveChat(chat);
      setSidebarOpen(false);
    } catch (requestError) { setError(requestError.message); }
  }

  async function selectChat(id) {
    try { setActiveChat(hydrateChat(await getChat(id))); setSidebarOpen(false); } catch (requestError) { setError(requestError.message); }
  }

  async function removeChat(id) {
    try {
      await deleteChat(id);
      const remaining = chats.filter((chat) => chat.id !== id);
      setChats(sortChats(remaining));
      setActiveChat(remaining.length ? await getChat(remaining[0].id) : null);
      localStorage.removeItem(`agent_attachments_${id}`);
      setMenuChatId(null);
    } catch (requestError) { setError(requestError.message); }
  }

  function togglePin(id) {
    const next = pinnedChats.includes(id) ? pinnedChats.filter((chatId) => chatId !== id) : [...pinnedChats, id];
    setPinnedChats(next);
    localStorage.setItem("agent_pinned_chats", JSON.stringify(next));
    setChats((items) => sortChats(items, next));
    setMenuChatId(null);
  }

  async function saveRename(event) {
    event.preventDefault();
    const title = renameValue.trim();
    if (!title || !editingChat) return;
    try {
      const updated = await renameChat(editingChat.id, title);
      setChats((items) => sortChats(items.map((chat) => chat.id === updated.id ? { ...chat, title: updated.title } : chat)));
      setActiveChat((chat) => chat?.id === updated.id ? { ...chat, title: updated.title } : chat);
      setEditingChat(null);
    } catch (requestError) { setError(requestError.message); }
  }

  async function sendMessage(event) {
    event.preventDefault();
    const content = input.trim();
    if (!content || !activeChat || busy) return;
    const isFirstPrompt = !(activeChat.messages || []).some((message) => message.role === "user");
    const generatedTitle = content.replace(/\s+/g, " ").slice(0, 57) + (content.replace(/\s+/g, " ").length > 60 ? "..." : "");
    setInput(""); setBusy(true); setError("");
    const controller = new AbortController();
    responseController.current = controller;
    const userMessage = { id: `local-user-${Date.now()}`, role: "user", content, attachments: attachedDocuments };
    const assistantMessage = { id: `local-assistant-${Date.now()}`, role: "assistant", content: "" };
    setAttachedDocuments([]);
    const savedAttachments = JSON.parse(localStorage.getItem(`agent_attachments_${activeChat.id}`) || "[]");
    localStorage.setItem(`agent_attachments_${activeChat.id}`, JSON.stringify([...savedAttachments, { content, attachments: attachedDocuments }]));
    setActiveChat((chat) => ({ ...chat, title: isFirstPrompt ? generatedTitle : chat.title, messages: [...(chat.messages || []), userMessage, assistantMessage] }));
    if (isFirstPrompt) setChats((items) => sortChats(items.map((chat) => chat.id === activeChat.id ? { ...chat, title: generatedTitle } : chat)));
    try {
      await streamMessage(activeChat.id, content, (token) => {
        setActiveChat((chat) => ({ ...chat, messages: chat.messages.map((message) => message.id === assistantMessage.id ? { ...message, content: message.content + token } : message) }));
      }, (message) => setError(message), controller.signal);
      refreshChats().catch(() => undefined);
    } catch (requestError) {
      if (requestError.name !== "AbortError") setError(requestError.message);
    } finally {
      if (responseController.current === controller) responseController.current = null;
      setBusy(false);
    }
  }

  function stopResponse() {
    responseController.current?.abort();
    responseController.current = null;
    setBusy(false);
  }

  async function handleUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    setError("");
    try {
      if (!activeChat) {
        setError("Create or select a conversation before uploading a document.");
        return;
      }
      const document = await uploadDocument(file, activeChat.id);
      setAttachedDocuments((items) => [document, ...items.filter((item) => item.id !== document.id)]);
    } catch (requestError) { setError(requestError.message); }
    event.target.value = "";
  }

  function handleComposerKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      event.currentTarget.form.requestSubmit();
    }
  }

  function editMessage(message) {
    setInput(message.content);
    setAttachedDocuments(message.attachments || []);
    requestAnimationFrame(() => document.querySelector(".composer textarea")?.focus());
  }

  if (loading) return <div className="loading-screen">Preparing your workspace...</div>;

  return (
    <main className={`app-shell ${sidebarOpen ? "sidebar-is-open" : ""}`}>
      <div className="mobile-backdrop" onClick={() => setSidebarOpen(false)} />
      <aside className="sidebar">
        <div className="sidebar-top"><div className="brand-mark small">PA</div><div><strong>Private AI</strong><span>Your personal workspace</span></div><button className="close-sidebar" onClick={() => setSidebarOpen(false)} aria-label="Close sidebar">×</button></div>
        <button className="new-chat" onClick={newConversation}><span>＋</span> New conversation</button>
        <p className="section-label">Your chats <span>{chats.length}</span></p>
        <div className="chat-list">{chats.length ? chats.map((chat) => <div className={`chat-row ${activeChat?.id === chat.id ? "selected" : ""}`} key={chat.id}><button className="chat-select" onClick={() => selectChat(chat.id)}><span className="chat-icon">{pinnedChats.includes(chat.id) ? "★" : "◇"}</span>{chat.title}</button><div className="chat-actions"><button onClick={(event) => { event.stopPropagation(); setEditingChat(chat); setRenameValue(chat.title); }} aria-label={`Rename ${chat.title}`} title="Rename">✎</button><button onClick={(event) => { event.stopPropagation(); togglePin(chat.id); }} aria-label={pinnedChats.includes(chat.id) ? `Unpin ${chat.title}` : `Pin ${chat.title}`} title={pinnedChats.includes(chat.id) ? "Unpin" : "Pin"}>{pinnedChats.includes(chat.id) ? "★" : "☆"}</button><button className="delete-chat" onClick={(event) => { event.stopPropagation(); removeChat(chat.id); }} aria-label={`Delete ${chat.title}`} title="Delete">×</button></div></div>) : <p className="sidebar-empty">Your conversations will appear here.</p>}</div>
        <div className="sidebar-bottom"><input ref={fileInput} type="file" accept=".pdf,.docx,.pptx,.txt,.csv" onChange={handleUpload} hidden /><button className="sidebar-action" onClick={() => setSettingsOpen(true)}><span>⚙</span> Settings</button><button className="logout-button" onClick={() => { logout(); onLogout(); }}><span>↪</span> Log out</button></div>
      </aside>
      <section className="chat-panel">
        <header className="chat-header"><button className="menu-button" onClick={() => setSidebarOpen(true)} aria-label="Open sidebar">☰</button><div className="conversation-heading"><p className="eyebrow">Conversation</p><h1>{activeChat?.title || "New conversation"}</h1></div><div className="header-actions"><div className="status-dot">Online</div><button className="theme-button" onClick={() => setTheme(theme === "dark" ? "light" : "dark")} aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}><span>{theme === "dark" ? "☼" : "◐"}</span></button></div></header>
        <div className="message-area">{!activeChat && <div className="empty-state"><div className="welcome-mark">✦</div><h2>How can I help you today?</h2><p>Ask a question, explore an idea, or work with your private documents.</p><div className="prompt-grid"><button onClick={() => setInput("Summarize my uploaded documents")}>Summarize a document <span>→</span></button><button onClick={() => setInput("Help me research this topic")}>Research a topic <span>→</span></button></div></div>}{activeChat?.messages?.map((message) => <article className={`message ${message.role}`} key={message.id}><div className="avatar">{message.role === "user" ? "Y" : "✦"}</div><div className="message-body"><div className="message-heading"><span className="message-role">{message.role === "user" ? "You" : "Private AI"}</span>{message.role === "user" && <button className="edit-message" onClick={() => editMessage(message)} title="Edit prompt">✎ Edit</button>}</div>{message.role === "user" && message.attachments?.length > 0 && <div className="message-attachments">{message.attachments.map((document) => <div className="sent-attachment" key={document.id}><span className="attachment-icon">{document.file_type === "pdf" ? "◉" : "▤"}</span><span>{document.filename}</span><span className="sent-attachment-type">{document.file_type.toUpperCase()}</span></div>)}</div>}<p>{message.content || (busy ? "Thinking..." : "")}</p></div></article>)}</div>
        {error && <div className="error-bar">{error}</div>}
        <form className="composer" onSubmit={sendMessage}>{attachedDocuments.length > 0 && <div className="attachment-list">{attachedDocuments.map((document) => <div className="attachment-card" key={document.id}><div className="attachment-icon">{document.file_type === "pdf" ? "◉" : "▤"}</div><div className="attachment-copy"><strong>{document.filename}</strong><span>{document.file_type.toUpperCase()} document</span></div><button type="button" onClick={() => setAttachedDocuments((items) => items.filter((item) => item.id !== document.id))} aria-label={`Remove ${document.filename}`}>×</button></div>)}</div>}<div className="composer-tools"><button type="button" className="attach-button" onClick={() => fileInput.current.click()} aria-label="Upload document">＋</button><textarea value={input} onChange={(event) => setInput(event.target.value)} onKeyDown={handleComposerKeyDown} placeholder={activeChat ? "Message Private AI..." : "Create a conversation to begin"} disabled={!activeChat || busy} rows="1" />{busy ? <button type="button" className="stop-button" onClick={stopResponse} aria-label="Stop response">■</button> : <button className="send-button" disabled={!activeChat || !input.trim()} aria-label="Send message">↑</button>}</div><p className="composer-note">{busy ? "Private AI is responding · Click stop to send another prompt" : "Press Enter to send · Shift + Enter for a new line"}</p></form>
      </section>
      {editingChat && <div className="modal-backdrop"><form className="modal-card" onSubmit={saveRename}><h2>Rename conversation</h2><input value={renameValue} onChange={(event) => setRenameValue(event.target.value)} autoFocus maxLength="200" /><div className="modal-actions"><button type="button" className="secondary-button" onClick={() => setEditingChat(null)}>Cancel</button><button className="primary-button">Save</button></div></form></div>}
      {settingsOpen && <div className="modal-backdrop" onClick={() => setSettingsOpen(false)}><section className="modal-card settings-card" onClick={(event) => event.stopPropagation()}><div className="settings-header"><div><p className="eyebrow">Workspace</p><h2>Settings</h2></div><button className="modal-close" onClick={() => setSettingsOpen(false)} aria-label="Close settings">×</button></div><div className="profile-row"><div className="profile-avatar">{profile?.email?.[0]?.toUpperCase() || "U"}</div><div><strong>{profile?.email || "Your profile"}</strong><span>Signed in account</span></div></div><div className="settings-row"><div><strong>Appearance</strong><span>{theme === "dark" ? "Dark theme" : "Light theme"}</span></div><button className="theme-switch" onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>{theme === "dark" ? "☼ Light" : "◐ Dark"}</button></div></section></div>}
    </main>
  );
}

function App() {
  const [authenticated, setAuthenticated] = useState(Boolean(localStorage.getItem("agent_token")));
  return authenticated ? <Dashboard onLogout={() => setAuthenticated(false)} /> : <AuthScreen onAuthenticated={() => setAuthenticated(true)} />;
}

createRoot(document.getElementById("root")).render(<StrictMode><App /></StrictMode>);
