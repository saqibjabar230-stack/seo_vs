# OpenSEO integration

This directory is an imported, isolated copy of
[every-app/open-seo](https://github.com/every-app/open-seo). It remains an
independent Vite/React application with its own package manager, migrations,
environment variables, and data storage.

## Run locally

From this directory:

```powershell
corepack enable
pnpm install --frozen-lockfile
Copy-Item .env.example .env.local
# Set DATAFORSEO_API_KEY and AUTH_MODE=local_noauth in .env.local
pnpm run db:migrate:local
$env:PORT = "3001"
pnpm run dev
```

The existing FastAPI dashboard links to the separate OpenSEO deployment through
the `OPENSEO_URL` environment variable. For local development, use
`http://localhost:3001`. Configure `OPENSEO_URL` in the dashboard's production
environment with the URL of the independently deployed OpenSEO app.

## Railway and Cloudflare Access

For a Railway deployment that is not protected by Cloudflare Access, set
`AUTH_MODE=local_noauth` for a trusted private deployment, or use
`AUTH_MODE=hosted` with the required Better Auth settings. Do not use
`AUTH_MODE=cloudflare_access` unless the Railway domain is intentionally placed
behind a Cloudflare Access application. Managed OAuth is only required for the
Cloudflare Access MCP flow; it is not required for a direct Railway deployment.

OpenSEO does not use the WordPress automation APIs or database. The dashboard
only provides a page shell and navigation link to the independently running
OpenSEO frontend.
