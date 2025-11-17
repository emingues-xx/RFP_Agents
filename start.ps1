# Script para iniciar o ambiente Docker
# Uso: .\start.ps1 [comando]
# Comandos: up, down, logs, status, restart, shell

param(
    [Parameter(Position=0)]
    [ValidateSet("up", "down", "logs", "status", "restart", "shell", "build", "help")]
    [string]$Command = "up"
)

$ErrorActionPreference = "Stop"

function Show-Help {
    Write-Host "`n=== RFP Agents - Docker Helper ===" -ForegroundColor Cyan
    Write-Host "`nUso: .\start.ps1 [comando]`n" -ForegroundColor Yellow
    Write-Host "Comandos disponíveis:" -ForegroundColor White
    Write-Host "  up       - Subir todos os serviços (padrão)" -ForegroundColor Gray
    Write-Host "  down     - Parar todos os serviços" -ForegroundColor Gray
    Write-Host "  logs     - Ver logs dos serviços" -ForegroundColor Gray
    Write-Host "  status   - Ver status dos serviços" -ForegroundColor Gray
    Write-Host "  restart  - Reiniciar todos os serviços" -ForegroundColor Gray
    Write-Host "  shell    - Abrir shell no container da aplicação" -ForegroundColor Gray
    Write-Host "  build    - Rebuild da aplicação" -ForegroundColor Gray
    Write-Host "  help     - Mostrar esta ajuda`n" -ForegroundColor Gray
}

function Test-Docker {
    try {
        docker --version | Out-Null
        docker-compose --version | Out-Null
        return $true
    } catch {
        Write-Host "❌ Docker não encontrado. Instale Docker Desktop primeiro." -ForegroundColor Red
        return $false
    }
}

function Test-DockerRunning {
    try {
        docker ps | Out-Null
        return $true
    } catch {
        Write-Host "❌ Docker não está rodando. Inicie o Docker Desktop." -ForegroundColor Red
        return $false
    }
}

function Start-Services {
    Write-Host "`n🚀 Subindo serviços Docker..." -ForegroundColor Cyan
    
    if (-not (Test-Path ".env")) {
        Write-Host "⚠️  Arquivo .env não encontrado. Copiando de .env.example..." -ForegroundColor Yellow
        if (Test-Path ".env.example") {
            Copy-Item ".env.example" ".env"
            Write-Host "✅ Arquivo .env criado. Configure as variáveis de ambiente antes de continuar." -ForegroundColor Yellow
        } else {
            Write-Host "❌ Arquivo .env.example não encontrado!" -ForegroundColor Red
            return
        }
    }
    
    docker-compose up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ Serviços iniciados com sucesso!`n" -ForegroundColor Green
        Start-Sleep -Seconds 3
        Show-Status
        Show-AccessInfo
    } else {
        Write-Host "`n❌ Erro ao iniciar serviços. Verifique os logs." -ForegroundColor Red
    }
}

function Stop-Services {
    Write-Host "`n🛑 Parando serviços Docker..." -ForegroundColor Cyan
    docker-compose down
    Write-Host "`n✅ Serviços parados.`n" -ForegroundColor Green
}

function Show-Logs {
    Write-Host "`n📋 Logs dos serviços (Ctrl+C para sair)...`n" -ForegroundColor Cyan
    docker-compose logs -f
}

function Show-Status {
    Write-Host "`n📊 Status dos serviços:`n" -ForegroundColor Cyan
    docker-compose ps
}

function Restart-Services {
    Write-Host "`n🔄 Reiniciando serviços..." -ForegroundColor Cyan
    docker-compose restart
    Write-Host "`n✅ Serviços reiniciados.`n" -ForegroundColor Green
    Show-Status
}

function Open-Shell {
    Write-Host "`n🐚 Abrindo shell no container da aplicação...`n" -ForegroundColor Cyan
    docker-compose exec app bash
    if ($LASTEXITCODE -ne 0) {
        Write-Host "`n⚠️  Container não está rodando. Execute '.\start.ps1 up' primeiro." -ForegroundColor Yellow
    }
}

function Build-Application {
    Write-Host "`n🔨 Rebuild da aplicação...`n" -ForegroundColor Cyan
    docker-compose build app
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ Build concluído com sucesso!`n" -ForegroundColor Green
    } else {
        Write-Host "`n❌ Erro no build. Verifique os logs.`n" -ForegroundColor Red
    }
}

function Show-AccessInfo {
    Write-Host "`n🌐 Acessos disponíveis:`n" -ForegroundColor Cyan
    Write-Host "  API:          http://localhost:8000" -ForegroundColor White
    Write-Host "  Langfuse:     http://localhost:3020" -ForegroundColor White
    Write-Host "  Prometheus:   http://localhost:9090" -ForegroundColor White
    Write-Host "  Grafana:      http://localhost:3001 (admin/admin)" -ForegroundColor White
    Write-Host "  MinIO:        http://localhost:9001 (minioadmin/minioadmin)`n" -ForegroundColor White
}

# Main
if (-not (Test-Docker)) {
    exit 1
}

switch ($Command) {
    "up" {
        if (-not (Test-DockerRunning)) { exit 1 }
        Start-Services
    }
    "down" {
        if (-not (Test-DockerRunning)) { exit 1 }
        Stop-Services
    }
    "logs" {
        if (-not (Test-DockerRunning)) { exit 1 }
        Show-Logs
    }
    "status" {
        if (-not (Test-DockerRunning)) { exit 1 }
        Show-Status
    }
    "restart" {
        if (-not (Test-DockerRunning)) { exit 1 }
        Restart-Services
    }
    "shell" {
        if (-not (Test-DockerRunning)) { exit 1 }
        Open-Shell
    }
    "build" {
        if (-not (Test-DockerRunning)) { exit 1 }
        Build-Application
    }
    "help" {
        Show-Help
    }
    default {
        Write-Host "Comando desconhecido: $Command" -ForegroundColor Red
        Show-Help
    }
}

