import { useEffect, useRef, useState } from 'react'
import axios from 'axios'
import {
  Typography,
  Button,
  Box,
  Alert,
  CircularProgress,
  LinearProgress,
  Paper,
} from '@mui/material'

interface FileUploaderProps {
  onUploadSuccess?: () => void // refresh docs list in <App>
}

interface JobStatus {
  state: string // queued | parsing | chunking | embedding | storing | done | error
  progress: number // 0.0 – 1.0
  phase?: string
  error?: string
}

const POLL_MS = 1_000 // how often to poll /status/<job_id>

export default function FileUploader({ onUploadSuccess }: FileUploaderProps) {
  const [message, setMessage] = useState<string>('')
  const [uploading, setUploading] = useState<boolean>(false)
  const [, setJobId] = useState<string | null>(null)
  const [status, setStatus] = useState<JobStatus | null>(null)

  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const backend = import.meta.env.VITE_BACKEND_URL

  // ─── progress‑bar helpers ───────────────────────────────────────────
  const isWorking = status && !['done', 'error'].includes(status.state)
  const isDeterm = status && ['parsing', 'chunking', 'embedding'].includes(status.state)
  const barVariant = isDeterm ? 'determinate' : 'indeterminate'
  const barValue = status ? Math.round((status.progress ?? 0) * 100) : 0
  // ────────────────────────────────────────────────────────────────────

  const startPolling = (id: string) => {
    timerRef.current = setInterval(async () => {
      try {
        const res = await axios.get<JobStatus>(`${backend}/status/${id}`)
        setStatus(res.data)

        if (['done', 'error'].includes(res.data.state)) {
          clearInterval(timerRef.current!)
          if (res.data.state === 'done') {
            setMessage('✅ Verarbeitung abgeschlossen')
            onUploadSuccess?.()
          } else {
            setMessage(`⚠️ Fehler: ${res.data.error}`)
          }
        }
      } catch (err) {
        console.error('Status polling failed', err)
        clearInterval(timerRef.current!)
        setMessage('⚠️ Statusabfrage fehlgeschlagen')
      }
    }, POLL_MS)
  }

  // clean‑up on unmount
  useEffect(() => () => clearInterval(timerRef.current!), [])

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setUploading(true)
    setMessage('')
    setStatus(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await axios.post<{ job_id: string; message: string }>(
        `${backend}/upload`,
        formData
      )

      setJobId(res.data.job_id)
      setMessage(res.data.message)
      startPolling(res.data.job_id)
    } catch (err: any) {
      console.error('Upload error', err)
      setMessage(
        err.response?.data?.detail
          ? `Upload fehlgeschlagen: ${err.response.data.detail}`
          : 'Upload fehlgeschlagen'
      )
    } finally {
      setUploading(false)
    }
  }

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        PDF hochladen
      </Typography>

      <Button
        variant="contained"
        component="label"
        disabled={uploading}
        startIcon={uploading && <CircularProgress size={20} />}
      >
        {uploading ? 'Wird hochgeladen…' : 'PDF auswählen & hochladen'}
        <input hidden type="file" accept=".pdf" onChange={handleFileChange} />
      </Button>

      {status && (
        <Paper variant="outlined" sx={{ mt: 2, p: 2 }}>
          <Typography variant="body2" gutterBottom>
            {status.state === 'done'
              ? '✅ Fertig'
              : status.state === 'error'
                ? '❌ Fehler'
                : `⏳ ${status.state}…`}
          </Typography>

          {isWorking && <LinearProgress variant={barVariant} value={barValue} />}
          {status?.phase && <Typography variant="caption">{status.phase}</Typography>}
        </Paper>
      )}

      {/* {message && (
        <Alert severity={message.startsWith('⚠️') ? 'error' : 'info'} sx={{ mt: 2 }}>
          {message}
        </Alert>
      )} */}
    </Box>
  )
}
