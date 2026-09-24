output "vpc_id" {
  description = "The ID of the provisioned VPC"
  value       = aws_vpc.main.id
}

output "eks_cluster_name" {
  description = "The Amazon EKS cluster name"
  value       = aws_eks_cluster.main.name
}

output "eks_cluster_endpoint" {
  description = "Endpoint URL for Amazon EKS control plane"
  value       = aws_eks_cluster.main.endpoint
}

output "ecr_repository_url" {
  description = "Amazon ECR Repository URL for container images"
  value       = aws_ecr_repository.app.repository_url
}

output "argocd_server_url" {
  description = "URL to access ArgoCD UI"
  value       = "https://argocd.${var.environment}.internal.infra"
}

output "grafana_dashboard_url" {
  description = "URL to access Prometheus Grafana Monitoring"
  value       = "https://grafana.${var.environment}.internal.infra"
}
