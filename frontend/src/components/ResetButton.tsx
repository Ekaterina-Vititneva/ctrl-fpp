import React from 'react'
import axios from 'axios'
import Button from '@mui/material/Button'
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline'

interface ResetButtonProps {
  onResetSuccess?: () => void
}

const ResetButton: React.FC<ResetButtonProps> = ({ onResetSuccess }) => {
  const handleReset = async () => {
    const confirm = window.confirm('Are you sure you want to clear the vectorstore?')
    if (!confirm) return

    try {
      await axios.post(`${import.meta.env.VITE_BACKEND_URL}/reset`)
      alert('Vectorstore has been cleared!')
      onResetSuccess?.() // ← call the callback
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
      startIcon={<DeleteOutlineIcon />}
      sx={{ mt: 2, justifyContent: 'left' }}
    >
      Reset Knowledge Base
    </Button>
  )
}

export default ResetButton
