import { useState } from 'react'
import axios from 'axios'

const QuestionBox = () => {
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState<any>(null)

  const handleAsk = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:8001/query', {
        question,
      })
      setAnswer(response.data)
    } catch (error) {
      setAnswer(null)
      console.error('Query failed', error)
    }
  }

  return (
    <div>
      <input type="text" value={question} onChange={e => setQuestion(e.target.value)} />
      <button onClick={handleAsk}>Ask</button>

      {answer && (
        <div>
          <h3>Results for: {answer.question}</h3>
          {answer.results?.map((r: any, idx: number) => (
            <div key={idx}>
              <p>Chunk: {r.chunk}</p>
              <p>Distance: {r.distance}</p>
              <hr />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default QuestionBox
