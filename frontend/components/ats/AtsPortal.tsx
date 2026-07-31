"use client"

import {
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
  useSyncExternalStore
} from "react"

import {
  CandidateDetails,
  CandidateMatchResult,
  CandidateEvidence,
  CopilotChatMessage,
  CopilotChatResponse,
  createJobDescription,
  createJob,
  getCandidate,
  getCandidateResumeUrl,
  getJobDescriptions,
  getJobs,
  JobDescription,
  JobPosting,
  loginUser,
  matchJobDescription,
  rankCandidates,
  RankedCandidate,
  registerUser,
  sendJDMatchEmail,
  shortlistCandidate,
  streamRecruiterCopilotMessage,
  suggestCandidateFeedback,
  submitCandidateApplication,
  unshortlistCandidate,
  uploadJobDescription,
  uploadResume
} from "@/lib/api"

import {
  Button,
  C,
  Card,
  EmptyState,
  Eyebrow,
  FieldLabel,
  Input,
  Modal,
  normalizeScore,
  ScoreBadge,
  ScoreBar,
  scoreColor,
  Select,
  Stat,
  Tag,
  Textarea
} from "./ui"


const AUTH_TOKEN_CHANGED_EVENT = "auth-token-changed"


type Portal = "candidate" | "recruiter" | null


function getErrorMessage(
  error: unknown,
  fallback: string
) {

  return error instanceof Error
    ? error.message
    : fallback
}


function getAuthSnapshot() {

  if (typeof window === "undefined") {

    return false
  }

  return Boolean(
    window.localStorage.getItem("token")
  )
}


function getAuthServerSnapshot() {

  return false
}


function subscribeToAuth(
  onStoreChange: () => void
) {

  window.addEventListener(
    "storage",
    onStoreChange
  )

  window.addEventListener(
    AUTH_TOKEN_CHANGED_EVENT,
    onStoreChange
  )

  return () => {

    window.removeEventListener(
      "storage",
      onStoreChange
    )

    window.removeEventListener(
      AUTH_TOKEN_CHANGED_EVENT,
      onStoreChange
    )
  }
}


function setStoredToken(
  token: string | null
) {

  if (token) {

    localStorage.setItem(
      "token",
      token
    )

  } else {

    localStorage.removeItem(
      "token"
    )
  }

  window.dispatchEvent(
    new Event(AUTH_TOKEN_CHANGED_EVENT)
  )
}


function PortalCard({
  label,
  icon,
  desc,
  features,
  accent,
  onClick
}: {
  label: string
  icon: string
  desc: string
  features: string[]
  accent: string
  onClick: () => void
}) {

  return (
    <button
      className="w-[300px] rounded-[20px] border p-7 text-left transition duration-200 hover:-translate-y-0.5 hover:shadow-[0_8px_32px_rgba(108,99,255,0.10)]"
      style={{
        background: C.surface,
        borderColor: C.border
      }}
      onClick={onClick}
      onMouseEnter={(event) => {
        event.currentTarget.style.borderColor = `${accent}60`
        event.currentTarget.style.boxShadow =
          `0 0 0 1px ${accent}30, 0 8px 32px ${accent}10`
      }}
      onMouseLeave={(event) => {
        event.currentTarget.style.borderColor = C.border
        event.currentTarget.style.boxShadow = "none"
      }}
      type="button"
    >
      <div className="mb-3 text-4xl">
        {icon}
      </div>

      <div
        className="mb-2 font-mono text-[10px] uppercase tracking-[0.3em]"
        style={{
          color: accent
        }}
      >
        {label} Portal
      </div>

      <div
        className="mb-2 text-[22px] font-bold"
        style={{
          color: C.text
        }}
      >
        {label}
      </div>

      <p
        className="mb-5 text-[13px] leading-6"
        style={{
          color: C.muted
        }}
      >
        {desc}
      </p>

      <div className="flex flex-col gap-2">
        {features.map((feature) => (
          <div
            className="flex items-center gap-2 text-xs"
            key={feature}
            style={{
              color: C.text
            }}
          >
            <span
              className="font-bold"
              style={{
                color: accent
              }}
            >
              -
            </span>
            {feature}
          </div>
        ))}
      </div>

      <div
        className="mt-6 inline-flex items-center gap-1.5 rounded-lg border px-4 py-2 text-[13px] font-semibold"
        style={{
          background: `${accent}18`,
          borderColor: `${accent}40`,
          color: accent
        }}
      >
        Enter Portal -
      </div>
    </button>
  )
}


function Landing({
  onSelect
}: {
  onSelect: (portal: Portal) => void
}) {

  return (
    <main
      className="flex min-h-screen flex-col items-center justify-center px-6 py-10"
      style={{
        background: C.bg
      }}
    >
      <div className="mb-14 text-center">
        <div
          className="mb-4 font-mono text-[10px] uppercase tracking-[0.4em]"
          style={{
            color: C.accent
          }}
        >
          AI-Powered ATS
        </div>

        <h1
          className="m-0 text-[42px] font-extrabold leading-[1.12] sm:text-[52px]"
          style={{
            background: `linear-gradient(135deg, ${C.text} 50%, ${C.accent})`,
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent"
          }}
        >
          Resume Screening
          <br />
          Platform
        </h1>

        <p
          className="mx-auto mt-4 max-w-[460px] text-[15px] leading-6"
          style={{
            color: C.muted
          }}
        >
          AI-powered matching between candidates and job descriptions. Select
          your portal to continue.
        </p>
      </div>

      <div className="flex max-w-[720px] flex-wrap justify-center gap-5">
        <PortalCard
          accent={C.green}
          desc="Browse open roles and apply by uploading your resume into the real ATS pipeline."
          features={[
            "Browse job listings",
            "Apply with resume upload"
          ]}
          icon="👤"
          label="Candidate"
          onClick={() => onSelect("candidate")}
        />

        <PortalCard
          accent={C.accent}
          desc="Upload resumes, rank candidates with pgvector scoring, inspect profiles, and download files."
          features={[
            "Protected recruiter login",
            "AI-ranked candidate list",
            "Analytics dashboard"
          ]}
          icon="🎯"
          label="Recruiter"
          onClick={() => onSelect("recruiter")}
        />
      </div>

      <p
        className="mt-10 font-mono text-[11px] uppercase tracking-[0.1em]"
        style={{
          color: C.muted
        }}
      >
        JWT Auth · Celery Queue · FastAPI Backend
      </p>
    </main>
  )
}


function Shell({
  role,
  onBack,
  onLogout,
  children,
  activeTab,
  setTab,
  tabs,
  isAuthenticated
}: {
  role: "candidate" | "recruiter"
  onBack: () => void
  onLogout?: () => void
  children: React.ReactNode
  activeTab: string
  setTab: (tab: string) => void
  tabs: Array<{
    id: string
    icon: string
    label: string
  }>
  isAuthenticated?: boolean
}) {

  const accent = role === "candidate"
    ? C.green
    : C.accent

  return (
    <div
      className="min-h-screen md:flex"
      style={{
        background: C.bg
      }}
    >
      <nav
        className="flex border-b md:min-h-screen md:w-[220px] md:min-w-[220px] md:flex-col md:border-b-0 md:border-r"
        style={{
          background: C.surface,
          borderColor: C.border
        }}
      >
        <div
          className="hidden border-b px-5 pb-6 pt-6 md:block"
          style={{
            borderColor: C.border
          }}
        >
          <div
            className="mb-1 font-mono text-[9px] uppercase tracking-[0.3em]"
            style={{
              color: accent
            }}
          >
            {role} Portal
          </div>

          <div
            className="text-[15px] font-extrabold leading-tight"
            style={{
              color: C.text
            }}
          >
            Resume
            <br />
            Screening
          </div>
        </div>

        <div className="flex flex-1 overflow-x-auto px-2 py-3 md:block md:px-0 md:py-4">
          {tabs.map((tab) => (
            <button
              className="flex shrink-0 items-center gap-2.5 border-l-0 border-t-2 px-4 py-2.5 text-left text-[13px] font-semibold transition md:w-full md:border-l-[3px] md:border-t-0 md:px-5"
              key={tab.id}
              onClick={() => setTab(tab.id)}
              style={{
                background:
                  activeTab === tab.id
                    ? `${accent}14`
                    : "transparent",
                borderColor:
                  activeTab === tab.id
                    ? accent
                    : "transparent",
                color:
                  activeTab === tab.id
                    ? C.text
                    : C.muted
              }}
              type="button"
            >
              <span className="text-[15px]">
                {tab.icon}
              </span>
              {tab.label}
            </button>
          ))}
        </div>

        <div className="hidden px-5 pb-6 md:block">
          {isAuthenticated && onLogout ? (
            <button
              className="mb-2 w-full rounded-lg border px-3.5 py-2 font-mono text-[11px]"
              onClick={onLogout}
              style={{
                borderColor: C.border,
                color: C.muted
              }}
              type="button"
            >
              Logout
            </button>
          ) : null}

          <button
            className="w-full rounded-lg border px-3.5 py-2 font-mono text-[11px]"
            onClick={onBack}
            style={{
              borderColor: C.border,
              color: C.muted
            }}
            type="button"
          >
            Switch Portal
          </button>
        </div>
      </nav>

      <main
        className={`flex-1 px-5 py-7 sm:px-8 md:px-10 md:py-9 ${
          activeTab === "copilot"
            ? "h-[calc(100vh-58px)] overflow-hidden md:h-screen"
            : "overflow-y-auto"
        }`}
      >
        {children}
      </main>
    </div>
  )
}


function Alert({
  type = "error",
  children
}: {
  type?: "error" | "success" | "info"
  children: React.ReactNode
}) {

  const color = type === "success"
    ? C.green
    : type === "info"
      ? C.accent
      : C.red

  return (
    <div
      className="rounded-xl border px-4 py-3 text-sm leading-6"
      style={{
        background: `${color}12`,
        borderColor: `${color}40`,
        color
      }}
    >
      {children}
    </div>
  )
}


function AuthPanel({
  title = "Recruiter Login",
  caption = "Use your existing ATS account to continue.",
  onAuthenticated
}: {
  title?: string
  caption?: string
  onAuthenticated?: () => void
}) {

  const [
    mode,
    setMode
  ] = useState<"login" | "register">("login")
  const [
    fullName,
    setFullName
  ] = useState("")
  const [
    email,
    setEmail
  ] = useState("")
  const [
    password,
    setPassword
  ] = useState("")
  const [
    loading,
    setLoading
  ] = useState(false)
  const [
    error,
    setError
  ] = useState("")
  const [
    notice,
    setNotice
  ] = useState("")

  async function submit() {

    setError("")
    setNotice("")
    setLoading(true)

    try {

      if (mode === "register") {

        await registerUser(
          fullName,
          email,
          password
        )

        setNotice(
          "Account created. Sign in with the same credentials."
        )
        setMode("login")

        return
      }

      const data = await loginUser(
        email,
        password
      )

      if (!data.access_token) {

        throw new Error("Login succeeded but no token was returned.")
      }

      setStoredToken(
        data.access_token
      )

      onAuthenticated?.()

    } catch (err) {

      setError(
        getErrorMessage(
          err,
          "Authentication failed"
        )
      )

    } finally {

      setLoading(false)
    }
  }

  return (
    <Card className="mx-auto w-full max-w-md">
      <Eyebrow>
        JWT Protected
      </Eyebrow>

      <h2
        className="mb-1 text-[26px] font-extrabold"
        style={{
          color: C.text
        }}
      >
        {title}
      </h2>

      <p
        className="mb-6 text-[13px] leading-6"
        style={{
          color: C.muted
        }}
      >
        {caption}
      </p>

      <div className="mb-5 grid grid-cols-2 gap-2">
        {(["login", "register"] as const).map((item) => (
          <button
            className="rounded-lg border px-3 py-2 text-sm font-semibold"
            key={item}
            onClick={() => {
              setMode(item)
              setError("")
              setNotice("")
            }}
            style={{
              background:
                mode === item
                  ? C.accentDim
                  : C.surface2,
              borderColor:
                mode === item
                  ? C.accentBorder
                  : C.border,
              color:
                mode === item
                  ? C.text
                  : C.muted
            }}
            type="button"
          >
            {item === "login"
              ? "Login"
              : "Register"}
          </button>
        ))}
      </div>

      <div className="flex flex-col gap-4">
        {mode === "register" ? (
          <div>
            <FieldLabel>
              Full name
            </FieldLabel>
            <Input
              onChange={(event) => setFullName(event.target.value)}
              placeholder="Recruiter name"
              value={fullName}
            />
          </div>
        ) : null}

        <div>
          <FieldLabel>
            Email
          </FieldLabel>
          <Input
            onChange={(event) => setEmail(event.target.value)}
            placeholder="you@company.com"
            type="email"
            value={email}
          />
        </div>

        <div>
          <FieldLabel>
            Password
          </FieldLabel>
          <Input
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Password"
            type="password"
            value={password}
          />
        </div>

        {error ? (
          <Alert>
            {error}
          </Alert>
        ) : null}

        {notice ? (
          <Alert type="success">
            {notice}
          </Alert>
        ) : null}

        <Button
          disabled={
            loading
            || !email
            || !password
            || (mode === "register" && !fullName)
          }
          onClick={submit}
          size="lg"
        >
          {loading
            ? "Please wait..."
            : mode === "login"
              ? "Login"
              : "Create Account"}
        </Button>
      </div>
    </Card>
  )
}


