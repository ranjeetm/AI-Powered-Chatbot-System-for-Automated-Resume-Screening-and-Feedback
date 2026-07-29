export const API_BASE_URL =
  "/api/backend"


export type LoginResponse = {
  access_token?: string
  token_type?: string
}


export type RegisterResponse = {
  message: string
  user_id: number
}


export type RankedCandidate = {
  candidate_id: number
  candidate_name?: string
  category?: string
  final_score: number
  semantic_similarity?: number
  skill_match?: number
  title_match?: number
  experience_match?: number
  experience_years?: number
  skills?: string[]
}


export type RankingResponse = {
  ranked_candidates: RankedCandidate[]
}


export type UploadResumeResponse = {
  message: string
  file_name: string
}


export type CandidateApplicationResponse = {
  message: string
  file_name: string
  candidate_name: string
  email: string
}


export type JobPosting = {
  id: number
  title: string
  department?: string | null
  location?: string | null
  type?: string | null
  description: string
  skills?: string[]
  created_at?: string | null
}


export type JobPostingCreate = {
  title: string
  department?: string
  location?: string
  type?: string
  description: string
  skills: string[]
}


export type CandidateDetails = {
  id: number
  file_name?: string
  candidate_name?: string
  email?: string
  phone?: string
  location?: string
  linkedin_url?: string
  github_url?: string
  category?: string
  experience_years?: number
  skills?: string[]
  job_titles?: string[]
  degrees?: string[]
  specializations?: string[]
  certifications?: string[]
  education?: unknown[]
  projects?: unknown[]
  experience?: unknown[]
  resume_summary?: string
  resume_text?: string
  resume_file_path?: string
  is_shortlisted?: boolean
  shortlist_updated_at?: string | null
  rejection_feedback?: string | null
}


export type ShortlistActionResponse = {
  message: string
  is_shortlisted: boolean
  email_sent: boolean
}


export type FeedbackSuggestionResponse = {
  feedback: string
  matched_skills: string[]
  missing_skills: string[]
  final_score: number
}


export type ChatRole = "user" | "assistant" | "system"


export type CopilotChatMessage = {
  role: ChatRole
  content: string
}


export type RelevantSection = {
  name: string
  snippet: string
  full_text?: string | null
}


export type CandidateEvidence = {
  candidate_id: number
  candidate_name?: string | null
  category?: string | null
  skills: string[]
  matched_skills: string[]
  missing_skills: string[]
  experience_years?: number | null
  recruiter_score?: number | null
  semantic_similarity: number
  keyword_score: number
  hybrid_score: number
  final_score: number
  matching_reasons: string[]
  relevant_sections: RelevantSection[]
  project_highlights: string[]
  experience_highlights: string[]
}


export type CopilotRetrievalFilters = {
  candidate_ids?: number[]
  skills?: string[]
  category?: string
  location?: string
  min_experience_years?: number
  job_id?: number
}


export type CopilotChatResponse = {
  answer: string
  candidates: CandidateEvidence[]
  diagnostics: {
    retrieval_count: number
    model: string
    intent: string
    filters_applied: Record<string, unknown>
  }
}


export type CopilotStreamEvent =
  | {
      type: "metadata"
      candidates: CandidateEvidence[]
      diagnostics: CopilotChatResponse["diagnostics"]
    }
  | {
      type: "token"
      content: string
    }
  | {
      type: "done"
    }


export type JobDescription = {
  id: number
  title: string
  description: string
  extracted_skills: string[]
  inferred_category?: string | null
  inferred_seniority?: string | null
  created_by?: number | null
  created_at?: string | null
}


export type CandidateMatchResult = {
  match_result_id: number
  candidate_id: number
  candidate_name?: string | null
  candidate_email?: string | null
  category?: string | null
  experience_years?: number | null
  semantic_score: number
  skill_score: number
  experience_score: number
  recruiter_score: number
  final_score: number
  matched_skills: string[]
  missing_skills: string[]
  strengths: string[]
  ai_feedback: {
    strengths?: string[]
    missing_skills?: string[]
    fit_summary?: string
    interview_recommendation?: string
    recruiter_notes?: string
    hiring_recommendation?: string
  }
}


export type MatchRunResponse = {
  job_description: JobDescription
  matches: CandidateMatchResult[]
  email_sent: boolean
}


export type RecruiterEmailResponse = {
  sent: boolean
  message: string
}


export function getToken() {

  if (typeof window === "undefined") {

    return null
  }

  return localStorage.getItem("token")
}


async function readError(
  response: Response,
  fallback: string
) {

  try {

    const data = await response.clone().json() as {
      detail?: unknown
      message?: unknown
    }

    if (typeof data.detail === "string") {

      return data.detail
    }

    if (typeof data.message === "string") {

      return data.message
    }

    return fallback

  } catch {

    const errorText = await response.text()

    return errorText || fallback
  }
}


