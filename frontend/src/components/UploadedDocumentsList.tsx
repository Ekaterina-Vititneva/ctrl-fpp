import { Typography, List, ListItem, ListItemIcon, ListItemText, Box } from '@mui/material'
import PictureAsPdfOutlinedIcon from '@mui/icons-material/PictureAsPdfOutlined'

interface UploadedDocumentsListProps {
  documents: string[]
}

export default function UploadedDocumentsList({ documents }: UploadedDocumentsListProps) {
  if (!documents.length) return null

  return (
    <div style={{ marginTop: '2rem' }}>
      <Typography variant="h6" gutterBottom>
        Hochgeladene PDFs ({documents.length})
      </Typography>
      <Box sx={{ height: '230px', overflowY: 'auto' }}>
        <List>
          {documents.map((doc, index) => (
            <ListItem key={index}>
              <ListItemIcon>
                <PictureAsPdfOutlinedIcon sx={{ color: theme => theme.palette.secondary.main }} />
              </ListItemIcon>
              <ListItemText
                primary={doc}
                slotProps={{
                  primary: {
                    sx: { fontSize: '0.8rem', overflow: 'hidden', textOverflow: 'ellipsis' },
                  },
                }}
              />
            </ListItem>
          ))}
        </List>
      </Box>
    </div>
  )
}
