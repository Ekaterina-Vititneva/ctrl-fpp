import { createTheme } from '@mui/material/styles'

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#5b5ed9',
    },
    secondary: {
      main: '#787878',
    },
    background: {
      default: '#1a1a1a',
      paper: '#111111',
    },
    text: {
      primary: '#ffffff',
      secondary: '#a1a1aa',
    },
    divider: 'rgba(255,255,255,0.08)',
  },
  typography: {
    fontFamily: ['"Inter"', 'system-ui', 'sans-serif'].join(','),
    fontSize: 14,
    h1: { fontSize: '2.5rem', fontWeight: 700 },
    h2: { fontSize: '2rem', fontWeight: 600 },
    h3: { fontSize: '1.5rem', fontWeight: 500 },
    button: {
      textTransform: 'none',
      fontWeight: 500,
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundColor: '#000000',
          color: '#ffffff',
          WebkitFontSmoothing: 'antialiased',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundColor: '#111111',
          boxShadow: 'none',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          backgroundColor: '#111111',
          color: '#ffffff',
          border: '1px solid rgba(255,255,255,0.08)',
          borderRadius: 6,
          padding: '8px 16px',
          fontWeight: 500,
          '&:hover': {
            backgroundColor: '#1a1a1a',
            borderColor: '#6366f1',
            color: '#ffffff',
          },
        },
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          backgroundColor: '#111111',
          borderRadius: 6,
          color: '#ffffff',
          '& .MuiOutlinedInput-notchedOutline': {
            borderColor: 'rgba(255,255,255,0.1)',
          },
          '&:hover .MuiOutlinedInput-notchedOutline': {
            borderColor: '#6366f1',
          },
          '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
            borderColor: '#6366f1',
          },
        },
        input: {
          color: '#ffffff',
        },
      },
    },
    MuiInputLabel: {
      styleOverrides: {
        root: {
          color: '#a1a1aa',
          '&.Mui-focused': {
            color: '#6366f1',
          },
        },
      },
    },
    MuiSelect: {
      styleOverrides: {
        select: {
          backgroundColor: '#111111',
          color: '#ffffff',
        },
        icon: {
          color: '#a1a1aa',
        },
      },
    },
  },
})

export default theme
