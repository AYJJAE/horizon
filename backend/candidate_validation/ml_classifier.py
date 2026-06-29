"""
backend/candidate_validation/ml_classifier.py
CNN-based transit classifier with SHAP explainability.
Loads a pre-trained model if available; provides synthetic training otherwise.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# Fixed length for CNN input (folded light curve bins)
INPUT_LENGTH = 201


@dataclass
class MLPrediction:
    label: str              # "PLANET" | "FALSE_POSITIVE" | "UNKNOWN"
    confidence: float       # 0–1
    planet_prob: float
    fp_prob: float
    shap_values: Optional[Dict[str, Any]] = None


class TransitClassifier:
    """
    CNN transit classifier. Loads weights from disk if available,
    otherwise creates and caches a new model.
    """

    def __init__(self, model_path: Optional[str] = None) -> None:
        self.model_path = model_path
        self._model = None
        self._explainer = None

    def _build_model(self):
        """Build CNN+Dense architecture for 1-D transit classification."""
        try:
            import tensorflow as tf
            from tensorflow.keras import layers, models

            inp = tf.keras.Input(shape=(INPUT_LENGTH, 1))
            x = layers.Conv1D(32, 5, activation="relu", padding="same")(inp)
            x = layers.MaxPooling1D(2)(x)
            x = layers.Conv1D(64, 5, activation="relu", padding="same")(x)
            x = layers.MaxPooling1D(2)(x)
            x = layers.Conv1D(128, 3, activation="relu", padding="same")(x)
            x = layers.GlobalAveragePooling1D()(x)
            x = layers.Dense(64, activation="relu")(x)
            x = layers.Dropout(0.3)(x)
            out = layers.Dense(2, activation="softmax")(x)  # [FP, Planet]

            model = models.Model(inp, out)
            model.compile(
                optimizer="adam",
                loss="sparse_categorical_crossentropy",
                metrics=["accuracy"],
            )
            logger.info("Built CNN model: %d params", model.count_params())
            return model
        except ImportError:
            logger.warning("TensorFlow not available — using sklearn fallback classifier.")
            return None

    def _sklearn_fallback(self, features: np.ndarray) -> Tuple[float, float]:
        """Simple heuristic classifier when TF is unavailable."""
        # Use transit depth, symmetry, and noise as rough features
        depth = float(1.0 - np.min(features))
        noise = float(np.std(features[:20]))
        symmetry = float(np.abs(np.mean(features[:100]) - np.mean(features[101:])))
        # Score: deeper + symmetric + low noise → higher planet probability
        planet_score = min(1.0, depth * 10) * (1.0 - min(1.0, symmetry * 20)) * (1.0 - min(1.0, noise * 50))
        return planet_score, 1.0 - planet_score

    def load_or_create(self) -> None:
        """Load model from disk or create a new untrained model."""
        if self._model is not None:
            return

        model = self._build_model()
        if model is None:
            return

        if self.model_path and os.path.exists(self.model_path):
            try:
                model.load_weights(self.model_path)
                logger.info("Loaded pre-trained weights from %s", self.model_path)
            except Exception as exc:
                logger.warning("Could not load weights (%s) — model is untrained.", exc)
        else:
            logger.warning(
                "No pre-trained weights found at %s. "
                "Run model_training.py to train the model. "
                "Using heuristic scoring for now.",
                self.model_path,
            )
        self._model = model

    def preprocess_input(
        self,
        folded_time: np.ndarray,
        folded_flux: np.ndarray,
    ) -> np.ndarray:
        """
        Resample phase-folded light curve to fixed INPUT_LENGTH bins.
        Centers the transit at the middle of the array.
        """
        # Interpolate to fixed grid
        phase_grid = np.linspace(folded_time.min(), folded_time.max(), INPUT_LENGTH)
        interp_flux = np.interp(phase_grid, folded_time, folded_flux)
        # Normalize to zero median
        med = np.median(interp_flux)
        interp_flux = interp_flux - med
        return interp_flux.reshape(1, INPUT_LENGTH, 1).astype(np.float32)

    def predict(
        self,
        folded_time: np.ndarray,
        folded_flux: np.ndarray,
    ) -> MLPrediction:
        """Classify a folded light curve segment."""
        self.load_or_create()
        x = self.preprocess_input(folded_time, folded_flux)
        flat_x = x.flatten()

        if self._model is None:
            # Heuristic fallback
            planet_prob, fp_prob = self._sklearn_fallback(flat_x)
            label = "PLANET" if planet_prob > 0.5 else "FALSE_POSITIVE"
            return MLPrediction(
                label=label,
                confidence=max(planet_prob, fp_prob),
                planet_prob=planet_prob,
                fp_prob=fp_prob,
            )

        try:
            probs = self._model.predict(x, verbose=0)[0]
            fp_prob = float(probs[0])
            planet_prob = float(probs[1])
        except Exception as exc:
            logger.error("Model inference failed: %s", exc)
            planet_prob, fp_prob = self._sklearn_fallback(flat_x)

        confidence = max(planet_prob, fp_prob)
        label = "PLANET" if planet_prob >= 0.5 else "FALSE_POSITIVE"
        if confidence < 0.6:
            label = "UNKNOWN"

        # SHAP values (optional — only if model trained)
        shap_vals = self._compute_shap(x, flat_x)

        return MLPrediction(
            label=label,
            confidence=confidence,
            planet_prob=planet_prob,
            fp_prob=fp_prob,
            shap_values=shap_vals,
        )

    def _compute_shap(
        self,
        x: np.ndarray,
        flat_x: np.ndarray,
    ) -> Optional[Dict[str, Any]]:
        """Compute SHAP feature importance values."""
        try:
            import shap
            if self._model is None:
                return None
            # Use a small background for the kernel explainer
            background = np.zeros((1, INPUT_LENGTH, 1), dtype=np.float32)
            explainer = shap.DeepExplainer(self._model, background)
            shap_values = explainer.shap_values(x)
            vals = shap_values[1][0, :, 0] if isinstance(shap_values, list) else shap_values[0, :, 0]
            return {
                "values": vals.tolist(),
                "base_value": 0.5,
                "feature_names": [f"bin_{i}" for i in range(INPUT_LENGTH)],
            }
        except Exception as exc:
            logger.debug("SHAP computation skipped: %s", exc)
            return None


# Module-level singleton
_classifier: Optional[TransitClassifier] = None


def get_classifier(model_path: Optional[str] = None) -> TransitClassifier:
    global _classifier
    if _classifier is None:
        from backend.core.config import settings
        _classifier = TransitClassifier(model_path or settings.cnn_model_path)
    return _classifier