async function requestJson<T>(
  path: string,
  options: RequestInit,
  fallbackError: string
): Promise<T> {

  try {

    const response = await fetch(
      `${API_BASE_URL}${path}`,
      options
    )

    if (!response.ok) {

      throw new Error(
        await readError(
          response,
          fallbackError
        )
      )
    }

    return await response.json()

  } catch (error) {

    if (error instanceof TypeError) {

      const detail = error.message
        ? ` Browser error: ${error.message}`
        : ""

      throw new Error(
        `The request reached the local API proxy, but the browser could not read the response.${detail} Restart the frontend dev server and try again.`
      )
    }

    throw error
  }
}


function authHeaders(
  contentType?: string
) {

  const token = getToken()
  const headers: Record<string, string> = {}

  if (contentType) {

    headers["Content-Type"] = contentType
  }

  if (token) {

    headers.Authorization = `Bearer ${token}`
  }

  return headers
}


export async function loginUser(
  email: string,
  password: string
): Promise<LoginResponse> {

  const formData = new URLSearchParams()

  formData.append("username", email)
  formData.append("password", password)

  return requestJson<LoginResponse>(
    "/login",
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/x-www-form-urlencoded"
      },
      body: formData.toString()
    },
    "Login failed"
  )
}


export async function registerUser(
  full_name: string,
  email: string,
  password: string
): Promise<RegisterResponse> {

  return requestJson<RegisterResponse>(
    "/register",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        full_name,
        email,
        password
      })
    },
    "Registration failed"
  )
}


export async function rankCandidates(
  jobDescription: string,
  topK = 10
): Promise<RankingResponse> {

  return requestJson<RankingResponse>(
    "/rank-candidates",
    {
      method: "POST",
      headers: authHeaders("application/json"),
      body: JSON.stringify({
        job_description: jobDescription,
        top_k: topK
      })
    },
    "Ranking failed"
  )
}


export async function uploadResume(
  file: File
): Promise<UploadResumeResponse> {

  const formData = new FormData()

  formData.append("file", file)

  return requestJson<UploadResumeResponse>(
    "/upload-resume",
    {
      method: "POST",
      headers: authHeaders(),
      body: formData
    },
    "Upload failed"
  )
}


export async function submitCandidateApplication(
  name: string,
  email: string,
  jobId: number,
  file: File
): Promise<CandidateApplicationResponse> {

  const formData = new FormData()

  formData.append("name", name)
  formData.append("email", email)
  formData.append("job_id", String(jobId))
  formData.append("file", file)

  return requestJson<CandidateApplicationResponse>(
    "/candidate-apply",
    {
      method: "POST",
      body: formData
    },
    "Application submission failed"
  )
}


export async function getJobs(): Promise<JobPosting[]> {

  return requestJson<JobPosting[]>(
    "/jobs",
    {
      method: "GET"
    },
    "Failed to fetch jobs"
  )
}


export async function createJob(
  payload: JobPostingCreate
): Promise<JobPosting> {

  return requestJson<JobPosting>(
    "/jobs",
    {
      method: "POST",
      headers: authHeaders("application/json"),
      body: JSON.stringify(payload)
    },
    "Failed to post job"
  )
}


export async function getCandidate(
  candidateId: number
): Promise<CandidateDetails> {

  return requestJson<CandidateDetails>(
    `/candidate/${candidateId}`,
    {
      headers: authHeaders()
    },
    "Failed to fetch candidate"
  )
}


export function getCandidateResumeUrl(
  candidateId: number
) {

  return `${API_BASE_URL}/candidate-resume/${candidateId}`
}


export async function sendRecruiterCopilotMessage({
  message,
  history,
  topK = 6,
  filters = {}
}: {
  message: string
  history: CopilotChatMessage[]
  topK?: number
  filters?: CopilotRetrievalFilters
}): Promise<CopilotChatResponse> {

  return requestJson<CopilotChatResponse>(
    "/recruiter-copilot/chat",
    {
      method: "POST",
      headers: authHeaders("application/json"),
      body: JSON.stringify({
        message,
        history,
        top_k: topK,
        filters
      })
    },
    "Recruiter copilot failed"
  )
}


