# Project

## ADHD Project

A FastAPI-based backend for a productivity and focus management application using SQLAlchemy and PostgreSQL.

### Running the ADHD Project

#### With Docker Compose

```bash
cd adhd_proj
docker compose up -d
```

#### With Kubernetes

We have provided Kubernetes manifests in the `adhd_proj/k8s/` directory.

**1. Build the Docker image:**
```bash
cd adhd_proj
docker build -t adhd-api:latest .
```

**2. Apply the manifests:**
```bash
kubectl apply -f k8s/
```

**3. Check the status:**
```bash
kubectl get pods
```

Once running, the application will be accessible at [http://localhost:8000](http://localhost:8000).

**4. Tear down:**
```bash
kubectl delete -f k8s/
```