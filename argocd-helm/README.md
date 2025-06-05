# ArgoCD Helm Applications

This directory contains ArgoCD Application manifests for deploying the application using Helm charts with hierarchical values.

## Overview

These applications deploy the same Flask application using Helm instead of Kustomize, allowing for side-by-side comparison of both deployment methods.

## Applications

### Development
- **Name**: `nodefront-helm-development`
- **Namespace**: `development-helm`
- **Values**: `values/development.yaml` (standalone)
- **Auto-sync**: Enabled

### Staging Environments
- **East US**: `nodefront-helm-staging-eastus` → `staging-eastus-helm`
- **West US3**: `nodefront-helm-staging-westus3` → `staging-westus3-helm`
- **Values**: `values/staging.yaml` + region-specific overrides
- **Auto-sync**: Enabled

### Production Environments
- **East US**: `nodefront-helm-production-eastus` → `production-eastus-helm`
- **West US3**: `nodefront-helm-production-westus3` → `production-westus3-helm`
- **Values**: `values/production.yaml` + region-specific overrides
- **Auto-sync**: **Disabled** (manual sync for safety)

## App-of-Apps Pattern

The `app-of-apps.yaml` creates a parent application that manages all Helm-based applications:

```bash
kubectl apply -f argocd-helm/app-of-apps.yaml
```

## Deployment Comparison

### Helm vs Kustomize ArgoCD Applications

| Aspect | Kustomize Apps | Helm Apps |
|--------|---------------|-----------|
| **Namespaces** | `development`, `staging-*`, `production-*` | `*-helm` (separate) |
| **Source Path** | `environments/*/` | `helm/myapp` |
| **Configuration** | Strategic merge patches | Hierarchical values files |
| **Values** | Complex patch operations | Simple YAML overrides |
| **Names** | Manual prefix handling | Template-based naming |

### Namespace Strategy

Helm applications use separate namespaces with `-helm` suffix to avoid conflicts:

- **Kustomize**: `development`, `staging-eastus`, `production-eastus`
- **Helm**: `development-helm`, `staging-eastus-helm`, `production-eastus-helm`

## Features

### Hierarchical Values
Helm applications use layered values files:
```yaml
helm:
  valueFiles:
    - values/production.yaml      # Environment layer
    - values/production-eastus.yaml  # Region layer
```

### Image Tag Management
Each application can override image tags via parameters:
```yaml
helm:
  parameters:
    - name: image.tag
      value: v1.0.0
```

### Production Safety
Production applications have:
- Manual sync (no auto-sync)
- Increased retry limits
- Extended revision history

## Usage

### Apply Individual Applications
```bash
# Development
kubectl apply -f argocd-helm/development.yaml

# Staging East
kubectl apply -f argocd-helm/staging-eastus.yaml

# Production East (manual sync required)
kubectl apply -f argocd-helm/production-eastus.yaml
```

### Apply All Applications
```bash
# App-of-Apps pattern
kubectl apply -f argocd-helm/app-of-apps.yaml
```

### View Applications
```bash
# List all Helm applications
kubectl get applications -n argocd -l deployment-method=helm

# Get specific application
kubectl get application nodefront-helm-staging-eastus -n argocd -o yaml
```

## Benefits Over Kustomize

1. **Cleaner Configuration**: Values files vs complex patches
2. **No Naming Issues**: Template-based resource naming
3. **Hierarchical Inheritance**: Shared settings with region overrides
4. **Conditional Logic**: Enable/disable features easily
5. **Type Safety**: Helm validates value types
6. **Rollback Support**: Native Helm rollback capabilities

## Migration Path

To migrate from Kustomize to Helm:

1. **Deploy Helm applications** in parallel (different namespaces)
2. **Test functionality** in `-helm` namespaces
3. **Validate configuration** matches Kustomize output
4. **Switch traffic** to Helm deployments
5. **Remove Kustomize applications** after validation