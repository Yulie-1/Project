# adhd-proj

A FastAPI-based backend for a productivity and focus management application using SQLAlchemy and PostgreSQL.

## Running with Docker Compose

To run the application and database using Docker Compose, simply execute:

```bash
docker compose up -d
```

This will build the API image if it doesn't exist and start both the `api` (on port 8000) and `db` (on port 5432) services.

## Running with Kubernetes

We have provided Kubernetes manifests in the `k8s/` directory to deploy the complete application (API + PostgreSQL) to a Kubernetes cluster.

### Prerequisites
Make sure you have a local cluster running (like Docker Desktop's Kubernetes, Minikube, or kind) and that it has access to the local `adhd-api:latest` Docker image. If you haven't built the image yet, you can build it using:

```bash
docker build -t adhd-api:latest .
```

### Deployment

To deploy all the resources (Secret, PVC, Deployments, Services), run:

```bash
kubectl apply -f k8s/
```

### Checking Status

You can monitor the status of your pods to see when they are fully up and running:

```bash
kubectl get pods
```

Wait until both the `api` and `postgres` pods show a status of `Running`. 
Once running, the application will be accessible via the LoadBalancer service at [http://localhost:8000](http://localhost:8000).

### Tearing Down

To remove all the Kubernetes resources associated with this project, run:

```bash
kubectl delete -f k8s/
```
