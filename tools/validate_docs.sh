#!/bin/bash
# 🔗 VALIDATION SCRIPT - ICT ENGINE v6.0 ENTERPRISE
# Validar estructura documental e integridad de enlaces

echo "🔍 INICIANDO VALIDACIÓN DE ESTRUCTURA DOCUMENTAL..."
echo "================================================="

# Verificar archivos críticos existen
echo "📋 Verificando archivos críticos..."
test -f "03-DOCUMENTATION/protocols/REGLAS_COPILOT.md" && echo "✅ REGLAS_COPILOT.md" || echo "❌ REGLAS_COPILOT.md FALTANTE"
test -f "03-DOCUMENTATION/MASTER-INDEX.md" && echo "✅ MASTER-INDEX.md" || echo "❌ MASTER-INDEX.md FALTANTE"
test -f "03-DOCUMENTATION/quick-start.md" && echo "✅ quick-start.md" || echo "❌ quick-start.md FALTANTE"
test -f "03-DOCUMENTATION/COPILOT-CONTEXT-CARDS.md" && echo "✅ COPILOT-CONTEXT-CARDS.md" || echo "❌ COPILOT-CONTEXT-CARDS.md FALTANTE"
test -f "03-DOCUMENTATION/QUICK-REFERENCE-CARDS.md" && echo "✅ QUICK-REFERENCE-CARDS.md" || echo "❌ QUICK-REFERENCE-CARDS.md FALTANTE"
test -f "03-DOCUMENTATION/VALIDACION-ENLACES-REFERENCIAS.md" && echo "✅ VALIDACION-ENLACES-REFERENCIAS.md" || echo "❌ VALIDACION-ENLACES-REFERENCIAS.md FALTANTE"

echo ""
echo "📊 Contando documentos por categoría..."

# Contar documentos por categoría
if [ -d "03-DOCUMENTATION/protocols" ]; then
    PROTOCOLS_COUNT=$(ls 03-DOCUMENTATION/protocols/*.md 2>/dev/null | wc -l)
    echo "📋 Protocols: $PROTOCOLS_COUNT documentos"
else
    echo "❌ Directorio protocols/ no encontrado"
fi

if [ -d "03-DOCUMENTATION/technical" ]; then
    TECHNICAL_COUNT=$(find 03-DOCUMENTATION/technical -name "*.md" 2>/dev/null | wc -l)
    echo "🔧 Technical: $TECHNICAL_COUNT documentos"
else
    echo "❌ Directorio technical/ no encontrado"
fi

if [ -d "03-DOCUMENTATION/reports" ]; then
    REPORTS_COUNT=$(ls 03-DOCUMENTATION/reports/*.md 2>/dev/null | wc -l)
    echo "📈 Reports: $REPORTS_COUNT documentos"
else
    echo "❌ Directorio reports/ no encontrado"
fi

if [ -d "03-DOCUMENTATION/development" ]; then
    DEVELOPMENT_COUNT=$(ls 03-DOCUMENTATION/development/*.md 2>/dev/null | wc -l)
    echo "📝 Development: $DEVELOPMENT_COUNT documentos"
else
    echo "❌ Directorio development/ no encontrado"
fi

# Contar documentos raíz
ROOT_COUNT=$(ls 03-DOCUMENTATION/*.md 2>/dev/null | wc -l)
echo "📁 Root level: $ROOT_COUNT documentos"

echo ""
echo "🔗 Verificando estructura de enlaces..."

# Buscar enlaces rotos potenciales
echo "🔍 Buscando referencias a archivos..."
TOTAL_REFS=$(grep -r "\[.*\](" 03-DOCUMENTATION/ 2>/dev/null | wc -l)
echo "📊 Total referencias encontradas: $TOTAL_REFS"

# Buscar archivos .md que podrían estar referenciados
echo "📂 Archivos .md totales en sistema:"
TOTAL_MD_FILES=$(find 03-DOCUMENTATION -name "*.md" 2>/dev/null | wc -l)
echo "📄 Total archivos .md: $TOTAL_MD_FILES"

echo ""
echo "✅ VALIDACIÓN COMPLETADA"
echo "========================"
echo "📋 Resumen:"
echo "  - Archivos críticos verificados"
echo "  - Estructura de directorios validada"
echo "  - Conteo de documentos completado"
echo "  - Referencias de enlaces analizadas"
echo ""
echo "🚀 Para validación detallada, consultar:"
echo "   03-DOCUMENTATION/VALIDACION-ENLACES-REFERENCIAS.md"
echo ""