function CandidatePortal({
  onBack
}: {
  onBack: () => void
}) {

  const [
    tab,
    setTab
  ] = useState("jobs")
  const [
    selectedJob,
    setSelectedJob
  ] = useState<JobPosting | null>(null)
  const [
    jobs,
    setJobs
  ] = useState<JobPosting[]>([])
  const [
    jobsLoading,
    setJobsLoading
  ] = useState(true)
  const [
    jobsError,
    setJobsError
  ] = useState("")

  async function loadJobs() {

    setJobsLoading(true)
    setJobsError("")

    try {

      setJobs(
        await getJobs()
      )

    } catch (err) {

      setJobsError(
        getErrorMessage(
          err,
          "Failed to load job postings"
        )
      )

    } finally {

      setJobsLoading(false)
    }
  }

  useEffect(() => {
    void loadJobs()
  }, [])

  const tabs = [
    {
      id: "jobs",
      icon: "💼",
      label: "Browse Jobs"
    },
    {
      id: "apply",
      icon: "📄",
      label: "Apply"
    }
  ]

  return (
    <Shell
      activeTab={tab}
      isAuthenticated={false}
      onBack={onBack}
      role="candidate"
      setTab={setTab}
      tabs={tabs}
    >
      {tab === "jobs" ? (
        <CandidateJobs
          error={jobsError}
          jobs={jobs}
          loading={jobsLoading}
          onApply={(job) => {
            setSelectedJob(job)
            setTab("apply")
          }}
          onRefresh={loadJobs}
        />
      ) : null}

      {tab === "apply" ? (
        <CandidateApply
          jobs={jobs}
          key={selectedJob?.id || "apply"}
          selectedJob={selectedJob}
        />
      ) : null}
    </Shell>
  )
}


function CandidateJobs({
  jobs,
  loading,
  error,
  onApply,
  onRefresh
}: {
  jobs: JobPosting[]
  loading: boolean
  error: string
  onApply: (job: JobPosting) => void
  onRefresh: () => void
}) {

  const [
    selected,
    setSelected
  ] = useState<JobPosting | null>(null)
  const [
    search,
    setSearch
  ] = useState("")

  const filtered = jobs.filter((job) => {

    const haystack = [
      job.title,
      job.department || "",
      job.location || "",
      ...(job.skills || [])
    ].join(" ").toLowerCase()

    return haystack.includes(
      search.toLowerCase()
    )
  })

  return (
    <div>
      <Eyebrow color={C.green}>
        Candidate Portal
      </Eyebrow>

      <h2
        className="mb-1.5 text-[26px] font-extrabold"
        style={{
          color: C.text
        }}
      >
        Open Positions
      </h2>

      <p
        className="mb-6 text-[13px]"
        style={{
          color: C.muted
        }}
      >
        {jobs.length} live job postings available
      </p>

      <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-center">
        <Input
          className="max-w-sm"
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Search roles, departments, skills..."
          value={search}
        />
        <Button
          onClick={onRefresh}
          variant="ghost"
        >
          Refresh
        </Button>
      </div>

      {error ? (
        <div className="mb-5">
          <Alert>
            {error}
          </Alert>
        </div>
      ) : null}

      {loading ? (
        <EmptyState title="Loading jobs">
          Fetching current postings from the recruiter portal.
        </EmptyState>
      ) : filtered.length === 0 ? (
        <EmptyState title="No job postings yet">
          Recruiters can post jobs from the recruiter portal. They will appear
          here automatically.
        </EmptyState>
      ) : (
        <div className="flex flex-col gap-3">
        {filtered.map((job) => (
          <Card
            hover
            key={job.id}
            onClick={() => setSelected(job)}
          >
            <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
              <div>
                <div
                  className="mb-1 text-base font-bold"
                  style={{
                    color: C.text
                  }}
                >
                  {job.title}
                </div>

                <div
                  className="mb-3 flex flex-wrap gap-x-3 gap-y-1 text-xs"
                  style={{
                    color: C.muted
                  }}
                >
                  <span>{job.department || "General"}</span>
                  <span>{job.location || "Remote"}</span>
                  <span>{job.created_at ? "Posted" : "Open now"}</span>
                </div>

                <div className="flex flex-wrap gap-1.5">
                  {(job.skills || []).slice(0, 4).map((skill) => (
                    <Tag key={skill}>
                      {skill}
                    </Tag>
                  ))}

                  {(job.skills || []).length > 4 ? (
                    <Tag color={C.muted}>
                      +{(job.skills || []).length - 4}
                    </Tag>
                  ) : null}
                </div>
              </div>

              <div className="flex shrink-0 items-center gap-2 lg:flex-col lg:items-end">
                <Tag color={C.green}>
                  {job.type || "Full-time"}
                </Tag>

                <Button
                  onClick={(event) => {
                    event.stopPropagation()
                    onApply(job)
                  }}
                  size="sm"
                  variant="success"
                >
                  Apply
                </Button>
              </div>
            </div>
          </Card>
        ))}
        </div>
      )}

      <Modal
        onClose={() => setSelected(null)}
        open={Boolean(selected)}
        title={selected?.title || "Role details"}
        width={600}
      >
        {selected ? (
          <div>
            <div className="mb-4 flex flex-wrap gap-3">
              <Tag color={C.green}>
                {selected.type || "Full-time"}
              </Tag>
              <Tag color={C.muted}>
                {selected.department || "General"}
              </Tag>
              <Tag color={C.muted}>
                {selected.location || "Remote"}
              </Tag>
            </div>

            <p
              className="mb-5 text-[13px] leading-7"
              style={{
                color: C.muted
              }}
            >
              {selected.description}
            </p>

            <div className="mb-5">
              <FieldLabel>
                Required Skills
              </FieldLabel>
              <div className="flex flex-wrap gap-1.5">
                {(selected.skills || []).map((skill) => (
                  <Tag key={skill}>
                    {skill}
                  </Tag>
                ))}
              </div>
            </div>

            <Button
              onClick={() => onApply(selected)}
              variant="success"
            >
              Apply for this role
            </Button>
          </div>
        ) : null}
      </Modal>
    </div>
  )
}


function CandidateApply({
  jobs,
  selectedJob
}: {
  jobs: JobPosting[]
  selectedJob: JobPosting | null
}) {

  const [
    candidateName,
    setCandidateName
  ] = useState("")
  const [
    candidateEmail,
    setCandidateEmail
  ] = useState("")
  const [
    roleId,
    setRoleId
  ] = useState(selectedJob ? String(selectedJob.id) : "")
  const [
    file,
    setFile
  ] = useState<File | null>(null)
  const [
    loading,
    setLoading
  ] = useState(false)
  const [
    error,
    setError
  ] = useState("")
  const [
    result,
    setResult
  ] = useState("")
  const fileRef = useRef<HTMLInputElement>(null)

  async function submit() {

    if (!candidateName.trim() || !candidateEmail.trim() || !file) {

      return
    }

    setLoading(true)
    setError("")
    setResult("")

    try {

      const response = await submitCandidateApplication(
        candidateName,
        candidateEmail,
        Number(roleId),
        file
      )

      setResult(
        `${response.message}: ${response.candidate_name} (${response.file_name})`
      )

    } catch (err) {

      setError(
        getErrorMessage(
          err,
          "Resume upload failed"
        )
      )

    } finally {

      setLoading(false)
    }
  }

  return (
    <div className="max-w-xl">
      <Eyebrow color={C.green}>
        Candidate Portal
      </Eyebrow>

      <h2
        className="mb-1.5 text-[26px] font-extrabold"
        style={{
          color: C.text
        }}
      >
        Apply for a Role
      </h2>

      <p
        className="mb-7 text-[13px]"
        style={{
          color: C.muted
        }}
      >
        Enter your contact details and upload your PDF resume. Processing
        happens asynchronously in Celery.
      </p>

      <div className="flex flex-col gap-5">
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <FieldLabel>
              Name
            </FieldLabel>
            <Input
              onChange={(event) => setCandidateName(event.target.value)}
              placeholder="Your full name"
              value={candidateName}
            />
          </div>

          <div>
            <FieldLabel>
              Email
            </FieldLabel>
            <Input
              onChange={(event) => setCandidateEmail(event.target.value)}
              placeholder="you@example.com"
              type="email"
              value={candidateEmail}
            />
          </div>
        </div>

        <div>
          <FieldLabel>
            Select Position
          </FieldLabel>
          <Select
            onChange={(event) => setRoleId(event.target.value)}
            value={roleId}
          >
            <option value="">
              Choose a role...
            </option>
            {jobs.map((role) => (
              <option
                key={role.id}
                value={role.id}
              >
                {role.title} - {role.department || "General"}
              </option>
            ))}
          </Select>
        </div>

        <div>
          <FieldLabel>
            Upload Resume (PDF)
          </FieldLabel>
          <button
            className="w-full rounded-xl border-2 border-dashed px-5 py-7 text-center transition"
            onClick={() => fileRef.current?.click()}
            style={{
              background: file
                ? C.greenDim
                : "transparent",
              borderColor: file
                ? `${C.green}60`
                : C.border
            }}
            type="button"
          >
            <div className="mb-2 text-3xl">
              {file
                ? "📄"
                : "↑"}
            </div>

            <div
              className="text-[13px] font-semibold"
              style={{
                color: file
                  ? C.green
                  : C.muted
              }}
            >
              {file
                ? file.name
                : "Click to upload PDF"}
            </div>

            {!file ? (
              <div
                className="mt-1 text-[11px]"
                style={{
                  color: C.muted
                }}
              >
                PDF files only
              </div>
            ) : null}
          </button>

          <input
            accept=".pdf,application/pdf"
            className="hidden"
            onChange={(event) => {
              const selectedFile = event.target.files?.[0]

              if (selectedFile) {

                setFile(selectedFile)
              }
            }}
            ref={fileRef}
            type="file"
          />
        </div>

        {error ? (
          <Alert>
            {error}
          </Alert>
        ) : null}

        {result ? (
          <Alert type="success">
            {result}
          </Alert>
        ) : null}

        <Button
          disabled={
            !candidateName.trim()
            || !candidateEmail.trim()
            || !roleId
            || !file
            || loading
          }
          onClick={submit}
          size="lg"
          variant="success"
        >
          {loading
            ? "Queueing..."
            : "Submit Application"}
        </Button>
      </div>
    </div>
  )
}


function RecruiterPortal({
  onBack,
  isAuthenticated,
  onLogout
}: {
  onBack: () => void
  isAuthenticated: boolean
  onLogout: () => void
}) {

  const [
    tab,
    setTab
  ] = useState("copilot")
  const [
    candidates,
    setCandidates
  ] = useState<RankedCandidate[]>([])

  const tabs = [
    {
      id: "copilot",
      icon: "AI",
      label: "AI Copilot"
    },
    {
      id: "rank",
      icon: "🏆",
      label: "Rank Candidates"
    },
    {
      id: "jobs",
      icon: "📋",
      label: "Job Postings"
    },
    {
      id: "upload",
      icon: "📥",
      label: "Resume Intake"
    },
    {
      id: "analytics",
      icon: "📊",
      label: "Analytics"
    }
  ]

  if (!isAuthenticated) {

    return (
      <div
        className="min-h-screen px-5 py-10"
        style={{
          background: C.bg
        }}
      >
        <div className="mx-auto mb-6 flex max-w-md justify-between">
          <Button
            onClick={onBack}
            variant="ghost"
          >
            Switch Portal
          </Button>
        </div>

        <AuthPanel
          onAuthenticated={() => setTab("copilot")}
        />
      </div>
    )
  }

  return (
    <Shell
      activeTab={tab}
      isAuthenticated={isAuthenticated}
      onBack={onBack}
      onLogout={onLogout}
      role="recruiter"
      setTab={setTab}
      tabs={tabs}
    >
      {tab === "copilot" ? (
        <RecruiterCopilot />
      ) : null}

      {tab === "rank" ? (
        <RecruiterRank
          candidates={candidates}
          setCandidates={setCandidates}
        />
      ) : null}

      {tab === "jobs" ? (
        <RecruiterJobs />
      ) : null}

      {tab === "upload" ? (
        <RecruiterUpload />
      ) : null}

      {tab === "analytics" ? (
        <RecruiterAnalytics candidates={candidates} />
      ) : null}
    </Shell>
  )
}


type CopilotTurn = {
  id: string
  role: "user" | "assistant"
  content: string
  candidates?: CandidateEvidence[]
  diagnostics?: CopilotChatResponse["diagnostics"]
}


