/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_WS_BASE_URL: string
  readonly VITE_PRIVY_APP_ID: string
  readonly VITE_FUUL_PROJECT_ID: string
  readonly VITE_FUUL_API_KEY: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
