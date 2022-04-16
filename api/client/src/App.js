import React, { useState } from 'react'
import Apollo from './Apollo'
import {
  colors,
  CssBaseline,
  ThemeProvider,
  createMuiTheme,
  AppBar,
  Tabs,
  Tab
} from '@material-ui/core'
import LatestFaces from './pages/LatestFaces'
import SelectedFaces from "./pages/SelectedFaces"
import SortableFaces from "./pages/SortableFaces"

const theme = createMuiTheme({
  palette: {
    primary: {
      main: '#556cd6'
    },
    secondary: {
      main: '#19857b'
    },
    error: {
      main: colors.red.A400
    },
    background: {
      default: '#fff'
    }
  },
  subtitle: {
    height: '10px'
  }
})

function a11yProps (index) {
  return {
    id: `simple-tab-${index}`,
    'aria-controls': `simple-tabpanel-${index}`
  }
}

export default function App () {
  const [tabValue, setTabValue] = useState(2)

  return (
    <Apollo>
      <ThemeProvider theme={theme}>
        {/* CssBaseline kickstart an elegant, consistent, and simple baseline to build upon. */}
        <CssBaseline />
        <AppBar position="static">
          <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} >
            <Tab label="Latest" {...a11yProps(0)} />
            <Tab label="Selected" {...a11yProps(1)} />
            <Tab label="Sortable" {...a11yProps(2)} />
          </Tabs>
        </AppBar>
      </ThemeProvider>
      { tabValue === 0 && (
        <LatestFaces />
      )}
      { tabValue === 1 && (
        <SelectedFaces />
      )}
      { tabValue === 2 && (
        <SortableFaces />
      )}

    </Apollo>
  )
}
