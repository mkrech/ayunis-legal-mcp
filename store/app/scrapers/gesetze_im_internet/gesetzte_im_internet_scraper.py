from app.models import Scraper, LegalText
from typing import List
import requests
import zipfile
import io
import re
from .xml_parser import GermanLegalXMLParser


class GesetzteImInternetScraper(Scraper):
    """Scraper for legal texts from Gesetzte im Internet"""

    def scrape(self, code: str) -> List[LegalText]:
        """Scrape a legal text from a code"""
        url = f"https://www.gesetze-im-internet.de/{code}/xml.zip"
        response = requests.get(url)
        response.raise_for_status()
        xml_data = self._extract_xml_from_zip(response.content)
        parser = GermanLegalXMLParser()
        result = parser.parse_bytes(xml_data)
        extracted_legal_texts: List[LegalText] = []
        print(len(result.norms))
        for norm in result.norms:
            if (
                norm.textdaten
                and norm.textdaten.text
                and norm.textdaten.text.formatted_text
            ):
                # Skip obsolete/repealed sections marked with "(weggefallen)"
                # Check both title and text content
                if norm.metadaten.titel and "(weggefallen)" in norm.metadaten.titel.lower():
                    continue
                
                # Check if all paragraphs contain only "(weggefallen)"
                paragraphs = norm.textdaten.text.formatted_text.paragraphs
                if paragraphs and all(
                    p.strip().lower() == "(weggefallen)" for p in paragraphs
                ):
                    continue
                
                if norm.metadaten.enbez:
                    # Group paragraphs by sub_section to avoid duplicates
                    # (multiple paragraphs with same sub_section get concatenated)
                    sub_section_texts: dict[str, list[str]] = {}
                    for p in norm.textdaten.text.formatted_text.paragraphs:
                        sub_section = self._extract_sub_section(p)
                        if sub_section not in sub_section_texts:
                            sub_section_texts[sub_section] = []
                        sub_section_texts[sub_section].append(p)

                    # Create one LegalText per unique sub_section
                    for sub_section, texts in sub_section_texts.items():
                        # Skip sub-sections that only contain "(weggefallen)" or "(aufgehoben)"
                        # Matches: "(weggefallen)", "(4)(weggefallen)", "(1a) (weggefallen)", "(aufgehoben)", etc.
                        combined_text = "\n\n".join(texts)
                        if re.match(r'^\s*(\([\da-z]+\)\s*)?\((weggefallen|aufgehoben)\)\s*$', combined_text, re.IGNORECASE):
                            continue
                        
                        extracted_legal_texts.append(
                            LegalText(
                                text=combined_text,
                                # we use the code from the url (e.g. rag_1) instead of the jurabk (e.g. RAG 1)
                                # so we know what to query later
                                code=code,
                                section=norm.metadaten.enbez,
                                sub_section=sub_section,
                            )
                        )
        return extracted_legal_texts

    def _extract_xml_from_zip(self, zip_file: bytes) -> bytes:
        with zipfile.ZipFile(io.BytesIO(zip_file), "r") as zip_ref:
            first_file = zip_ref.namelist()[0]
            with zip_ref.open(first_file) as file:
                return file.read()

    def _extract_sub_section(self, section: str) -> str:
        # if section number is present, the str begins with (n)
        if section.startswith("("):
            return section.split("(")[1].split(")")[0]
        # If no subsection number found, return empty string instead of full text
        return ""
