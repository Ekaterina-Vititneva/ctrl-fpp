import AskBox from './components/AskBox'
import FileUploader from './components/FileUploader'
import QuestionBox from './components/QuestionBox'

function App() {
  return (
    <div style={{ padding: '2rem' }}>
      <h1>Ctrl+F++</h1>
      <FileUploader />
      <hr />
      <QuestionBox />
      <AskBox />
    </div>
  )
}

export default App
