# api/services/features_service.py
"""
Servicio de Features para Modelo XGBoost con 24 Variables.
Este es el CEREBRO del sistema ML - calcula todas las features en tiempo real.
"""
from __future__ import annotations
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from db import db

# Constantes de negocio
CAPACIDAD_GRANJA = 1000  # Capacidad maxima de animales
DISTANCIAS_KM = {
    "Santa Cruz": 350,
    "Beni": 520,
    "Pando": 680,
    "La Paz": 400,
    "Cochabamba": 300,
}

# Costos fijos mensuales (para prorrateo)
SUELDOS_MENSUALES = 11000.0
GASTOS_OPERATIVOS_MENSUALES = 3250.0
MANTENIMIENTO_CAMION_MENSUAL = 3000.0


async def _calcular_feriado_proximo(fecha_lote: datetime) -> tuple[bool, int]:
    """
    Calcula si hay un feriado en los proximos 7 dias.
    Returns: (es_feriado_proximo, dias_para_festividad)
    """
    fecha_limite = fecha_lote + timedelta(days=7)
    
    feriados_proximos = await db.feriado.find_many(
        where={
            "fecha": {
                "gte": fecha_lote,
                "lte": fecha_limite
            }
        },
        order={"fecha": "asc"}
    )
    
    if feriados_proximos:
        feriado_cercano = feriados_proximos[0]
        dias = (feriado_cercano.fecha - fecha_lote).days
        return (True, dias)
    else:
        return (False, 999)


async def _calcular_prorrateo_gastos_mensuales(
    fecha_lote: datetime,
    cantidad_animales: int
) -> Dict[str, float]:
    """
    Calcula el prorrateo de gastos mensuales para el lote.
    Returns: dict con costos prorrateados
    """
    mes = fecha_lote.month
    anio = fecha_lote.year
    
    # Obtener gastos del mes
    gastos_mes = await db.gastomensual.find_many(
        where={"mes": mes, "anio": anio},
        include={"tipo_costo": True}
    )
    
    if not gastos_mes:
        # Si no hay gastos registrados, usar valores por defecto
        return {
            "tasa_consumo_energia_agua": 0.0,
            "costo_mano_obra_asignada": 0.0,
            "gasto_total_mes": 0.0
        }
    
    # Calcular total de animales vendidos en el mes
    inicio_mes = datetime(anio, mes, 1)
    if mes == 12:
        fin_mes = datetime(anio + 1, 1, 1)
    else:
        fin_mes = datetime(anio, mes + 1, 1)
    
    lotes_del_mes = await db.lote.find_many(
        where={
            "fecha_adquisicion": {
                "gte": inicio_mes,
                "lt": fin_mes
            }
        }
    )
    
    total_animales_mes = sum(l.cantidad_animales for l in lotes_del_mes)
    
    if total_animales_mes == 0:
        total_animales_mes = cantidad_animales  # Evitar division por cero
    
    # Calcular prorrateo
    gasto_total_mes = sum(g.monto for g in gastos_mes)
    
    # Separar por tipo
    servicios_basicos = sum(
        g.monto for g in gastos_mes 
        if "servicio" in g.tipo_costo.nombre_tipo.lower() or "energia" in g.tipo_costo.nombre_tipo.lower()
    )
    mano_obra = sum(
        g.monto for g in gastos_mes 
        if "mano" in g.tipo_costo.nombre_tipo.lower() or "sueldo" in g.tipo_costo.nombre_tipo.lower()
    )
    
    # Prorrateo proporcional
    proporcion = cantidad_animales / total_animales_mes
    
    return {
        "tasa_consumo_energia_agua": servicios_basicos * proporcion,
        "costo_mano_obra_asignada": mano_obra * proporcion,
        "gasto_total_mes": gasto_total_mes * proporcion
    }


