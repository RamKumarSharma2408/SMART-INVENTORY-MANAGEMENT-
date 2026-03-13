from datetime import date, timedelta

from src.smart_inventory import InventoryItem, SmartInventoryManager


def manager_with_data() -> SmartInventoryManager:
    manager = SmartInventoryManager()
    manager.add_item(
        InventoryItem(
            item_id="LAB-001",
            name="Microscope Slides",
            category="Lab",
            location="Bio Lab",
            unit_cost=2.0,
            quantity_on_hand=50,
            reorder_point=25,
            preferred_vendor="LabVendor",
        )
    )

    for i in range(1, 16):
        manager.record_usage("LAB-001", 2, date.today() - timedelta(days=i))
    return manager


def test_usage_analytics_totals():
    manager = manager_with_data()
    analytics = manager.usage_analytics("LAB-001", days=10)

    assert analytics["total_used"] == 20.0
    assert analytics["avg_daily_usage"] == 2.0


def test_predict_restocking_returns_order_quantity():
    manager = manager_with_data()
    prediction = manager.predict_restocking("LAB-001", forecast_days=20, lead_time_days=5)

    assert prediction["baseline_daily_usage"] > 0
    assert prediction["recommended_order_qty"] >= 0


def test_procurement_suggestions_sorted():
    manager = manager_with_data()
    suggestions = manager.automatic_procurement_suggestions()

    assert len(suggestions) == 1
    assert suggestions[0].item_id == "LAB-001"
