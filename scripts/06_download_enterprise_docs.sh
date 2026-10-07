#!/bin/bash
set -e

DOCS_DIR="$HOME/ForgeLM/data/docs"
TEMP_DIR=$(mktemp -d)

echo "🚀 Starting Enterprise Documentation Downloader..."

# Create organized subdirectories
mkdir -p "$DOCS_DIR/gitlab_runbooks"
mkdir -p "$DOCS_DIR/pagerduty_ic"
mkdir -p "$DOCS_DIR/k8s_debug"

echo ""
echo "========== 1. Fetching GitLab Production Runbooks =========="
git clone --depth 1 https://gitlab.com/gitlab-com/runbooks.git "$TEMP_DIR/gitlab"
# Copy only the high-value database and kubernetes runbooks
cp -r "$TEMP_DIR/gitlab/docs/patroni" "$DOCS_DIR/gitlab_runbooks/" 2>/dev/null || true
cp -r "$TEMP_DIR/gitlab/docs/pgbouncer" "$DOCS_DIR/gitlab_runbooks/" 2>/dev/null || true
cp -r "$TEMP_DIR/gitlab/docs/redis" "$DOCS_DIR/gitlab_runbooks/" 2>/dev/null || true
cp -r "$TEMP_DIR/gitlab/docs/kube" "$DOCS_DIR/gitlab_runbooks/" 2>/dev/null || true
echo "✅ GitLab runbooks successfully extracted."

echo ""
echo "========== 2. Fetching PagerDuty Incident Response Docs =========="
git clone --depth 1 https://github.com/PagerDuty/incident-response-docs.git "$TEMP_DIR/pagerduty"
cp -r "$TEMP_DIR/pagerduty/docs/"* "$DOCS_DIR/pagerduty_ic/"
echo "✅ PagerDuty documentation successfully extracted."

echo ""
echo "========== 3. Fetching Kubernetes Official Debugging Guides =========="
# The K8s repo is large, so this might take 30-60 seconds even with depth 1
git clone --depth 1 https://github.com/kubernetes/website.git "$TEMP_DIR/k8s"
cp -r "$TEMP_DIR/k8s/content/en/docs/tasks/debug/"* "$DOCS_DIR/k8s_debug/"
echo "✅ Kubernetes debugging guides successfully extracted."

echo ""
echo "🧹 Cleaning up temporary files..."
rm -rf "$TEMP_DIR"

echo "🎉 Done! Hundreds of enterprise markdown files have been added to $DOCS_DIR"
echo ""
echo "👉 Next Step: Run 'python scripts/05_ingest_docs.py' to vectorize the new data!"