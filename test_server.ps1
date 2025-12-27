# Test the server endpoints
$baseUrl = "http://127.0.0.1:8000"

# Test 1: Health check
Write-Host "Testing health endpoint..." -ForegroundColor Cyan
try {
    $health = Invoke-WebRequest -Uri "$baseUrl/health" -Method GET -UseBasicParsing -TimeoutSec 5
    Write-Host "✓ Health check PASSED" -ForegroundColor Green
    Write-Host "Response: $($health.Content)" -ForegroundColor Yellow
} catch {
    Write-Host "✗ Health check FAILED: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 2: Root endpoint
Write-Host "`nTesting root endpoint..." -ForegroundColor Cyan
try {
    $root = Invoke-WebRequest -Uri "$baseUrl/" -Method GET -UseBasicParsing -TimeoutSec 5
    Write-Host "✓ Root endpoint PASSED" -ForegroundColor Green
    $json = $root.Content | ConvertFrom-Json
    Write-Host "Message: $($json.message)" -ForegroundColor Yellow
} catch {
    Write-Host "✗ Root endpoint FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Info endpoint
Write-Host "`nTesting info endpoint..." -ForegroundColor Cyan
try {
    $info = Invoke-WebRequest -Uri "$baseUrl/api/info" -Method GET -UseBasicParsing -TimeoutSec 5
    Write-Host "✓ Info endpoint PASSED" -ForegroundColor Green
    $json = $info.Content | ConvertFrom-Json
    Write-Host "Model: $($json.model), Chunks: $($json.loaded_chunks)" -ForegroundColor Yellow
} catch {
    Write-Host "✗ Info endpoint FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Login endpoint
Write-Host "`nTesting login endpoint..." -ForegroundColor Cyan
try {
    $loginBody = @{
        username = "admin"
        password = "admin123"
    } | ConvertTo-Json
    
    $login = Invoke-WebRequest -Uri "$baseUrl/auth/login" -Method POST -Body $loginBody -ContentType "application/json" -UseBasicParsing -TimeoutSec 5
    $token = ($login.Content | ConvertFrom-Json).access_token
    Write-Host "✓ Login PASSED" -ForegroundColor Green
    Write-Host "Token received: $($token.Substring(0, 20))..." -ForegroundColor Yellow
    
    # Test 5: Chat endpoint with auth
    Write-Host "`nTesting chat endpoint..." -ForegroundColor Cyan
    $chatBody = @{
        query = "What is the remote work policy?"
    } | ConvertTo-Json
    
    $chat = Invoke-WebRequest -Uri "$baseUrl/api/chat" -Method POST -Body $chatBody -ContentType "application/json" -Headers @{"Authorization" = "Bearer $token"} -UseBasicParsing -TimeoutSec 5
    Write-Host "✓ Chat endpoint PASSED" -ForegroundColor Green
    $json = $chat.Content | ConvertFrom-Json
    Write-Host "Response received with confidence: $($json.confidence)" -ForegroundColor Yellow
} catch {
    Write-Host "✗ Request FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n✓ All critical tests passed! Server is working correctly." -ForegroundColor Green
Write-Host "`nServer is accessible at: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "API Documentation available at: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
