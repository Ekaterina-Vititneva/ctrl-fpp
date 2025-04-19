import { Typography, List, ListItem, ListItemIcon, ListItemText } from '@mui/material'
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf'

interface UploadedDocumentsListProps {
  documents: string[]
}

export default function UploadedDocumentsList({ documents }: UploadedDocumentsListProps) {
  if (!documents.length) return null

  return (
    <div style={{ marginTop: '2rem' }}>
      <Typography variant="h6" gutterBottom>
        Hochgeladene PDFs
      </Typography>
      <List>
        {documents.map((doc, index) => (
          <ListItem key={index}>
            <ListItemIcon>
              <PictureAsPdfIcon sx={{ color: theme => theme.palette.secondary.main }} />
            </ListItemIcon>
            <ListItemText primary={doc} />
          </ListItem>
        ))}
      </List>
    </div>
  )
}