export async function streamRecruiterCopilotMessage({
  message,
  history,
  topK = 6,
  filters = {},
  onEvent
}: {
  message: string
  history: CopilotChatMessage[]
  topK?: number
  filters?: CopilotRetrievalFilters
  onEvent: (event: CopilotStreamEvent) => void
}) {

  const response = await fetch(
    `${API_BASE_URL}/recruiter-copilot/chat/stream`,
    {
      method: "POST",
      headers: authHeaders("application/json"),
      body: JSON.stringify({
        message,
        history,
        top_k: topK,
        filters,
        stream: true
      })
    }
  )

  if (!response.ok) {

    throw new Error(
      await readError(
        response,
        "Recruiter copilot stream failed"
      )
    )
  }

  if (!response.body) {

    const data = await sendRecruiterCopilotMessage({
      message,
      history,
      topK,
      filters
    })

    onEvent({
      type: "metadata",
      candidates: data.candidates,
      diagnostics: data.diagnostics
    })
    onEvent({
      type: "token",
      content: data.answer
    })
    onEvent({
      type: "done"
    })

    return
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ""

  while (true) {

    const {
      done,
      value
    } = await reader.read()

    if (done) {

      break
    }

    buffer += decoder.decode(
      value,
      {
        stream: true
      }
    )

    const events = buffer.split("\n\n")
    buffer = events.pop() || ""

    for (const rawEvent of events) {

      const dataLine = rawEvent
        .split("\n")
        .find((line) => line.startsWith("data:"))

      if (!dataLine) {

        continue
      }

      const payload = dataLine.replace(/^data:\s*/, "")

      try {

        onEvent(JSON.parse(payload) as CopilotStreamEvent)

      } catch {

        continue
      }
    }
  }
}


export async function createJobDescription(
  title: string,
  description: string
): Promise<JobDescription> {

  return requestJson<JobDescription>(
    "/jd-matching/job-descriptions",
    {
      method: "POST",
      headers: authHeaders("application/json"),
      body: JSON.stringify({
        title,
        description
      })
    },
    "Failed to create job description"
  )
}


export async function uploadJobDescription(
  title: string,
  file: File
): Promise<JobDescription> {

  const formData = new FormData()

  formData.append("title", title)
  formData.append("file", file)

  return requestJson<JobDescription>(
    "/jd-matching/job-descriptions/upload",
    {
      method: "POST",
      headers: authHeaders(),
      body: formData
    },
    "Failed to upload job description"
  )
}


export async function getJobDescriptions(): Promise<JobDescription[]> {

  return requestJson<JobDescription[]>(
    "/jd-matching/job-descriptions",
    {
      method: "GET",
      headers: authHeaders()
    },
    "Failed to fetch job descriptions"
  )
}


export async function matchJobDescription({
  jobDescriptionId,
  topK,
  generateAiFeedback,
  notifyRecruiter,
  recruiterEmail
}: {
  jobDescriptionId: number
  topK: number
  generateAiFeedback: boolean
  notifyRecruiter: boolean
  recruiterEmail?: string
}): Promise<MatchRunResponse> {

  return requestJson<MatchRunResponse>(
    "/jd-matching/match",
    {
      method: "POST",
      headers: authHeaders("application/json"),
      body: JSON.stringify({
        job_description_id: jobDescriptionId,
        top_k: topK,
        generate_ai_feedback: generateAiFeedback,
        notify_recruiter: notifyRecruiter,
        recruiter_email: recruiterEmail || undefined
      })
    },
    "JD matching failed"
  )
}


export async function shortlistCandidate({
  candidateId,
  jobTitle
}: {
  candidateId: number
  jobTitle?: string
}): Promise<ShortlistActionResponse> {

  return requestJson<ShortlistActionResponse>(
    `/candidates/${candidateId}/shortlist`,
    {
      method: "POST",
      headers: authHeaders("application/json"),
      body: JSON.stringify({
        job_title: jobTitle || undefined
      })
    },
    "Failed to shortlist candidate"
  )
}


export async function unshortlistCandidate({
  candidateId,
  feedback,
  jobTitle
}: {
  candidateId: number
  feedback: string
  jobTitle?: string
}): Promise<ShortlistActionResponse> {

  return requestJson<ShortlistActionResponse>(
    `/candidates/${candidateId}/unshortlist`,
    {
      method: "POST",
      headers: authHeaders("application/json"),
      body: JSON.stringify({
        feedback,
        job_title: jobTitle || undefined
      })
    },
    "Failed to unshortlist candidate"
  )
}


export async function suggestCandidateFeedback({
  candidateId,
  jobDescriptionId,
  jobTitle,
  jobDescription
}: {
  candidateId: number
  jobDescriptionId?: number
  jobTitle?: string
  jobDescription?: string
}): Promise<FeedbackSuggestionResponse> {

  return requestJson<FeedbackSuggestionResponse>(
    `/candidates/${candidateId}/feedback-suggestion`,
    {
      method: "POST",
      headers: authHeaders("application/json"),
      body: JSON.stringify({
        job_description_id: jobDescriptionId || undefined,
        job_title: jobTitle || undefined,
        job_description: jobDescription || undefined
      })
    },
    "Failed to suggest candidate feedback"
  )
}


export async function sendJDMatchEmail({
  jobDescriptionId,
  matchResultIds,
  recipientEmail,
  emailType
}: {
  jobDescriptionId: number
  matchResultIds: number[]
  recipientEmail: string
  emailType: "shortlist" | "interview" | "feedback"
}): Promise<RecruiterEmailResponse> {

  return requestJson<RecruiterEmailResponse>(
    "/jd-matching/email",
    {
      method: "POST",
      headers: authHeaders("application/json"),
      body: JSON.stringify({
        job_description_id: jobDescriptionId,
        match_result_ids: matchResultIds,
        recipient_email: recipientEmail,
        email_type: emailType
      })
    },
    "Failed to send JD match email"
  )
}
