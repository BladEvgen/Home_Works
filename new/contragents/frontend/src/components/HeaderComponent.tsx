import AppBar from '@mui/material/AppBar'
import Box from '@mui/material/Box'
import Toolbar from '@mui/material/Toolbar'
import Typography from '@mui/material/Typography'
import Button from '@mui/material/Button'
import { useLocation, useNavigate } from 'react-router-dom'
import Cookies from 'js-cookie'
import { useEffect } from 'react'

const HeaderComponent = () => {
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    if (!Cookies.get('access_token')) {
      navigate('/register')
      // @ts-ignore
    } else if (location === '/register') {
      navigate('/')
    }
  }, [])

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Contracts manager
          </Typography>
          <Button
            onClick={() => {
              navigate('/register')
            }}
            color="inherit"
          >
            Зарегистрировать
          </Button>
        </Toolbar>
      </AppBar>
    </Box>
  )
}

export default HeaderComponent
