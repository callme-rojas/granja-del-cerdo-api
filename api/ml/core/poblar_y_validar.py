#!/usr/bin/env python3
"""
Script completo para poblar base de datos, entrenar modelo y ejecutar validación cruzada.
Genera resultados reales para documentación.
"""

import sys
import os
from pathlib import Path
import asyncio
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import json

# Agregar paths
api_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(api_dir))
sys.path.insert(0, str(Path(__file__).parent.parent))

# Cargar variables de entorno ANTES de importar db
try:
    from dotenv import load_dotenv
except ImportError:
    print("⚠️  python-dotenv no está instalado. Instalando...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv"])
    from dotenv import load_dotenv

# Buscar y cargar .env desde api/.env
env_path = api_dir / ".env"
env_cargado = False

# Configurar encoding para evitar problemas con emojis en Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

if env_path.exists():
    load_dotenv(env_path, override=True)
    print(f"[OK] Variables de entorno cargadas desde: {env_path}")
    env_cargado = True
else:
    # Intentar cargar desde la raíz del proyecto
    root_env = api_dir.parent / ".env"
    if root_env.exists():
        load_dotenv(root_env, override=True)
        print(f"[OK] Variables de entorno cargadas desde: {root_env}")
        env_cargado = True
    else:
        print(f"[WARNING] No se encontro archivo .env en:")
        print(f"   - {env_path}")
        print(f"   - {root_env}")
        print(f"   Intentando usar variables de entorno del sistema...")

# Verificar que DATABASE_URL esté configurada
database_url = os.getenv("DATABASE_URL")
if not database_url:
    print("\n[ERROR] DATABASE_URL no encontrada en variables de entorno")
    print("   Asegurate de tener un archivo .env en api/ con la siguiente linea:")
    print("   DATABASE_URL=postgresql://usuario:password@host:puerto/database")
    print("\n   El archivo .env debe estar en: api/.env")
    if not env_cargado:
        print("\n   [TIP] Crea el archivo api/.env con tu DATABASE_URL")
    sys.exit(1)
else:
    # Mostrar solo los primeros caracteres por seguridad
    url_preview = database_url.split('@')[-1] if '@' in database_url else database_url[:30]
    print(f"[OK] DATABASE_URL configurada: ...@{url_preview}")

# Imports de base de datos (después de cargar .env)
from db import db, connect_db, disconnect_db

# Imports de ML
from ml.data.generate_data import generar_lote, construir_features
from ml.core.training_12_months import comprehensive_model_comparison, save_final_model
from ml.core.cross_validation import (
    cross_validation_evaluation,
    generate_cross_validation_report,
    compare_models_cross_validation
)
from sklearn.preprocessing import StandardScaler
import joblib


