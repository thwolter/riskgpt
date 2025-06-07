"""Chain package initialization.

Imports are wrapped in ``try`` blocks so that optional dependencies do not
prevent basic functionality such as importing lightweight helpers.
"""

# mypy: ignore-errors
from __future__ import annotations

try:  # pragma: no cover - optional dependencies
    from .base import BaseChain  # noqa: F401
except Exception:  # pragma: no cover - optional dependency
    BaseChain = None

try:  # pragma: no cover - optional dependencies
    from .get_categories import (
        async_get_categories_chain,
        get_categories_chain,
    )
except Exception:  # pragma: no cover - optional dependency
    get_categories_chain = None
    async_get_categories_chain = None

try:  # pragma: no cover - optional dependencies
    from .get_risks import async_get_risks_chain, get_risks_chain  # noqa: F401
except Exception:  # pragma: no cover - optional dependency
    get_risks_chain = None
    async_get_risks_chain = None

try:  # pragma: no cover - optional dependencies
    from .check_definition import (
        async_check_definition_chain,
        check_definition_chain,
    )
except Exception:  # pragma: no cover - optional dependency
    check_definition_chain = None
    async_check_definition_chain = None

try:  # pragma: no cover - optional dependencies
    from .get_drivers import async_get_drivers_chain, get_drivers_chain  # noqa: F401
except Exception:  # pragma: no cover - optional dependency
    get_drivers_chain = None
    async_get_drivers_chain = None

try:  # pragma: no cover - optional dependencies
    from .get_assessment import (  # noqa: F401
        async_get_assessment_chain,
        get_assessment_chain,
    )
except Exception:  # pragma: no cover - optional dependency
    get_assessment_chain = None
    async_get_assessment_chain = None

try:  # pragma: no cover - optional dependencies
    from .get_mitigations import (  # noqa: F401
        async_get_mitigations_chain,
        get_mitigations_chain,
    )
except Exception:  # pragma: no cover - optional dependency
    get_mitigations_chain = None
    async_get_mitigations_chain = None

try:  # pragma: no cover - optional dependencies
    from .prioritize_risks import (
        async_prioritize_risks_chain,
        prioritize_risks_chain,
    )
except Exception:  # pragma: no cover - optional dependency
    prioritize_risks_chain = None
    async_prioritize_risks_chain = None

try:  # pragma: no cover - optional dependencies
    from .cost_benefit import async_cost_benefit_chain, cost_benefit_chain  # noqa: F401
except Exception:  # pragma: no cover - optional dependency
    cost_benefit_chain = None
    async_cost_benefit_chain = None

try:  # pragma: no cover - optional dependencies
    from .get_monitoring import (  # noqa: F401
        async_get_monitoring_chain,
        get_monitoring_chain,
    )
except Exception:  # pragma: no cover - optional dependency
    get_monitoring_chain = None
    async_get_monitoring_chain = None

try:  # pragma: no cover - optional dependencies
    from .get_opportunities import (  # noqa: F401
        async_get_opportunities_chain,
        get_opportunities_chain,
    )
except Exception:  # pragma: no cover - optional dependency
    get_opportunities_chain = None
    async_get_opportunities_chain = None

try:  # pragma: no cover - optional dependencies
    from .communicate_risks import (  # noqa: F401
        async_communicate_risks_chain,
        communicate_risks_chain,
    )
except Exception:  # pragma: no cover - optional dependency
    communicate_risks_chain = None
    async_communicate_risks_chain = None

try:  # pragma: no cover - optional dependencies
    from .bias_check import async_bias_check_chain, bias_check_chain  # noqa: F401
except Exception:  # pragma: no cover - optional dependency
    bias_check_chain = None
    async_bias_check_chain = None

try:  # pragma: no cover - optional dependencies
    from .get_correlation_tags import (
        async_get_correlation_tags_chain,
        get_correlation_tags_chain,
    )
except Exception:  # pragma: no cover - optional dependency
    get_correlation_tags_chain = None
    async_get_correlation_tags_chain = None

__all__ = [
    "BaseChain",
    "get_categories_chain",
    "get_risks_chain",
    "check_definition_chain",
    "get_drivers_chain",
    "get_assessment_chain",
    "get_mitigations_chain",
    "prioritize_risks_chain",
    "cost_benefit_chain",
    "get_monitoring_chain",
    "get_opportunities_chain",
    "communicate_risks_chain",
    "bias_check_chain",
    "get_correlation_tags_chain",
    "async_get_categories_chain",
    "async_get_risks_chain",
    "async_check_definition_chain",
    "async_get_drivers_chain",
    "async_get_assessment_chain",
    "async_get_mitigations_chain",
    "async_prioritize_risks_chain",
    "async_cost_benefit_chain",
    "async_get_monitoring_chain",
    "async_get_opportunities_chain",
    "async_communicate_risks_chain",
    "async_bias_check_chain",
    "async_get_correlation_tags_chain",
]
