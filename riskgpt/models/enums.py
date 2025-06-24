"""
Enum definitions for RiskGPT.

This module contains all the enum definitions used throughout the RiskGPT system.
"""

from enum import Enum


class LanguageEnum(str, Enum):
    """Supported languages for responses."""

    english = "english"
    german = "german"
    french = "fr"
    spanish = "es"
    italian = "it"
    portuguese = "pt"
    dutch = "nl"
    swedish = "sv"
    norwegian = "no"
    danish = "da"
    finnish = "fi"
    polish = "pl"
    russian = "ru"
    japanese = "ja"
    chinese = "zh"
    korean = "ko"


class AudienceEnum(str, Enum):
    """Supported audiences for presentation output."""

    executive = "executive"
    workshop = "workshop"
    risk_internal = "risk_internal"
    audit = "audit"
    regulator = "regulator"
    project_owner = "project_owner"
    investor = "investor"
    operations = "operations"
