import { Container, Typography, Box, Divider, ThemeProvider, CssBaseline } from '@mui/material'
import AskBox from './components/AskBox'
import FileUploader from './components/FileUploader'
import ResetButton from './components/ResetButton'
import theme from './theme'

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Typography variant="h3" gutterBottom>
          Ctrl+F ++
        </Typography>

        <Box my={3}>
          <FileUploader />
        </Box>

        <Divider sx={{ my: 4 }} />

        {/* <Box my={3}>
          <QuestionBox />
        </Box> */}

        <Box my={3}>
          <AskBox />
        </Box>

        <Box my={4}>
          <ResetButton />
        </Box>
      </Container>
    </ThemeProvider>
  )
}

export default App
