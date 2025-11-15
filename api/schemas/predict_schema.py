from pydantic import BaseModel, Field

class PredictRequest(BaseModel):
    id_lote: int
    precio_compra_kg: float = Field(gt=0)
    costo_logistica_total: float = Field(ge=0)
    peso_salida_total: float = Field(gt=0)
