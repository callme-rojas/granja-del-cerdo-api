# RESUMEN EJECUTIVO - ENTRENAMIENTO ML
## Fecha: 2025-10-28 22:34:43

## DATASETS GENERADOS
- **Dataset de 12 meses**: 360 lotes, 9 features
- **Rango de precios**: 17.69 - 27.48 Bs/kg
- **Distribucion mensual**: Realista para negocio de reventa

## COMPARACION DE 3 ALGORITMOS (Segun Diseño Academico)
1. **Regresion Lineal Multiple**: Baseline
2. **Random Forest Regressor**: Robusto y preciso  
3. **Gradient Boosting Regressor**: Secuencialmente mas fuerte

## ENTRENAMIENTO PROFESIONAL DE 12 MESES
### Ranking de Modelos:
1. **VotingRegressor**: MAE = 0.457 Bs/kg, R² = 0.933 (GANADOR)
2. **LinearRegression**: MAE = 0.461 Bs/kg, R² = 0.931
3. **Ridge**: MAE = 0.465 Bs/kg, R² = 0.930
4. **Lasso**: MAE = 0.495 Bs/kg, R² = 0.928
5. **RandomForest**: MAE = 0.498 Bs/kg, R² = 0.923
6. **ElasticNet**: MAE = 0.500 Bs/kg, R² = 0.924
7. **GradientBoosting**: MAE = 0.530 Bs/kg, R² = 0.913

## FEATURES MAS IMPORTANTES
1. **precio_compra_kg**: 93.8% (dominante)
2. **costo_logistica_total**: 1.4%
3. **mes_adquisicion**: 1.4% (estacionalidad)
4. **peso_promedio_entrada**: 1.2%
5. **costo_total_lote**: 0.6% (Feature Engineering)

## CONCLUSIONES
- **Mejor modelo**: VotingRegressor (Ensemble)
- **Precision**: MAE < 0.5 Bs/kg (excelente)
- **Capacidad explicativa**: R² > 0.93 (excelente)
- **Listo para**: Integracion con backend

## ARCHIVOS GENERADOS
- dataset_12_meses.csv
- comparacion_3_algoritmos.json
- entrenamiento_12_meses.json
- RESUMEN_EJECUTIVO.md
