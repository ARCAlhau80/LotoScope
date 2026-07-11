const MAX_INPUT_LENGTH = 2000
const SQL_PATTERNS = [
  /'.*OR.*'/, /'.*AND.*'/, /SELECT.*FROM/i, /DROP\s+TABLE/i,
  /DELETE\s+FROM/i, /INSERT\s+INTO/i, /UPDATE\s+.*SET/i,
  /CREATE\s+TABLE/i, /ALTER\s+TABLE/i, /EXEC\s*\(/i,
  /EXECUTE\s*\(/i, /UNION\s+SELECT/i, /--/, /\/\*.*\*\//,
  /;\s*DROP/i, /WAITFOR\s+DELAY/i, /BENCHMARK\s*\(/i,
  /INFORMATION_SCHEMA/i, /sysobjects/i, /xp_cmdshell/i,
]
const INJECTION_PATTERNS = [
  /ignore.*(?:instruction|prompt|system|context)/i,
  /forget.*(?:everything|previous|above|instructions)/i,
  /you are now/i, /act as/i, /pretend/i,
  /system.*prompt/i, /new.*instruction/i,
  /override/i, /disregard/i, /ignore.*previous/i,
  /reveal.*prompt/i, /show.*system/i,
  /role.?play/i, /jailbreak/i,
]

export interface ValidationResult {
  valid: boolean
  error?: string
}

export function validateInput(input: string): ValidationResult {
  if (!input || input.trim().length === 0) {
    return { valid: false, error: 'Mensagem vazia.' }
  }
  if (input.length > MAX_INPUT_LENGTH) {
    return { valid: false, error: `Mensagem muito longa (máx. ${MAX_INPUT_LENGTH} caracteres).` }
  }
  for (const pattern of SQL_PATTERNS) {
    if (pattern.test(input)) {
      return { valid: false, error: 'Entrada inválida detectada.' }
    }
  }
  for (const pattern of INJECTION_PATTERNS) {
    if (pattern.test(input)) {
      return { valid: false, error: 'Tentativa de manipulação detectada.' }
    }
  }
  return { valid: true }
}
