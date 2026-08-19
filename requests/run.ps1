param(
    [Parameter(Position = 0)]
    [ValidateSet(
        "help",
        "health",
        "profile",
        "unknown",
        "multiturn",
        "privacy",
        "no-auth",
        "bad-auth",
        "malformed",
        "stream"
    )]
    [string]$Case = "help",

    [string]$ServiceUrl = $(
        if ($env:SERVICE_URL) { $env:SERVICE_URL.TrimEnd("/") }
        else { "http://127.0.0.1:8000" }
    ),

    [string]$AgentBaseUrl = $(
        if ($env:AGENT_BASE_URL) { $env:AGENT_BASE_URL.TrimEnd("/") }
        else { "http://127.0.0.1:8000/v1" }
    ),

    [string]$ApiKey = $env:AGENT_API_KEY
)

$ErrorActionPreference = "Stop"
$payloadDirectory = Join-Path $PSScriptRoot "payloads"

function Show-Help {
    Write-Output "Casos disponibles:"
    Write-Output "  health      Comprueba GET /health."
    Write-Output "  profile     Pregunta válida no streaming."
    Write-Output "  unknown     Comprueba manejo de información ausente."
    Write-Output "  multiturn   Envía una transcripción con seguimiento."
    Write-Output "  privacy     Comprueba protección de datos privados."
    Write-Output "  no-auth     Omite Authorization; espera HTTP 401."
    Write-Output "  bad-auth    Utiliza una clave inválida; espera HTTP 401."
    Write-Output "  malformed   Envía JSON inválido; espera HTTP 400 o 422."
    Write-Output "  stream      Solicita SSE y evita buffering de curl."
}

function Require-ApiKey {
    if ([string]::IsNullOrWhiteSpace($ApiKey)) {
        throw "Falta AGENT_API_KEY. Defínela en la sesión de PowerShell; no la guardes en este archivo."
    }
}

function Invoke-CurlRequest {
    param(
        [Parameter(Mandatory = $true)]
        [string]$PayloadName,
        [string]$Authorization,
        [switch]$NoBuffer
    )

    $payloadPath = Join-Path $payloadDirectory $PayloadName
    if (-not (Test-Path -LiteralPath $payloadPath)) {
        throw "No existe el payload esperado: $payloadPath"
    }

    $arguments = @(
        "-sS",
        "-i",
        "-X", "POST",
        "$AgentBaseUrl/responses",
        "-H", "Content-Type: application/json"
    )
    if ($Authorization) {
        $arguments += @("-H", "Authorization: Bearer $Authorization")
    }
    if ($NoBuffer) {
        $arguments += "-N"
    }
    $arguments += @("--data-binary", "@$payloadPath")

    & curl.exe @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "curl.exe terminó con código $LASTEXITCODE."
    }
}

switch ($Case) {
    "help" {
        Show-Help
    }
    "health" {
        & curl.exe -sS -i "$ServiceUrl/health"
        if ($LASTEXITCODE -ne 0) {
            throw "No fue posible consultar $ServiceUrl/health."
        }
    }
    "profile" {
        Require-ApiKey
        Invoke-CurlRequest -PayloadName "profile.json" -Authorization $ApiKey
    }
    "unknown" {
        Require-ApiKey
        Invoke-CurlRequest -PayloadName "unknown.json" -Authorization $ApiKey
    }
    "multiturn" {
        Require-ApiKey
        Invoke-CurlRequest -PayloadName "multiturn.json" -Authorization $ApiKey
    }
    "privacy" {
        Require-ApiKey
        Invoke-CurlRequest -PayloadName "privacy.json" -Authorization $ApiKey
    }
    "no-auth" {
        Invoke-CurlRequest -PayloadName "profile.json"
    }
    "bad-auth" {
        Invoke-CurlRequest -PayloadName "profile.json" -Authorization "invalid-manual-test-key"
    }
    "malformed" {
        Require-ApiKey
        Invoke-CurlRequest -PayloadName "malformed.json" -Authorization $ApiKey
    }
    "stream" {
        Require-ApiKey
        Invoke-CurlRequest -PayloadName "stream.json" -Authorization $ApiKey -NoBuffer
    }
}

