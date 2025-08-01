#!/usr/bin/env python3
"""
Script pour entraîner le modèle T5 de correction automatique
"""
import os
import pandas as pd
import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration, Trainer, TrainingArguments
from torch.utils.data import Dataset
from pathlib import Path
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CorrectionDataset(Dataset):
    """Dataset personnalisé pour l'entraînement du modèle de correction"""
    
    def __init__(self, data, tokenizer, max_length=512):
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data.iloc[idx]
        
        # Préparer l'entrée (texte original)
        input_text = f"correct: {item['original_text']}"
        
        # Préparer la cible (texte corrigé)
        target_text = item['corrected_text']
        
        # Tokeniser l'entrée
        inputs = self.tokenizer(
            input_text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        # Tokeniser la cible
        targets = self.tokenizer(
            target_text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': inputs['input_ids'].flatten(),
            'attention_mask': inputs['attention_mask'].flatten(),
            'labels': targets['input_ids'].flatten()
        }

def load_correction_data():
    """Charge les données de correction depuis le CSV"""
    csv_file = "corrections.csv"
    
    if not os.path.exists(csv_file):
        logger.error(f"Fichier {csv_file} non trouvé. Exécutez d'abord generate_correction_csv.py")
        return None
    
    try:
        df = pd.read_csv(csv_file, encoding='utf-8')
        logger.info(f"✅ {len(df)} paires de corrections chargées")
        return df
    except Exception as e:
        logger.error(f"Erreur lors du chargement des données: {e}")
        return None

def prepare_training_data(df):
    """Prépare les données pour l'entraînement"""
    # Filtrer les données valides
    valid_data = df[
        (df['original_text'].notna()) & 
        (df['corrected_text'].notna()) &
        (df['original_text'].str.len() > 10) &
        (df['corrected_text'].str.len() > 10)
    ].copy()
    
    logger.info(f"📊 {len(valid_data)} paires valides pour l'entraînement")
    
    # Diviser en train/validation (80/20)
    train_size = int(0.8 * len(valid_data))
    train_data = valid_data[:train_size]
    val_data = valid_data[train_size:]
    
    logger.info(f"📈 Train: {len(train_data)}, Validation: {len(val_data)}")
    
    return train_data, val_data

def train_correction_model():
    """Entraîne le modèle de correction T5"""
    print("🤖 Entraînement du modèle de correction T5...")
    
    # Charger les données
    df = load_correction_data()
    if df is None:
        return
    
    # Préparer les données
    train_data, val_data = prepare_training_data(df)
    
    if len(train_data) < 5:
        print("❌ Pas assez de données pour l'entraînement (minimum 5 paires)")
        return
    
    # Initialiser le tokenizer et le modèle
    print("📥 Chargement du modèle T5...")
    model_name = "t5-small"  # Modèle plus léger pour commencer
    
    try:
        tokenizer = T5Tokenizer.from_pretrained(model_name)
        model = T5ForConditionalGeneration.from_pretrained(model_name)
    except Exception as e:
        print(f"❌ Erreur lors du chargement du modèle: {e}")
        return
    
    # Créer les datasets
    train_dataset = CorrectionDataset(train_data, tokenizer)
    val_dataset = CorrectionDataset(val_data, tokenizer)
    
    # Configuration de l'entraînement
    training_args = TrainingArguments(
        output_dir="./correction_model",
        num_train_epochs=3,
        per_device_train_batch_size=2,
        per_device_eval_batch_size=2,
        warmup_steps=100,
        weight_decay=0.01,
        logging_dir="./logs",
        logging_steps=10,
        evaluation_strategy="steps",
        eval_steps=50,
        save_steps=100,
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
    )
    
    # Initialiser le trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=tokenizer,
    )
    
    # Entraîner le modèle
    print("🚀 Début de l'entraînement...")
    trainer.train()
    
    # Sauvegarder le modèle
    print("💾 Sauvegarde du modèle...")
    model.save_pretrained("./correction_model")
    tokenizer.save_pretrained("./correction_model")
    
    print("✅ Modèle de correction entraîné et sauvegardé!")
    print("📁 Modèle disponible dans: ./correction_model/")
    
    # Test rapide
    print("\n🧪 Test du modèle...")
    test_text = "bonjour le monde"
    inputs = tokenizer(f"correct: {test_text}", return_tensors="pt")
    
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=50)
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"Test: '{test_text}' → '{result}'")

if __name__ == "__main__":
    train_correction_model() 