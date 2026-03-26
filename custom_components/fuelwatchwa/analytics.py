"""Analytics helper for FuelWatch WA integration."""
from __future__ import annotations

from datetime import datetime, timedelta
from statistics import mean, stdev
from typing import Any

from homeassistant.components.recorder import get_instance
from homeassistant.components.recorder.statistics import (
    get_last_statistics,
    statistics_during_period,
)
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util


async def get_price_statistics(
    hass: HomeAssistant,
    entity_id: str,
    days: int,
) -> dict[str, Any] | None:
    """Get price statistics for the given entity over the specified days.
    
    Returns:
        Dictionary with mean, min, max, change, trend, volatility
        None if insufficient data
    """
    if not await get_instance(hass).async_add_executor_job(
        lambda: get_instance(hass).states
    ):
        return None

    end_time = dt_util.now()
    start_time = end_time - timedelta(days=days)

    # Get statistics from recorder
    stats = await get_instance(hass).async_add_executor_job(
        statistics_during_period,
        hass,
        start_time,
        end_time,
        {entity_id},
        "hour",
        None,
        {"mean"},
    )

    if not stats or entity_id not in stats:
        return None

    data_points = stats[entity_id]
    if len(data_points) < 2:
        return None

    # Extract mean values
    values = [point["mean"] for point in data_points if point.get("mean") is not None]
    
    if len(values) < 2:
        return None

    # Calculate statistics
    avg_price = round(mean(values), 2)
    min_price = round(min(values), 2)
    max_price = round(max(values), 2)
    
    # Calculate trend (comparing first half to second half)
    mid_point = len(values) // 2
    first_half_avg = mean(values[:mid_point]) if mid_point > 0 else values[0]
    second_half_avg = mean(values[mid_point:])
    price_change = round(second_half_avg - first_half_avg, 2)
    
    # Determine trend direction
    if abs(price_change) < 1.0:  # Less than 1 cent change
        trend = "stable"
    elif price_change > 0:
        trend = "increasing"
    else:
        trend = "decreasing"
    
    # Calculate volatility (standard deviation)
    volatility = round(stdev(values), 2) if len(values) > 1 else 0.0
    
    # Calculate percentage change
    if first_half_avg > 0:
        percent_change = round((price_change / first_half_avg) * 100, 2)
    else:
        percent_change = 0.0

    return {
        "average": avg_price,
        "minimum": min_price,
        "maximum": max_price,
        "price_change": price_change,
        "percent_change": percent_change,
        "trend": trend,
        "volatility": volatility,
        "data_points": len(values),
    }


async def get_latest_price(
    hass: HomeAssistant,
    entity_id: str,
) -> float | None:
    """Get the most recent price from statistics."""
    stats = await get_instance(hass).async_add_executor_job(
        get_last_statistics,
        hass,
        1,
        entity_id,
        True,
        {"mean"},
    )
    
    if not stats or entity_id not in stats:
        return None
    
    data = stats[entity_id]
    if not data or not data[0].get("mean"):
        return None
    
    return round(data[0]["mean"], 2)
