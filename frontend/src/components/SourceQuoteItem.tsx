import { useState } from 'react'
import { Paper, Box, Typography, Button } from '@mui/material'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'

const MAX_LENGTH = 300

interface SourceQuoteItemProps {
  chunk: string
  source: string
  distance: number
  page: number // optional if some chunks don't have a page
}

export default function SourceQuoteItem({ chunk, source, distance, page }: SourceQuoteItemProps) {
  const [expanded, setExpanded] = useState(false)
  const handleToggle = () => setExpanded(!expanded)

  function truncateText(text: string, maxLength: number) {
    if (text.length <= maxLength) return text
    return text.slice(0, maxLength) + '…'
  }

  const isTruncated = chunk.length > MAX_LENGTH
  const displayText = expanded ? chunk : truncateText(chunk, MAX_LENGTH)

  return (
    <Paper
      variant="outlined"
      sx={{
        p: 2,
        backgroundColor: 'background.default',
        borderLeft: '4px solid #1976d2',
      }}
    >
      <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', mb: 1 }}>
        “{displayText}”
      </Typography>

      <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
        📄 {source}
        {page != null && ` (Seite ${page})`} {/* Render if page is not null */}
        {' • '}🔍 {distance.toFixed(4)}
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
