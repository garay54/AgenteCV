variable "project_id" {
  description = "Proyecto de Google Cloud que almacenará el monitoreo."
  type        = string
}

variable "service_host" {
  description = "Host público sin esquema ni ruta, por ejemplo servicio.run.app."
  type        = string
}

variable "notification_channel_names" {
  description = "Nombres completos de canales existentes de Cloud Monitoring."
  type        = list(string)
  default     = []
}
