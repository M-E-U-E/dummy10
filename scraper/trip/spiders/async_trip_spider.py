import scrapy
import json
import re
import random
import os
import asyncio
import aiohttp
import requests  # For interacting with Ollama API


class AsyncHotelSpider(scrapy.Spider):
    """
    Spider for scraping hotel data from Trip.com with async image downloading and Ollama integration.
    """
    name = "async_trip"
    start_urls = ["https://uk.trip.com/hotels/?locale=en-GB&curr=GBP"]

    ollama_url = os.getenv("OLLAMA_URL", "http://ollama:11434")

    def parse(self, response):
        """
        Parse the main page and extract city data.
        """
        script_data = self.extract_script_data(response)
        if not script_data:
            self.logger.warning("No script data found. Cannot extract hotel data.")
            return

        try:
            # Load JSON string into a Python dictionary
            data = json.loads(script_data)
            hotel_list = data.get("initData", {}).get("firstPageList", {}).get("hotelList", [])

            for hotel in hotel_list:
                item = {
                    "city_name": hotel.get("cityName", ""),
                    "property_name": hotel.get("hotelName", ""),
                    "hotel_id": hotel.get("hotelId", ""),
                    "price": hotel.get("price", 0),
                    "rating": float(hotel.get("rating", 0.0)),
                    "address": hotel.get("address", ""),
                    "latitude": hotel.get("latitude", 0.0),
                    "longitude": hotel.get("longitude", 0.0),
                    "room_type": hotel.get("roomType", ""),
                    "image": hotel.get("imageUrl", ""),
                }

                # Use Ollama to rewrite property details
                item = self.process_with_ollama(item)

                self.logger.info(f"Yielding item: {item}")
                yield item
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON Decode Error: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error during parsing: {e}")

    def process_with_ollama(self, item):
        """
        Use Ollama to rewrite property descriptions or generate summaries.
        """
        try:
            if not self.ollama_url:
                self.logger.warning("OLLAMA_URL is not set. Skipping Ollama processing.")
                return item

            prompt = (
                f"Rewrite this property name: {item['property_name']}. "
                f"Rewrite this description: {item['address']}."
            )
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={"model": "llama-2-7b", "prompt": prompt}
            )

            if response.status_code == 200:
                result = response.json()
                item["property_name"] = result.get("output", item["property_name"])
                item["address"] = result.get("output", item["address"])
                self.logger.info(f"Ollama processed: {item}")
            else:
                self.logger.warning(f"Ollama API request failed with status {response.status_code}")
        except Exception as e:
            self.logger.error(f"Error processing with Ollama: {e}")

        return item

    def extract_script_data(self, response):
        """
        Extract the script content containing the JSON data as a string.
        """
        script_content = response.xpath(
            '//script[contains(text(), "window.IBU_HOTEL")]/text()'
        ).get()

        if not script_content:
            self.logger.warning("Script content not found. Check the XPath selector.")
            return None

        # Extract the JSON-like content as a string
        match = re.search(r"window\.IBU_HOTEL\s*=\s*(\{.*?\});", script_content, re.DOTALL)
        if match:
            self.logger.info("Successfully extracted script data.")
            return match.group(1)  # Return JSON string
        else:
            self.logger.warning("No match for window.IBU_HOTEL.")
            return None

    def parse_json_data(self, script_data):
        """
        Parse JSON-like script data.
        """
        try:
            return json.loads(script_data)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON: {e}")
            return {}

    def save_to_json(self, data, path):
        """
        Save hotel data to a JSON file.
        """
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error saving JSON to {path}: {e}")
