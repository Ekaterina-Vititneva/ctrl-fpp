import { useState } from 'react'
import { Paper, Box, Typography, Button, useTheme } from '@mui/material'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import Highlighter from 'react-highlight-words'

const MAX_LENGTH = 300

interface SourceQuoteItemProps {
  chunk: string
  source: string
  distance?: number
  score?: number
  page?: number
  questionWords?: string[]
}

function truncateText(text: string, maxLength: number) {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '…'
}

export default function SourceQuoteItem({
  chunk,
  source,
  distance,
  score,
  page,
  questionWords = [],
}: SourceQuoteItemProps) {
  const theme = useTheme()
  const [expanded, setExpanded] = useState(false)
  const handleToggle = () => setExpanded(!expanded)

  const isTruncated = chunk.length > MAX_LENGTH
  const displayText = expanded ? chunk : truncateText(chunk, MAX_LENGTH)
  const displaySimilarity = distance ?? score ?? 0

  return (
    <Paper
      variant="outlined"
      sx={{
        p: 2,
        backgroundColor: 'background.default',
        borderLeft: `4px solid ${theme.palette.primary.main}`,
      }}
    >
      <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', mb: 1 }}>
        <Highlighter
          highlightStyle={{
            backgroundColor: `${theme.palette.primary.main}25`,
            color: `${theme.palette.primary.main}`,
            padding: '1px',
            borderRadius: '4px',
          }}
          searchWords={questionWords}
          autoEscape={true}
          textToHighlight={`“${displayText}”`}
        />
      </Typography>

      <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
        📄 {source}
        {page != null && ` (Seite ${page})`}
        {' • '}🔍 Relevanz: {displaySimilarity.toFixed(4)}
      </Typography>

      {isTruncated && (
        <Box display="flex" justifyContent="flex-end">
          <Button
            variant="text"
            onClick={handleToggle}
            endIcon={
              <ExpandMoreIcon
                sx={{
                  transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
                  transition: 'transform 0.2s',
                }}
              />
            }
          >
            {expanded ? 'Show Less' : 'Show More'}
          </Button>
        </Box>
      )}
    </Paper>
  )
}