async def _calcular_viajes_mes(fecha_lote: datetime) -> int:
    """Calcula cuantos viajes se hicieron en el mes del lote."""
    mes = fecha_lote.month
    anio = fecha_lote.year
    
    inicio_mes = datetime(anio, mes, 1)
    if mes == 12:
        fin_mes = datetime(anio + 1, 1, 1)
    else:
        fin_mes = datetime(anio, mes + 1, 1)
    
    lotes_mes = await db.lote.count(
        where={
            "fecha_adquisicion": {
                "gte": inicio_mes,
                "lt": fin_mes
            }
        }
    )
    
    return max(lotes_mes, 1)  # Minimo 1 para evitar division por cero


async def _calcular_ocupacion_granja(fecha_lote: datetime) -> float:
    """
    Calcula el factor de ocupacion de la granja en la fecha del lote.
    Simula ocupacion basada en lotes activos.
    """
    # Buscar lotes activos en un rango de +/- 7 dias
    fecha_inicio = fecha_lote - timedelta(days=7)
    fecha_fin = fecha_lote + timedelta(days=7)
    
    lotes_activos = await db.lote.find_many(
        where={
            "fecha_adquisicion": {
                "gte": fecha_inicio,
                "lte": fecha_fin
            }
        }
    )
    
    total_animales = sum(l.cantidad_animales for l in lotes_activos)
    factor_ocupacion = min(total_animales / CAPACIDAD_GRANJA, 1.0)
    
    return factor_ocupacion


