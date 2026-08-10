/**
 * URL Sanitization & Security Helpers.
 * Prevents DOM XSS, JavaScript scheme execution, and open redirect vulnerabilities.
 */

const ALLOWED_SCHEMES = new Set(['http:', 'https:']);

/**
 * Validates whether a given URL string is a safe HTTP/HTTPS URL or relative path.
 * Disallows javascript:, data:, vbscript:, and control characters.
 */
export function isSafeUrl(url: string): boolean {
  if (!url || typeof url !== 'string') {
    return false;
  }

  const trimmed = url.trim();

  // Disallow control characters and newlines (CRLF injection)
  for (let i = 0; i < trimmed.length; i++) {
    const code = trimmed.charCodeAt(i);
    if (code < 32 || code === 127) {
      return false;
    }
  }

  // Safe relative paths starting with / (e.g. /api or /auth)
  if (trimmed.startsWith('/') && !trimmed.startsWith('//') && !trimmed.startsWith('/\\')) {
    return true;
  }

  try {
    const parsed = new URL(trimmed, window.location.origin);
    return ALLOWED_SCHEMES.has(parsed.protocol);
  } catch {
    return false;
  }
}

/**
 * Constructs a safe redirect or API target URL.
 * Throws an Error if the base URL or constructed URL is unsafe.
 */
export function buildSafeTargetUrl(baseUrl: string, path: string): string {
  const cleanBase = baseUrl.trim().replace(/\/+$/, '');
  const cleanPath = path.trim().replace(/^\/+/, '');

  if (!isSafeUrl(cleanBase)) {
    throw new Error(`Invalid or unsafe base URL: ${cleanBase}`);
  }

  const fullUrl = `${cleanBase}/${cleanPath}`;
  if (!isSafeUrl(fullUrl)) {
    throw new Error(`Unsafe constructed target URL: ${fullUrl}`);
  }

  return fullUrl;
}
