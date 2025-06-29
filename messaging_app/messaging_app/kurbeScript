#!/usr/bin/env pwsh

# Check if minikube is installed
try {
    $minikubeCheck = Get-Command minikube -ErrorAction Stop
    Write-Host "Minikube is installed at: $($minikubeCheck.Source)"
} catch {
    Write-Host "Minikube is not installed. Please install minikube first."
    exit 1
}

# Start minikube cluster
Write-Host "Starting minikube cluster..."
minikube start --driver=docker

# Verify cluster is running
Write-Host "Verifying cluster status..."
kubectl cluster-info

# Get available pods in all namespaces
Write-Host "Retrieving available pods..."
kubectl get pods --all-namespaces