async def build_features_24_xgboost(
    id_lote: int,
    with_detalle: bool = False
) -> Dict[str, Any]:
    """
    Construye las 24 features para el modelo XGBoost.
    Este es el CEREBRO del sistema - calcula todo en tiempo real.
    
    Args:
        id_lote: ID del lote
        with_detalle: Si True, incluye desglose detallado de costos
        
    Returns:
        Dict con features, extras y opcionalmente detalle
    """
    # 1. Obtener lote
    lote = await db.lote.find_unique(where={"id_lote": id_lote})
    if lote is None:
        raise ValueError("lote_not_found")
    
    # ========================================
    # GRUPO 1: Variables de Adquisicion
    # ========================================
    cantidad_animales = float(lote.cantidad_animales)
    peso_promedio_entrada = float(lote.peso_promedio_entrada)
    precio_compra_kg = float(lote.precio_compra_kg or 0.0)
    costo_adquisicion_total = cantidad_animales * peso_promedio_entrada * precio_compra_kg
    
    # ========================================
    # GRUPO 2: Logistica y Transporte
    # ========================================
    # Obtener distancia (si no esta en BD, usar default)
    ubicacion = lote.ubicacion_origen or "Santa Cruz"
    distancia_km = DISTANCIAS_KM.get(ubicacion, 350)
    
    # Costos logisticos desde BD o calcular
    costo_combustible_viaje = float(lote.costo_combustible or 0.0)
    if costo_combustible_viaje == 0:
        # Calcular: Diesel ~3.7 Bs/litro, consumo ~25 km/litro
        litros_diesel = distancia_km / 25.0
        costo_combustible_viaje = litros_diesel * 3.7
    
    costo_peajes_lavado = float(lote.costo_peajes_lavado or 0.0)
    if costo_peajes_lavado == 0:
        # Estimar: 3 peajes * 40 Bs + lavado 100 Bs
        costo_peajes_lavado = (3 * 40) + 100
    
    costo_flete_estimado = float(lote.costo_flete or 0.0)
    if costo_flete_estimado == 0:
        # Estimar: base + por km + por animal
        costo_flete_estimado = 300 + (distancia_km * 1.0) + (cantidad_animales * 10)
    
    # Mantenimiento camion prorrateado
    viajes_mes = await _calcular_viajes_mes(lote.fecha_adquisicion)
    mantenimiento_camion_prorrateado = MANTENIMIENTO_CAMION_MENSUAL / viajes_mes
    
    # ========================================
    # GRUPO 3: Costos Fijos Dinamicos
    # ========================================
    duracion_estadia_dias = int(lote.duracion_estadia_dias or 0)
    
    # Costo fijo diario del lote
    costo_fijo_diario = (SUELDOS_MENSUALES + GASTOS_OPERATIVOS_MENSUALES) / 30
    costo_fijo_diario_lote = costo_fijo_diario * duracion_estadia_dias
    
    # Factor de ocupacion
    factor_ocupacion_granja = await _calcular_ocupacion_granja(lote.fecha_adquisicion)
    
    # Prorrateo de gastos mensuales
    prorrateo = await _calcular_prorrateo_gastos_mensuales(
        lote.fecha_adquisicion,
        int(cantidad_animales)
    )
    tasa_consumo_energia_agua = prorrateo["tasa_consumo_energia_agua"]
    costo_mano_obra_asignada = prorrateo["costo_mano_obra_asignada"]
    
    # ========================================
    # GRUPO 4: Estadia, Alimento y Sanidad
    # ========================================
    # Costo alimentacion
    costo_alimentacion_total = cantidad_animales * duracion_estadia_dias * 1.5
    
    # Costo sanitario (vacunas + higiene)
    costo_sanitario_total = cantidad_animales * 10.0  # Promedio 10 Bs/animal
    
    # Merma de peso en transporte
    merma_peso_transporte = float(lote.merma_peso_transporte or 0.0)
    if merma_peso_transporte == 0:
        # Estimar: 0.5 kg por cerdo
        merma_peso_transporte = cantidad_animales * 0.5
    
    # Peso de salida esperado
    if duracion_estadia_dias > 0:
        ganancia_por_dia = 1.15  # kg/dia/cerdo promedio
        peso_ganado = ganancia_por_dia * duracion_estadia_dias
        peso_salida_promedio = peso_promedio_entrada + peso_ganado - (merma_peso_transporte / cantidad_animales)
        peso_salida_esperado = peso_salida_promedio * cantidad_animales
    else:
        peso_salida_esperado = cantidad_animales * peso_promedio_entrada
    
    # ========================================
    # GRUPO 5: Variables Temporales y de Mercado
    # ========================================
    mes_adquisicion = lote.fecha_adquisicion.month
    dia_semana_llegada = lote.fecha_adquisicion.weekday()
    
    # Calcular feriado proximo
    es_feriado_proximo, dias_para_festividad = await _calcular_feriado_proximo(lote.fecha_adquisicion)
    
    # ========================================
    # GRUPO 6: Variables Compuestas
    # ========================================
    costo_logistica = costo_flete_estimado + costo_combustible_viaje + costo_peajes_lavado
    costo_operativo_por_cabeza = (costo_logistica + costo_fijo_diario_lote) / cantidad_animales
    
    ratio_alimento_precio_compra = costo_alimentacion_total / costo_adquisicion_total if costo_adquisicion_total > 0 else 0
    
    indicador_eficiencia_estadia = peso_promedio_entrada / duracion_estadia_dias if duracion_estadia_dias > 0 else 0
    
    # ========================================
    # Construir vector de features (24 features)
    # ========================================
    features = {
        # Grupo 1: Adquisicion
        "cantidad_animales": cantidad_animales,
        "peso_promedio_entrada": peso_promedio_entrada,
        "precio_compra_kg": precio_compra_kg,
        "costo_adquisicion_total": costo_adquisicion_total,
        
        # Grupo 2: Logistica
        "costo_combustible_viaje": costo_combustible_viaje,
        "costo_peajes_lavado": costo_peajes_lavado,
        "costo_flete_estimado": costo_flete_estimado,
        "mantenimiento_camion_prorrateado": mantenimiento_camion_prorrateado,
        
        # Grupo 3: Costos Fijos Dinamicos
        "costo_fijo_diario_lote": costo_fijo_diario_lote,
        "factor_ocupacion_granja": factor_ocupacion_granja,
        "tasa_consumo_energia_agua": tasa_consumo_energia_agua,
        "costo_mano_obra_asignada": costo_mano_obra_asignada,
        
        # Grupo 4: Estadia
        "duracion_estadia_dias": duracion_estadia_dias,
        "costo_alimentacion_total": costo_alimentacion_total,
        "costo_sanitario_total": costo_sanitario_total,
        "merma_peso_transporte": merma_peso_transporte,
        "peso_salida_esperado": peso_salida_esperado,
        
        # Grupo 5: Temporales
        "mes_adquisicion": mes_adquisicion,
        "dia_semana_llegada": dia_semana_llegada,
        "es_feriado_proximo": int(es_feriado_proximo),
        "dias_para_festividad": dias_para_festividad,
        
        # Grupo 6: Compuestas
        "costo_operativo_por_cabeza": costo_operativo_por_cabeza,
        "ratio_alimento_precio_compra": ratio_alimento_precio_compra,
        "indicador_eficiencia_estadia": indicador_eficiencia_estadia,
    }
    
    # ========================================
    # Extras para analisis
    # ========================================
    extras = {
        "costo_logistica_total": costo_logistica,
        "costo_fijo_total": costo_fijo_diario_lote + tasa_consumo_energia_agua + costo_mano_obra_asignada,
        "costo_variable_total": costo_adquisicion_total + costo_logistica + costo_alimentacion_total + costo_sanitario_total,
        "kilos_entrada": cantidad_animales * peso_promedio_entrada,
        "peso_salida_total": peso_salida_esperado,
        "ubicacion_origen": ubicacion,
        "distancia_km": distancia_km,
        "viajes_mes": viajes_mes,
    }
    
    resultado = {
        "lote_id": id_lote,
        "features": features,
        "extras": extras,
    }
    
    # Desglose detallado si se solicita
    if with_detalle:
        resultado["detalle"] = {
            "grupo_1_adquisicion": {
                "cantidad_animales": cantidad_animales,
                "peso_promedio_entrada": peso_promedio_entrada,
                "precio_compra_kg": precio_compra_kg,
                "costo_adquisicion_total": costo_adquisicion_total,
            },
            "grupo_2_logistica": {
                "costo_combustible_viaje": costo_combustible_viaje,
                "costo_peajes_lavado": costo_peajes_lavado,
                "costo_flete_estimado": costo_flete_estimado,
                "mantenimiento_camion_prorrateado": mantenimiento_camion_prorrateado,
            },
            "grupo_3_costos_fijos": {
                "costo_fijo_diario_lote": costo_fijo_diario_lote,
                "factor_ocupacion_granja": factor_ocupacion_granja,
                "tasa_consumo_energia_agua": tasa_consumo_energia_agua,
                "costo_mano_obra_asignada": costo_mano_obra_asignada,
                "gasto_total_mes_prorrateado": prorrateo["gasto_total_mes"],
            },
            "grupo_4_estadia": {
                "duracion_estadia_dias": duracion_estadia_dias,
                "costo_alimentacion_total": costo_alimentacion_total,
                "costo_sanitario_total": costo_sanitario_total,
                "merma_peso_transporte": merma_peso_transporte,
                "peso_salida_esperado": peso_salida_esperado,
            },
            "grupo_5_temporales": {
                "mes_adquisicion": mes_adquisicion,
                "dia_semana_llegada": dia_semana_llegada,
                "es_feriado_proximo": es_feriado_proximo,
                "dias_para_festividad": dias_para_festividad,
            },
            "grupo_6_compuestas": {
                "costo_operativo_por_cabeza": costo_operativo_por_cabeza,
                "ratio_alimento_precio_compra": ratio_alimento_precio_compra,
                "indicador_eficiencia_estadia": indicador_eficiencia_estadia,
            },
        }
    
    return resultado


# Mantener funcion legacy para compatibilidad
async def build_features_para_modelo(
    id_lote: int,
    desde: Optional[str] = None,
    hasta: Optional[str] = None,
    with_detalle: bool = False
) -> Dict[str, Any]:
    """
    Funcion legacy - redirige a la nueva implementacion.
    Mantiene compatibilidad con codigo existente.
    """
    return await build_features_24_xgboost(id_lote, with_detalle=with_detalle)
