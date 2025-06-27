import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/_layout/open-tabs')({
  component: () => <div>Hello /_layout/open-tabs!</div>
})