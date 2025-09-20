# CHOCH ML Package

Objetivo: ayudar a los módulos CHOCH a (a) encontrar CHOCH antiguos de forma fiable desde la memoria persistente y (b) clasificar validez/dirección con modelos base.

Componentes:
- `dataset.py`: carga `04-DATA/memory_persistence/market_context_state.json` y normaliza eventos CHOCH a DataFrame.
- `features.py`: transforma eventos en features numéricas.
- `models.py`: clasificadores base (scikit-learn) para validez y dirección.
- `retrieval.py`: utilidades de consulta rápida (recientes, por símbolo/TF).

Entrenamiento rápido:

```powershell
# Desde la raíz del repo
python -X utf8 .\scripts\train_choch_classifier.py --min-confidence 60
```

Salida:
- Modelos en `04-DATA/models/choch/`: `validity_rf.joblib`, `direction_lr.joblib`.

Integración sugerida:
- Los detectores CHOCH pueden llamar a `retrieval.get_recent_choch()` para contexto.
- Para inferencia ML, cargar modelos con `load_model` y preprocesar con `build_feature_matrix`.
