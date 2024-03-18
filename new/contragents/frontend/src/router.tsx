import { createBrowserRouter } from 'react-router-dom'

import MainPage from './pages/MainPage.tsx'
import StaffPage from './pages/StaffPage.tsx'

const status = false

const router = createBrowserRouter([
  {
    path: '/',
    element: status ? <StaffPage/> : <MainPage/>
  }
])


export default router