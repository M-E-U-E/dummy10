from django.core.management.base import BaseCommand
from app.models import Property, Summary
import requests
import os
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Generate property summaries and reviews using Ollama"

    def handle(self, *args, **kwargs):
        # Get Ollama URL from environment variables
        ollama_url = os.getenv("OLLAMA_URL", "http://ollama:11434")
        if not ollama_url:
            logger.error("OLLAMA_URL environment variable is not set.")
            return

        # Fetch all properties
        properties = Property.objects.all()
        if not properties.exists():
            logger.info("No properties found in the database.")
            return

        # Process each property
        for property in properties:
            self.generate_property_data(property, ollama_url)

    def generate_property_data(self, property, ollama_url):
        """
        Generate rewritten title, description, and summary for a property using Ollama.
        """
        try:
            # Rewrite title and description
            rewrite_prompt = f"Rewrite title: {property.property_name}. Rewrite description: {property.address}."
            rewrite_response = self.call_ollama_api(ollama_url, rewrite_prompt)
            if rewrite_response:
                property.property_name = rewrite_response.get("output", property.property_name)
                property.address = rewrite_response.get("output", property.address)
                property.save()
                logger.info(f"Updated property: {property.property_name}")

            # Generate summary
            summary_prompt = f"Summarize property: {property.property_name}. Address: {property.address}."
            summary_response = self.call_ollama_api(ollama_url, summary_prompt)
            if summary_response:
                summary_output = summary_response.get("output", "No summary generated.")
                summary, created = Summary.objects.update_or_create(
                    property=property,
                    defaults={"description": summary_output}
                )
                if created:
                    logger.info(f"Summary created for property: {property.property_name}")
                else:
                    logger.info(f"Summary updated for property: {property.property_name}")

        except Exception as e:
            logger.error(f"Error processing property {property.property_name}: {e}")

    def call_ollama_api(self, ollama_url, prompt):
        """
        Call the Ollama API with the given prompt and return the response.
        """
        try:
            response = requests.post(
                f"{ollama_url}/api/generate",
                json={"model": "llama-2-7b", "prompt": prompt},
                timeout=30  # Add a timeout for safety
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Ollama API error (status {response.status_code}): {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error connecting to Ollama API: {e}")
            return None
