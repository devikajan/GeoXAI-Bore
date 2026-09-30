import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { sendChat } from './api'
import type { AssistantLanguage, ChatMessage, PredictionResult } from './api'
import assistantIcon from './assets/ai-assistant.svg'

type Recognition = {
  lang: string
  interimResults: boolean
  start: () => void
  stop: () => void
  onresult: ((event: { results: { 0: { 0: { transcript: string } } } }) => void) | null
  onerror: (() => void) | null
  onend: (() => void) | null
}
type RecognitionConstructor = new () => Recognition

const languageOptions: { code: AssistantLanguage; label: string; voice: string }[] = [
  { code: 'auto', label: 'Auto · Same as message', voice: navigator.language || 'en-IN' },
  { code: 'en', label: 'English', voice: 'en-IN' },
  { code: 'te', label: 'తెలుగు · Telugu', voice: 'te-IN' },
  { code: 'hi', label: 'हिन्दी · Hindi', voice: 'hi-IN' },
  { code: 'ta', label: 'தமிழ் · Tamil', voice: 'ta-IN' },
  { code: 'kn', label: 'ಕನ್ನಡ · Kannada', voice: 'kn-IN' },
  { code: 'ml', label: 'മലയാളം · Malayalam', voice: 'ml-IN' },
  { code: 'mr', label: 'मराठी · Marathi', voice: 'mr-IN' },
  { code: 'bn', label: 'বাংলা · Bengali', voice: 'bn-IN' },
  { code: 'gu', label: 'ગુજરાતી · Gujarati', voice: 'gu-IN' },
  { code: 'pa', label: 'ਪੰਜਾਬੀ · Punjabi', voice: 'pa-IN' },
  { code: 'ur', label: 'اردو · Urdu', voice: 'ur-IN' },
  { code: 'or', label: 'ଓଡ଼ିଆ · Odia', voice: 'or-IN' },
]

const copy = {
  en: {
    title: 'GeoXAI help assistant', subtitle: 'Ask by typing or speaking', hello: 'How can I help with your borewell?',
    intro: 'Use simple words. I can explain risk, pump care, water levels, and this app.', privacy: 'Your message is sent to Gemini for an answer.',
    prompts: ['Explain my risk result', 'What pump warning signs should I check?', 'How do I fill the borewell form?'],
    placeholder: 'Type or use the microphone…', send: 'Send', you: 'You', assistant: 'Assistant', thinking: 'Preparing a simple answer…',
    fieldNote: 'For electrical or high-risk problems, call a qualified technician.', clear: 'Clear', open: 'AI help', close: 'Close assistant',
    voiceUnavailable: 'Voice input is not available in this browser. You can type your question.', listening: 'Listening… speak now', read: 'Read answer aloud',
  },
  te: {
    title: 'GeoXAI సహాయకుడు', subtitle: 'టైప్ చేయండి లేదా మాట్లాడండి', hello: 'మీ బోరు గురించి ఎలా సహాయం చేయగలను?',
    intro: 'సులభమైన మాటల్లో అడగండి. ప్రమాదం, పంపు సంరక్షణ, నీటి మట్టం మరియు ఈ యాప్ గురించి వివరిస్తాను.', privacy: 'సమాధానం కోసం మీ సందేశం Geminiకి పంపబడుతుంది.',
    prompts: ['నా ప్రమాద ఫలితాన్ని వివరించండి', 'పంపులో ఏ హెచ్చరికలను చూడాలి?', 'బోరు వివరాల ఫారం ఎలా నింపాలి?'],
    placeholder: 'టైప్ చేయండి లేదా మైక్ ఉపయోగించండి…', send: 'పంపండి', you: 'మీరు', assistant: 'సహాయకుడు', thinking: 'సులభమైన సమాధానం సిద్ధం చేస్తున్నాను…',
    fieldNote: 'విద్యుత్ లేదా అధిక ప్రమాద సమస్యలకు నిపుణుడిని పిలవండి.', clear: 'తొలగించు', open: 'AI సహాయం', close: 'సహాయకుడిని మూసివేయండి',
    voiceUnavailable: 'ఈ బ్రౌజర్‌లో వాయిస్ అందుబాటులో లేదు. మీ ప్రశ్నను టైప్ చేయండి.', listening: 'వింటున్నాను… ఇప్పుడు మాట్లాడండి', read: 'సమాధానం వినండి',
  },
}

