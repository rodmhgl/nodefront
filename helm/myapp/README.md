# MyApp Helm Chart

This Helm chart deploys the Flask-based MyApp application to Kubernetes.

## Features

- Flask application deployment with configurable resources
- Azure File storage integration for persistent volumes
- Azure Key Vault integration via Secret Store CSI driver
- Horizontal Pod Autoscaling
- Ingress with TLS support
- Environment-specific configurations

## Installation

### Prerequisites

- Helm 3.x
- Kubernetes cluster with:
  - Ingress controller (nginx)
  - cert-manager (for TLS certificates)
  - Secret Store CSI driver (for Azure Key Vault)

### Basic Installation

```bash
# Install with default values
helm install myapp ./helm/myapp

# Install with environment-specific values
helm install myapp-dev ./helm/myapp -f ./helm/myapp/values/development.yaml -n development

# Install for staging east
helm install myapp-staging ./helm/myapp -f ./helm/myapp/values/staging-eastus.yaml -n staging-eastus

# Install for production
helm install myapp-prod ./helm/myapp -f ./helm/myapp/values/production-eastus.yaml -n production-eastus
```

### Template Generation (for testing)

```bash
# Generate templates for development
helm template myapp-dev ./helm/myapp -f ./helm/myapp/values/development.yaml

# Generate templates for staging
helm template myapp-staging ./helm/myapp -f ./helm/myapp/values/staging-eastus.yaml
```

## Configuration

### Key Values

| Parameter | Description | Default |
|-----------|-------------|---------|
| `environment` | Environment name | `base` |
| `image.repository` | Container image repository | `rodstewart/nodefront` |
| `image.tag` | Container image tag | `""` |
| `replicaCount` | Number of replicas | `1` |
| `persistence.secretName` | Azure File secret name | `azure-pv-secret` |
| `persistence.shareName` | Azure File share name | `app-pages` |
| `secretStore.enabled` | Enable Azure Key Vault integration | `true` |
| `ingress.hosts[0].host` | Ingress hostname | `myapp.example.com` |

### Environment Files

- `values/development.yaml` - Development environment
- `values/staging-eastus.yaml` - Staging East US
- `values/staging-westus3.yaml` - Staging West US3
- `values/production-eastus.yaml` - Production East US
- `values/production-westus3.yaml` - Production West US3

## Comparison with Kustomize

### Advantages of Helm

1. **Cleaner Configuration**: Single values file vs multiple patches
2. **No Name Prefix Issues**: Proper template-based naming
3. **Conditional Logic**: Enable/disable features easily
4. **Type Safety**: Helm validates value types
5. **Dependency Management**: Built-in chart dependencies

### Example: Secret Store Configuration

**Kustomize Approach:**
```yaml
# Requires manual patch for each environment
- op: replace
  path: /spec/template/spec/volumes/1/csi/volumeAttributes/secretProviderClass
  value: dev-myapp-secret-provider-class
```

**Helm Approach:**
```yaml
# Automatic template generation
secretProviderClass: {{ include "myapp.fullname" . }}-secret-provider-class
# Becomes: myapp-dev-secret-provider-class
```

## Migration from Kustomize

To migrate from the existing Kustomize setup:

1. **Test Helm charts** with `helm template` commands
2. **Validate generated manifests** match Kustomize output
3. **Update ArgoCD applications** to use Helm instead of Kustomize
4. **Remove Kustomize configurations** after successful migration

## Deployment Commands

```bash
# Development
helm upgrade --install myapp-dev ./helm/myapp \
  -f ./helm/myapp/values/development.yaml \
  -n development --create-namespace

# Staging East
helm upgrade --install myapp-staging ./helm/myapp \
  -f ./helm/myapp/values/staging-eastus.yaml \
  -n staging-eastus --create-namespace

# Production East
helm upgrade --install myapp-prod ./helm/myapp \
  -f ./helm/myapp/values/production-eastus.yaml \
  -n production-eastus --create-namespace
```