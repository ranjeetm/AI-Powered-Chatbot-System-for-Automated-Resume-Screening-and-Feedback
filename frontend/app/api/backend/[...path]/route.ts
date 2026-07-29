import { NextRequest } from "next/server"


const BACKEND_API_URL =
  process.env.BACKEND_API_URL
  || process.env.NEXT_PUBLIC_API_URL
  || "http://127.0.0.1:8000"


type RouteContext = {
  params: Promise<{
    path: string[]
  }>
}


function copyRequestHeaders(
  request: NextRequest,
  contentType: string
) {

  const headers = new Headers()

  const authorization = request.headers.get("authorization")

  if (authorization) {

    headers.set(
      "authorization",
      authorization
    )
  }

  if (contentType) {

    headers.set(
      "content-type",
      contentType
    )
  }

  return headers
}


async function getRequestBody(
  request: NextRequest
) {

  if (
    request.method === "GET"
    || request.method === "HEAD"
  ) {

    return undefined
  }

  return await request.arrayBuffer()
}


function getBackendApiUrls() {

  const urls = [
    BACKEND_API_URL,
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://127.0.0.1:8001",
    "http://localhost:8001"
  ]

  return Array.from(
    new Set(urls)
  )
}


function copyResponseHeaders(
  response: Response
) {

  const headers = new Headers()

  for (const header of [
    "content-type",
    "content-disposition"
  ]) {

    const value = response.headers.get(header)

    if (value) {

      headers.set(
        header,
        value
      )
    }
  }

  return headers
}


async function proxyRequest(
  request: NextRequest,
  context: RouteContext
) {

  const { path } = await context.params
  const url = new URL(request.url)
  const backendUrl = new URL(
    `/${path.join("/")}${url.search}`,
    BACKEND_API_URL
  )
  const contentType = request.headers.get("content-type") || ""
  const requestBody = await getRequestBody(request)

  let response: Response | null = null

  const fetchOptions: RequestInit = {
    method: request.method,
    headers: copyRequestHeaders(
      request,
      contentType
    ),
    body: requestBody,
    cache: "no-store"
  }

  for (const apiUrl of getBackendApiUrls()) {

    const candidateUrl = new URL(
      backendUrl.pathname + backendUrl.search,
      apiUrl
    )

    try {

      response = await fetch(
        candidateUrl,
        fetchOptions
      )

      break

    } catch {

      continue
    }
  }

  if (!response) {

    return Response.json(
      {
        detail:
          "Cannot connect to FastAPI. Tried http://127.0.0.1:8000, http://localhost:8000, http://127.0.0.1:8001, and http://localhost:8001. For direct uvicorn, run it on port 8000."
      },
      {
        status: 502
      }
    )
  }

  return new Response(
    response.body,
    {
      status: response.status,
      statusText: response.statusText,
      headers: copyResponseHeaders(response)
    }
  )
}


export async function GET(
  request: NextRequest,
  context: RouteContext
) {

  return proxyRequest(
    request,
    context
  )
}


export async function POST(
  request: NextRequest,
  context: RouteContext
) {

  return proxyRequest(
    request,
    context
  )
}


export async function OPTIONS() {

  return new Response(null, {
    status: 204
  })
}