export default function AssistantChat({ result }: { result: PredictionResult | null }) {
  const [open, setOpen] = useState(false)
  const [language, setLanguage] = useState<AssistantLanguage>('auto')
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [listening, setListening] = useState(false)
  const [error, setError] = useState('')
  const bottom = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const recognitionRef = useRef<Recognition | null>(null)
  const text = language === 'te' ? copy.te : copy.en
  const voiceLanguage = languageOptions.find((option) => option.code === language)?.voice ?? 'en-IN'

  useEffect(() => { bottom.current?.scrollIntoView({ block: 'nearest' }) }, [messages, busy, open])
  useEffect(() => { if (open) inputRef.current?.focus() }, [open])
  useEffect(() => () => {
    window.speechSynthesis.cancel()
    recognitionRef.current?.stop()
  }, [])

  function closeAssistant() {
    window.speechSynthesis.cancel()
    recognitionRef.current?.stop()
    recognitionRef.current = null
    setListening(false)
    setOpen(false)
  }

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
      const assessment = result ? {
        risk_category: result.risk_category,
        ensemble_probability: result.ensemble_probability,
        top_features: result.top_features.slice(0, 5),
      } : undefined
      const reply = await sendChat(next, language, assessment)
      setMessages([...next, { role: 'assistant', content: reply }])
    } catch (failure) {
      setMessages(messages)
      setInput(question)
      setError(failure instanceof Error ? failure.message : 'Unable to answer. Please try again.')
    } finally { setBusy(false) }
  }

  function startVoiceInput() {
    const voiceWindow = window as unknown as { SpeechRecognition?: RecognitionConstructor; webkitSpeechRecognition?: RecognitionConstructor }
    const RecognitionApi = voiceWindow.SpeechRecognition ?? voiceWindow.webkitSpeechRecognition
    if (!RecognitionApi) { setError(text.voiceUnavailable); return }
    setError('')
    const recognition = new RecognitionApi()
    recognitionRef.current = recognition
    recognition.lang = voiceLanguage
    recognition.interimResults = false
    recognition.onresult = (event) => setInput(event.results[0][0].transcript)
    recognition.onerror = () => setError(text.voiceUnavailable)
    recognition.onend = () => { recognitionRef.current = null; setListening(false) }
    setListening(true)
    recognition.start()
  }

  function readAnswer(content: string) {
    window.speechSynthesis.cancel()
    const speech = new SpeechSynthesisUtterance(content)
    speech.lang = voiceLanguage
    speech.rate = 0.9
    window.speechSynthesis.speak(speech)
  }

  return <div className="assistant-widget">
    {open && <section className="assistant-panel" aria-label={text.title}>
      <div className="assistant-header"><img src={assistantIcon} alt="" /><div><strong>{text.title}</strong><small>{text.subtitle}</small></div><button type="button" onClick={closeAssistant} aria-label={text.close}>×</button></div>
      <div className="assistant-tools"><label htmlFor="assistant-language">Answer language</label><select id="assistant-language" value={language} onChange={(event) => setLanguage(event.target.value as AssistantLanguage)}>{languageOptions.map((option) => <option key={option.code} value={option.code}>{option.label}</option>)}</select></div>
      {result && <div className={`assistant-result ${result.risk_category.toLowerCase()}`}><span>{language === 'te' ? 'తాజా ఫలితం జతచేయబడింది' : 'Latest result attached'}</span><strong>{result.risk_category} · {(result.ensemble_probability * 100).toFixed(1)}%</strong></div>}
      <div className="assistant-messages" role="log" aria-live="polite" aria-busy={busy}>
        {!messages.length && <div className="assistant-welcome"><h3>{text.hello}</h3><p>{text.intro}</p><p className="assistant-note">{text.privacy}</p>{text.prompts.map((question) => <button type="button" key={question} onClick={() => { setInput(question); inputRef.current?.focus() }}>{question}</button>)}</div>}
        {messages.map((message, index) => <div className={`assistant-message ${message.role}`} key={index}><small>{message.role === 'user' ? text.you : text.assistant}</small><p>{message.content}</p>{message.role === 'assistant' && <button className="read-answer" type="button" onClick={() => readAnswer(message.content)}>🔊 {text.read}</button>}</div>)}
        {busy && <p className="assistant-note">{text.thinking}</p>}
        <div ref={bottom} />
      </div>
      {listening && <p className="assistant-listening" role="status">● {text.listening}</p>}
      {error && <p className="assistant-error" role="alert">{error}</p>}
      <form className="assistant-form" onSubmit={submit}><button className="voice-button" type="button" onClick={startVoiceInput} disabled={busy || listening} aria-label={text.listening}>🎙️</button><label className="assistant-input"><span className="sr-only">{text.placeholder}</span><input ref={inputRef} value={input} onChange={(event) => setInput(event.target.value)} maxLength={4000} placeholder={text.placeholder} disabled={busy} /></label><button type="submit" disabled={busy || !input.trim()}>{text.send}</button></form>
      <div className="assistant-footer"><span>{text.fieldNote}</span><button type="button" disabled={busy} onClick={() => { window.speechSynthesis.cancel(); setMessages([]); setError(''); setInput('') }}>{text.clear}</button></div>
    </section>}
    <button className="assistant-launcher" type="button" aria-expanded={open} onClick={() => open ? closeAssistant() : setOpen(true)}><img src={assistantIcon} alt="" />{open ? text.close : text.open}</button>
  </div>
}
