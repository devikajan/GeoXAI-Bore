import { useEffect, useState } from 'react'
import { checkApiHealth } from './api'

export default function useApiStatus() {
  const [status, setStatus] = useState<'checking' | 'ready' | 'offline'>('checking')
  const [retry, setRetry] = useState(0)
  useEffect(() => {
    let active = true
    let running = false
    let timer: number | undefined
    let firstFailureAt = 0
    async function check() {
      if (!active || running) return
      running = true
      window.clearTimeout(timer)
      const available = await checkApiHealth()
      running = false
      if (!active) return
      if (available) {
        firstFailureAt = 0
        setStatus('ready')
      } else {
        if (!firstFailureAt) firstFailureAt = Date.now()
        setStatus(Date.now() - firstFailureAt >= 180000 ? 'offline' : 'checking')
      }
      timer = window.setTimeout(check, available ? 60000 : 8000)
    }
    const checkOnReturn = () => {
      if (document.visibilityState === 'visible') void check()
    }
    void check()
    window.addEventListener('online', checkOnReturn)
    window.addEventListener('focus', checkOnReturn)
    document.addEventListener('visibilitychange', checkOnReturn)
    return () => {
      active = false
      window.clearTimeout(timer)
      window.removeEventListener('online', checkOnReturn)
      window.removeEventListener('focus', checkOnReturn)
      document.removeEventListener('visibilitychange', checkOnReturn)
    }
  }, [retry])
  return { apiStatus: status, reconnect: () => { setStatus('checking'); setRetry(value => value + 1) } }
}
