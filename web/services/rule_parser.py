"""Rule parser service for Scene rules.

This service parses Scene rules (especially [2022] eBOOK) and extracts
structured specifications for packaging validation.
"""

from __future__ import annotations

import re
from typing import Any


class RuleParserService:
    """Parse and extract specifications from Scene rules."""

    def parse_ebook_rule_2022(self, rule_content: str) -> dict[str, Any]:
        """Parse [2022] eBOOK rule completely.

        Args:
            rule_content: Content of the [2022] eBOOK rule.

        Returns:
            Dictionary with structured specifications:
            - file_formats: Accepted file formats
            - naming: Naming format structure
            - required_files: Required files (ZIP, RAR, NFO, DIZ, SFV)
            - packaging: Packaging rules
        """
        return {
            "file_formats": self.extract_file_formats(rule_content),
            "naming": self.extract_naming_format(rule_content),
            "required_files": self.extract_required_files(rule_content),
            "packaging": self.extract_packaging_rules(rule_content),
        }

    def extract_file_formats(self, rule_content: str) -> list[str]:
        """Extract accepted file formats from rule.

        Args:
            rule_content: Rule content.

        Returns:
            List of accepted file extensions (lowercase, with dot).
        """
        formats: list[str] = []

        # Look for OTHER section (formats acceptés)
        # Pattern: "OTHER" followed by formats list
        other_pattern = r"(?:^|\n)\s*OTHER\s*[:;]?\s*(.*?)(?=\n\n|\n[A-Z]{2,}|$)"
        match = re.search(
            other_pattern, rule_content, re.IGNORECASE | re.DOTALL | re.MULTILINE
        )

        if match:
            formats_text = match.group(1)
            # Extract formats: PDF, EPUB, CBZ, Kindle (.azw, .kf8), MOBIPOCKET (.prc, .mobi)
            # Extract PDF
            if re.search(r"\bPDF\b", formats_text, re.IGNORECASE):
                formats.append(".pdf")
            # Extract EPUB
            if re.search(r"\bEPUB\b", formats_text, re.IGNORECASE):
                formats.append(".epub")
            # Extract CBZ
            if re.search(r"\bCBZ\b", formats_text, re.IGNORECASE):
                formats.append(".cbz")
            # Extract Kindle formats (.azw, .kf8)
            if re.search(r"\.azw\b|Kindle.*\.azw", formats_text, re.IGNORECASE):
                formats.append(".azw")
            if re.search(r"\.kf8\b|Kindle.*\.kf8", formats_text, re.IGNORECASE):
                formats.append(".kf8")
            # Extract MOBIPOCKET formats (.prc, .mobi)
            if re.search(r"\.prc\b|MOBIPOCKET.*\.prc", formats_text, re.IGNORECASE):
                formats.append(".prc")
            if re.search(r"\.mobi\b|MOBIPOCKET.*\.mobi", formats_text, re.IGNORECASE):
                formats.append(".mobi")

        # Default formats if not found (based on [2022] eBOOK rule)
        if not formats:
            formats = [".pdf", ".epub", ".cbz", ".azw", ".kf8", ".prc", ".mobi"]

        return sorted(set(formats))

    def extract_naming_format(self, rule_content: str) -> dict[str, Any]:
        """Extract naming format from rule.

        Args:
            rule_content: Rule content.

        Returns:
            Dictionary with naming format structure.
        """
        # Look for DIRNAMING section
        dirnaming_pattern = r"DIRNAMING\s*[:;]?\s*(.*?)(?=\n\n|\n[A-Z]|$)"
        match = re.search(dirnaming_pattern, rule_content, re.IGNORECASE | re.DOTALL)

        if match:
            naming_text = match.group(1)
            # Extract format pattern: GroupName-Author-Title-Format-Language-Year-ISBN-eBook
            format_match = re.search(r"([A-Za-z]+(?:-[A-Za-z]+)*)", naming_text)
            if format_match:
                format_str = format_match.group(1)
                components = format_str.split("-")

                return {
                    "format": format_str,
                    "separators": ["-"],
                    "components": {
                        comp: {"required": True, "format": "string"}
                        for comp in components
                    },
                    "max_length": 243,  # From rule: dirname max 243 chars
                }

        # Default format based on [2022] eBOOK rule
        return {
            "format": "GroupName-Author-Title-Format-Language-Year-ISBN-eBook",
            "separators": ["-"],
            "components": {
                "GroupName": {"required": True, "format": "SceneGroup"},
                "Author": {"required": True, "format": "AuthorName"},
                "Title": {"required": True, "format": "BookTitle"},
                "Format": {
                    "required": True,
                    "values": ["EPUB", "PDF", "CBZ", "MOBI", "AZW", "KF8", "PRC"],
                },
                "Language": {"required": False, "format": "ISO639"},
                "Year": {"required": True, "format": "YYYY"},
                "ISBN": {"required": False, "format": "ISBN13"},
                "eBook": {"required": True, "fixed": "eBook"},
            },
            "max_length": 243,
        }

    def extract_required_files(self, rule_content: str) -> list[str]:
        """Extract required files from rule.

        Args:
            rule_content: Rule content.

        Returns:
            List of required file types (lowercase).
        """
        required: list[str] = []

        # Look for PACKAGING section
        packaging_pattern = r"PACKAGING\s*[:;]?\s*(.*?)(?=\n\n|\n[A-Z]|$)"
        match = re.search(packaging_pattern, rule_content, re.IGNORECASE | re.DOTALL)

        if match:
            packaging_text = match.group(1)

            # Check for ZIP+DIZ obligatoire
            if re.search(r"ZIP.*DIZ.*obligatoire", packaging_text, re.IGNORECASE):
                required.extend(["zip", "diz"])

            # Check for .nfo file obligatoire
            if re.search(r"\.nfo.*obligatoire", packaging_text, re.IGNORECASE):
                required.append("nfo")

            # Check for RAR (optional usually)
            if re.search(r"RAR", packaging_text, re.IGNORECASE):
                # RAR is usually optional, but check if required
                if re.search(r"RAR.*obligatoire", packaging_text, re.IGNORECASE):
                    required.append("rar")

        # Default based on [2022] eBOOK rule: ZIP+DIZ+NFO obligatoire
        if not required:
            required = ["zip", "diz", "nfo"]

        return sorted(set(required))

    def extract_packaging_rules(self, rule_content: str) -> dict[str, Any]:
        """Extract packaging rules from rule.

        Args:
            rule_content: Rule content.

        Returns:
            Dictionary with packaging rules.
        """
        packaging_rules: dict[str, Any] = {
            "zip": {
                "required": True,
                "allowed_sizes": [
                    5000000,
                    10000000,
                    50000000,
                    100000000,
                    150000000,
                    200000000,
                    250000000,
                ],
                "max_files": 99,
            },
            "rar": {
                "required": False,
            },
            "nfo": {
                "required": True,
                "max_width": 80,
            },
            "diz": {
                "required": True,
                "max_width": 44,
                "max_height": 30,
            },
        }

        # Look for ZIP sizes in rule
        zip_pattern = r"ZIP.*?(\d+[.,]?\d*)\s*(?:bytes|MB|mb)"
        zip_matches = re.findall(zip_pattern, rule_content, re.IGNORECASE)

        if zip_matches:
            sizes = []
            for match in zip_matches:
                size_str = match.replace(",", "").replace(".", "")
                try:
                    size = int(size_str)
                    sizes.append(size)
                except ValueError:
                    pass
            if sizes:
                packaging_rules["zip"]["allowed_sizes"] = sorted(sizes)

        return packaging_rules
