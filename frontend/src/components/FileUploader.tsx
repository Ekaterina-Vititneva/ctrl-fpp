import { useState } from 'react'
import axios from 'axios'
import { Typography, Button, Box, Alert, InputLabel, Stack } from '@mui/material'

const FileUploader = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [message, setMessage] = useState<string>('')

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files?.length) {
      setSelectedFile(event.target.files[0])
      setMessage('') // clear message on new selection
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) return

    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      const response = await axios.post(`${import.meta.env.VITE_BACKEND_URL}/upload`, formData, {})
      setMessage(response.data.message)
    } catch (error: any) {
      console.error('Upload error:', error)

      if (error.response) {
        setMessage(`Upload failed: ${error.response.data?.detail ?? 'Unknown server error'}`)
      } else if (error.request) {
        setMessage('Upload failed: No response from server')
      } else {
        setMessage(`Upload failed: ${error.message}`)
      }
    }
  }

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        PDF hochladen
      </Typography>

      <Stack direction="row" spacing={2} alignItems="center">
        <InputLabel htmlFor="file-upload">
          <Button variant="outlined" component="label">
            Datei wählen
            <input hidden id="file-upload" type="file" onChange={handleFileChange} accept=".pdf" />
          </Button>
        </InputLabel>

        <Button variant="contained" onClick={handleUpload} disabled={!selectedFile}>
          Hochladen
        </Button>
      </Stack>

      {selectedFile && (
        <Typography variant="body2" sx={{ mt: 1 }}>
          Ausgewählt: {selectedFile.name}
        </Typography>
      )}

      {message && (
        <Alert severity={message.startsWith('Upload failed') ? 'error' : 'success'} sx={{ mt: 2 }}>
          {message}
        </Alert>
      )}
    </Box>
  )
}

export default FileUploader
