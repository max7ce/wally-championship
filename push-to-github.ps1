# ============================================
# SCRIPT PARA SUBIR WALLY CHAMPIONSHIP A GITHUB (WINDOWS)
# ============================================

Write-Host "🚀 SUBIENDO PROYECTO A GITHUB" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""

# PASO 1: Verificar que estamos en la carpeta correcta
Write-Host "📁 Paso 1: Verificando carpeta..." -ForegroundColor Yellow
if (-not (Test-Path "README.md")) {
    Write-Host "❌ Error: Ejecutá este script desde la carpeta wally-championship/" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Carpeta correcta" -ForegroundColor Green
Write-Host ""

# PASO 2: Pedir URL del repositorio
Write-Host "📝 Paso 2: Ingresá la URL de tu repositorio GitHub" -ForegroundColor Yellow
Write-Host "Ejemplo: https://github.com/tu-usuario/wally-championship.git"
$REPO_URL = Read-Host "URL del repo"

if ([string]::IsNullOrWhiteSpace($REPO_URL)) {
    Write-Host "❌ Error: URL vacía" -ForegroundColor Red
    exit 1
}
Write-Host ""

# PASO 3: Configurar git (si es necesario)
Write-Host "⚙️  Paso 3: Configurando Git..." -ForegroundColor Yellow
$gitUserName = git config --global user.name
if ([string]::IsNullOrWhiteSpace($gitUserName)) {
    $userName = Read-Host "Ingresá tu nombre para Git"
    git config --global user.name "$userName"
}

$gitUserEmail = git config --global user.email
if ([string]::IsNullOrWhiteSpace($gitUserEmail)) {
    $userEmail = Read-Host "Ingresá tu email para Git"
    git config --global user.email "$userEmail"
}
Write-Host "✅ Git configurado" -ForegroundColor Green
Write-Host ""

# PASO 4: Inicializar repo local
Write-Host "📦 Paso 4: Inicializando repositorio local..." -ForegroundColor Yellow
if (-not (Test-Path ".git")) {
    git init
    git add .
    git commit -m "Initial commit - Wally Championship system"
}
Write-Host "✅ Repositorio local listo" -ForegroundColor Green
Write-Host ""

# PASO 5: Configurar remote
Write-Host "🔗 Paso 5: Configurando remote..." -ForegroundColor Yellow
git remote remove origin 2>$null
git remote add origin $REPO_URL
Write-Host "✅ Remote configurado" -ForegroundColor Green
Write-Host ""

# PASO 6: Subir a GitHub
Write-Host "⬆️  Paso 6: Subiendo código a GitHub..." -ForegroundColor Yellow
git branch -M main
git push -u origin main

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host "🎉 PROYECTO SUBIDO EXITOSAMENTE" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""
Write-Host "Ahora podés:"
Write-Host "1. Ver tu repo en: $($REPO_URL -replace '\.git$', '')"
Write-Host "2. Clonarlo en tu compu: git clone $REPO_URL"
Write-Host ""
