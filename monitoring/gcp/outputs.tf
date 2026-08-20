output "uptime_check_id" {
  description = "Identificador de la verificación pública creada."
  value       = google_monitoring_uptime_check_config.agent_health.uptime_check_id
}

output "alert_policy_name" {
  description = "Nombre completo de la política de indisponibilidad."
  value       = google_monitoring_alert_policy.agent_unavailable.name
}
