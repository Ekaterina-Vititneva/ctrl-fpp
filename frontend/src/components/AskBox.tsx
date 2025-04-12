import { useState } from 'react'
import axios from 'axios'

const LocalAskBox = () => {
  const [question, setQuestion] = useState('')
  const [response, setResponse] = useState<any>(null)

  const handleAsk = async () => {
    try {
      const res = await axios.post('http://127.0.0.1:8001/askLocal', { question })
      setResponse(res.data)
    } catch (error) {
      console.error('Ask local failed', error)
    }
  }

  return (
    <div>
      <h2>Ask Local LLM</h2>
      <input type="text" value={question} onChange={e => setQuestion(e.target.value)} />
      <button onClick={handleAsk}>Ask</button>

      {response && (
        <div>
          <p>
            <strong>Q:</strong> {response.question}
          </p>
          <p>
            <strong>A:</strong> {response.answer}
          </p>
        </div>
      )}
    </div>
  )
}

export default LocalAskBox
