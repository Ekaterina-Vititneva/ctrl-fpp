import { useState } from 'react'
import axios from 'axios'

const FileUploader = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [message, setMessage] = useState('')

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setSelectedFile(event.target.files[0])
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) return

    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      const response = await axios.post('http://127.0.0.1:8001/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      setMessage(response.data.message)
    } catch (error: any) {
      console.error('Upload error:', error)

      if (error.response) {
        console.log('Error response:', error.response)
        setMessage(`Upload failed: ${error.response.data?.detail ?? 'Unknown server error'}`)
      } else if (error.request) {
        console.log('Error request:', error.request)
        setMessage('Upload failed: No response from server')
      } else {
        setMessage(`Upload failed: ${error.message}`)
      }
    }
  }

  return (
    <div>
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleUpload}>Upload PDF</button>
      {message && <p>{message}</p>}
    </div>
  )
}

export default FileUploader
