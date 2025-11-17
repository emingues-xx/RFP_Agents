# Script de Teste do Docker Compose
# Execute este script para validar a implementação da TAREFA_1.2

Write-Host "=== Teste do Docker Compose ===" -ForegroundColor Cyan
Write-Host ""

# 1. Validar configuração
Write-Host "1. Validando configuração do docker-compose..." -ForegroundColor Yellow
docker-compose config --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Configuração válida" -ForegroundColor Green
} else {
    Write-Host "   ✗ Erro na configuração" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 2. Subir serviços básicos primeiro
Write-Host "2. Subindo serviços de infraestrutura..." -ForegroundColor Yellow
Write-Host "   - PostgreSQL"
Write-Host "   - Redis"
docker-compose up -d postgres redis
Start-Sleep -Seconds 5
Write-Host ""

# 3. Verificar saúde dos serviços
Write-Host "3. Verificando saúde dos serviços..." -ForegroundColor Yellow
docker-compose ps
Write-Host ""

# 4. Testar conexão PostgreSQL
Write-Host "4. Testando conexão com PostgreSQL..." -ForegroundColor Yellow
docker-compose exec -T postgres psql -U postgres -d rfp_agents -c "SELECT 1;" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ PostgreSQL funcionando" -ForegroundColor Green
} else {
    Write-Host "   ✗ Erro ao conectar no PostgreSQL" -ForegroundColor Red
}
Write-Host ""

# 5. Testar conexão Redis
Write-Host "5. Testando conexão com Redis..." -ForegroundColor Yellow
docker-compose exec -T redis redis-cli --no-auth-warning -a redis_password ping 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Redis funcionando" -ForegroundColor Green
} else {
    Write-Host "   ✗ Erro ao conectar no Redis" -ForegroundColor Red
}
Write-Host ""

# 6. Subir serviços restantes (opcional)
Write-Host "6. Para testar todos os serviços, execute:" -ForegroundColor Cyan
Write-Host "   docker-compose up -d" -ForegroundColor White
Write-Host ""

Write-Host "=== Teste Concluído ===" -ForegroundColor Cyan

