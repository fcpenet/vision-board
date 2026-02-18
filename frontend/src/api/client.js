import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api',
  headers: {
    'X-API-Key': import.meta.env.VITE_API_KEY ?? '',
  },
})

export default client
