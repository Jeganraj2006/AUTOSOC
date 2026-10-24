import os

k8s_dir = "infrastructure/kubernetes/base"
os.makedirs(k8s_dir, exist_ok=True)

manifests = {
    "web-deployment.yaml": """apiVersion: apps/v1
kind: Deployment
metadata:
  name: autosoc-web
  namespace: autosoc
spec:
  replicas: 1
  selector:
    matchLabels:
      app: autosoc-web
  template:
    metadata:
      labels:
        app: autosoc-web
    spec:
      containers:
      - name: web
        image: autosoc/web:latest
        ports:
        - containerPort: 3000
        envFrom:
        - configMapRef:
            name: autosoc-config
---
apiVersion: v1
kind: Service
metadata:
  name: autosoc-web
  namespace: autosoc
spec:
  selector:
    app: autosoc-web
  ports:
    - protocol: TCP
      port: 3000
      targetPort: 3000
""",
    "workers-deployment.yaml": """apiVersion: apps/v1
kind: Deployment
metadata:
  name: autosoc-worker-ingestion
  namespace: autosoc
spec:
  replicas: 1
  selector:
    matchLabels:
      app: worker-ingestion
      role: worker
  template:
    metadata:
      labels:
        app: worker-ingestion
        role: worker
    spec:
      containers:
      - name: worker
        image: autosoc/worker-ingestion:latest
        envFrom:
        - configMapRef:
            name: autosoc-config
        - secretRef:
            name: autosoc-secrets
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
""",
    "postgres-statefulset.yaml": """apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: autosoc
spec:
  serviceName: "postgres"
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: autosoc-secrets
              key: POSTGRES_USER
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: autosoc-secrets
              key: POSTGRES_PASSWORD
        - name: POSTGRES_DB
          value: autosoc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: autosoc
spec:
  selector:
    app: postgres
  ports:
    - protocol: TCP
      port: 5432
      targetPort: 5432
""",
    "ingress.yaml": """apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: autosoc-ingress
  namespace: autosoc
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  rules:
  - host: autosoc.local
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: autosoc-api
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: autosoc-web
            port:
              number: 3000
"""
}

for filename, content in manifests.items():
    with open(os.path.join(k8s_dir, filename), "w") as f:
        f.write(content)

print("Created Kubernetes manifests.")
