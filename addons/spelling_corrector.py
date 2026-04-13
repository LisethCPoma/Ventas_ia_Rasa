import warnings
import re
from typing import Dict, Text, Any, List

from rasa.engine.graph import GraphComponent, ExecutionContext
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.training_data import TrainingData

try:
    from spellchecker import SpellChecker
except ImportError:
    warnings.warn("pyspellchecker no está instalado. Por favor ejecuta: pip install pyspellchecker")
    SpellChecker = None

@DefaultV1Recipe.register(
    [DefaultV1Recipe.ComponentType.MESSAGE_TOKENIZER], 
    is_trainable=False
)
class SpellingCorrector(GraphComponent):
    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> GraphComponent:
        return cls(config)

    def __init__(self, config: Dict[Text, Any]) -> None:
        self.config = config
        self.spell = SpellChecker(language='es') if SpellChecker else None
        
        # Agregamos palabras clave propias del instituto para que no intente "corregirlas"
        if self.spell:
            palabras_propias = [
                'consultina', 'daniela', 'cge', 'senescyt', 'uteq', 'istcge', 
                'naturopatía', 'naturopatia', 'inyectología', 'inyectologia', 
                'bach', 'odontología', 'odontologia', 'rehabilitación', 'rehabilitacion',
                'párvulos', 'emergencias', 'farmacia', 'paramédico', 
                'marketing', 'ecu', 'iess', 'médicas', 'medicas', 'física', 'fisica',
                'clínico', 'clinico', 'básica', 'basica', 'automotriz', 'ia'
            ]
            self.spell.word_frequency.load_words(palabras_propias)

    def process_training_data(self, training_data: TrainingData) -> TrainingData:
        # Los datos de entrenamiento ya están bien escritos, no los modificamos
        return training_data

    def process(self, messages: List[Message]) -> List[Message]:
        if not self.spell:
            return messages

        for message in messages:
            text = message.get("text", "")
            if not text:
                continue

            # Separar por espacios para mantener signos de puntuación pegados
            words = text.split()
            corrected_words = []
            
            for word in words:
                # Extraer solo las letras para buscar en el diccionario (limpiar '?¡!.,')
                clean_word = re.sub(r'[^\w\s]', '', word).lower()
                
                # Si la palabra tiene caracteres y no está en el diccionario, la corregimos
                if clean_word and len(clean_word) > 2 and clean_word not in self.spell.word_frequency.dictionary:
                    corrected = self.spell.correction(clean_word)
                    # A veces correction() devuelve None si no encuentra sugerencias
                    if corrected and corrected != clean_word:
                        # Reemplazamos sutilmente manteniendo los signos de admiración/interrogación
                        word = word.replace(clean_word, corrected)
                        # También intentar reemplazar en mayúscula/minúscula original
                        word = word.replace(re.sub(r'[^\w\s]', '', word), corrected)
                
                corrected_words.append(word)
            
            corrected_text = " ".join(corrected_words)
            
            # Sobreescribir el texto original que verá DIETClassifier y Gemini
            message.set("text", corrected_text, add_to_output=True)

        return messages