async def poblar_base_datos(n_lotes: int = 360, id_usuario: int = 1):
    """
    Pobla la base de datos con lotes generados.
    
    Args:
        n_lotes: Número de lotes a generar (default: 360 para 12 meses)
        id_usuario: ID del usuario creador (default: 1)
    """
    print("="*70)
    print("POBLANDO BASE DE DATOS CON LOTES")
    print("="*70)
    
    # Generar datos sintéticos
    print(f"\n1. Generando {n_lotes} lotes sintéticos...")
    df_lotes = generar_lote(n_lotes)
    
    # Preparar fechas distribuidas en 12 meses
    fecha_inicio = datetime(2024, 1, 1, 0, 0, 0)  # Asegurar hora 00:00:00
    fechas = []
    for i in range(n_lotes):
        # Distribuir uniformemente en 12 meses
        dias_offset = int((i / n_lotes) * 365)
        fecha = fecha_inicio + timedelta(days=dias_offset)
        # Asegurar que la fecha solo tenga fecha (sin hora)
        fecha = fecha.replace(hour=0, minute=0, second=0, microsecond=0)
        fechas.append(fecha)
    
    df_lotes['fecha_adquisicion'] = fechas
    
    print(f"   ✅ {len(df_lotes)} lotes generados")
    print(f"   Rango de fechas: {min(fechas).strftime('%Y-%m-%d')} a {max(fechas).strftime('%Y-%m-%d')}")
    
    # Conectar a base de datos
    print(f"\n2. Conectando a base de datos...")
    await connect_db()
    
    try:
        # Verificar si existe usuario
        usuario = await db.usuario.find_unique(where={"id_usuario": id_usuario})
        if not usuario:
            print(f"   ⚠️  Usuario {id_usuario} no existe. Creando usuario de prueba...")
            # Crear usuario de prueba si no existe
            usuario = await db.usuario.create(
                data={
                    "nombre_completo": "Usuario Prueba",
                    "email": f"prueba_{id_usuario}@test.com",
                    "password_hash": "hash_temporal"
                }
            )
            id_usuario = usuario.id_usuario
            print(f"   ✅ Usuario creado: ID {id_usuario}")
        
        # Insertar lotes en la base de datos
        print(f"\n3. Insertando lotes en base de datos...")
        lotes_insertados = 0
        
        for idx, row in df_lotes.iterrows():
            try:
                # Asegurar que siempre haya una fecha válida
                fecha_adq = row.get('fecha_adquisicion')
                if fecha_adq is None or (hasattr(fecha_adq, '__iter__') and str(fecha_adq) == 'NaT'):
                    # Si no hay fecha, usar la fecha calculada del índice
                    dias_offset = int((idx / n_lotes) * 365)
                    fecha_adq = fecha_inicio + timedelta(days=dias_offset)
                
                # Convertir a datetime si es necesario
                if isinstance(fecha_adq, str):
                    try:
                        fecha_adq = datetime.strptime(fecha_adq, "%Y-%m-%d")
                    except:
                        dias_offset = int((idx / n_lotes) * 365)
                        fecha_adq = fecha_inicio + timedelta(days=dias_offset)
                
                # Asegurar que la fecha solo tenga fecha (sin hora)
                if isinstance(fecha_adq, datetime):
                    fecha_adq = fecha_adq.replace(hour=0, minute=0, second=0, microsecond=0)
                
                lote = await db.lote.create(
                    data={
                        "fecha_adquisicion": fecha_adq,
                        "cantidad_animales": int(row['cantidad_animales']),
                        "peso_promedio_entrada": float(row['peso_promedio_entrada']),
                        "duracion_estadia_dias": int(row['duracion_estadia_dias']),
                        "precio_compra_kg": float(row['precio_compra_kg']),
                        "id_usuario_creador": id_usuario,
                    }
                )
                lotes_insertados += 1
                
                if (lotes_insertados % 50) == 0:
                    print(f"   Progreso: {lotes_insertados}/{n_lotes} lotes insertados...")
                    
            except Exception as e:
                print(f"   ⚠️  Error insertando lote {idx+1}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"\n   ✅ {lotes_insertados} lotes insertados exitosamente")
        
        return lotes_insertados
        
    finally:
        await disconnect_db()


def preparar_dataset_para_entrenamiento():
    """
    Prepara el dataset desde los datos generados para entrenamiento.
    Usa el mismo generador pero sin insertar en BD (más rápido para ML).
    """
    print("\n" + "="*70)
    print("PREPARANDO DATASET PARA ENTRENAMIENTO")
    print("="*70)
    
    # Generar dataset de 12 meses (360 lotes)
    print("\nGenerando dataset de 12 meses (360 lotes)...")
    df_lotes = generar_lote(360)
    df_features = construir_features(df_lotes)
    
    print(f"   ✅ Dataset generado: {len(df_features)} muestras")
    print(f"   Features: {len(df_features.columns) - 1}")
    print(f"   Target: precio_venta_final_kg")
    print(f"   Rango target: {df_features['precio_venta_final_kg'].min():.2f} - {df_features['precio_venta_final_kg'].max():.2f} Bs/kg")
    
    return df_features


def entrenar_y_validar():
    """
    Entrena modelos y ejecuta validación cruzada completa.
    """
    print("\n" + "="*70)
    print("ENTRENAMIENTO Y VALIDACIÓN CRUZADA")
    print("="*70)
    
    # Preparar datos
    df = preparar_dataset_para_entrenamiento()
    
    # Features según diseño académico - INCLUYENDO COSTOS FIJOS
    feature_cols = [
        "cantidad_animales", "peso_promedio_entrada", "precio_compra_kg",
        "costo_logistica_total", "costo_alimentacion_estadia", "duracion_estadia_dias",
        "mes_adquisicion", "costo_total_lote", "peso_salida",
        "costo_fijo_por_kg"  # NUEVO: Costos Fijos como feature
    ]
    
    X = df[feature_cols].values
    y = df["precio_venta_final_kg"].values
    
    print(f"\nDataset preparado:")
    print(f"   Features: {len(feature_cols)}")
    print(f"   Muestras: {len(X):,}")
    print(f"   Target range: {y.min():.2f} - {y.max():.2f} Bs/kg")
    
    # Comparación de modelos con validación cruzada
    # Nota: comprehensive_model_comparison hace la normalización internamente
    print(f"\n{'='*70}")
    print("COMPARACIÓN DE MODELOS CON VALIDACIÓN CRUZADA")
    print(f"{'='*70}")
    
    results, scaler_final, feature_names = comprehensive_model_comparison(X, y, feature_cols)
    
    # Generar reporte completo de validación cruzada para el mejor modelo
    print(f"\n{'='*70}")
    print("GENERANDO REPORTE DE VALIDACIÓN CRUZADA")
    print(f"{'='*70}")
    
    # Seleccionar mejor modelo
    best_name = min(results.keys(), key=lambda x: results[x]['cv_mae_mean'])
    best_result = results[best_name]
    best_model = best_result['model']
    
    print(f"\nMejor modelo: {best_name}")
    print(f"   CV MAE:  {best_result['cv_mae_mean']:.4f} ± {best_result['cv_mae_std']:.4f} Bs/kg")
    print(f"   CV RMSE: {best_result['cv_rmse_mean']:.4f} ± {best_result['cv_rmse_std']:.4f} Bs/kg")
    
    # Preparar datos normalizados para el reporte final
    X_normalized = scaler_final.transform(X)
    
    # Generar reporte completo
    report = generate_cross_validation_report(
        best_model, best_name, X_normalized, y,
        cv_folds=5,
        output_path="api/ml/docs/cross_validation_report.json"
    )
    
    # Guardar resultados completos
    resultados_completos = {
        'fecha_ejecucion': datetime.now().isoformat(),
        'dataset_info': {
            'total_muestras': len(X),
            'features': feature_cols,
            'target_range': {
                'min': float(y.min()),
                'max': float(y.max())
            }
        },
        'modelos_evaluados': {
            name: {
                'mae_test': float(result['mae']),
                'rmse_test': float(result['rmse']),
                'r2': float(result['r2']),
                'cv_mae_mean': float(result['cv_mae_mean']),
                'cv_mae_std': float(result['cv_mae_std']),
                'cv_rmse_mean': float(result['cv_rmse_mean']),
                'cv_rmse_std': float(result['cv_rmse_std'])
            }
            for name, result in results.items()
        },
        'mejor_modelo': {
            'nombre': best_name,
            'cv_mae_mean': float(best_result['cv_mae_mean']),
            'cv_mae_std': float(best_result['cv_mae_std']),
            'cv_rmse_mean': float(best_result['cv_rmse_mean']),
            'cv_rmse_std': float(best_result['cv_rmse_std']),
            'mae_test': float(best_result['mae']),
            'rmse_test': float(best_result['rmse']),
            'r2': float(best_result['r2'])
        },
        'reporte_validacion_cruzada': report
    }
    
    # Guardar resultados
    resultados_path = "api/ml/docs/resultados_validacion_completa.json"
    Path(resultados_path).parent.mkdir(parents=True, exist_ok=True)
    with open(resultados_path, 'w', encoding='utf-8') as f:
        json.dump(resultados_completos, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Resultados completos guardados en: {resultados_path}")
    
    # Guardar el modelo entrenado
    print(f"\n{'='*70}")
    print("GUARDANDO MODELO ENTRENADO")
    print(f"{'='*70}")
    model_path = save_final_model(results, scaler_final, feature_cols)
    print(f"✅ Modelo guardado en: {model_path}")
    
    # Mostrar resumen final
    print(f"\n{'='*70}")
    print("RESUMEN FINAL - RESULTADOS DE VALIDACIÓN")
    print(f"{'='*70}")
    
    print(f"\n📊 COMPARACIÓN DE MODELOS:")
    print(f"{'Modelo':<25} {'CV MAE':<15} {'CV RMSE':<15} {'R²':<10}")
    print("-" * 70)
    for name, result in sorted(results.items(), key=lambda x: x[1]['cv_mae_mean']):
        print(f"{name:<25} "
              f"{result['cv_mae_mean']:.4f}±{result['cv_mae_std']:.4f}  "
              f"{result['cv_rmse_mean']:.4f}±{result['cv_rmse_std']:.4f}  "
              f"{result['r2']:.4f}")
    
    print(f"\n🏆 MEJOR MODELO: {best_name}")
    print(f"   CV MAE:  {best_result['cv_mae_mean']:.4f} ± {best_result['cv_mae_std']:.4f} Bs/kg")
    print(f"   CV RMSE: {best_result['cv_rmse_mean']:.4f} ± {best_result['cv_rmse_std']:.4f} Bs/kg")
    print(f"   Test MAE:  {best_result['mae']:.4f} Bs/kg")
    print(f"   Test RMSE: {best_result['rmse']:.4f} Bs/kg")
    print(f"   R² Score:  {best_result['r2']:.4f}")
    
    print(f"\n💡 INTERPRETACIÓN:")
    print(f"   {report['metrics']['mae']['interpretation']}")
    print(f"   {report['metrics']['rmse']['interpretation']}")
    
    print(f"\n📋 RECOMENDACIÓN:")
    print(f"   {report['recommendation']}")
    
    return resultados_completos


async def main(poblar_bd: bool = True, n_lotes: int = 360):
    """
    Función principal.
    
    Args:
        poblar_bd: Si True, pobla la base de datos (default: True)
        n_lotes: Número de lotes a generar si poblar_bd=True (default: 360)
    """
    print("="*70)
    print("PROCESO COMPLETO: POBLAR BD + ENTRENAR + VALIDAR")
    print("="*70)
    
    try:
        # Paso 1: Poblar base de datos
        if poblar_bd:
            print("\n" + "="*70)
            print("PASO 1: POBLAR BASE DE DATOS")
            print("="*70)
            
            try:
                lotes_insertados = await poblar_base_datos(n_lotes=n_lotes)
                print(f"\n✅ Base de datos poblada con {lotes_insertados} lotes")
            except Exception as e:
                print(f"\n❌ Error al poblar base de datos: {e}")
                print("   Continuando con entrenamiento y validación sin poblar BD...")
                import traceback
                traceback.print_exc()
        else:
            print("\n⏭️  Omitiendo población de base de datos (modo entrenamiento/validación)")
        
        # Paso 2: Entrenar y validar
        print("\n" + "="*70)
        print("PASO 2: ENTRENAR MODELOS Y VALIDACIÓN CRUZADA")
        print("="*70)
        
        resultados = entrenar_y_validar()
        
        print(f"\n{'='*70}")
        print("✅ PROCESO COMPLETADO EXITOSAMENTE")
        print(f"{'='*70}")
        print(f"\n📁 Archivos generados:")
        print(f"   - api/ml/docs/cross_validation_report.json")
        print(f"   - api/ml/docs/resultados_validacion_completa.json")
        print(f"\n📊 Los resultados están listos para documentación")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error durante el proceso: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Poblar BD, entrenar modelos y ejecutar validación cruzada")
    parser.add_argument("--no-poblar-bd", action="store_true", help="NO poblar base de datos (por defecto SÍ se pobla)")
    parser.add_argument("--n-lotes", type=int, default=360, help="Número de lotes a generar (default: 360)")
    
    args = parser.parse_args()
    
    # Por defecto poblar_bd=True, a menos que se use --no-poblar-bd
    poblar_bd = not args.no_poblar_bd
    
    exit_code = asyncio.run(main(poblar_bd=poblar_bd, n_lotes=args.n_lotes))
    exit(exit_code)

