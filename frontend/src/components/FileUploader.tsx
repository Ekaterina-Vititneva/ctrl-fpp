import { useState } from 'react'
import axios from 'axios'
import { Typography, Button, Box, Alert, CircularProgress } from '@mui/material'

interface FileUploaderProps {
  onUploadSuccess?: () => void
}

const FileUploader = ({ onUploadSuccess }: FileUploaderProps) => {
  const [message, setMessage] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(false)

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setLoading(true)
    setMessage('')

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await axios.post(`${import.meta.env.VITE_BACKEND_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      setMessage(response.data.message)
      onUploadSuccess?.()
    } catch (error: any) {
      console.error('Upload error:', error)
      if (error.response) {
        setMessage(`Upload failed: ${error.response.data?.detail ?? 'Unknown server error'}`)
      } else if (error.request) {
        setMessage('Upload failed: No response from server')
      } else {
        setMessage(`Upload failed: ${error.message}`)
      }
    } finally {
      setLoading(false)
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
        disabled={loading}
        startIcon={loading ? <CircularProgress size={20} /> : null}
      >
        {loading ? 'Wird hochgeladen...' : 'PDF auswählen & hochladen'}
        <input hidden type="file" accept=".pdf" onChange={handleFileChange} />
      </Button>

      {message && (
        <Alert severity={message.startsWith('Upload failed') ? 'error' : 'success'} sx={{ mt: 2 }}>
          {message}
        </Alert>
      )}
    </Box>
  )
}

export default FileUploader
