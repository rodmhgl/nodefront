# Argo CD Application Manifests

This directory contains Argo CD application manifests for deploying the nodefront Flask application across different environments.

## Structure

```
argo-cd/
├── appproject.yaml                    # Argo CD AppProject definition
├── applications/                      # Individual application manifests
│   ├── nodefront-development.yaml     # Development environment
│   ├── nodefront-staging.yaml         # Staging environment
│   └── nodefront-production.yaml      # Production environment
├── kustomization.yaml                 # Kustomize configuration
└── README.md                          # This file
```

## Prerequisites

1. Argo CD must be installed in your Kubernetes cluster
2. Update the repository URL in all application manifests from `https://github.com/rodstewart/nodefront.git` to your actual repository URL
3. Ensure the Argo CD server has access to your Git repository

## Deployment

### Option 1: Deploy All Resources Using Kustomize

```bash
# Preview the resources
kubectl kustomize argo-cd/

# Apply all resources
kubectl apply -k argo-cd/
```

### Option 2: Deploy Individual Resources

```bash
# Create the AppProject first
kubectl apply -f argo-cd/appproject.yaml

# Deploy individual applications
kubectl apply -f argo-cd/applications/nodefront-development.yaml
kubectl apply -f argo-cd/applications/nodefront-staging.yaml
kubectl apply -f argo-cd/applications/nodefront-production.yaml
```

### Option 3: App of Apps Pattern

Create a parent application that manages all environment applications:

```bash
kubectl apply -f argo-cd/app-of-apps.yaml
```

## Environment Configuration

### Development Environment
- **Application Name**: nodefront-development
- **Namespace**: nodefront-dev
- **Sync Policy**: Automated with self-healing
- **Features**: 
  - Auto-sync enabled
  - Prune enabled
  - Self-healing enabled

### Staging Environment
- **Application Name**: nodefront-staging
- **Namespace**: nodefront-staging
- **Sync Policy**: Automated with self-healing
- **Features**:
  - Auto-sync enabled
  - Prune enabled
  - Self-healing enabled
  - Apply out-of-sync only

### Production Environment
- **Application Name**: nodefront-production
- **Namespace**: nodefront-prod
- **Sync Policy**: Manual (for safety)
- **Features**:
  - Manual sync required
  - Extended revision history (20 revisions)
  - Sync windows configured (Monday-Friday 6AM-6PM UTC)
  - Higher criticality label

## AppProject Features

The `nodefront` AppProject includes:

### RBAC Roles
- **admin**: Full access to all applications
- **developer**: Read and sync permissions
- **viewer**: Read-only access

### Sync Windows
Production deployments are restricted to:
- Monday through Friday
- 6:00 AM to 6:00 PM UTC
- Manual sync override available

### Resource Whitelisting
- All namespaced resources are allowed
- Namespace creation is allowed

## Managing Applications

### Sync an Application

```bash
# Using Argo CD CLI
argocd app sync nodefront-development

# Using kubectl
kubectl patch application nodefront-development -n argocd --type merge -p '{"metadata": {"annotations": {"argocd.argoproj.io/refresh": "hard"}}}'
```

### Check Application Status

```bash
# Using Argo CD CLI
argocd app get nodefront-staging

# Using kubectl
kubectl get application nodefront-staging -n argocd
```

### Enable Auto-Sync for Production

To enable automated sync for production, edit the production application manifest and uncomment the automated sync policy:

```yaml
syncPolicy:
  automated:
    prune: true
    selfHeal: true
    allowEmpty: false
```

## Troubleshooting

### Application Not Syncing
1. Check if the repository URL is correct
2. Verify Argo CD has access to the Git repository
3. Check application logs: `argocd app logs nodefront-<env>`

### Sync Windows
If production sync is blocked:
1. Check current time against sync window
2. Use manual sync override if urgent
3. Review sync window configuration in appproject.yaml

### Resource Conflicts
1. Check if resources exist in target namespace
2. Verify RBAC permissions
3. Check for resource quotas or limit ranges

## Security Considerations

1. Production uses manual sync by default
2. Sync windows prevent accidental production deployments
3. RBAC roles limit access based on team membership
4. Each environment uses a separate namespace
5. Resource whitelisting prevents unauthorized resource types

## Best Practices

1. Always test changes in development first
2. Use staging for pre-production validation
3. Review production changes during allowed sync windows
4. Monitor application health after deployments
5. Keep revision history for rollback capability
6. Use Git tags for production releases

## Customization

To customize for your environment:

1. Update repository URLs in all application manifests
2. Adjust namespaces to match your convention
3. Modify sync windows in appproject.yaml
4. Update RBAC group names to match your organization
5. Adjust resource limits and requests in Kustomize overlays
