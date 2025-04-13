import { useState } from 'react'
import axios from 'axios'

const AskBox = () => {
  const [question, setQuestion] = useState('')
  const [response, setResponse] = useState<any>(null)

  const handleAsk = async () => {
    try {
      const res = await axios.post('http://127.0.0.1:8001/ask', { question })
      setResponse(res.data)
    } catch (error) {
      console.error('Ask failed', error)
    }
  }

  return (
    <div>
      <h2>Ask LLM</h2>
      <input type="text" value={question} onChange={e => setQuestion(e.target.value)} />
      <button onClick={handleAsk}>Ask</button>

      {response && (
        <div>
          {response.question && (
            <p>
              <strong>Q:</strong> {response.question}
            </p>
          )}
          {response.answer ? (
            <p>
              <strong>A:</strong> {response.answer}
            </p>
          ) : (
            <p style={{ color: 'red' }}>⚠️ No answer returned from the backend</p>
          )}
        </div>
      )}
    </div>
  )
}

export default AskBox
