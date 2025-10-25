from flask import Flask, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from routes.v1.auth import bp as auth_bp
from routes.v1.predict import bp as predict_bp
from routes.v1.lotes import bp as lotes_bp
from routes.v1.costos import bp as costos_bp
from routes.v1.tipos_costo import bp as tipos_costo_bp
from routes.v1.analytics import bp as analytics_bp
from routes.features import bp as features_bp
from config import settings

# 🔹 Crear la instancia del limiter fuera de la función
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.RATE_LIMIT]
)

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Seguridad básica
    @app.after_request
    def secure_headers(resp):
        resp.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["X-Content-Type-Options"] = "nosniff"
        return resp

    # 🔹 Inicializar el limiter dentro de la app
    limiter.init_app(app)

    # Rutas
    app.register_blueprint(auth_bp, url_prefix="/api/v1")
    app.register_blueprint(predict_bp, url_prefix="/api/v1")
    app.register_blueprint(lotes_bp, url_prefix="/api/v1")
    app.register_blueprint(costos_bp, url_prefix="/api/v1")
    app.register_blueprint(tipos_costo_bp, url_prefix="/api/v1")
    app.register_blueprint(analytics_bp, url_prefix="/api/v1")
    app.register_blueprint(features_bp, url_prefix="/api/v1")

    @app.get("/")
    def home():
        return jsonify(
            message="API Granja del Cerdo live",
            endpoints=[
                "/api/v1/login", 
                "/api/v1/predict", 
                "/api/v1/lotes",
                "/api/v1/tipos-costo",
                "/api/v1/lotes/{id}/costos",
                "/api/v1/lotes/{id}/costos/aggregates",
                "/api/v1/lotes/{id}/features",
                "/health"
            ]
        )

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host=settings.API_HOST, port=settings.API_PORT)
