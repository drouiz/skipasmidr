# ─── Backstage — test image with SQLite ──────────────────────────────────────
# Build time: ~15-20 min | Image size: ~3-4 GB (normal for Backstage)
# This Dockerfile creates a full Backstage app at build time.
# For production, create a separate repo and use a multi-stage build.
#
# NOTE: The scaffolder plugin is removed because isolated-vm v6 fails to
# compile in Docker environments. Catalog, search and TechDocs still work.
# ─────────────────────────────────────────────────────────────────────────────
FROM node:20-bookworm

RUN apt-get update && apt-get install -y \
    python3-dev make g++ build-essential git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Create the Backstage app without the internal yarn install
# (--skip-install so we can patch deps before installing)
RUN echo "backstage" | npx --yes @backstage/create-app@latest --skip-install

WORKDIR /workspace/backstage

# Override: SQLite in-memory + Traefik URLs
COPY app-config.local.yaml .
COPY patch-backend.js /tmp/

# Remove scaffolder plugin (depends on isolated-vm which fails to compile in Docker).
# Handles both single-line and multi-line backend.add(import(...)) patterns.
# Catalog, search, TechDocs and core features are unaffected.
RUN node /tmp/patch-backend.js

RUN yarn install

RUN yarn build:backend

# Extract the bundle tarball (WORKDIR is /workspace/backstage).
# build:backend packs output into dist/bundle.tar.gz; extracting it places
# the compiled JS at packages/backend/dist/index.cjs.js (relative to WORKDIR).
RUN tar -xzf packages/backend/dist/bundle.tar.gz

EXPOSE 7007

ENV NODE_ENV=production

# Entry point produced by backstage-cli backend:bundle (relative to WORKDIR)
CMD ["node", "packages/backend/dist/index.cjs.js", \
     "--config", "app-config.yaml", \
     "--config", "app-config.local.yaml"]
