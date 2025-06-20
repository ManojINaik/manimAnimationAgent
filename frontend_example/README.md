## Environment Variables

-APPWRITE_API_KEY: Appwrite server key

Optional:

* `GITHUB_API_TIMEOUT_MS`: Timeout for GitHub API dispatch in milliseconds (default 30000). Increase if GitHub is slow from the deployment environment.

The GitHub workflow dispatch includes automatic retry logic (3 attempts with exponential backoff) to handle network timeouts and temporary connectivity issues. 