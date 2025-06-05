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

### Hierarchical Values Installation

This chart uses a layered values approach:
- **Base defaults**: `values.yaml`
- **Environment layer**: `staging.yaml` or `production.yaml`
- **Region layer**: `staging-eastus.yaml`, `production-westus3.yaml`, etc.

```bash
# Development (standalone)
helm install myapp-dev ./helm/myapp \
  -f ./helm/myapp/values/development.yaml \
  -n development --create-namespace

# Staging East US (layered: defaults -> staging -> region)
helm install myapp-staging-east ./helm/myapp \
  -f ./helm/myapp/values/staging.yaml \
  -f ./helm/myapp/values/staging-eastus.yaml \
  -n staging-eastus --create-namespace

# Staging West US3 (layered: defaults -> staging -> region)
helm install myapp-staging-west ./helm/myapp \
  -f ./helm/myapp/values/staging.yaml \
  -f ./helm/myapp/values/staging-westus3.yaml \
  -n staging-westus3 --create-namespace

# Production East US (layered: defaults -> production -> region)
helm install myapp-prod-east ./helm/myapp \
  -f ./helm/myapp/values/production.yaml \
  -f ./helm/myapp/values/production-eastus.yaml \
  -n production-eastus --create-namespace

# Production West US3 (layered: defaults -> production -> region)
helm install myapp-prod-west ./helm/myapp \
  -f ./helm/myapp/values/production.yaml \
  -f ./helm/myapp/values/production-westus3.yaml \
  -n production-westus3 --create-namespace
```

### Template Generation (for testing)

```bash
# Development
helm template myapp-dev ./helm/myapp \
  -f ./helm/myapp/values/development.yaml

# Staging East with layered values
helm template myapp-staging-east ./helm/myapp \
  -f ./helm/myapp/values/staging.yaml \
  -f ./helm/myapp/values/staging-eastus.yaml

# Production West with layered values
helm template myapp-prod-west ./helm/myapp \
  -f ./helm/myapp/values/production.yaml \
  -f ./helm/myapp/values/production-westus3.yaml
```

## Hierarchical Values Structure

The chart uses a three-layer values hierarchy:

### Values Files Structure

```
values/
├── development.yaml     # Standalone dev configuration
├── staging.yaml        # Common staging settings
├── production.yaml     # Common production settings
├── staging-eastus.yaml # Staging East region overrides
├── staging-westus3.yaml # Staging West region overrides
├── production-eastus.yaml # Production East region overrides
└── production-westus3.yaml # Production West region overrides
```

### Value Inheritance Flow

1. **Base defaults** (`values.yaml`)
2. **Environment layer** (`staging.yaml` or `production.yaml`)
3. **Region layer** (`*-eastus.yaml` or `*-westus3.yaml`)

Each layer overrides the previous, allowing for:
- **Common environment settings** (all staging regions share staging.yaml)
- **Region-specific overrides** (hostnames, storage shares)
- **Minimal duplication** (change staging config once, affects all regions)

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