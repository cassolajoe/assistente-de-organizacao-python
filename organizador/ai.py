import magic
import mimetypes
import logging
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import joblib
import os

class AIAnalyzer:
    def __init__(self, model_path: str = "models/ai_classifier.pkl"):
        self.model_path = Path(model_path)
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        self.vectorizer = TfidfVectorizer(max_features=100)
        self.classifier = KMeans(n_clusters=5, n_init='auto')
        self.is_trained = False
        self._load_model()

    def _load_model(self):
        if self.model_path.exists():
            try:
                data = joblib.load(self.model_path)
                self.vectorizer = data['vectorizer']
                self.classifier = data['classifier']
                self.is_trained = True
            except Exception as e:
                logging.error(f"Erro ao carregar modelo de IA: {e}")

    def _save_model(self):
        try:
            joblib.dump({'vectorizer': self.vectorizer, 'classifier': self.classifier}, self.model_path)
        except Exception as e:
            logging.error(f"Erro ao salvar modelo de IA: {e}")

    def get_real_extension(self, filepath: str | Path) -> str:
        try:
            mime = magic.from_file(str(filepath), mime=True)
            if mime:
                ext = mimetypes.guess_extension(mime)
                if ext: return ext
            return ""
        except Exception as e:
            logging.error(f"Erro ao analisar Magic Number de {filepath}: {e}")
            return ""

    def suggest_category_for_unknown(self, filepath: str | Path) -> tuple[str, str]:
        try:
            mime = magic.from_file(str(filepath), mime=True)
            if mime:
                if mime.startswith('text/'): return "Documentos", "TXT"
                elif mime.startswith('image/'): return "Imagens", "OUTROS"
                elif mime.startswith('video/'): return "Vídeos", "OUTROS"
                elif mime.startswith('audio/'): return "Áudio", "OUTROS"
                elif mime == 'application/pdf': return "Documentos", "PDF"
                elif mime == 'application/zip' or 'compressed' in mime: return "Compactados", "OUTROS"
            
            if mime and mime.startswith('text/'):
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(1024)
                if self.is_trained:
                    vec = self.vectorizer.transform([content])
                    cluster = self.classifier.predict(vec)[0]
                    return "Outros", f"CLUSTER_{cluster}"
        except Exception as e:
            logging.error(f"Erro na IA para {filepath}: {e}")
        return "Outros", "DESCONHECIDO"

    def train_on_new_file(self, filepath: str | Path):
        pass
