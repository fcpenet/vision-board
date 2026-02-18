import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import VisionBoard from './pages/VisionBoard'
import Chat from './pages/Chat'
import Checklist from './pages/Checklist'
import Notes from './pages/Notes'
import './index.css'

const queryClient = new QueryClient()

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<VisionBoard />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/checklist" element={<Checklist />} />
          <Route path="/notes" element={<Notes />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>
)
