import { useEffect, useState } from 'react'
import axios from 'axios'
import { Container, Typography, Box, Divider, ThemeProvider, CssBaseline } from '@mui/material'

import AskBox from './components/AskBox'
import FileUploader from './components/FileUploader'
import ResetButton from './components/ResetButton'
import UploadedDocumentsList from './components/UploadedDocumentsList'
import theme from './theme'

function App() {
  const [documents, setDocuments] = useState<string[]>([])

  const fetchDocuments = async () => {
    try {
      const res = await axios.get(`${import.meta.env.VITE_BACKEND_URL}/documents`)
      setDocuments(res.data.documents)
    } catch (error) {
      console.error('Error loading documents:', error)
    }
  }

  useEffect(() => {
    fetchDocuments()
  }, [])

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Typography variant="h3" gutterBottom>
          Ctrl+F ++
        </Typography>

        <Box my={3}>
          <FileUploader onUploadSuccess={fetchDocuments} />
          <UploadedDocumentsList documents={documents} />
        </Box>

        <Divider sx={{ my: 4 }} />

        <Box my={3}>
          <AskBox />
        </Box>

        <Box my={4}>
          <ResetButton />
        </Box>
      </Container>
    </ThemeProvider>
  )
}

export default App
