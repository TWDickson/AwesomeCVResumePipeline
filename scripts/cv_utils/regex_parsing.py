"""Regex parsing utilities for CV scripts."""


import re
from datetime import date


def clean_latex_text(text: str, *, convert_bold_italic=True, handle_today=False) -> str:
    r"""
    Remove LaTeX commands and clean up text.
    Options:
        convert_bold_italic: If True, convert \\textbf, \\textit, \\emph to markdown.
        handle_today: If True, replace \\today with current date.
    """

    # Replace escaped LaTeX special characters with their literal equivalents before any other processing
    # Use a placeholder for escaped percent to preserve it through comment removal
    PERCENT_PLACEHOLDER = '<<PERCENT_SIGN_PLACEHOLDER>>'
    text = re.sub(r'\\%', PERCENT_PLACEHOLDER, text)
    text = re.sub(r'\\_', '_', text)
    text = re.sub(r'\\\$', '$', text)
    text = re.sub(r'\\&', '&', text)

    # Remove comments: only unescaped % (count preceding backslashes to check)
    def remove_latex_comment(line):
        i = 0
        while i < len(line):
            if line[i] == '%':
                # Count preceding backslashes
                bs = 0
                j = i - 1
                while j >= 0 and line[j] == '\\':
                    bs += 1
                    j -= 1
                if bs % 2 == 0:
                    return line[:i].rstrip()
            i += 1
        return line
    text = '\n'.join(remove_latex_comment(line) for line in text.splitlines())
    # Restore percent placeholders
    text = text.replace(PERCENT_PLACEHOLDER, '%')

    if convert_bold_italic:
        text = re.sub(r'\\textbf\{([^}]+)\}', r'**\1**', text)
        text = re.sub(r'\\textit\{([^}]+)\}', r'*\1*', text)
        text = re.sub(r'\\emph\{([^}]+)\}', r'*\1*', text)
    else:
        text = re.sub(r'\\textbf\{([^}]+)\}', r'\1', text)
        text = re.sub(r'\\textit\{([^}]+)\}', r'\1', text)
        text = re.sub(r'\\emph\{([^}]+)\}', r'\1', text)

    # Remove various LaTeX spacing commands and replace with space
    text = re.sub(r'\\enskip|\\quad|\\qquad|~', ' ', text)
    text = re.sub(r'\\cdotp', '·', text)

    # Remove nested braces that just contain spacing commands (common in taglines)
    text = re.sub(r'\{(\s*·?\s*)\}', r'\1', text)

    # Remove remaining backslash commands (but not escaped special characters or percent signs)
    # Only match commands that are not followed by %, _, $, or &
    text = re.sub(r'\\(?![%_\$&])[a-zA-Z]+(\[[^\]]*\])?(\{[^}]*\})?', '', text)

    # Remove any leftover empty braces
    text = re.sub(r'\{\}', '', text)

    if handle_today:
        text = re.sub(r'\\today', date.today().strftime('%B %d, %Y'), text)

    # Clean up whitespace (including multiple spaces and spaces around dots)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s*·\s*', ' · ', text)  # Normalize spacing around separators
    text = text.strip()
    return text


def normalize_company(company: str) -> str:
    """Normalize company names for matching."""
    normalized = re.sub(r'\s*-{2,}\s*', ' - ', company)
    normalized = re.sub(r'\s+-\s+Ministry of the\s+', ' - ', normalized, flags=re.IGNORECASE)
    return normalized.strip()


def normalize_dates(dates: str, present_year='2024') -> str:
    """Normalize date formats for matching."""
    normalized = re.sub(r'\s*-{2,}\s*', ' - ', dates)
    normalized = re.sub(r'Present', present_year, normalized, flags=re.IGNORECASE)
    normalized = re.sub(r'\s+', '', normalized)
    return normalized
