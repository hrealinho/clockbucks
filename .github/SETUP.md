# GitHub Repository Settings for Clock Bucks

## Required Secrets
Add these secrets to your GitHub repository settings (Settings → Secrets and variables → Actions):

### Container Registry
- `GITHUB_TOKEN` - Automatically provided by GitHub

### Kubernetes Deployment
- `KUBE_CONFIG_STAGING` - Base64 encoded kubeconfig for staging cluster
- `KUBE_CONFIG_PRODUCTION` - Base64 encoded kubeconfig for production cluster

### Notifications
- `SLACK_WEBHOOK` - Slack webhook URL for deployment notifications
- `EMAIL_USERNAME` - Email address for failure notifications
- `EMAIL_PASSWORD` - Email app password for SMTP
- `NOTIFICATION_EMAIL` - Email address to receive notifications

## Environment Configuration
Create these environments in GitHub (Settings → Environments):

### staging
- Required reviewers: (optional)
- Deployment branches: `develop`, `master`
- Environment secrets: Any staging-specific configurations

### production
- Required reviewers: (recommended - add team members)
- Deployment branches: `main`, `master`
- Environment secrets: Any production-specific configurations

## Branch Protection Rules
Recommended branch protection rules (Settings → Branches):

### For `main` branch:
- ✅ Require a pull request before merging
- ✅ Require approvals: 1
- ✅ Dismiss stale PR approvals when new commits are pushed
- ✅ Require review from code owners
- ✅ Require status checks to pass before merging
  - Required status checks:
    - `🧪 Test & Quality Checks`
    - `🔒 Security Scan`
    - `🐳 Build Docker Images`
- ✅ Require branches to be up to date before merging
- ✅ Require linear history
- ✅ Include administrators

### For `develop` branch:
- ✅ Require a pull request before merging
- ✅ Require status checks to pass before merging
  - Required status checks:
    - `🧪 Test & Quality Checks`
    - `🔒 Security Scan`

## Repository Settings

### General
- ✅ Allow merge commits
- ❌ Allow squash merging (optional)
- ❌ Allow rebase merging (optional)
- ✅ Automatically delete head branches

### Security
- ✅ Enable vulnerability alerts
- ✅ Enable security updates
- ✅ Enable secret scanning
- ✅ Enable push protection for secrets

### Code security and analysis
- ✅ Dependency graph
- ✅ Dependabot alerts
- ✅ Dependabot security updates
- ✅ CodeQL analysis

## Webhook Configuration (Optional)
If using external services:

### Slack Integration
1. Create a Slack app in your workspace
2. Add incoming webhooks capability
3. Generate webhook URL
4. Add to repository secrets as `SLACK_WEBHOOK`

### Email Notifications
1. Use an app-specific password for Gmail/Outlook
2. Add credentials to repository secrets
3. Configure SMTP settings in workflow

## Setup Instructions

1. **Fork/Clone the repository**
   ```bash
   git clone https://github.com/hrealinho/clock-bucks.git
   cd clock-bucks
   ```

2. **Configure repository settings**
   - Go to repository Settings
   - Add required secrets
   - Create environments
   - Configure branch protection

3. **Update workflow files**
   - Replace `your-username` with your GitHub username
   - Update domain names and URLs
   - Customize notification settings

4. **Test the pipeline**
   - Create a feature branch
   - Make a small change
   - Open a pull request
   - Verify all workflows run successfully

5. **Deploy to staging**
   - Merge to `develop` branch
   - Monitor staging deployment

6. **Deploy to production**
   - Merge to `main` branch
   - Monitor production deployment

## Troubleshooting

### Common Issues
1. **Secret not found**: Ensure secrets are added at repository level
2. **Kubernetes deployment fails**: Check kubeconfig and cluster connectivity
3. **Docker build fails**: Verify Dockerfile syntax and dependencies
4. **Tests fail**: Check test environment and dependencies

### Logs and Monitoring
- Check GitHub Actions logs for detailed error messages
- Monitor Kubernetes pods: `kubectl get pods -n clockbucks-production`
- Check application logs: `kubectl logs -f deployment/clockbucks-api -n clockbucks-production`
