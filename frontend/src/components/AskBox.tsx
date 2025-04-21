import { useState } from 'react'
import axios from 'axios'
import {
  TextField,
  Typography,
  Card,
  CardContent,
  CircularProgress,
  Box,
  Paper,
  Stack,
  IconButton,
  InputAdornment,
} from '@mui/material'
import SendIcon from '@mui/icons-material/Send'
import ReactMarkdown from 'react-markdown'
import SourceQuoteItem from './SourceQuoteItem'

const AskBox = () => {
  const [question, setQuestion] = useState('')
  const [response, setResponse] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  // This helper splits the question into an array of words, removing punctuation and short words
  const getQuestionWords = (q: string) => {
    return q
      .split(/\s+/)
      .map(word => word.replace(/[^\p{L}\p{N}]+/gu, ''))
      .filter(Boolean)
      .filter(word => word.length >= 4)
  }

  const handleAsk = async () => {
    if (!question.trim()) return
    setLoading(true)

    try {
      const res = await axios.post(`${import.meta.env.VITE_BACKEND_URL}/ask`, { question })
      setResponse(res.data)
    } catch (error: any) {
      console.error('Ask failed:', error)
      setResponse({ answer: '⚠️ Anfrage fehlgeschlagen. Bitte erneut versuchen.' })
    } finally {
      setLoading(false)
    }
  }

  // We'll compute the array of words to highlight
  const questionWords = getQuestionWords(question)

  return (
    <Card
      variant="outlined"
      sx={{
        height: '10a0%',
        width: '100%',
        display: 'flex',
        flexDirection: 'column',
        flexGrow: 1,
        overflow: 'hidden',
      }}
    >
      <Box
        sx={{
          overflowY: 'auto',
          height: '100%',
          pr: '8px', // This moves scrollbar inward
        }}
      >
        <CardContent
          sx={{
            flexGrow: 1,
            display: 'flex',
            flexDirection: 'column',
            overflowY: 'auto',
            pr: 0, // No padding here
          }}
        >
          <Typography variant="h6" gutterBottom mb={2}>
            Frage stellen
          </Typography>

          <Box display="flex" gap={2} flexWrap="wrap" mb={2}>
            <TextField
              fullWidth
              label="Frage"
              value={question}
              onChange={e => setQuestion(e.target.value)}
              variant="outlined"
              size="small"
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      edge="end"
                      color="primary"
                      onClick={handleAsk}
                      disabled={loading || !question.trim()}
                    >
                      {loading ? <CircularProgress size={20} /> : <SendIcon />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
          </Box>

          {response?.answer && (
            <>
              <Box sx={{}}>
                <Typography variant="h6" gutterBottom>
                  Antwort:
                </Typography>
                <Paper elevation={1} sx={{ p: 2 }}>
                  <ReactMarkdown
                    components={{
                      p: props => <Typography variant="body2" {...props} />,
                      h1: props => <Typography variant="h5" {...props} />,
                      h2: props => <Typography variant="h5" {...props} />,
                      h3: props => <Typography variant="h5" {...props} />,
                      h4: props => <Typography variant="h5" {...props} />,
                      h5: props => <Typography variant="h5" {...props} />,
                      li: props => <li style={{ fontSize: '0.875rem' }} {...props} />,
                    }}
                  >
                    {response.answer}
                  </ReactMarkdown>
                </Paper>
              </Box>
            </>
          )}

          {response?.sources?.length > 0 && (
            <Box mt={4}>
              <Typography variant="subtitle1" gutterBottom>
                📚 Verwendete Textstellen:
              </Typography>
              <Box
                sx={{
                  flexGrow: 1,
                  mb: 2,
                }}
              >
                <Stack spacing={2}>
                  {response.sources.map((src: any, idx: number) => (
                    <SourceQuoteItem
                      key={idx}
                      chunk={src.chunk}
                      source={src.source}
                      distance={src.distance}
                      page={src.page}
                      questionWords={questionWords} // pass the array to highlight
                    />
                  ))}
                </Stack>
              </Box>
            </Box>
          )}
        </CardContent>
      </Box>
    </Card>
  )
}

export default AskBox
