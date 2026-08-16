import { useCallback, useState } from 'react'
import type {
  JobDescription,
  MatchResult,
  ParsedJD,
  ParsedResume,
  ResumeUploadResponse,
} from '../types/api'
import {
  parseJobDescription,
  parseResume,
  runMatch,
  uploadJobDescriptionFile,
  uploadJobDescriptionText,
  uploadResume,
} from '../services/api'
import { getErrorMessage } from '../utils/errors'

type AsyncStatus = 'idle' | 'loading' | 'success' | 'error'

interface AsyncState<T> {
  status: AsyncStatus
  data: T | null
  error: string | null
}

function idleState<T>(): AsyncState<T> {
  return { status: 'idle', data: null, error: null }
}

function loadingState<T>(previous?: AsyncState<T>): AsyncState<T> {
  return {
    status: 'loading',
    data: previous?.data ?? null,
    error: null,
  }
}

export function useScreeningWorkflow() {
  const [resumeUpload, setResumeUpload] =
    useState<AsyncState<ResumeUploadResponse>>(idleState())
  const [parsedResume, setParsedResume] =
    useState<AsyncState<ParsedResume>>(idleState())
  const [jdUpload, setJdUpload] = useState<AsyncState<JobDescription>>(
    idleState(),
  )
  const [parsedJd, setParsedJd] = useState<AsyncState<ParsedJD>>(idleState())
  const [matchResult, setMatchResult] =
    useState<AsyncState<MatchResult>>(idleState())

  const handleUploadResume = useCallback(async (file: File) => {
    setResumeUpload(loadingState())
    setParsedResume(idleState())
    setMatchResult(idleState())

    try {
      const data = await uploadResume(file)
      setResumeUpload({ status: 'success', data, error: null })
    } catch (error) {
      setResumeUpload({
        status: 'error',
        data: null,
        error: getErrorMessage(error),
      })
    }
  }, [])

  const handleParseResume = useCallback(async () => {
    const resumeId = resumeUpload.data?.resume_id
    if (!resumeId) return

    setParsedResume(loadingState())
    setMatchResult(idleState())

    try {
      const data = await parseResume(resumeId)
      setParsedResume({ status: 'success', data, error: null })
    } catch (error) {
      setParsedResume({
        status: 'error',
        data: null,
        error: getErrorMessage(error),
      })
    }
  }, [resumeUpload.data?.resume_id])

  const handleUploadJdFile = useCallback(async (file: File) => {
    setJdUpload(loadingState())
    setParsedJd(idleState())
    setMatchResult(idleState())

    try {
      const data = await uploadJobDescriptionFile(file)
      setJdUpload({ status: 'success', data, error: null })
    } catch (error) {
      setJdUpload({
        status: 'error',
        data: null,
        error: getErrorMessage(error),
      })
    }
  }, [])

  const handleUploadJdText = useCallback(async (text: string) => {
    setJdUpload(loadingState())
    setParsedJd(idleState())
    setMatchResult(idleState())

    try {
      const data = await uploadJobDescriptionText(text)
      setJdUpload({ status: 'success', data, error: null })
    } catch (error) {
      setJdUpload({
        status: 'error',
        data: null,
        error: getErrorMessage(error),
      })
    }
  }, [])

  const handleParseJd = useCallback(async () => {
    const jdId = jdUpload.data?.jd_id
    if (!jdId) return

    setParsedJd(loadingState())
    setMatchResult(idleState())

    try {
      const data = await parseJobDescription(jdId)
      setParsedJd({ status: 'success', data, error: null })
    } catch (error) {
      setParsedJd({
        status: 'error',
        data: null,
        error: getErrorMessage(error),
      })
    }
  }, [jdUpload.data?.jd_id])

  const handleRunMatch = useCallback(async () => {
    const resumeId = resumeUpload.data?.resume_id
    const jdId = jdUpload.data?.jd_id
    if (!resumeId || !jdId) return

    setMatchResult(loadingState())

    try {
      const data = await runMatch({ resume_id: resumeId, jd_id: jdId })
      setMatchResult({ status: 'success', data, error: null })
    } catch (error) {
      setMatchResult({
        status: 'error',
        data: null,
        error: getErrorMessage(error),
      })
    }
  }, [resumeUpload.data?.resume_id, jdUpload.data?.jd_id])

  const resetWorkflow = useCallback(() => {
    setResumeUpload(idleState())
    setParsedResume(idleState())
    setJdUpload(idleState())
    setParsedJd(idleState())
    setMatchResult(idleState())
  }, [])

  return {
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
  }
}

export type ScreeningWorkflow = ReturnType<typeof useScreeningWorkflow>
