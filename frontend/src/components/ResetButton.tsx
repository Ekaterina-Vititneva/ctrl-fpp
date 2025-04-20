import React from 'react'
import axios from 'axios'
import Button from '@mui/material/Button'

const ResetButton: React.FC = () => {
  const handleReset = async () => {
    const confirm = window.confirm('Are you sure you want to clear the vectorstore?')
    if (!confirm) return

    try {
      await axios.post(`${import.meta.env.VITE_BACKEND_URL}/reset`)
      alert('Vectorstore has been cleared!')
    } catch (error) {
      console.error('Error resetting vectorstore:', error)
      alert('Reset failed')
    }
  }

  return (
    <Button
      variant="contained"
      size="small"
      onClick={handleReset}
      startIcon={<span>🧹</span>}
      sx={{ mt: 2 }}
    >
      Reset Knowledge Base
    </Button>
  )
}

export default ResetButton
