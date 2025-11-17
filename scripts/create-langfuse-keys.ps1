# Script para criar e obter keys do Langfuse
# Execute após o Langfuse estar acessível em http://localhost:3020

Write-Host "`n=== Configurar Keys do Langfuse ===" -ForegroundColor Cyan
Write-Host "`n📋 Passos:`n" -ForegroundColor Yellow

Write-Host "1. Acesse: http://localhost:3020" -ForegroundColor White
Write-Host "2. Crie sua conta (primeira vez)" -ForegroundColor White
Write-Host "3. IMPORTANTE: Crie o bucket no MinIO primeiro:" -ForegroundColor Yellow
Write-Host "   - Acesse: http://localhost:9001" -ForegroundColor Gray
Write-Host "   - Login: minioadmin / minioadmin" -ForegroundColor Gray
Write-Host "   - Crie um bucket chamado 'langfuse'`n" -ForegroundColor Gray
Write-Host "4. Volte ao Langfuse e vá em Settings > API Keys" -ForegroundColor White
Write-Host "5. Clique em 'Create API Key'" -ForegroundColor White
Write-Host "6. Copie as keys geradas`n" -ForegroundColor White

$publicKey = Read-Host "Cole a LANGFUSE_PUBLIC_KEY (pk-...)"
$secretKey = Read-Host "Cole a LANGFUSE_SECRET_KEY (sk-...)"

if ($publicKey -and $secretKey) {
    # Ler .env se existir, senão criar novo
    $envContent = @()
    if (Test-Path ".env") {
        $envContent = Get-Content ".env"
    } elseif (Test-Path ".env.example") {
        $envContent = Get-Content ".env.example"
    }
    
    # Remover linhas antigas do Langfuse
    $envContent = $envContent | Where-Object { 
        $_ -notmatch "^LANGFUSE_PUBLIC_KEY=" -and 
        $_ -notmatch "^LANGFUSE_SECRET_KEY=" -and
        $_ -notmatch "^LANGFUSE_URL="
    }
    
    # Adicionar novas keys
    $envContent += ""
    $envContent += "# Langfuse"
    $envContent += "LANGFUSE_URL=http://localhost:3020"
    $envContent += "LANGFUSE_PUBLIC_KEY=$publicKey"
    $envContent += "LANGFUSE_SECRET_KEY=$secretKey"
    
    # Salvar .env
    $envContent | Set-Content ".env"
    
    Write-Host "`n✅ Keys do Langfuse adicionadas ao .env!`n" -ForegroundColor Green
    Write-Host "📝 Próximos passos:" -ForegroundColor Yellow
    Write-Host "   - Reinicie os serviços para aplicar as mudanças:" -ForegroundColor White
    Write-Host "     docker-compose restart app`n" -ForegroundColor Gray
} else {
    Write-Host "`n❌ Keys não fornecidas. Execute o script novamente quando tiver as keys.`n" -ForegroundColor Red
}

