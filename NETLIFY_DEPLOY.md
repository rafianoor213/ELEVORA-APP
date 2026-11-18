# Netlify deployment

This repository contains the redesigned ELEVORA AI React/Vite frontend. Netlify serves the frontend while the AI API remains on the existing AppDeploy backend.

## Build settings
- Base directory: repository root
- Build command: `npm run build`
- Publish directory: `dist`
- Node.js: 22 (configured in `netlify.toml`)

The `/api/*` rewrite in `netlify.toml` proxies AI requests to the existing AppDeploy backend. Keep that backend deployed for AI advisor and project-feedback features.

## Deploy
Import `rafianoor213/ELEVORA-APP` from GitHub in Netlify and deploy the `main` branch. Future commits to `main` will trigger deploys automatically.
