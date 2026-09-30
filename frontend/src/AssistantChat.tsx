import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { sendChat } from './api'
import type { ChatMessage } from './api'

export default function AssistantChat() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const bottom = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  useEffect(() => { bottom.current?.scrollIntoView({ block: 'nearest' }) }, [messages, busy, open])
  useEffect(() => { if (open) inputRef.current?.focus() }, [open])

  async function submit(event: FormEvent) {
    event.preventDefault()
    const question = input.trim()
    if (!question || busy) return
    setBusy(true)
    setError('')
    const next: ChatMessage[] = [...messages, { role: 'user', content: question }]
    setMessages(next)
    setInput('')
    try {
      const reply = await sendChat(next)
      setMessages([...next, { role: 'assistant', content: reply }])
    } catch (failure) {
      setMessages(messages)
      setInput(question)
      setError(failure instanceof Error ? failure.message : 'Unable to answer. Please try again.')
    } finally { setBusy(false) }
  }

  return <div className="assistant-widget">
    {open && <section className="assistant-panel" aria-label="GeoXAI assistant">
      <div className="assistant-header"><div><strong>GeoXAI assistant</strong><small>Powered by Gemini</small></div><button type="button" onClick={() => setOpen(false)} aria-label="Close assistant">×</button></div>
      <div className="assistant-messages" role="log" aria-live="polite" aria-busy={busy}>
        {!messages.length && <div className="assistant-welcome"><h3>How can I help?</h3><p>Ask about borewell inputs, risk scores, maintenance, or uploading a dataset.</p><p className="assistant-note">Messages are sent to Gemini. The assistant can discuss results you share here.</p>{['What do the risk categories mean?', 'How do I prepare a CSV?', 'What does SHAP explain?'].map((question) => <button type="button" key={question} onClick={() => { setInput(question); inputRef.current?.focus() }}>{question}</button>)}</div>}
        {messages.map((message, index) => <div className={`assistant-message ${message.role}`} key={index}><small>{message.role === 'user' ? 'You' : 'Assistant'}</small><p>{message.content}</p></div>)}
        {busy && <p className="assistant-note">Thinking…</p>}
        <div ref={bottom} />
      </div>
      {error && <p className="assistant-error" role="alert">{error}</p>}
      <form className="assistant-form" onSubmit={submit}><label className="assistant-input"><span className="sr-only">Message the assistant</span><input ref={inputRef} value={input} onChange={(event) => setInput(event.target.value)} maxLength={4000} placeholder="Ask a question…" disabled={busy} /></label><button type="submit" disabled={busy || !input.trim()}>Send</button></form>
      <div className="assistant-footer"><span>Check AI guidance against field observations.</span><button type="button" disabled={busy} onClick={() => { setMessages([]); setError(''); setInput('') }}>Clear chat</button></div>
    </section>}
    <button className="assistant-launcher" type="button" aria-expanded={open} onClick={() => setOpen(!open)}>{open ? 'Close assistant' : '✦ AI assistant'}</button>
  </div>
}
