import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import client from '../api/client'

export function useChecklist(category) {
  return useQuery({
    queryKey: ['checklist', category],
    queryFn: () =>
      client.get('/checklist', { params: category ? { category } : undefined }).then((r) => r.data),
  })
}

export function useUpdateChecklistStatus() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, status }) => client.patch(`/checklist/${id}`, { status }).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['checklist'] }),
  })
}

export function useDeleteChecklistItem() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id) => client.delete(`/checklist/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['checklist'] }),
  })
}
