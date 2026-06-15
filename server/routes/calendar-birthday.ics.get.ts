import { setResponseHeader } from 'h3'

export default defineEventHandler(async (_event) => {
  const ics = await buildICS('birthday')

  setResponseHeader(_event, 'Content-Type', 'text/calendar; charset=utf-8')
  setResponseHeader(_event, 'Cache-Control', 'public, max-age=3600')
  return ics
})
