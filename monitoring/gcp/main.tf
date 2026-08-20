resource "google_monitoring_uptime_check_config" "agent_health" {
  project            = var.project_id
  display_name       = "agent-api-health"
  period             = "60s"
  timeout            = "10s"
  checker_type       = "STATIC_IP_CHECKERS"
  log_check_failures = true

  http_check {
    path           = "/health"
    port           = 443
    use_ssl        = true
    validate_ssl   = true
    request_method = "GET"
  }

  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = var.service_host
    }
  }

  content_matchers {
    content = "\"status\":\"ok\""
    matcher = "CONTAINS_STRING"
  }

  user_labels = {
    service = "agent-api"
  }
}

resource "google_monitoring_alert_policy" "agent_unavailable" {
  project      = var.project_id
  display_name = "Agent API unavailable"
  combiner     = "OR"
  enabled      = true

  documentation {
    mime_type = "text/markdown"
    content   = "`GET /health` no ha respondido correctamente durante dos minutos."
  }

  conditions {
    display_name = "Public uptime check failed"

    condition_threshold {
      filter = join(" ", [
        "resource.type = \"uptime_url\"",
        "AND metric.type = \"monitoring.googleapis.com/uptime_check/check_passed\"",
        "AND metric.label.check_id = \"${google_monitoring_uptime_check_config.agent_health.uptime_check_id}\""
      ])
      comparison      = "COMPARISON_LT"
      threshold_value = 1
      duration        = "120s"

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_NEXT_OLDER"
      }

      trigger {
        count = 1
      }
    }
  }

  notification_channels = var.notification_channel_names

  alert_strategy {
    auto_close = "1800s"
  }

  user_labels = {
    severity = "critical"
    service  = "agent-api"
  }
}
