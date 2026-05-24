#!/bin/bash

# ============================================
# SCRIPT PARA SUBIR WALLY CHAMPIONSHIP A GITHUB
# ============================================

echo "🚀 SUBIENDO PROYECTO A GITHUB"
echo "======================================"
echo ""

# PASO 1: Verificar que estás en la carpeta correcta
echo "📁 Paso 1: Verificando carpeta..."
if [ ! -f "README.md" ]; then
    echo "❌ Error: Ejecutá este script desde la carpeta wally-championship/"
    exit 1
fi
echo "✅ Carpeta correcta"
echo ""

# PASO 2: Pedir URL del repositorio
echo "📝 Paso 2: Ingresá la URL de tu repositorio GitHub"
echo "Ejemplo: https://github.com/tu-usuario/wally-championship.git"
read -p "URL del repo: " REPO_URL

if [ -z "$REPO_URL" ]; then
    echo "❌ Error: URL vacía"
    exit 1
fi
echo ""

# PASO 3: Configurar remote
echo "🔗 Paso 3: Configurando remote..."
git remote add origin "$REPO_URL" 2>/dev/null || git remote set-url origin "$REPO_URL"
echo "✅ Remote configurado"
echo ""

# PASO 4: Subir a GitHub
echo "⬆️  Paso 4: Subiendo código a GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "======================================"
echo "🎉 PROYECTO SUBIDO EXITOSAMENTE"
echo "======================================"
echo ""
echo "Ahora podés:"
echo "1. Ver tu repo en: ${REPO_URL%.git}"
echo "2. Clonarlo en tu compu: git clone $REPO_URL"
echo ""
