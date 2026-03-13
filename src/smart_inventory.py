from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from statistics import mean
from typing import Dict, List, Optional


@dataclass
class InventoryItem:
    item_id: str
    name: str
    category: str
    location: str
    unit_cost: float
    quantity_on_hand: int
    reorder_point: int
    preferred_vendor: str


@dataclass
class UsageEvent:
    item_id: str
    event_date: date
    quantity_used: int


@dataclass
class ProcurementSuggestion:
    item_id: str
    item_name: str
    recommended_order_qty: int
    urgency_score: float
    estimated_cost: float
    reason: str


@dataclass
class SmartInventoryManager:
    items: Dict[str, InventoryItem] = field(default_factory=dict)
    usage_events: List[UsageEvent] = field(default_factory=list)

    def add_item(self, item: InventoryItem) -> None:
        self.items[item.item_id] = item

    def record_usage(self, item_id: str, quantity_used: int, event_date: Optional[date] = None) -> None:
        if item_id not in self.items:
            raise ValueError(f"Unknown item_id: {item_id}")
        if quantity_used <= 0:
            raise ValueError("quantity_used must be positive")

        item = self.items[item_id]
        item.quantity_on_hand = max(0, item.quantity_on_hand - quantity_used)
        self.usage_events.append(
            UsageEvent(item_id=item_id, quantity_used=quantity_used, event_date=event_date or date.today())
        )

    def usage_analytics(self, item_id: str, days: int = 30) -> Dict[str, float]:
        if item_id not in self.items:
            raise ValueError(f"Unknown item_id: {item_id}")

        start_date = date.today() - timedelta(days=days)
        filtered = [e for e in self.usage_events if e.item_id == item_id and e.event_date >= start_date]
        total_used = sum(e.quantity_used for e in filtered)
        avg_daily_usage = total_used / days if days else 0
        active_days = len({e.event_date for e in filtered})

        return {
            "days": float(days),
            "total_used": float(total_used),
            "avg_daily_usage": round(avg_daily_usage, 2),
            "active_days": float(active_days),
            "usage_frequency": round((active_days / days) * 100, 2) if days else 0,
        }

    def predict_restocking(self, item_id: str, forecast_days: int = 30, lead_time_days: int = 7) -> Dict[str, float]:
        if item_id not in self.items:
            raise ValueError(f"Unknown item_id: {item_id}")

        item = self.items[item_id]
        daily_usage_series = self._daily_usage(item_id, lookback_days=60)
        baseline_daily_usage = mean(daily_usage_series) if daily_usage_series else 0

        demand_during_lead_time = baseline_daily_usage * lead_time_days
        safety_stock = max(item.reorder_point * 0.25, 5)
        reorder_threshold = demand_during_lead_time + safety_stock
        projected_demand = baseline_daily_usage * forecast_days
        projected_stockout_days = (
            (item.quantity_on_hand / baseline_daily_usage) if baseline_daily_usage > 0 else float("inf")
        )

        recommended_order_qty = max(0, int(round((projected_demand + safety_stock) - item.quantity_on_hand)))

        return {
            "baseline_daily_usage": round(baseline_daily_usage, 2),
            "demand_during_lead_time": round(demand_during_lead_time, 2),
            "reorder_threshold": round(reorder_threshold, 2),
            "current_stock": float(item.quantity_on_hand),
            "forecast_days": float(forecast_days),
            "projected_stockout_days": round(projected_stockout_days, 2)
            if projected_stockout_days != float("inf")
            else float("inf"),
            "recommended_order_qty": float(recommended_order_qty),
        }

    def automatic_procurement_suggestions(self, budget_cap: Optional[float] = None) -> List[ProcurementSuggestion]:
        suggestions: List[ProcurementSuggestion] = []

        for item_id, item in self.items.items():
            prediction = self.predict_restocking(item_id)
            recommended_qty = int(prediction["recommended_order_qty"])
            threshold = prediction["reorder_threshold"]
            if recommended_qty <= 0 and item.quantity_on_hand > threshold:
                continue

            stock_risk = max(0.0, threshold - item.quantity_on_hand)
            urgency_score = round((stock_risk + recommended_qty) / max(1, item.reorder_point), 2)
            estimated_cost = round(recommended_qty * item.unit_cost, 2)
            reason = (
                "Below predictive reorder threshold"
                if item.quantity_on_hand <= threshold
                else "Upcoming demand indicates replenishment"
            )

            suggestions.append(
                ProcurementSuggestion(
                    item_id=item_id,
                    item_name=item.name,
                    recommended_order_qty=recommended_qty,
                    urgency_score=urgency_score,
                    estimated_cost=estimated_cost,
                    reason=reason,
                )
            )

        suggestions.sort(key=lambda s: s.urgency_score, reverse=True)

        if budget_cap is not None:
            selected: List[ProcurementSuggestion] = []
            spent = 0.0
            for suggestion in suggestions:
                if spent + suggestion.estimated_cost <= budget_cap:
                    selected.append(suggestion)
                    spent += suggestion.estimated_cost
            return selected

        return suggestions

    def _daily_usage(self, item_id: str, lookback_days: int = 60) -> List[int]:
        start_date = date.today() - timedelta(days=lookback_days)
        usage_by_day: Dict[date, int] = {}

        for event in self.usage_events:
            if event.item_id != item_id or event.event_date < start_date:
                continue
            usage_by_day[event.event_date] = usage_by_day.get(event.event_date, 0) + event.quantity_used

        days = [start_date + timedelta(days=i) for i in range(lookback_days + 1)]
        return [usage_by_day.get(day, 0) for day in days]
