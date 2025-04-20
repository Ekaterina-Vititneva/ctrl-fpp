import axios from 'axios'

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
    <button onClick={handleReset} style={{ marginTop: '1rem', padding: '0.5rem 1rem' }}>
      🧹 Reset Knowledge Base
    </button>
  )
}

export default ResetButton