function MarkdownText({
  content
}: {
  content: string
}) {

  function inline(
    text: string
  ) {

    return text.split(/(\*\*[^*]+\*\*)/g).map((part, index) => {

      if (part.startsWith("**") && part.endsWith("**")) {

        return (
          <strong
            key={index}
            style={{
              color: C.text
            }}
          >
            {part.slice(2, -2)}
          </strong>
        )
      }

      return (
        <span key={index}>
          {part}
        </span>
      )
    })
  }

  return (
    <div className="flex flex-col gap-2">
      {content.split("\n").map((line, index) => {

        const trimmed = line.trim()

        if (!trimmed) {

          return (
            <div
              className="h-1"
              key={index}
            />
          )
        }

        if (trimmed.startsWith("###")) {

          return (
            <div
              className="pt-2 text-[15px] font-bold"
              key={index}
              style={{
                color: C.text
              }}
            >
              {inline(trimmed.replace(/^#+\s*/, ""))}
            </div>
          )
        }

        if (/^\d+\.\s+/.test(trimmed)) {

          return (
            <div
              className="pl-1 text-[13px] leading-6"
              key={index}
              style={{
                color: C.muted
              }}
            >
              {inline(trimmed)}
            </div>
          )
        }

        if (trimmed.startsWith("-")) {

          return (
            <div
              className="flex gap-2 text-[13px] leading-6"
              key={index}
              style={{
                color: C.muted
              }}
            >
              <span style={{ color: C.accent }}>
                -
              </span>
              <span>
                {inline(trimmed.replace(/^-\s*/, ""))}
              </span>
            </div>
          )
        }

        return (
          <p
            className="text-[13px] leading-6"
            key={index}
            style={{
              color: C.muted
            }}
          >
            {inline(trimmed)}
          </p>
        )
      })}
    </div>
  )
}


function CandidateEvidenceCard({
  candidate
}: {
  candidate: CandidateEvidence
}) {

  const score = normalizeScore(
    candidate.final_score
  )
  const [
    selectedSection,
    setSelectedSection
  ] = useState<{
    name: string
    text: string
  } | null>(null)

  function cleanPreview(
    text: string
  ) {

    const compact = text
      .replace(/\s+/g, " ")
      .replace(/^\.\.\./, "")
      .trim()

    if (compact.length <= 190) {

      return compact
    }

    return `${compact.slice(0, 190).trim()}...`
  }

  return (
    <div
      className="rounded-xl border px-4 py-3"
      style={{
        background: C.surface2,
        borderColor: C.border
      }}
    >
      <div className="mb-3 flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div
            className="truncate text-sm font-bold"
            style={{
              color: C.text
            }}
          >
            {candidate.candidate_name || "Unknown Candidate"}
          </div>

          <div
            className="mt-1 text-[11px]"
            style={{
              color: C.muted
            }}
          >
            Candidate #{candidate.candidate_id} · {candidate.category || "Uploaded"} ·{" "}
            {candidate.experience_years || 0} yrs exp
          </div>
        </div>

        <ScoreBadge score={score} />
      </div>

      <div className="mb-3 grid gap-2 sm:grid-cols-3">
        <div>
          <div
            className="mb-1 font-mono text-[10px] uppercase tracking-[0.1em]"
            style={{
              color: C.muted
            }}
          >
            Semantic
          </div>
          <ScoreBar value={candidate.semantic_similarity} />
        </div>
        <div>
          <div
            className="mb-1 font-mono text-[10px] uppercase tracking-[0.1em]"
            style={{
              color: C.muted
            }}
          >
            Keyword
          </div>
          <ScoreBar
            color={C.amber}
            value={candidate.keyword_score}
          />
        </div>
        <div>
          <div
            className="mb-1 font-mono text-[10px] uppercase tracking-[0.1em]"
            style={{
              color: C.muted
            }}
          >
            Hybrid
          </div>
          <ScoreBar
            color={C.green}
            value={candidate.hybrid_score}
          />
        </div>
      </div>

      {candidate.matched_skills.length ? (
        <div className="mb-3">
          <FieldLabel>
            Matched Skills
          </FieldLabel>
          <div className="flex flex-wrap gap-1.5">
            {candidate.matched_skills.slice(0, 8).map((skill) => (
              <Tag
                color={C.green}
                key={skill}
              >
                {skill}
              </Tag>
            ))}
          </div>
        </div>
      ) : null}

      {candidate.missing_skills.length ? (
        <div className="mb-3">
          <FieldLabel>
            Missing or Unconfirmed
          </FieldLabel>
          <div className="flex flex-wrap gap-1.5">
            {candidate.missing_skills.slice(0, 8).map((skill) => (
              <Tag
                color={C.amber}
                key={skill}
              >
                {skill}
              </Tag>
            ))}
          </div>
        </div>
      ) : null}

      <div className="mb-3">
        <FieldLabel>
          Why Matched
        </FieldLabel>
        <div className="flex flex-col gap-1.5">
          {candidate.matching_reasons.slice(0, 4).map((reason) => (
            <div
              className="text-xs leading-5"
              key={reason}
              style={{
                color: C.muted
              }}
            >
              - {reason}
            </div>
          ))}
        </div>
      </div>

      {candidate.relevant_sections.length ? (
        <div>
          <FieldLabel>
            Relevant Sections
          </FieldLabel>
          <div className="flex flex-col gap-2">
            {candidate.relevant_sections.slice(0, 3).map((section) => {

              const fullText = section.full_text || section.snippet

              return (
              <button
                className="group rounded-lg border px-3 py-2 text-left transition hover:-translate-y-0.5 hover:shadow-[0_0_0_1px_rgba(108,99,255,0.35),0_10px_26px_rgba(108,99,255,0.12)]"
                key={`${candidate.candidate_id}-${section.name}-${section.snippet}`}
                onClick={() => setSelectedSection({
                  name: section.name,
                  text: fullText
                })}
                style={{
                  background: "#0a0a10",
                  borderColor: C.border
                }}
                type="button"
              >
                <div className="mb-1 flex items-center justify-between gap-3">
                  <span
                    className="text-[11px] font-bold"
                    style={{
                      color: C.text
                    }}
                  >
                    {section.name}
                  </span>
                  <span
                    className="text-[10px] font-semibold opacity-0 transition group-hover:opacity-100"
                    style={{
                      color: C.accent
                    }}
                  >
                    Open
                  </span>
                </div>
                <div
                  className="text-[11px] leading-5"
                  style={{
                    color: C.muted
                  }}
                >
                  {cleanPreview(fullText)}
                </div>
              </button>
              )
            })}
          </div>
        </div>
      ) : null}

      <div className="mt-3">
        <button
          className="rounded-[10px] border px-3.5 py-1.5 text-xs font-semibold transition hover:-translate-y-0.5 hover:shadow-[0_0_0_1px_rgba(45,212,160,0.65),0_0_24px_rgba(45,212,160,0.22)]"
          onClick={() => window.open(
            getCandidateResumeUrl(candidate.candidate_id),
            "_blank"
          )}
          style={{
            background: C.greenDim,
            borderColor: `${C.green}45`,
            color: C.green
          }}
          type="button"
        >
          View Resume
        </button>
      </div>

      <Modal
        onClose={() => setSelectedSection(null)}
        open={Boolean(selectedSection)}
        title={selectedSection?.name || "Resume Section"}
        width={760}
      >
        <div
          className="ats-stable-scroll max-h-[62vh] overflow-y-auto whitespace-pre-wrap rounded-xl border px-4 py-3 text-[13px] leading-7"
          style={{
            background: "#0a0a10",
            borderColor: C.border,
            color: C.muted
          }}
        >
          {selectedSection?.text || "No section text available."}
        </div>
      </Modal>
    </div>
  )
}


function RecruiterCopilot() {

  const examples = [
    "Find backend developers with FastAPI and Docker",
    "Who has the strongest NLP background?",
    "Summarize the top 3 candidates",
    "Who lacks Kubernetes experience?",
    "Explain why the strongest candidate should be shortlisted"
  ]
  const [
    input,
    setInput
  ] = useState("")
  const [
    topK,
    setTopK
  ] = useState(6)
  const [
    skillFilter,
    setSkillFilter
  ] = useState("")
  const [
    categoryFilter,
    setCategoryFilter
  ] = useState("")
  const [
    minExperience,
    setMinExperience
  ] = useState("")
  const [
    turns,
    setTurns
  ] = useState<CopilotTurn[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Ask me to search, compare, summarize, explain rankings, analyze missing skills, or match candidates to a JD. I will answer from ATS evidence and show the candidate cards I used."
    }
  ])
  const [
    loading,
    setLoading
  ] = useState(false)
  const [
    error,
    setError
  ] = useState("")
  const chatScrollRef = useRef<HTMLDivElement>(null)
  const shouldStickToBottomRef = useRef(true)
  const scrollFrameRef = useRef<number | null>(null)
  const activeAssistantIdRef = useRef<string | null>(null)
  const answerStartedRef = useRef(false)
  const didScrollToAnswerTopRef = useRef(false)

  function isNearChatBottom() {

    const element = chatScrollRef.current

    if (!element) {

      return true
    }

    return (
      element.scrollHeight
      - element.scrollTop
      - element.clientHeight
    ) < 140
  }

  function scrollChatToBottom() {

    const element = chatScrollRef.current

    if (!element) {

      return
    }

    element.scrollTo({
      top: element.scrollHeight,
      behavior: "auto"
    })
  }

  function scrollTurnToTop(
    turnId: string
  ) {

    const scrollElement = chatScrollRef.current

    if (!scrollElement) {

      return
    }

    const turnElement = scrollElement.querySelector<HTMLElement>(
      `[data-turn-id="${turnId}"]`
    )

    if (!turnElement) {

      return
    }

    scrollElement.scrollTo({
      top: Math.max(
        turnElement.offsetTop - 12,
        0
      ),
      behavior: "auto"
    })
  }

  useLayoutEffect(() => {
    const activeAssistantId = activeAssistantIdRef.current

    if (
      loading
      && activeAssistantId
      && !answerStartedRef.current
    ) {

      if (!didScrollToAnswerTopRef.current) {

        if (scrollFrameRef.current !== null) {

          cancelAnimationFrame(
            scrollFrameRef.current
          )
        }

        scrollFrameRef.current = requestAnimationFrame(() => {
          scrollTurnToTop(activeAssistantId)
          didScrollToAnswerTopRef.current = true
          scrollFrameRef.current = null
        })
      }

      return
    }

    if (!shouldStickToBottomRef.current && !loading) {

      return
    }

    if (scrollFrameRef.current !== null) {

      cancelAnimationFrame(
        scrollFrameRef.current
      )
    }

    scrollFrameRef.current = requestAnimationFrame(() => {
      scrollChatToBottom()
      scrollFrameRef.current = null
    })

    return () => {
      if (scrollFrameRef.current !== null) {

        cancelAnimationFrame(
          scrollFrameRef.current
        )

        scrollFrameRef.current = null
      }
    }
  }, [turns, loading])

  function historyForApi(
    nextTurns: CopilotTurn[]
  ): CopilotChatMessage[] {

    return nextTurns
      .filter((turn) => turn.id !== "welcome")
      .slice(-8)
      .map((turn) => ({
        role: turn.role,
        content: turn.content
      }))
  }

  async function submit(
    override?: string
  ) {

    const message = (override || input).trim()

    if (!message || loading) {

      return
    }

    setInput("")
    setError("")
    setLoading(true)
    shouldStickToBottomRef.current = true

    const userTurn: CopilotTurn = {
      id: `user-${Date.now()}`,
      role: "user",
      content: message
    }
    const assistantId = `assistant-${Date.now()}`
    activeAssistantIdRef.current = assistantId
    answerStartedRef.current = false
    didScrollToAnswerTopRef.current = false

    const assistantTurn: CopilotTurn = {
      id: assistantId,
      role: "assistant",
      content: "",
      candidates: []
    }
    const nextTurns = [
      ...turns,
      userTurn,
      assistantTurn
    ]

    setTurns(nextTurns)

    const filters = {
      skills: skillFilter
        .split(",")
        .map((skill) => skill.trim())
        .filter(Boolean),
      category: categoryFilter.trim() || undefined,
      min_experience_years: minExperience
        ? Number(minExperience)
        : undefined
    }

    try {

      await streamRecruiterCopilotMessage({
        message,
        history: historyForApi(nextTurns),
        topK,
        filters,
        onEvent: (event) => {
          setTurns((current) => current.map((turn) => {

            if (turn.id !== assistantId) {

              return turn
            }

            if (event.type === "metadata") {

              return {
                ...turn,
                candidates: event.candidates,
                diagnostics: event.diagnostics
              }
            }

            if (event.type === "token") {

              answerStartedRef.current = true
              shouldStickToBottomRef.current = true

              return {
                ...turn,
                content: `${turn.content}${event.content}`
              }
            }

            return turn
          }))
        }
      })

    } catch (err) {

      setError(
        getErrorMessage(
          err,
          "Copilot request failed"
        )
      )
      setTurns((current) => current.map((turn) => (
        turn.id === assistantId
          ? {
              ...turn,
              content:
                "I could not complete the copilot request. Check the backend, OpenRouter API key, and database connection, then try again."
            }
          : turn
      )))

    } finally {

      setLoading(false)
      activeAssistantIdRef.current = null
      answerStartedRef.current = false
      didScrollToAnswerTopRef.current = false
    }
  }

  return (
    <div className="grid h-full min-h-0 gap-5 xl:grid-cols-[minmax(0,1fr)_320px]">
      <section className="flex min-h-0 flex-col overflow-hidden rounded-[14px] border"
        style={{
          background: C.surface,
          borderColor: C.border
        }}
      >
        <div
          className="border-b px-5 py-4"
          style={{
            borderColor: C.border
          }}
        >
          <Eyebrow>
            Recruiter Portal
          </Eyebrow>
          <h2
            className="text-[24px] font-extrabold"
            style={{
              color: C.text
            }}
          >
            AI Recruiter Copilot
          </h2>
          <p
            className="mt-1 text-[13px]"
            style={{
              color: C.muted
            }}
          >
            RAG over candidate profiles, resume sections, embeddings, skills,
            projects, experience, education, and recruiter scores.
          </p>
        </div>

        <div
          className="ats-stable-scroll min-h-0 flex-1 overflow-y-auto px-5 py-5"
          onScroll={() => {
            shouldStickToBottomRef.current = isNearChatBottom()
          }}
          ref={chatScrollRef}
        >
          <div className="flex flex-col gap-5">
            {turns.map((turn) => (
              <div
                className={`flex ${turn.role === "user" ? "justify-end" : "justify-start"}`}
                data-turn-id={turn.id}
                key={turn.id}
              >
                <div
                  className="max-w-[880px] rounded-[14px] border px-4 py-3"
                  style={{
                    background:
                      turn.role === "user"
                        ? C.accentDim
                        : C.surface2,
                    borderColor:
                      turn.role === "user"
                        ? C.accentBorder
                        : C.border
                  }}
                >
                  <div
                    className="mb-2 font-mono text-[10px] uppercase tracking-[0.12em]"
                    style={{
                      color:
                        turn.role === "user"
                          ? C.accent
                          : C.green
                    }}
                  >
                    {turn.role === "user"
                      ? "Recruiter"
                      : "AI Copilot"}
                  </div>

                  {turn.content ? (
                    <MarkdownText content={turn.content} />
                  ) : (
                    <div
                      className="text-sm"
                      style={{
                        color: C.muted
                      }}
                    >
                      Searching candidate evidence and drafting response...
                    </div>
                  )}

                  {turn.content && turn.diagnostics ? (
                    <div
                      className="mt-3 font-mono text-[10px] uppercase tracking-[0.1em]"
                      style={{
                        color: C.muted
                      }}
                    >
                      {turn.diagnostics.intent} · {turn.diagnostics.retrieval_count} candidates · {turn.diagnostics.model}
                    </div>
                  ) : null}

                  {turn.content && turn.candidates?.length ? (
                    <div className="mt-4 flex flex-col gap-3">
                      {turn.candidates.slice(0, 4).map((candidate) => (
                        <CandidateEvidenceCard
                          candidate={candidate}
                          key={candidate.candidate_id}
                        />
                      ))}
                    </div>
                  ) : null}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div
          className="border-t px-5 py-4"
          style={{
            borderColor: C.border
          }}
        >
          {error ? (
            <div className="mb-3">
              <Alert>
                {error}
              </Alert>
            </div>
          ) : null}

          <div className="mb-3 flex flex-wrap gap-2">
            {examples.map((example) => (
              <button
                className="rounded-lg border px-3 py-1.5 text-[12px] transition"
                disabled={loading}
                key={example}
                onClick={() => submit(example)}
                style={{
                  background: C.surface2,
                  borderColor: C.border,
                  color: C.muted
                }}
                type="button"
              >
                {example}
              </button>
            ))}
          </div>

          <div className="flex flex-col gap-3 lg:flex-row">
            <Textarea
              className="min-h-[58px] flex-1 resize-none"
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault()
                  void submit()
                }
              }}
              placeholder="Ask about candidates, missing skills, JD fit, comparisons, or ranking decisions..."
              rows={2}
              value={input}
            />
            <Button
              className="lg:w-[120px]"
              disabled={!input.trim() || loading}
              onClick={() => submit()}
              size="lg"
            >
              {loading
                ? "Thinking"
                : "Send"}
            </Button>
          </div>
        </div>
      </section>

      <aside className="ats-stable-scroll flex min-h-0 flex-col gap-4 overflow-y-auto">
        <Card>
          <FieldLabel>
            Retrieval Controls
          </FieldLabel>

          <div className="flex flex-col gap-4">
            <div>
              <FieldLabel>
                Top Candidates
              </FieldLabel>
              <Input
                max={12}
                min={1}
                onChange={(event) => setTopK(Number(event.target.value))}
                type="number"
                value={topK}
              />
            </div>

            <div>
              <FieldLabel>
                Required Skills
              </FieldLabel>
              <Input
                onChange={(event) => setSkillFilter(event.target.value)}
                placeholder="FastAPI, Docker"
                value={skillFilter}
              />
            </div>

            <div>
              <FieldLabel>
                Category
              </FieldLabel>
              <Input
                onChange={(event) => setCategoryFilter(event.target.value)}
                placeholder="data_science"
                value={categoryFilter}
              />
            </div>

            <div>
              <FieldLabel>
                Min Experience
              </FieldLabel>
              <Input
                min={0}
                onChange={(event) => setMinExperience(event.target.value)}
                placeholder="2"
                type="number"
                value={minExperience}
              />
            </div>
          </div>
        </Card>

        <Card>
          <FieldLabel>
            Retrieval Pipeline
          </FieldLabel>
          <div className="flex flex-col gap-2 text-[12px] leading-5">
            {[
              "Query embedding",
              "pgvector semantic search",
              "Keyword and metadata matching",
              "Recruiter score boosting",
              "Reranking and evidence extraction",
              "Structured context to OpenRouter"
            ].map((item) => (
              <div
                key={item}
                style={{
                  color: C.muted
                }}
              >
                - {item}
              </div>
            ))}
          </div>
        </Card>
      </aside>
    </div>
  )
}


function CandidateShortlistControls({
  candidateId,
  candidateName,
  jobTitle,
  jobDescriptionId,
  jobDescription,
  isShortlisted,
  disabled,
  onStatusChange,
  onNotice
}: {
  candidateId: number
  candidateName?: string
  jobTitle?: string
  jobDescriptionId?: number
  jobDescription?: string
  isShortlisted: boolean
  disabled?: boolean
  onStatusChange: (isShortlisted: boolean) => void
  onNotice?: (message: string) => void
}) {

  const [
    loading,
    setLoading
  ] = useState(false)
  const [
    showFeedbackModal,
    setShowFeedbackModal
  ] = useState(false)
  const [
    feedback,
    setFeedback
  ] = useState("")
  const [
    actionError,
    setActionError
  ] = useState("")
  const [
    suggestingFeedback,
    setSuggestingFeedback
  ] = useState(false)

  async function suggestFeedback(
    event: { stopPropagation: () => void }
  ) {

    event.stopPropagation()

    if (!jobDescriptionId && !jobDescription?.trim()) {

      setActionError("Select or paste a job description before generating feedback.")
      return
    }

    setSuggestingFeedback(true)
    setActionError("")

    try {

      const response = await suggestCandidateFeedback({
        candidateId,
        jobDescriptionId,
        jobTitle,
        jobDescription
      })

      setFeedback(response.feedback)

    } catch (err) {

      setActionError(
        getErrorMessage(
          err,
          "Failed to suggest feedback"
        )
      )

    } finally {

      setSuggestingFeedback(false)
    }
  }

  async function handleShortlist(
    event: { stopPropagation: () => void }
  ) {

    event.stopPropagation()
    setLoading(true)
    setActionError("")

    try {

      const response = await shortlistCandidate({
        candidateId,
        jobTitle
      })

      onStatusChange(true)
      onNotice?.(response.message)

    } catch (err) {

      setActionError(
        getErrorMessage(
          err,
          "Failed to shortlist candidate"
        )
      )

    } finally {

      setLoading(false)
    }
  }

  async function submitUnshortlist(
    event: { preventDefault: () => void }
  ) {

    event.preventDefault()

    if (!feedback.trim()) {

      setActionError("Feedback is required before unshortlisting.")
      return
    }

    setLoading(true)
    setActionError("")

    try {

      const response = await unshortlistCandidate({
        candidateId,
        feedback: feedback.trim(),
        jobTitle
      })

      onStatusChange(false)
      onNotice?.(response.message)
      setShowFeedbackModal(false)
      setFeedback("")

    } catch (err) {

      setActionError(
        getErrorMessage(
          err,
          "Failed to unshortlist candidate"
        )
      )

    } finally {

      setLoading(false)
    }
  }

  return (
    <>
      <div
        className="flex flex-wrap items-center gap-2"
        onClick={(event) => event.stopPropagation()}
      >
        {isShortlisted ? (
          <Tag color={C.green}>
            Shortlisted
          </Tag>
        ) : null}

        {isShortlisted ? (
          <Button
            disabled={disabled || loading}
            onClick={(event) => {
              event.stopPropagation()
              setActionError("")
              setShowFeedbackModal(true)
            }}
            size="sm"
            variant="secondary"
          >
            Unshortlist
          </Button>
        ) : (
          <>
            <Button
              disabled={disabled || loading}
              onClick={handleShortlist}
              size="sm"
              variant="success"
            >
              {loading
                ? "Saving..."
                : "Shortlist"}
            </Button>
            <Button
              disabled={disabled || loading}
              onClick={(event) => {
                event.stopPropagation()
                setActionError("")
                setShowFeedbackModal(true)
              }}
              size="sm"
              variant="secondary"
            >
              Feedback
            </Button>
          </>
        )}

        {actionError && !showFeedbackModal ? (
          <span
            className="text-[11px]"
            style={{
              color: C.red
            }}
          >
            {actionError}
          </span>
        ) : null}
      </div>

      <Modal
        onClose={() => {
          if (!loading) {
            setShowFeedbackModal(false)
            setActionError("")
          }
        }}
        open={showFeedbackModal}
        title={
          isShortlisted
            ? `Unshortlist ${candidateName || "Candidate"}`
            : `Feedback for ${candidateName || "Candidate"}`
        }
        width={520}
      >
        <form onSubmit={submitUnshortlist}>
          <p
            className="mb-4 text-[13px] leading-6"
            style={{
              color: C.muted
            }}
          >
            Provide professional feedback for{" "}
            {candidateName || "this candidate"}. It will be included in the
            automated application update email.
          </p>

          <FieldLabel>
            Feedback for candidate
          </FieldLabel>
          <div className="mb-2 flex justify-end">
            <Button
              disabled={loading || suggestingFeedback}
              onClick={suggestFeedback}
              size="sm"
              type="button"
              variant="ghost"
            >
              {suggestingFeedback
                ? "Suggesting..."
                : "Suggest Feedback"}
            </Button>
          </div>
          <Textarea
            onChange={(event) => setFeedback(event.target.value)}
            placeholder="Thank you for applying. At this time we are moving forward with candidates whose experience more closely aligns with..."
            rows={6}
            value={feedback}
          />

          {actionError ? (
            <p
              className="mt-3 text-[12px]"
              style={{
                color: C.red
              }}
            >
              {actionError}
            </p>
          ) : null}

          <div className="mt-5 flex flex-wrap gap-2.5">
            <Button
              disabled={loading}
              type="submit"
              variant="secondary"
            >
              {loading
                ? "Sending..."
                : isShortlisted
                ? "Confirm Unshortlist"
                : "Send Feedback"}
            </Button>
            <Button
              disabled={loading}
              onClick={() => {
                setShowFeedbackModal(false)
                setActionError("")
              }}
              type="button"
              variant="ghost"
            >
              Cancel
            </Button>
          </div>
        </form>
      </Modal>
    </>
  )
}


function MatchResultCard({
  match,
  selected,
  onToggle,
  isShortlisted,
  jobTitle,
  jobDescriptionId,
  jobDescription,
  onShortlistChange,
  onNotice
}: {
  match: CandidateMatchResult
  selected: boolean
  onToggle: () => void
  isShortlisted?: boolean
  jobTitle?: string
  jobDescriptionId?: number
  jobDescription?: string
  onShortlistChange?: (candidateId: number, isShortlisted: boolean) => void
  onNotice?: (message: string) => void
}) {

  const score = normalizeScore(
    match.final_score
  )
  const feedback = match.ai_feedback || {}

  return (
    <Card>
      <div className="mb-4 flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0">
          <div
            className="text-base font-bold"
            style={{
              color: C.text
            }}
          >
            {match.candidate_name || "Unknown Candidate"}
          </div>
          <div
            className="mt-1 text-xs"
            style={{
              color: C.muted
            }}
          >
            Candidate #{match.candidate_id} · {match.category || "Uploaded"} ·{" "}
            {match.experience_years || 0} yrs exp
          </div>
        </div>

        <div className="flex flex-col items-end gap-2 sm:flex-row sm:items-center">
          <label
            className="flex items-center gap-2 rounded-lg border px-3 py-2 text-xs font-semibold"
            style={{
              background: selected
                ? C.greenDim
                : C.surface2,
              borderColor: selected
                ? C.greenBorder
                : C.border,
              color: selected
                ? C.green
                : C.muted
            }}
          >
            <input
              checked={selected}
              onChange={onToggle}
              type="checkbox"
            />
            Include in email
          </label>
          <CandidateShortlistControls
            candidateId={match.candidate_id}
            candidateName={match.candidate_name || undefined}
            isShortlisted={Boolean(isShortlisted)}
            jobDescription={jobDescription}
            jobDescriptionId={jobDescriptionId}
            jobTitle={jobTitle}
            onNotice={onNotice}
            onStatusChange={(next) => {
              onShortlistChange?.(match.candidate_id, next)
            }}
          />
          <ScoreBadge score={score} />
        </div>
      </div>

      <div className="mb-4 grid gap-3 sm:grid-cols-4">
        {[
          {
            label: "Semantic",
            value: match.semantic_score,
            color: C.accent
          },
          {
            label: "Skills",
            value: match.skill_score,
            color: C.green
          },
          {
            label: "Experience",
            value: match.experience_score,
            color: C.amber
          },
          {
            label: "Recruiter",
            value: match.recruiter_score,
            color: C.muted
          }
        ].map((item) => (
          <div key={item.label}>
            <div
              className="mb-1 font-mono text-[10px] uppercase tracking-[0.1em]"
              style={{
                color: C.muted
              }}
            >
              {item.label}
            </div>
            <ScoreBar
              color={item.color}
              value={item.value}
            />
          </div>
        ))}
      </div>

      <div className="mb-4 grid gap-4 lg:grid-cols-2">
        <div>
          <FieldLabel>
            Matched Skills
          </FieldLabel>
          <div className="flex flex-wrap gap-1.5">
            {(match.matched_skills || []).length ? (
              match.matched_skills.map((skill) => (
                <Tag
                  color={C.green}
                  key={skill}
                >
                  {skill}
                </Tag>
              ))
            ) : (
              <Tag color={C.muted}>
                None confirmed
              </Tag>
            )}
          </div>
        </div>

        <div>
          <FieldLabel>
            Missing Skills
          </FieldLabel>
          <div className="flex flex-wrap gap-1.5">
            {(match.missing_skills || []).length ? (
              match.missing_skills.map((skill) => (
                <Tag
                  color={C.amber}
                  key={skill}
                >
                  {skill}
                </Tag>
              ))
            ) : (
              <Tag color={C.green}>
                No JD skill gaps
              </Tag>
            )}
          </div>
        </div>
      </div>

      <div
        className="rounded-xl border px-4 py-3"
        style={{
          background: "#0a0a10",
          borderColor: C.border
        }}
      >
        <FieldLabel>
          AI Feedback
        </FieldLabel>
        <div
          className="mb-2 text-sm font-semibold"
          style={{
            color: C.text
          }}
        >
          {feedback.hiring_recommendation || feedback.interview_recommendation || "Review candidate fit"}
        </div>
        <p
          className="mb-3 text-[13px] leading-6"
          style={{
            color: C.muted
          }}
        >
          {feedback.fit_summary || "AI feedback was generated from the match scores and resume evidence."}
        </p>
        <p
          className="text-[12px] leading-6"
          style={{
            color: C.muted
          }}
        >
          {feedback.recruiter_notes || "Validate critical requirements during recruiter screening."}
        </p>
      </div>
    </Card>
  )
}


function RecruiterJDMatching() {

  const [
    title,
    setTitle
  ] = useState("")
  const [
    description,
    setDescription
  ] = useState("")
  const [
    jdFile,
    setJdFile
  ] = useState<File | null>(null)
  const [
    jobDescriptions,
    setJobDescriptions
  ] = useState<JobDescription[]>([])
  const [
    selectedJdId,
    setSelectedJdId
  ] = useState("")
  const [
    topK,
    setTopK
  ] = useState(10)
  const [
    recruiterEmail,
    setRecruiterEmail
  ] = useState("")
  const [
    matches,
    setMatches
  ] = useState<CandidateMatchResult[]>([])
  const [
    selectedMatchIds,
    setSelectedMatchIds
  ] = useState<Set<number>>(new Set())
  const [
    loading,
    setLoading
  ] = useState(false)
  const [
    error,
    setError
  ] = useState("")
  const [
    notice,
    setNotice
  ] = useState("")
  const [
    shortlistByCandidateId,
    setShortlistByCandidateId
  ] = useState<Record<number, boolean>>({})
  const fileRef = useRef<HTMLInputElement>(null)

  const selectedJd = jobDescriptions.find(
    (item) => String(item.id) === selectedJdId
  )

  function updateCandidateShortlist(
    candidateId: number,
    isShortlisted: boolean
  ) {

    setShortlistByCandidateId((current) => ({
      ...current,
      [candidateId]: isShortlisted
    }))
  }

  async function loadJobDescriptions() {

    try {

      const data = await getJobDescriptions()
      setJobDescriptions(data)

      if (!selectedJdId && data[0]) {

        setSelectedJdId(String(data[0].id))
      }

    } catch (err) {

      setError(
        getErrorMessage(
          err,
          "Failed to load job descriptions"
        )
      )
    }
  }

  useEffect(() => {
    void loadJobDescriptions()
  }, [])

  async function saveJobDescription() {

    setLoading(true)
    setError("")
    setNotice("")

    try {

      const created = jdFile
        ? await uploadJobDescription(title, jdFile)
        : await createJobDescription(title, description)

      setJobDescriptions((current) => [
        created,
        ...current
      ])
      setSelectedJdId(String(created.id))
      setNotice("Job description saved and embedded.")
      setJdFile(null)

    } catch (err) {

      setError(
        getErrorMessage(
          err,
          "Failed to save job description"
        )
      )

    } finally {

      setLoading(false)
    }
  }

  async function runMatch() {

    if (!selectedJdId) {

      return
    }

    setLoading(true)
    setError("")
    setNotice("")
    setMatches([])
    setSelectedMatchIds(new Set())

    try {

      const result = await matchJobDescription({
        jobDescriptionId: Number(selectedJdId),
        topK,
        generateAiFeedback: true,
        notifyRecruiter: Boolean(recruiterEmail),
        recruiterEmail: recruiterEmail || undefined
      })

      setMatches(result.matches)
      setSelectedMatchIds(
        new Set(
          result.matches
            .filter((match) => normalizeScore(match.final_score) >= 70)
            .map((match) => match.match_result_id)
        )
      )
      setNotice(
        result.email_sent
          ? "Matching complete and recruiter summary email sent."
          : "Matching complete. Review AI feedback and shortlist candidates."
      )

    } catch (err) {

      setError(
        getErrorMessage(
          err,
          "JD matching failed"
        )
      )

    } finally {

      setLoading(false)
    }
  }

  async function sendEmail(
    emailType: "shortlist" | "interview" | "feedback"
  ) {

    if (!selectedJdId || !recruiterEmail) {

      setError("Enter recruiter email before sending.")
      return
    }

    setLoading(true)
    setError("")
    setNotice("")

    try {

      const response = await sendJDMatchEmail({
        jobDescriptionId: Number(selectedJdId),
        matchResultIds: Array.from(selectedMatchIds),
        recipientEmail: recruiterEmail,
        emailType
      })

      if (!response.sent) {

        throw new Error(response.message)
      }

      setNotice(response.message)

    } catch (err) {

      setError(
        getErrorMessage(
          err,
          "Failed to send email"
        )
      )

    } finally {

      setLoading(false)
    }
  }

  function toggleMatch(
    matchResultId: number
  ) {

    setSelectedMatchIds((current) => {
      const next = new Set(current)

      if (next.has(matchResultId)) {

        next.delete(matchResultId)
      } else {

        next.add(matchResultId)
      }

      return next
    })
  }

 
  return (
    <div>
      <Eyebrow>
        Recruiter Portal
      </Eyebrow>

      <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h2
            className="mb-1 text-[26px] font-extrabold"
            style={{
              color: C.text
            }}
          >
            Resume to JD Matching
          </h2>
          <p
            className="text-[13px]"
            style={{
              color: C.muted
            }}
          >
            Save reusable job descriptions, match candidate resumes, generate AI feedback, and email recruiter summaries.
          </p>
        </div>
        <Button
          onClick={loadJobDescriptions}
          variant="ghost"
        >
          Refresh
        </Button>
      </div>

      {error ? (
        <div className="mb-5">
          <Alert>
            {error}
          </Alert>
        </div>
      ) : null}

      {notice ? (
        <div className="mb-5">
          <Alert type="success">
            {notice}
          </Alert>
        </div>
      ) : null}

      <div className="mb-6 grid gap-5 xl:grid-cols-[minmax(0,1fr)_340px]">
        <Card>
          <div className="mb-5 grid gap-4 sm:grid-cols-2">
            <div>
              <FieldLabel>
                JD Title
              </FieldLabel>
              <Input
                onChange={(event) => setTitle(event.target.value)}
                placeholder="Senior Backend Engineer"
                value={title}
              />
            </div>

            <div>
              <FieldLabel>
                Upload JD
              </FieldLabel>
              <button
                className="w-full rounded-[10px] border px-3.5 py-2.5 text-left text-[13px]"
                onClick={() => fileRef.current?.click()}
                style={{
                  background: jdFile
                    ? C.accentDim
                    : C.surface2,
                  borderColor: jdFile
                    ? C.accentBorder
                    : C.border,
                  color: jdFile
                    ? C.accent
                    : C.muted
                }}
                type="button"
              >
                {jdFile
                  ? jdFile.name
                  : "Optional .txt, .md, or .pdf"}
              </button>
              <input
                accept=".txt,.md,.pdf,application/pdf,text/plain,text/markdown"
                className="hidden"
                onChange={(event) => setJdFile(event.target.files?.[0] || null)}
                ref={fileRef}
                type="file"
              />
            </div>
          </div>

          <div className="mb-4">
            <FieldLabel>
              JD Text
            </FieldLabel>
            <Textarea
              disabled={Boolean(jdFile)}
              onChange={(event) => setDescription(event.target.value)}
              placeholder="Paste complete job description here..."
              rows={8}
              value={description}
            />
          </div>

          <Button
            disabled={
              loading
              || !title.trim()
              || (!jdFile && description.trim().length < 20)
            }
            onClick={saveJobDescription}
          >
            {loading
              ? "Saving..."
              : "Save JD"}
          </Button>
        </Card>

        <Card>
          <FieldLabel>
            Matching Controls
          </FieldLabel>

          <div className="flex flex-col gap-4">
            <div>
              <FieldLabel>
                Saved JD
              </FieldLabel>
              <Select
                onChange={(event) => setSelectedJdId(event.target.value)}
                value={selectedJdId}
              >
                <option value="">
                  Select a JD
                </option>
                {jobDescriptions.map((jd) => (
                  <option
                    key={jd.id}
                    value={jd.id}
                  >
                    {jd.title}
                  </option>
                ))}
              </Select>
            </div>

            {selectedJd ? (
              <div className="flex flex-wrap gap-1.5">
                <Tag>
                  {selectedJd.inferred_category || "general"}
                </Tag>
                <Tag color={C.amber}>
                  {selectedJd.inferred_seniority || "Mid"}
                </Tag>
                {(selectedJd.extracted_skills || []).slice(0, 5).map((skill) => (
                  <Tag
                    color={C.green}
                    key={skill}
                  >
                    {skill}
                  </Tag>
                ))}
              </div>
            ) : null}

            <div>
              <FieldLabel>
                Top Candidates
              </FieldLabel>
              <Input
                max={50}
                min={1}
                onChange={(event) => setTopK(Number(event.target.value))}
                type="number"
                value={topK}
              />
            </div>

            <div>
              <FieldLabel>
                Recruiter Email
              </FieldLabel>
              <Input
                onChange={(event) => setRecruiterEmail(event.target.value)}
                placeholder="recruiter@company.com"
                type="email"
                value={recruiterEmail}
              />
            </div>

            <Button
              disabled={!selectedJdId || loading}
              onClick={runMatch}
              size="lg"
            >
              {loading
                ? "Matching..."
                : "Run Match"}
            </Button>
          </div>
        </Card>
      </div>

      {matches.length ? (
        <div>
          <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div
              className="text-[13px]"
              style={{
                color: C.muted
              }}
            >
              {matches.length} candidate matches · {selectedMatchIds.size} shortlisted
            </div>
            <div className="flex flex-wrap gap-2">
              <Button
                disabled={loading || !recruiterEmail}
                onClick={() => sendEmail("shortlist")}
                size="sm"
                variant="success"
              >
                Email Shortlist
              </Button>
              <Button
                disabled={loading || !recruiterEmail}
                onClick={() => sendEmail("interview")}
                size="sm"
                variant="secondary"
              >
                Email Interviews
              </Button>
            </div>
          </div>

          <div className="flex flex-col gap-3">
            {matches.map((match) => (
              <MatchResultCard
                key={match.match_result_id}
                isShortlisted={shortlistByCandidateId[match.candidate_id]}
                jobDescription={selectedJd?.description}
                jobDescriptionId={selectedJdId ? Number(selectedJdId) : undefined}
                jobTitle={selectedJd?.title}
                match={match}
                onNotice={setNotice}
                onShortlistChange={updateCandidateShortlist}
                onToggle={() => toggleMatch(match.match_result_id)}
                selected={selectedMatchIds.has(match.match_result_id)}
              />
            ))}
          </div>
        </div>
      ) : (
        <EmptyState title="No JD match run yet">
          Save or select a job description, then run matching to generate ranked candidates, AI feedback, and recruiter email actions.
        </EmptyState>
      )}
    </div>
  )
}


function RecruiterRank({
  candidates,
  setCandidates
}: {
  candidates: RankedCandidate[]
  setCandidates: (candidates: RankedCandidate[]) => void
}) {

  const [
    jd,
    setJd
  ] = useState("")
  const [
    jdTitle,
    setJdTitle
  ] = useState("")
  const [
    minScore,
    setMinScore
  ] = useState(0)
  const [
    topK,
    setTopK
  ] = useState(10)
  const [
    jobDescriptions,
    setJobDescriptions
  ] = useState<JobDescription[]>([])
  const [
    jobs,
    setJobs
  ] = useState<JobPosting[]>([])
  const [
    selectedJdId,
    setSelectedJdId
  ] = useState("")
  const [
    jdMatches,
    setJdMatches
  ] = useState<CandidateMatchResult[]>([])
  const [
    selectedMatchIds,
    setSelectedMatchIds
  ] = useState<Set<number>>(new Set())
  const [
    recruiterEmail,
    setRecruiterEmail
  ] = useState("")
  const [
    loading,
    setLoading
  ] = useState(false)
  const [
    error,
    setError
  ] = useState("")
  const [
    notice,
    setNotice
  ] = useState("")
  const [
    selected,
    setSelected
  ] = useState<RankedCandidate | null>(null)
  const [
    selectedFull,
    setSelectedFull
  ] = useState<CandidateDetails | null>(null)
  const [
    modalLoading,
    setModalLoading
  ] = useState(false)
  const [
    shortlistByCandidateId,
    setShortlistByCandidateId
  ] = useState<Record<number, boolean>>({})

  const selectedJd = jobDescriptions.find(
    (item) => String(item.id) === selectedJdId
  )

  const selectedJob = jobs.find(
    (item) => `job-${item.id}` === selectedJdId
  )

  function updateCandidateShortlist(
    candidateId: number,
    isShortlisted: boolean
  ) {

    setShortlistByCandidateId((current) => ({
      ...current,
      [candidateId]: isShortlisted
    }))
  }

  async function loadJobDescriptions() {

    try {

      const [jdData, jobData] = await Promise.all([
        getJobDescriptions(),
        getJobs()
      ])

      setJobDescriptions(jdData)
      setJobs(jobData)

      // Auto-select first job posting if nothing is selected
      if (!selectedJdId && jobData[0]) {
        const firstJobId = `job-${jobData[0].id}`
        setSelectedJdId(firstJobId)
        setJd(jobData[0].description)
        setJdTitle(jobData[0].title)
      } else if (!selectedJdId && jdData[0]) {
        setSelectedJdId(String(jdData[0].id))
      }

    } catch (err) {

      setError(
        getErrorMessage(
          err,
          "Failed to load job postings"
        )
      )
    }
  }

  function handleJdSelect(value: string) {
    setSelectedJdId(value)

    // If a job posting is selected (prefixed with "job-")
    if (value.startsWith("job-")) {
      const jobId = Number(value.replace("job-", ""))
      const job = jobs.find((j) => j.id === jobId)
      if (job) {
        setJd(job.description)
        setJdTitle(job.title)
      }
    } else if (value) {
      // If a saved JD is selected
      const savedJd = jobDescriptions.find((j) => String(j.id) === value)
      if (savedJd) {
        setJd(savedJd.description)
        setJdTitle(savedJd.title)
      }
    } else {
      setJd("")
      setJdTitle("")
    }
  }

  useEffect(() => {
    void loadJobDescriptions()
  }, [])

  async function handleRank() {

    setLoading(true)
    setError("")
    setNotice("")
    setJdMatches([])
    setSelectedMatchIds(new Set())

    try {

      const data = await rankCandidates(
        jd,
        topK
      )

      setCandidates(
        data.ranked_candidates || []
      )

    } catch (err) {

      setError(
        getErrorMessage(
          err,
          "Ranking failed"
        )
      )

    } finally {

      setLoading(false)
    }
  }

  async function savePastedJD() {

    if (!jdTitle.trim() || jd.trim().length < 20) {

      return
    }

    setLoading(true)
    setError("")
    setNotice("")

    try {

      const created = await createJobDescription(
        jdTitle,
        jd
      )

      setJobDescriptions((current) => [
        created,
        ...current
      ])
      setSelectedJdId(String(created.id))
      setNotice("JD saved. You can now click Match JD from this same screen.")

    } catch (err) {

      setError(
        getErrorMessage(
          err,
          "Failed to save JD"
        )
      )

    } finally {

      setLoading(false)
    }
  }

  async function handleSavedJDMatch() {

    if (!selectedJdId) {

      return
    }

    setLoading(true)
    setError("")
    setNotice("")
    setJdMatches([])
    setSelectedMatchIds(new Set())

    try {

      const result = await matchJobDescription({
        jobDescriptionId: Number(selectedJdId),
        topK,
        generateAiFeedback: true,
        notifyRecruiter: false
      })

      setJdMatches(result.matches)
      setSelectedMatchIds(
        new Set(
          result.matches
            .filter((match) => normalizeScore(match.final_score) >= 70)
            .map((match) => match.match_result_id)
        )
      )
      setCandidates(
        result.matches.map((match) => ({
          candidate_id: match.candidate_id,
          candidate_name: match.candidate_name || undefined,
          category: match.category || undefined,
          final_score: match.final_score,
          semantic_similarity: match.semantic_score,
          skill_match: match.skill_score,
          experience_match: match.experience_score,
          experience_years: match.experience_years || 0,
          skills: match.matched_skills
        }))
      )
      setNotice(
        "Saved JD match complete. AI feedback cards are shown below."
      )

    } catch (err) {

      setError(
        getErrorMessage(
          err,
          "Saved JD matching failed"
        )
      )

    } finally {

      setLoading(false)
    }
  }

  async function sendRankEmail(
    emailType: "shortlist" | "interview" | "feedback"
  ) {

    if (!selectedJdId || !recruiterEmail) {

      setError("Select a saved JD and enter recruiter email before sending.")
      return
    }

    setLoading(true)
    setError("")
    setNotice("")

    try {

      const response = await sendJDMatchEmail({
        jobDescriptionId: Number(selectedJdId),
        matchResultIds: Array.from(selectedMatchIds),
        recipientEmail: recruiterEmail,
        emailType
      })

      if (!response.sent) {

        throw new Error(response.message)
      }

      setNotice(response.message)

    } catch (err) {

      setError(
        getErrorMessage(
          err,
          "Failed to send recruiter email"
        )
      )

    } finally {

      setLoading(false)
    }
  }

  function toggleJDMatch(
    matchResultId: number
  ) {

    setSelectedMatchIds((current) => {
      const next = new Set(current)

      if (next.has(matchResultId)) {

        next.delete(matchResultId)
      } else {

        next.add(matchResultId)
      }

      return next
    })
  }

  async function openCandidate(
    candidate: RankedCandidate
  ) {

    setSelected(candidate)
    setSelectedFull(null)
    setModalLoading(true)

    try {

      const details = await getCandidate(
        candidate.candidate_id
      )

      setSelectedFull(details)

      if (typeof details.is_shortlisted === "boolean") {

        setShortlistByCandidateId((current) => ({
          ...current,
          [candidate.candidate_id]: details.is_shortlisted as boolean
        }))
      }

    } catch (err) {

      setError(
        getErrorMessage(
          err,
          "Failed to load candidate"
        )
      )

    } finally {

      setModalLoading(false)
    }
  }

  const filtered = candidates.filter((candidate) => {

    return normalizeScore(candidate.final_score) >= minScore
  })
  const filteredJdMatches = jdMatches.filter((match) => (
    normalizeScore(match.final_score) >= minScore
  ))

  return (
    <div>
      <Eyebrow>
        Recruiter Portal
      </Eyebrow>

      <h2
        className="mb-1.5 text-[26px] font-extrabold"
        style={{
          color: C.text
        }}
      >
        Rank Candidates
      </h2>

      <p
        className="mb-6 text-[13px]"
        style={{
          color: C.muted
        }}
      >
        Paste a job description or select a saved JD to match candidates through
        semantic scoring, skill overlap, experience alignment, and AI feedback.
      </p>

      <div className="mb-6 grid gap-5 xl:grid-cols-[1fr_320px]">
        <div>
          <FieldLabel>
            Job Description
          </FieldLabel>
          <Textarea
            onChange={(event) => setJd(event.target.value)}
            placeholder="Paste full job description here..."
            rows={7}
            value={jd}
          />
        </div>

        <div className="flex flex-col gap-3.5">
          <div>
            <FieldLabel>
              JD Title
            </FieldLabel>
            <Input
              onChange={(event) => setJdTitle(event.target.value)}
              placeholder="Junior ML Engineer"
              value={jdTitle}
            />
          </div>

          <div>
            <FieldLabel>
              Saved JD
            </FieldLabel>
            <Select
              onChange={(event) => handleJdSelect(event.target.value)}
              value={selectedJdId}
            >
              <option value="">
                Select a job posting...
              </option>
              {jobs.length > 0 && (
                <optgroup label="Job Postings">
                  {jobs.map((item) => (
                    <option
                      key={`job-${item.id}`}
                      value={`job-${item.id}`}
                    >
                      {item.title}
                    </option>
                  ))}
                </optgroup>
              )}
              {jobDescriptions.length > 0 && (
                <optgroup label="Saved JDs">
                  {jobDescriptions.map((item) => (
                    <option
                      key={`jd-${item.id}`}
                      value={String(item.id)}
                    >
                      {item.title}
                    </option>
                  ))}
                </optgroup>
              )}
            </Select>
          </div>

          {selectedJd ? (
            <div className="flex flex-wrap gap-1.5">
              <Tag>
                {selectedJd.inferred_category || "general"}
              </Tag>
              <Tag color={C.amber}>
                {selectedJd.inferred_seniority || "Mid"}
              </Tag>
              {(selectedJd.extracted_skills || []).slice(0, 4).map((skill) => (
                <Tag
                  color={C.green}
                  key={skill}
                >
                  {skill}
                </Tag>
              ))}
            </div>
          ) : null}

          <div>
            <FieldLabel>
              Top K Results
            </FieldLabel>
            <Input
              min={1}
              onChange={(event) => setTopK(Number(event.target.value))}
              type="number"
              value={topK}
            />
          </div>

          <div>
            <FieldLabel>
              Min Score Filter
            </FieldLabel>
            <Input
              min={0}
              onChange={(event) => setMinScore(Number(event.target.value))}
              placeholder="0"
              type="number"
              value={minScore || ""}
            />
          </div>

          <div>
            <FieldLabel>
              Recruiter Email
            </FieldLabel>
            <Input
              onChange={(event) => setRecruiterEmail(event.target.value)}
              placeholder="recruiter@company.com"
              type="email"
              value={recruiterEmail}
            />
          </div>

          <div className="grid grid-cols-2 gap-2">
            <Button
              disabled={!jdTitle.trim() || jd.trim().length < 20 || loading}
              onClick={savePastedJD}
              variant="ghost"
            >
              Save JD
            </Button>

            <Button
              disabled={!selectedJdId || loading}
              onClick={() => {
                if (selectedJd) {
                  setJd(selectedJd.description)
                }
              }}
              variant="secondary"
            >
              Use Text
            </Button>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <Button
              disabled={!selectedJdId || loading}
              onClick={handleSavedJDMatch}
              variant="success"
            >
              {loading
                ? "Matching..."
                : "Match JD"}
            </Button>

            <Button
              disabled={!jd || loading}
              onClick={handleRank}
            >
              {loading
                ? "Ranking..."
                : "Quick Rank"}
            </Button>
          </div>
        </div>
      </div>

      {error ? (
        <div className="mb-5">
          <Alert>
            {error}
          </Alert>
        </div>
      ) : null}

      {notice ? (
        <div className="mb-5">
          <Alert type="success">
            {notice}
          </Alert>
        </div>
      ) : null}

      {jdMatches.length ? (
        <div>
          <div
            className="mb-4 flex flex-col gap-3 text-[13px] sm:flex-row sm:items-center sm:justify-between"
            style={{
              color: C.muted
            }}
          >
            <span>
              Showing{" "}
              <span
                className="font-semibold"
                style={{
                  color: C.text
                }}
              >
                {filteredJdMatches.length}
              </span>
              {" "}JD matches · {selectedMatchIds.size} shortlisted
            </span>

            <div className="flex flex-wrap gap-2">
              <Button
                disabled={loading || !recruiterEmail}
                onClick={() => sendRankEmail("shortlist")}
                size="sm"
                variant="success"
              >
                Email Shortlist
              </Button>
              <Button
                disabled={loading || !recruiterEmail}
                onClick={() => sendRankEmail("interview")}
                size="sm"
                variant="secondary"
              >
                Email Interviews
              </Button>
            </div>
          </div>

          <div className="flex flex-col gap-3">
            {filteredJdMatches.map((match) => (
              <MatchResultCard
                key={match.match_result_id}
                isShortlisted={shortlistByCandidateId[match.candidate_id]}
                jobDescription={selectedJd?.description || jd}
                jobDescriptionId={selectedJdId ? Number(selectedJdId) : undefined}
                jobTitle={selectedJd?.title}
                match={match}
                onNotice={setNotice}
                onShortlistChange={updateCandidateShortlist}
                onToggle={() => toggleJDMatch(match.match_result_id)}
                selected={selectedMatchIds.has(match.match_result_id)}
              />
            ))}
          </div>
        </div>
      ) : candidates.length === 0 ? (
        <EmptyState title="No ranking run yet">
          Paste a JD for quick ranking, or select a saved JD and click Match JD
          to generate AI feedback and shortlist actions.
        </EmptyState>
      ) : (
        <div>
          <div
            className="mb-4 flex items-center justify-between text-[13px]"
            style={{
              color: C.muted
            }}
          >
            <span>
              Showing{" "}
              <span
                className="font-semibold"
                style={{
                  color: C.text
                }}
              >
                {filtered.length}
              </span>
              {" "}candidates
              {minScore > 0
                ? ` above ${minScore}%`
                : ""}
            </span>
          </div>

          <div className="flex flex-col gap-2.5">
            {filtered.map((candidate, index) => {

              const score = normalizeScore(candidate.final_score)

              return (
                <Card
                  hover
                  key={candidate.candidate_id}
                  onClick={() => openCandidate(candidate)}
                >
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-center">
                    <div
                      className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full border font-mono text-[13px] font-bold"
                      style={{
                        background:
                          index < 3
                            ? C.accentDim
                            : C.surface2,
                        borderColor:
                          index < 3
                            ? C.accentBorder
                            : C.border,
                        color:
                          index < 3
                            ? C.accent
                            : C.muted
                      }}
                    >
                      #{index + 1}
                    </div>

                    <div className="min-w-0 flex-1">
                      <div className="mb-1 flex items-center justify-between gap-3">
                        <div
                          className="truncate text-[15px] font-bold"
                          style={{
                            color: C.text
                          }}
                        >
                          {candidate.candidate_name || "Unknown Candidate"}
                        </div>
                        {shortlistByCandidateId[candidate.candidate_id] ? (
                          <Tag color={C.green}>
                            Shortlisted
                          </Tag>
                        ) : null}

                        <ScoreBadge score={score} />
                      </div>

                      <div
                        className="mb-2 text-[11px]"
                        style={{
                          color: C.muted
                        }}
                      >
                        {candidate.category || "Uploaded"} ·{" "}
                        {candidate.experience_years || 0} yrs exp
                      </div>

                      <ScoreBar
                        max={100}
                        value={score}
                      />
                    </div>

                    <CandidateShortlistControls
                      candidateId={candidate.candidate_id}
                      candidateName={candidate.candidate_name}
                      jobDescription={selectedJd?.description || jd}
                      jobDescriptionId={selectedJdId ? Number(selectedJdId) : undefined}
                      isShortlisted={Boolean(
                        shortlistByCandidateId[candidate.candidate_id]
                      )}
                      jobTitle={selectedJd?.title}
                      onNotice={setNotice}
                      onStatusChange={(next) => {
                        updateCandidateShortlist(
                          candidate.candidate_id,
                          next
                        )
                      }}
                    />

                    <div className="flex max-w-[240px] flex-wrap gap-1.5">
                      {(candidate.skills || []).slice(0, 3).map((skill) => (
                        <Tag key={skill}>
                          {skill}
                        </Tag>
                      ))}

                      {(candidate.skills || []).length > 3 ? (
                        <Tag color={C.muted}>
                          +{(candidate.skills || []).length - 3}
                        </Tag>
                      ) : null}
                    </div>
                  </div>
                </Card>
              )
            })}
          </div>
        </div>
      )}

      <CandidateModal
        isShortlisted={
          selected
            ? Boolean(shortlistByCandidateId[selected.candidate_id])
            : false
        }
        jobDescription={selectedJd?.description || jd}
        jobDescriptionId={selectedJdId ? Number(selectedJdId) : undefined}
        jobTitle={selectedJd?.title}
        loading={modalLoading}
        onClose={() => {
          setSelected(null)
          setSelectedFull(null)
        }}
        onNotice={setNotice}
        onShortlistChange={updateCandidateShortlist}
        rankedCandidate={selected}
        selectedFull={selectedFull}
      />
    </div>
  )
}


function CandidateModal({
  rankedCandidate,
  selectedFull,
  loading,
  onClose,
  isShortlisted,
  jobTitle,
  jobDescriptionId,
  jobDescription,
  onShortlistChange,
  onNotice
}: {
  rankedCandidate: RankedCandidate | null
  selectedFull: CandidateDetails | null
  loading: boolean
  onClose: () => void
  isShortlisted?: boolean
  jobTitle?: string
  jobDescriptionId?: number
  jobDescription?: string
  onShortlistChange?: (candidateId: number, isShortlisted: boolean) => void
  onNotice?: (message: string) => void
}) {

  const open = Boolean(rankedCandidate)
  const detail = selectedFull
  const score = normalizeScore(
    rankedCandidate?.final_score
  )
  const candidateId = detail?.id || rankedCandidate?.candidate_id

  return (
    <Modal
      onClose={onClose}
      open={open}
      title={rankedCandidate?.candidate_name || detail?.candidate_name || "Candidate"}
      width={740}
    >
      {loading ? (
        <div
          className="py-8 text-center text-sm"
          style={{
            color: C.muted
          }}
        >
          Loading candidate profile...
        </div>
      ) : (
        <div>
          <div className="mb-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <Stat
              color={scoreColor(score)}
              label="Match Score"
              value={`${score}%`}
            />
            <Stat
              label="Experience"
              value={`${detail?.experience_years || rankedCandidate?.experience_years || 0}y`}
            />
            <Stat
              color={C.green}
              label="Skill Match"
              value={`${normalizeScore(rankedCandidate?.skill_match)}%`}
            />
            <Stat
              color={C.amber}
              label="Semantic Sim"
              value={`${normalizeScore(rankedCandidate?.semantic_similarity)}%`}
            />
          </div>

          {detail?.resume_summary ? (
            <div className="mb-5">
              <FieldLabel>
                LLM Summary
              </FieldLabel>
              <p
                className="rounded-[10px] border px-4 py-3 text-[13px] leading-6"
                style={{
                  background: "#0a0a10",
                  borderColor: C.border,
                  color: C.muted
                }}
              >
                {detail.resume_summary}
              </p>
            </div>
          ) : null}

          <div className="mb-5 grid gap-3 sm:grid-cols-2">
            {[
              {
                label: "Email",
                value: detail?.email
              },
              {
                label: "Phone",
                value: detail?.phone
              },
              {
                label: "Location",
                value: detail?.location
              },
              {
                label: "Category",
                value: detail?.category || rankedCandidate?.category
              }
            ].map((item) => (
              <div
                className="rounded-[10px] border px-3 py-2.5"
                key={item.label}
                style={{
                  background: C.surface2,
                  borderColor: C.border
                }}
              >
                <div
                  className="font-mono text-[10px] uppercase tracking-[0.1em]"
                  style={{
                    color: C.muted
                  }}
                >
                  {item.label}
                </div>
                <div
                  className="mt-1 truncate text-sm font-semibold"
                  style={{
                    color: item.value
                      ? C.text
                      : C.muted
                  }}
                >
                  {item.value || "Not extracted"}
                </div>
              </div>
            ))}
          </div>

          <div className="mb-5">
            <FieldLabel>
              Score Breakdown
            </FieldLabel>
            {[
              {
                label: "Semantic Similarity (50%)",
                value: rankedCandidate?.semantic_similarity || 0
              },
              {
                label: "Skill Match (30%)",
                value: rankedCandidate?.skill_match || 0
              },
              {
                label: "Title Match (10%)",
                value: rankedCandidate?.title_match || 0
              },
              {
                label: "Experience Match (10%)",
                value: rankedCandidate?.experience_match || 0
              }
            ].map((row) => (
              <div
                className="mb-2.5"
                key={row.label}
              >
                <div
                  className="mb-1 flex justify-between text-xs"
                  style={{
                    color: C.muted
                  }}
                >
                  <span>
                    {row.label}
                  </span>
                  <span
                    className="font-mono"
                    style={{
                      color: C.text
                    }}
                  >
                    {normalizeScore(row.value)}%
                  </span>
                </div>
                <ScoreBar value={row.value} />
              </div>
            ))}
          </div>

          <div className="mb-5">
            <FieldLabel>
              Skills
            </FieldLabel>
            <div className="flex flex-wrap gap-1.5">
              {(detail?.skills || rankedCandidate?.skills || []).map((skill) => (
                <Tag key={skill}>
                  {skill}
                </Tag>
              ))}
            </div>
          </div>

          {detail?.resume_text ? (
            <div className="mb-5">
              <FieldLabel>
                Resume Text
              </FieldLabel>
              <pre
                className="max-h-52 overflow-y-auto whitespace-pre-wrap rounded-[10px] border px-4 py-3 font-mono text-[11px] leading-5"
                style={{
                  background: "#0a0a10",
                  borderColor: C.border,
                  color: C.muted
                }}
              >
                {detail.resume_text}
              </pre>
            </div>
          ) : null}

          <div className="mb-5">
            <FieldLabel>
              Shortlist Status
            </FieldLabel>
            {candidateId ? (
              <CandidateShortlistControls
                candidateId={candidateId}
                candidateName={
                  detail?.candidate_name
                    || rankedCandidate?.candidate_name
                }
                jobDescription={jobDescription}
                jobDescriptionId={jobDescriptionId}
                isShortlisted={Boolean(isShortlisted)}
                jobTitle={jobTitle}
                onNotice={onNotice}
                onStatusChange={(next) => {
                  onShortlistChange?.(candidateId, next)
                }}
              />
            ) : null}
          </div>

          <div className="flex flex-wrap gap-2.5">
            {candidateId ? (
              <Button
                onClick={() => window.open(
                  getCandidateResumeUrl(candidateId),
                  "_blank"
                )}
                variant="success"
              >
                Download Resume
              </Button>
            ) : null}

            <Button
              onClick={onClose}
              variant="ghost"
            >
              Close
            </Button>
          </div>
        </div>
      )}
    </Modal>
  )
}


function RecruiterJobs() {

  const emptyForm = {
    title: "",
    department: "",
    location: "",
    type: "Full-time",
    description: "",
    skills: ""
  }
  const [
    jobs,
    setJobs
  ] = useState<JobPosting[]>([])
  const [
    showForm,
    setShowForm
  ] = useState(false)
  const [
    form,
    setForm
  ] = useState(emptyForm)
  const [
    loading,
    setLoading
  ] = useState(false)
  const [
    fetching,
    setFetching
  ] = useState(true)
  const [
    error,
    setError
  ] = useState("")
  const [
    notice,
    setNotice
  ] = useState("")

  async function loadJobs() {

    setFetching(true)
    setError("")

    try {

      setJobs(
        await getJobs()
      )

    } catch (err) {

      setError(
        getErrorMessage(
          err,
          "Failed to load job postings"
        )
      )

    } finally {

      setFetching(false)
    }
  }

  useEffect(() => {
    void loadJobs()
  }, [])

  function updateForm(
    key: keyof typeof emptyForm,
    value: string
  ) {

    setForm((current) => ({
      ...current,
      [key]: value
    }))
  }

  async function submit() {

    setLoading(true)
    setError("")
    setNotice("")

    try {

      const created = await createJob({
        title: form.title,
        department: form.department,
        location: form.location,
        type: form.type,
        description: form.description,
        skills: form.skills
          .split(",")
          .map((skill) => skill.trim())
          .filter(Boolean)
      })

      setJobs((current) => [
        created,
        ...current
      ])
      setForm(emptyForm)
      setShowForm(false)
      setNotice("Job posting published and visible in the candidate portal.")

    } catch (err) {

      setError(
        getErrorMessage(
          err,
          "Failed to publish job"
        )
      )

    } finally {

      setLoading(false)
    }
  }

  return (
    <div>
      <Eyebrow>
        Recruiter Portal
      </Eyebrow>

      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2
            className="mb-1 text-[26px] font-extrabold"
            style={{
              color: C.text
            }}
          >
            Job Postings
          </h2>

          <p
            className="text-[13px]"
            style={{
              color: C.muted
            }}
          >
            {jobs.length} live postings shown in the candidate portal
          </p>
        </div>

        <div className="flex gap-2">
          <Button
            onClick={loadJobs}
            variant="ghost"
          >
            Refresh
          </Button>
          <Button
            onClick={() => {
              setForm(emptyForm)
              setShowForm(true)
            }}
          >
            Post New Job
          </Button>
        </div>
      </div>

      {error ? (
        <div className="mb-5">
          <Alert>
            {error}
          </Alert>
        </div>
      ) : null}

      {notice ? (
        <div className="mb-5">
          <Alert type="success">
            {notice}
          </Alert>
        </div>
      ) : null}

      {fetching ? (
        <EmptyState title="Loading jobs">
          Fetching job postings from the backend.
        </EmptyState>
      ) : jobs.length === 0 ? (
        <EmptyState title="No job postings yet">
          Post your first role. Once published, it appears in the candidate
          Browse Jobs and Apply screens.
        </EmptyState>
      ) : (
        <div className="flex flex-col gap-3">
          {jobs.map((job) => (
            <Card key={job.id}>
              <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div className="flex-1">
                  <div
                    className="mb-1 text-base font-bold"
                    style={{
                      color: C.text
                    }}
                  >
                    {job.title}
                  </div>

                  <div
                    className="mb-3 flex flex-wrap gap-x-3 gap-y-1 text-xs"
                    style={{
                      color: C.muted
                    }}
                  >
                    <span>{job.department || "General"}</span>
                    <span>{job.location || "Remote"}</span>
                    <span>{job.type || "Full-time"}</span>
                  </div>

                  <p
                    className="mb-3 max-w-2xl text-xs leading-6"
                    style={{
                      color: C.muted
                    }}
                  >
                    {job.description.length > 180
                      ? `${job.description.slice(0, 180)}...`
                      : job.description}
                  </p>

                  <div className="flex flex-wrap gap-1.5">
                    {(job.skills || []).map((skill) => (
                      <Tag key={skill}>
                        {skill}
                      </Tag>
                    ))}
                  </div>
                </div>

                <Tag>
                  Visible to candidates
                </Tag>
              </div>
            </Card>
          ))}
        </div>
      )}

      <Modal
        onClose={() => setShowForm(false)}
        open={showForm}
        title="Post New Job"
        width={620}
      >
        <div className="flex flex-col gap-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <FieldLabel>
                Job Title
              </FieldLabel>
              <Input
                onChange={(event) => updateForm("title", event.target.value)}
                placeholder="e.g. ML Engineer"
                value={form.title}
              />
            </div>

            <div>
              <FieldLabel>
                Department
              </FieldLabel>
              <Input
                onChange={(event) => updateForm("department", event.target.value)}
                placeholder="e.g. AI Research"
                value={form.department}
              />
            </div>

            <div>
              <FieldLabel>
                Location
              </FieldLabel>
              <Input
                onChange={(event) => updateForm("location", event.target.value)}
                placeholder="Bangalore / Remote"
                value={form.location}
              />
            </div>

            <div>
              <FieldLabel>
                Type
              </FieldLabel>
              <Select
                onChange={(event) => updateForm("type", event.target.value)}
                value={form.type}
              >
                <option>
                  Full-time
                </option>
                <option>
                  Part-time
                </option>
                <option>
                  Contract
                </option>
                <option>
                  Internship
                </option>
              </Select>
            </div>
          </div>

          <div>
            <FieldLabel>
              Description
            </FieldLabel>
            <Textarea
              onChange={(event) => updateForm("description", event.target.value)}
              placeholder="Full job description..."
              rows={5}
              value={form.description}
            />
          </div>

          <div>
            <FieldLabel>
              Required Skills
            </FieldLabel>
            <Input
              onChange={(event) => updateForm("skills", event.target.value)}
              placeholder="Python, FastAPI, PostgreSQL"
              value={form.skills}
            />
          </div>

          <div className="flex flex-wrap gap-2">
            <Button
              disabled={!form.title.trim() || !form.description.trim() || loading}
              onClick={submit}
            >
              {loading
                ? "Publishing..."
                : "Publish Job"}
            </Button>

            <Button
              onClick={() => setShowForm(false)}
              variant="ghost"
            >
              Cancel
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}


function RecruiterUpload() {

  const [
    file,
    setFile
  ] = useState<File | null>(null)
  const [
    loading,
    setLoading
  ] = useState(false)
  const [
    error,
    setError
  ] = useState("")
  const [
    result,
    setResult
  ] = useState("")
  const fileRef = useRef<HTMLInputElement>(null)

  async function submit() {

    if (!file) {

      return
    }

    setLoading(true)
    setError("")
    setResult("")

    try {

      const response = await uploadResume(file)

      setResult(
        `${response.message}: ${response.file_name}`
      )

    } catch (err) {

      setError(
        getErrorMessage(
          err,
          "Resume upload failed"
        )
      )

    } finally {

      setLoading(false)
    }
  }

  return (
    <div className="max-w-xl">
      <Eyebrow>
        Recruiter Portal
      </Eyebrow>

      <h2
        className="mb-1.5 text-[26px] font-extrabold"
        style={{
          color: C.text
        }}
      >
        Resume Intake
      </h2>

      <p
        className="mb-7 text-[13px]"
        style={{
          color: C.muted
        }}
      >
        Upload a candidate PDF. The request returns immediately after queueing
        Celery processing.
      </p>

      <div className="flex flex-col gap-5">
        <button
          className="w-full rounded-xl border-2 border-dashed px-5 py-8 text-center transition"
          onClick={() => fileRef.current?.click()}
          style={{
            background: file
              ? C.accentDim
              : "transparent",
            borderColor: file
              ? C.accentBorder
              : C.border
          }}
          type="button"
        >
          <div className="mb-2 text-3xl">
            {file
              ? "📄"
              : "↑"}
          </div>

          <div
            className="text-[13px] font-semibold"
            style={{
              color: file
                ? C.accent
                : C.muted
            }}
          >
            {file
              ? file.name
              : "Click to upload PDF"}
          </div>
        </button>

        <input
          accept=".pdf,application/pdf"
          className="hidden"
          onChange={(event) => {
            const selectedFile = event.target.files?.[0]

            if (selectedFile) {

              setFile(selectedFile)
            }
          }}
          ref={fileRef}
          type="file"
        />

        {error ? (
          <Alert>
            {error}
          </Alert>
        ) : null}

        {result ? (
          <Alert type="success">
            {result}
          </Alert>
        ) : null}

        <Button
          disabled={!file || loading}
          onClick={submit}
          size="lg"
        >
          {loading
            ? "Queueing..."
            : "Upload Resume"}
        </Button>
      </div>
    </div>
  )
}


function RecruiterAnalytics({
  candidates
}: {
  candidates: RankedCandidate[]
}) {

  const analytics = useMemo(() => {

    const scores = candidates.map((candidate) => normalizeScore(candidate.final_score))
    const avgScore = scores.length
      ? Math.round(scores.reduce((total, score) => total + score, 0) / scores.length)
      : 0
    const shortlisted = scores.filter((score) => score >= 80).length
    const skillCounts = new Map<string, number>()

    candidates.forEach((candidate) => {
      ;(candidate.skills || []).forEach((skill) => {
        skillCounts.set(
          skill,
          (skillCounts.get(skill) || 0) + 1
        )
      })
    })

    const topSkills = Array.from(skillCounts.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8)

    const scoreBuckets = [
      {
        label: "90-100%",
        count: scores.filter((score) => score >= 90).length,
        color: C.green
      },
      {
        label: "75-89%",
        count: scores.filter((score) => score >= 75 && score < 90).length,
        color: C.accent
      },
      {
        label: "60-74%",
        count: scores.filter((score) => score >= 60 && score < 75).length,
        color: C.amber
      },
      {
        label: "Below 60%",
        count: scores.filter((score) => score < 60).length,
        color: C.red
      }
    ]

    return {
      avgScore,
      shortlisted,
      topSkills,
      skillCount: skillCounts.size,
      scoreBuckets
    }
  }, [candidates])

  const maxSkillCount = Math.max(
    ...analytics.topSkills.map(([, count]) => count),
    1
  )
  const maxBucket = Math.max(
    ...analytics.scoreBuckets.map((bucket) => bucket.count),
    1
  )

  return (
    <div>
      <Eyebrow>
        Recruiter Portal
      </Eyebrow>

      <h2
        className="mb-1.5 text-[26px] font-extrabold"
        style={{
          color: C.text
        }}
      >
        Analytics
      </h2>

      <p
        className="mb-7 text-[13px]"
        style={{
          color: C.muted
        }}
      >
        Analytics are computed from the latest real ranking response.
      </p>

      {candidates.length === 0 ? (
        <EmptyState title="No ranking data yet">
          Run a candidate ranking first. This dashboard will then populate with
          score distribution, top skills, and the candidate table.
        </EmptyState>
      ) : (
        <>
          <div className="mb-8 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <Stat
              label="Total Candidates"
              value={candidates.length}
            />
            <Stat
              color={C.green}
              label="Avg Match Score"
              value={`${analytics.avgScore}%`}
            />
            <Stat
              color={C.amber}
              label="Strong Matches"
              sub="Score at least 80%"
              value={analytics.shortlisted}
            />
            <Stat
              color={C.muted}
              label="Unique Skills"
              value={analytics.skillCount}
            />
          </div>

          <div className="mb-7 grid gap-5 xl:grid-cols-2">
            <Card>
              <FieldLabel>
                Score Distribution
              </FieldLabel>
              <div className="flex flex-col gap-3">
                {analytics.scoreBuckets.map((bucket) => (
                  <div key={bucket.label}>
                    <div className="mb-1 flex justify-between text-xs">
                      <span
                        style={{
                          color: C.muted
                        }}
                      >
                        {bucket.label}
                      </span>
                      <span
                        className="font-mono font-bold"
                        style={{
                          color: bucket.color
                        }}
                      >
                        {bucket.count}
                      </span>
                    </div>
                    <div
                      className="h-2 rounded"
                      style={{
                        background: C.border
                      }}
                    >
                      <div
                        className="h-full rounded transition-[width] duration-500"
                        style={{
                          background: bucket.color,
                          minWidth: bucket.count > 0
                            ? 6
                            : 0,
                          width: `${Math.round((bucket.count / maxBucket) * 100)}%`
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            <Card>
              <FieldLabel>
                Top Skills in Pool
              </FieldLabel>
              <div className="flex flex-col gap-2.5">
                {analytics.topSkills.map(([skill, count]) => (
                  <div key={skill}>
                    <div className="mb-1 flex justify-between text-xs">
                      <span
                        style={{
                          color: C.text
                        }}
                      >
                        {skill}
                      </span>
                      <span
                        className="font-mono"
                        style={{
                          color: C.accent
                        }}
                      >
                        {count}
                      </span>
                    </div>
                    <div
                      className="h-1.5 rounded"
                      style={{
                        background: C.border
                      }}
                    >
                      <div
                        className="h-full rounded transition-[width] duration-500"
                        style={{
                          background: C.accent,
                          width: `${Math.round((count / maxSkillCount) * 100)}%`
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          <Card className="overflow-x-auto">
            <FieldLabel>
              All Candidates
            </FieldLabel>
            <table className="w-full min-w-[760px] border-collapse text-[13px]">
              <thead>
                <tr
                  className="border-b"
                  style={{
                    borderColor: C.border
                  }}
                >
                  {[
                    "Name",
                    "Category",
                    "Exp",
                    "Skills",
                    "Semantic",
                    "Skill Match",
                    "Final Score"
                  ].map((heading) => (
                    <th
                      className="px-2.5 py-2 text-left font-mono text-[11px] font-semibold"
                      key={heading}
                      style={{
                        color: C.muted
                      }}
                    >
                      {heading}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {candidates.map((candidate, index) => {

                  const score = normalizeScore(candidate.final_score)

                  return (
                    <tr
                      className="border-b"
                      key={candidate.candidate_id}
                      style={{
                        background:
                          index % 2 === 0
                            ? "transparent"
                            : `${C.surface2}50`,
                        borderColor: C.border
                      }}
                    >
                      <td
                        className="px-2.5 py-2.5 font-semibold"
                        style={{
                          color: C.text
                        }}
                      >
                        {candidate.candidate_name || "Unknown"}
                      </td>
                      <td
                        className="px-2.5 py-2.5 text-xs"
                        style={{
                          color: C.muted
                        }}
                      >
                        {candidate.category || "Uploaded"}
                      </td>
                      <td
                        className="px-2.5 py-2.5 font-mono"
                        style={{
                          color: C.muted
                        }}
                      >
                        {candidate.experience_years || 0}y
                      </td>
                      <td className="px-2.5 py-2.5">
                        <div className="flex flex-wrap gap-1">
                          {(candidate.skills || []).slice(0, 2).map((skill) => (
                            <Tag key={skill}>
                              {skill}
                            </Tag>
                          ))}
                          {(candidate.skills || []).length > 2 ? (
                            <span
                              className="text-[10px]"
                              style={{
                                color: C.muted
                              }}
                            >
                              +{(candidate.skills || []).length - 2}
                            </span>
                          ) : null}
                        </div>
                      </td>
                      <td
                        className="px-2.5 py-2.5 font-mono text-xs"
                        style={{
                          color: C.amber
                        }}
                      >
                        {normalizeScore(candidate.semantic_similarity)}%
                      </td>
                      <td
                        className="px-2.5 py-2.5 font-mono text-xs"
                        style={{
                          color: C.green
                        }}
                      >
                        {normalizeScore(candidate.skill_match)}%
                      </td>
                      <td className="px-2.5 py-2.5">
                        <ScoreBadge score={score} />
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </Card>
        </>
      )}
    </div>
  )
}


export default function AtsPortal() {

  const [
    portal,
    setPortal
  ] = useState<Portal>(null)
  const isAuthenticated = useSyncExternalStore(
    subscribeToAuth,
    getAuthSnapshot,
    getAuthServerSnapshot
  )

  function logout() {

    setStoredToken(null)
  }

  if (!portal) {

    return (
      <Landing onSelect={setPortal} />
    )
  }

  if (portal === "candidate") {

    return (
      <CandidatePortal
        onBack={() => setPortal(null)}
      />
    )
  }

  return (
    <RecruiterPortal
      isAuthenticated={isAuthenticated}
      onBack={() => setPortal(null)}
      onLogout={logout}
    />
  )
}
