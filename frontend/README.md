# Welcome to your Lovable project

[![Node.js CI](https://github.com/miltmon/clausebotai/actions/workflows/node.js.yml/badge.svg)](https://github.com/miltmon/clausebotai/actions/workflows/node.js.yml)
[![SLSA Provenance](https://github.com/miltmon/clausebotai/actions/workflows/slsa-generator.yml/badge.svg)](https://github.com/miltmon/clausebotai/actions/workflows/slsa-generator.yml)
[![Gulp Build](https://github.com/miltmon/clausebotai/actions/workflows/gulp.yml/badge.svg)](https://github.com/miltmon/clausebotai/actions/workflows/gulp.yml)

## CI/CD Workflows

This project uses several automated workflows to ensure code quality, security, and reproducible builds:

### 1. Node.js CI Workflow
**File:** `.github/workflows/node.js.yml`

Automated continuous integration workflow that runs on every push and pull request to the main branch. This workflow:
- Tests the application across multiple Node.js versions (18.x, 20.x)
- Runs ESLint for code quality checks
  Executes the test suite
- Builds the project and uploads artifacts
- Generates and signs Software Bill of Materials (SBOM) for releases
- Sends email notifications on job failures
- Uses pinned GitHub Actions (by SHA) for security
- Enforces locked dependency versions via `npm ci`

### 2. SLSA v3 Generator Workflow
**File:** `.github/workflows/slsa-generator.yml`

Provides signed artifact provenance using SLSA (Supply chain Levels for Software Artifacts) Level 3 standards. This workflow:
- Generates cryptographically signed provenance for release artifacts
  Creates and signs SBOM (Software Bill of Materials) using CycloneDX and cosign
  Produces verifiable build attestations
- Uploads signed artifacts and provenance to releases
  Uses the official SLSA GitHub generator framework
  Sends email notifications on job failures
- Ensures supply chain security and transparency

### 3. Gulp Build Workflow
**File:** `.github/workflows/gulp.yml`

Automated asset processing, linting, and minification using Gulp. This workflow:
- Processes and optimizes static assets
- Runs linting tasks on CSS/JavaScript files
- Minifies assets for production
- Executes complete Gulp build pipeline
- Uploads processed assets as artifacts
  Sends email notifications on job failures
- Uses pinned GitHub Actions for reproducibility

**Note:** All workflows use SHA pinned actions for security and locked dependency versions. Email notifications require configuring the following secrets:
- `MAIL_SERVER`: SMTP server address
- `MAIL_PORT`: SMTP server port
- `MAIL_USERNAME`: SMTP authentication username
- `MAIL_PASSWORD`: SMTP authentication password
  `NOTIFICATION_EMAIL`: Email address to receive notifications

## Project info

**URL**: https://lovable.dev/projects/35d72d2e-6e25-40e5-9b0c-c0d1a7c1b727

## How can I edit this code?

There are several ways of editing your application.

**Use Lovable**

Simply visit the [Lovable Project](https://lovable.dev/projects/35d72d2e-6e25-40e5-9b0c-c0d1a7c1b727) and start prompting.

Changes made via Lovable will be committed automatically to this repo.

**Use your preferred IDE**

If you want to work locally using your own IDE, you can clone this repo and push changes. Pushed changes will also be reflected in Lovable.

The only requirement is having Node.js & npm installed - [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)

Follow these steps:

```sh
# Step 1: Clone the repository using the project's Git URL.
git clone <your_git_url>

# Step 2: Navigate to the project directory.
cd <your_project_name>

# Step 3: Install the necessary dependencies.
npm i

# Step 4: Start the development server with auto-reloading and an instant preview.
npm run dev
```

**Edit a file directly in GitHub**

- Navigate to the desired file(s).
- Click the "Edit" button (pencil icon) at the top right of the file view.
- Make your changes and commit the changes.

**Use GitHub Codespaces**

- Navigate to the main page of your repository.
- Click on the "Code" button (green button) near the top right.
- Select the "Codespaces" tab.
- Click on "New codespace" to launch a new Codespace environment.
- Edit files directly within the Codespace and commit and push your changes once you're done.

## What technologies are used for this project?

This project is built with .

- Vite
- TypeScript
- React
- shadcn-ui
- Tailwind CSS

## How can I deploy this project?

Simply open [Lovable](https://lovable.dev/projects/35d72d2e-6e25-40e5-9b0c-c0d1a7c1b727) and click on Share -> Publish.

## I want to use a custom domain - is that possible?

We don't support custom domains (yet). If you want to deploy your project under your own domain then we recommend using Netlify. Visit our docs for more details: [Custom domains](https://docs.lovable.dev/tips-tricks/custom-domain/)
