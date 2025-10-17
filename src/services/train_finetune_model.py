"""
Script to export training data from MySQL and start OpenAI fine-tune.
"""

from src.services.ai_service import AIService
from src.services.schema_cache import SchemaCache
from src.core.config import Config
import os

def main():
    # Load config
    config = Config()
    config.validate()

    # Prepare MySQL connection dict
    mysql_config = {
        "host": config.MYSQL_HOST,
        "port": config.MYSQL_PORT,
        "user": config.MYSQL_USER,
        "password": config.MYSQL_PASSWORD,
        "database": config.MYSQL_DATABASE
    }

    # Output file for JSONL
    output_file = "training_data.jsonl"

    # Initialize AIService
    ai_service = AIService()

    # Initialize schema cache
    schema_cache = SchemaCache()
    if not schema_cache.is_cache_valid():
        print("📂 Schema cache not found. Generating schema cache...")
        schema_cache.save_schema_to_cache()
    else:
        print("📂 Loading schema from cache...")

    print("📦 Exporting training data from MySQL...")
    try:
        export_msg = ai_service.export_training_data_to_jsonl(
            mysql_config=mysql_config,
            table_name="training_data",
            output_file=output_file,
            schema_cache=schema_cache
        )
        print(export_msg)
    except Exception as e:
        print(f"❌ Error exporting data: {e}")
        return

    print("\n🚀 Starting fine-tune training...")
    try:
        train_info = ai_service.start_finetune_training(
            base_model=config.FINETUNED_MODEL or "gpt-4o-mini",  # fallback to base model
            training_file_path=output_file
        )
        print("\n✅ Fine-tuning initiated successfully:")
        print(train_info)
    except Exception as e:
        print(f"❌ Error starting fine-tune: {e}")


if __name__ == "__main__":
    main()
