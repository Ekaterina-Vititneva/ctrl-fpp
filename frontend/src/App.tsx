import { useEffect, useState } from 'react'
import axios from 'axios'
import { Typography, Box, CssBaseline, ThemeProvider, Divider, Paper } from '@mui/material'

import AskBox from './components/AskBox'
import FileUploader from './components/FileUploader'
import ResetButton from './components/ResetButton'
import UploadedDocumentsList from './components/UploadedDocumentsList'
import theme from './theme'

export default function App() {
  const [documents, setDocuments] = useState<string[]>([])

  const fetchDocuments = async () => {
    try {
      const res = await axios.get(`${import.meta.env.VITE_BACKEND_URL}/documents`)
      setDocuments(res.data.documents)
    } catch (err) {
      console.error('Error loading documents', err)
    }
  }

  useEffect(() => {
    fetchDocuments()
  }, [])

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />

      <Box sx={{ p: 2, height: '5%', boxSizing: 'border-box' }}>
        {/* ─────────── FLEX LAYOUT ─────────── */}
        <Box
          sx={{
            display: 'flex',
            gap: 4,
            mt: 3,
            // make it scroll nicely on small screens
            flexDirection: { xs: 'column', md: 'row' },
          }}
        >
          {/* ---- FIXED LEFT RAIL ---- */}
          <Box
            elevation={1}
            sx={{
              width: 240,
              flexShrink: 0,
              p: 0,
              display: 'flex',
              flexDirection: 'column',
              flexGrow: 1,
              overflowY: 'auto',
              height: 'calc(100vh - 64px)',
            }}
          >
            <Typography variant="h3" gutterBottom>
              Ctrl+F ++
              {/* AskMyPDF */}
            </Typography>
            <FileUploader onUploadSuccess={fetchDocuments} />
            <UploadedDocumentsList documents={documents} />
            <Divider sx={{ my: 1 }} />
            <ResetButton onResetSuccess={fetchDocuments} />
          </Box>
          {/* ---- EXPANDING RIGHT PANEL ---- */}
          <Box
            sx={{
              flexGrow: 1,
              display: 'flex',
              /* make the column as tall as the viewport minus top padding (2 * 8px) */
              height: 'calc(100vh - 64px)',
              width: '100%',
            }}
          >
            <AskBox />
          </Box>
        </Box>
      </Box>
    </ThemeProvider>
  )
}
