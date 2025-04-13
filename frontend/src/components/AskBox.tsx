// AskBox.tsx
import { useState } from 'react'
import axios from 'axios'
import {
  TextField,
  Button,
  Typography,
  Card,
  CardContent,
  CircularProgress,
  Box,
  Paper,
  Stack,
} from '@mui/material'
import SourceQuoteItem from './SourceQuoteItem' // <-- import the new child

const AskBox = () => {
  const [question, setQuestion] = useState('')
  const [response, setResponse] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const handleAsk = async () => {
    if (!question.trim()) return
    setLoading(true)

    try {
      const res = await axios.post('http://127.0.0.1:8001/ask', { question })
      setResponse(res.data)
    } catch (error: any) {
      console.error('Ask failed:', error)
      setResponse({ answer: '⚠️ Anfrage fehlgeschlagen. Bitte erneut versuchen.' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card variant="outlined" sx={{ mt: 4 }}>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          Frage stellen
        </Typography>

        <Box display="flex" gap={2} flexWrap="wrap" mb={2}>
          <TextField
            fullWidth
            label="Frage"
            value={question}
            onChange={e => setQuestion(e.target.value)}
            variant="outlined"
          />
          <Button variant="contained" onClick={handleAsk} disabled={loading}>
            {loading ? <CircularProgress size={24} /> : 'Absenden'}
          </Button>
        </Box>

        {response?.answer && (
          <>
            <Typography variant="subtitle1" gutterBottom>
              <strong>Antwort:</strong>
            </Typography>
            <Paper elevation={1} sx={{ p: 2 }}>
              <Typography variant="body1">{response.answer}</Typography>
            </Paper>
          </>
        )}

        {response?.sources?.length > 0 && (
          <Box mt={4}>
            <Typography variant="subtitle1" gutterBottom>
              📚 Verwendete Textstellen:
            </Typography>

            <Stack spacing={2}>
              {response.sources.map((src: any, idx: number) => (
                <SourceQuoteItem
                  key={idx}
                  chunk={src.chunk}
                  source={src.source}
                  distance={src.distance}
                />
              ))}
            </Stack>
          </Box>
        )}
      </CardContent>
    </Card>
  )
}

export default AskBox
