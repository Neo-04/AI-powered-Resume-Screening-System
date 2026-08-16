import { useEffect, useId, useState } from 'react'
import Alert from '../components/Alert'
import Button from '../components/Button'
import LoadingSpinner from '../components/LoadingSpinner'
import MatchResults from '../components/MatchResults'
import ParsedJdCard from '../components/ParsedJdCard'
import ParsedResumeCard from '../components/ParsedResumeCard'
import WorkflowStepper from '../components/WorkflowStepper'
import type { ScreeningWorkflow } from '../hooks/useScreeningWorkflow'
import { checkHealth } from '../services/api'

interface HomePageProps {
  workflow: ScreeningWorkflow
}

type JdInputMode = 'file' | 'text'

export default function HomePage({ workflow }: HomePageProps) {
  const resumeInputId = useId()
  const jdFileInputId = useId()
  const jdTextInputId = useId()

  const [resumeFile, setResumeFile] = useState<File | null>(null)
  const [jdInputMode, setJdInputMode] = useState<JdInputMode>('file')
  const [jdFile, setJdFile] = useState<File | null>(null)
  const [jdText, setJdText] = useState('')
  const [backendStatus, setBackendStatus] = useState<
    'checking' | 'online' | 'offline'
  >('checking')

  const {
    resumeUpload,
    parsedResume,
    jdUpload,
    parsedJd,
    matchResult,
    handleUploadResume,
    handleParseResume,
    handleUploadJdFile,
    handleUploadJdText,
    handleParseJd,
    handleRunMatch,
    resetWorkflow,
  } = workflow

  useEffect(() => {
    let active = true

    checkHealth()
      .then(() => {
        if (active) setBackendStatus('online')
      })
      .catch(() => {
        if (active) setBackendStatus('offline')
      })

    return () => {
      active = false
    }
  }, [])

  const resumeUploaded = resumeUpload.status === 'success'
  const resumeParsed = parsedResume.status === 'success'
  const jdUploaded = jdUpload.status === 'success'
  const jdParsed = parsedJd.status === 'success'
  const matchComplete = matchResult.status === 'success'

  const canUploadResume = Boolean(resumeFile) && resumeUpload.status !== 'loading'
  const canParseResume = resumeUploaded && parsedResume.status !== 'loading'
  const canUploadJd =
    jdUpload.status !== 'loading' &&
    ((jdInputMode === 'file' && Boolean(jdFile)) ||
      (jdInputMode === 'text' && jdText.trim().length > 0))
  const canParseJd = jdUploaded && parsedJd.status !== 'loading'
  const canRunMatch =
    resumeParsed &&
    jdParsed &&
    matchResult.status !== 'loading'

  const onResumeUpload = () => {
    if (resumeFile) {
      void handleUploadResume(resumeFile)
    }
  }

  const onJdUpload = () => {
    if (jdInputMode === 'file' && jdFile) {
      void handleUploadJdFile(jdFile)
      return
    }
    if (jdInputMode === 'text' && jdText.trim()) {
      void handleUploadJdText(jdText.trim())
    }
  }

  const onReset = () => {
    setResumeFile(null)
    setJdFile(null)
    setJdText('')
    resetWorkflow()
  }

  return (
    <div className="page">
      <header className="site-header">
        <div className="brand">
          <img
            src="/resume-screening.svg"
            alt="AI Resume Screening logo"
            width={40}
            height={40}
          />
          <div>
            <h1>AI Resume Screening</h1>
            <p>Upload, parse, and match candidates to job descriptions.</p>
          </div>
        </div>
        <div className="backend-status" aria-live="polite">
          {backendStatus === 'checking' && <span>Checking backend…</span>}
          {backendStatus === 'online' && (
            <span className="status-online">Backend connected</span>
          )}
          {backendStatus === 'offline' && (
            <span className="status-offline">Backend unavailable</span>
          )}
        </div>
      </header>

      <WorkflowStepper
        resumeUploaded={resumeUploaded}
        resumeParsed={resumeParsed}
        jdUploaded={jdUploaded}
        jdParsed={jdParsed}
        matchComplete={matchComplete}
      />

      <div className="workflow-grid">
        <section className="panel" aria-labelledby="resume-section-heading">
          <h2 id="resume-section-heading">1. Resume</h2>

          <div className="field">
            <label htmlFor={resumeInputId}>Resume PDF</label>
            <input
              id={resumeInputId}
              type="file"
              accept="application/pdf,.pdf"
              onChange={(event) => {
                setResumeFile(event.target.files?.[0] ?? null)
              }}
            />
            <p className="field-hint">Only PDF files are supported.</p>
          </div>

          <div className="panel-actions">
            <Button
              onClick={onResumeUpload}
              disabled={!canUploadResume}
              loading={resumeUpload.status === 'loading'}
            >
              Upload Resume
            </Button>
            <Button
              variant="secondary"
              onClick={() => void handleParseResume()}
              disabled={!canParseResume}
              loading={parsedResume.status === 'loading'}
            >
              Parse Resume
            </Button>
          </div>

          {resumeUpload.status === 'error' && resumeUpload.error && (
            <Alert variant="error" onRetry={onResumeUpload}>
              {resumeUpload.error}
            </Alert>
          )}

          {resumeUpload.status === 'success' && resumeUpload.data && (
            <div className="upload-summary">
              <p>
                Uploaded <strong>{resumeUpload.data.filename}</strong> (
                {resumeUpload.data.char_count.toLocaleString()} characters)
              </p>
            </div>
          )}

          {parsedResume.status === 'loading' && (
            <LoadingSpinner label="Parsing resume" />
          )}

          {parsedResume.status === 'error' && parsedResume.error && (
            <Alert
              variant="error"
              onRetry={() => void handleParseResume()}
            >
              {parsedResume.error}
            </Alert>
          )}

          {parsedResume.status === 'success' && parsedResume.data && (
            <ParsedResumeCard data={parsedResume.data} />
          )}
        </section>

        <section className="panel" aria-labelledby="jd-section-heading">
          <h2 id="jd-section-heading">2. Job Description</h2>

          <div className="tab-row" role="tablist" aria-label="Job description input mode">
            <button
              type="button"
              role="tab"
              aria-selected={jdInputMode === 'file'}
              className={jdInputMode === 'file' ? 'tab active' : 'tab'}
              onClick={() => setJdInputMode('file')}
            >
              Upload File
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={jdInputMode === 'text'}
              className={jdInputMode === 'text' ? 'tab active' : 'tab'}
              onClick={() => setJdInputMode('text')}
            >
              Paste Text
            </button>
          </div>

          {jdInputMode === 'file' ? (
            <div className="field">
              <label htmlFor={jdFileInputId}>Job description file</label>
              <input
                id={jdFileInputId}
                type="file"
                accept="application/pdf,.pdf,text/plain,.txt"
                onChange={(event) => {
                  setJdFile(event.target.files?.[0] ?? null)
                }}
              />
              <p className="field-hint">PDF or TXT files are supported.</p>
            </div>
          ) : (
            <div className="field">
              <label htmlFor={jdTextInputId}>Job description text</label>
              <textarea
                id={jdTextInputId}
                rows={8}
                value={jdText}
                placeholder="Paste the full job description here…"
                onChange={(event) => setJdText(event.target.value)}
              />
            </div>
          )}

          <div className="panel-actions">
            <Button
              onClick={onJdUpload}
              disabled={!canUploadJd}
              loading={jdUpload.status === 'loading'}
            >
              Upload Job Description
            </Button>
            <Button
              variant="secondary"
              onClick={() => void handleParseJd()}
              disabled={!canParseJd}
              loading={parsedJd.status === 'loading'}
            >
              Parse Job Description
            </Button>
          </div>

          {jdUpload.status === 'error' && jdUpload.error && (
            <Alert variant="error" onRetry={onJdUpload}>
              {jdUpload.error}
            </Alert>
          )}

          {jdUpload.status === 'success' && jdUpload.data && (
            <div className="upload-summary">
              <p>
                Uploaded <strong>{jdUpload.data.filename}</strong> (
                {jdUpload.data.char_count.toLocaleString()} characters)
              </p>
            </div>
          )}

          {parsedJd.status === 'loading' && (
            <LoadingSpinner label="Parsing job description" />
          )}

          {parsedJd.status === 'error' && parsedJd.error && (
            <Alert variant="error" onRetry={() => void handleParseJd()}>
              {parsedJd.error}
            </Alert>
          )}

          {parsedJd.status === 'success' && parsedJd.data && (
            <ParsedJdCard data={parsedJd.data} />
          )}
        </section>
      </div>

      <section className="panel match-panel" aria-labelledby="match-section-heading">
        <div className="match-panel-header">
          <h2 id="match-section-heading">3. Matching</h2>
          <Button variant="ghost" onClick={onReset}>
            Start Over
          </Button>
        </div>

        {!resumeParsed || !jdParsed ? (
          <p className="empty-note">
            Parse both the resume and job description before running matching.
          </p>
        ) : (
          <div className="panel-actions">
            <Button
              onClick={() => void handleRunMatch()}
              disabled={!canRunMatch}
              loading={matchResult.status === 'loading'}
            >
              Run Matching
            </Button>
          </div>
        )}

        {matchResult.status === 'loading' && (
          <LoadingSpinner label="Running matching" />
        )}

        {matchResult.status === 'error' && matchResult.error && (
          <Alert variant="error" onRetry={() => void handleRunMatch()}>
            {matchResult.error}
          </Alert>
        )}

        {matchResult.status === 'success' && matchResult.data && (
          <MatchResults data={matchResult.data} />
        )}
      </section>
    </div>
  )
}
