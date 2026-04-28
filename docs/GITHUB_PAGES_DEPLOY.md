# GitHub Pages Deployment

## What Gets Deployed

GitHub Pages should host the `web/` frontend only.

That means visitors can:

- see the landing page
- watch the demo
- read the architecture and CLI reference
- follow installation steps

The native Python gesture engine still runs locally on the user's machine.

## Repo URL

Repository:

- `https://github.com/arnav-sutraway/HandOS`

Expected GitHub Pages URL:

- `https://arnav-sutraway.github.io/HandOS/`

## Setup In GitHub

1. Open `arnav-sutraway/HandOS` on GitHub.
2. Go to `Settings`.
3. Open `Pages`.
4. Under `Build and deployment`, set `Source` to `GitHub Actions`.
5. Save.

## Deploy

After Pages is set to `GitHub Actions`:

1. Push your branch to `main`.
2. GitHub Actions will run `.github/workflows/deploy-pages.yml`.
3. The workflow will build `web/` and deploy `web/dist`.
4. The site should appear at:
   `https://arnav-sutraway.github.io/HandOS/`

## Local Test

```powershell
cd web
npm install
npm run build
npm run preview
```

## Important Base Path Note

Because the repository name is `HandOS`, the Vite base path must be:

```ts
base: "/HandOS/"
```

If the repository name changes later, update `web/vite.config.ts`.
