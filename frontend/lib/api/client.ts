const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface OutputFile {
  filename: string;
  size_bytes: number;
  download_url: string;
  mime_type: string;
  metadata?: Record<string, any>;
}

export interface JobProgress {
  step: string;
  percentage: number;
  message: string;
}

export interface JobResponse {
  id: string;
  tool: string;
  status: "queued" | "processing" | "completed" | "failed" | "cancelled";
  progress: JobProgress;
  created_at: string;
  updated_at: string;
  files_count: number;
  outputs: OutputFile[];
  error?: string;
  execution_time_seconds?: number;
  stats?: Record<string, any>;
}

export async function createJob(
  tool: string,
  files: File[] = [],
  options?: Record<string, any>,
  htmlContent?: string
): Promise<JobResponse> {
  const formData = new FormData();
  formData.append("tool", tool);

  if (options) {
    formData.append("options", JSON.stringify(options));
  }

  if (htmlContent) {
    formData.append("html_content", htmlContent);
  }

  for (const file of files) {
    formData.append("files", file);
  }

  const res = await fetch(`${API_BASE_URL}/api/jobs`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Upload failed with HTTP ${res.status}`);
  }

  return res.json();
}

export async function getJobStatus(jobId: string): Promise<JobResponse> {
  const res = await fetch(`${API_BASE_URL}/api/jobs/${jobId}`, {
    cache: "no-store",
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch job status: HTTP ${res.status}`);
  }

  return res.json();
}

export function getDownloadUrl(jobId: string, filename?: string): string {
  const base = `${API_BASE_URL}/api/jobs/${jobId}/download`;
  return filename ? `${base}?filename=${encodeURIComponent(filename)}` : base;
}

export async function cancelJob(jobId: string): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/jobs/${jobId}`, {
      method: "DELETE",
    });
    return res.ok;
  } catch {
    return false;
  }
}

export async function inspectPdf(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE_URL}/api/tools/inspect-pdf`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    throw new Error("Failed to inspect PDF");
  }

  return res.json();
}

export async function getHealth() {
  const res = await fetch(`${API_BASE_URL}/api/health`, {
    cache: "no-store",
  });
  if (!res.ok) return null;
  return res.json();
}
