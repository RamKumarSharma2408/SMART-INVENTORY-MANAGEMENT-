from datetime import date, timedelta

from smart_inventory import InventoryItem, SmartInventoryManager


def build_demo_manager() -> SmartInventoryManager:
    manager = SmartInventoryManager()
    manager.add_item(
        InventoryItem(
            item_id="LAB-CHEM-001",
            name="Sodium Chloride Pack",
            category="Lab Chemical",
            location="Chemistry Lab A",
            unit_cost=12.5,
            quantity_on_hand=120,
            reorder_point=60,
            preferred_vendor="EduChem Supplies",
        )
    )
    manager.add_item(
        InventoryItem(
            item_id="LIB-BOOK-042",
            name="Data Structures Textbook",
            category="Library Book",
            location="Central Library",
            unit_cost=45.0,
            quantity_on_hand=35,
            reorder_point=20,
            preferred_vendor="Academic Books Co",
        )
    )

    today = date.today()
    for day_offset in range(1, 46):
        usage_date = today - timedelta(days=day_offset)
        manager.record_usage("LAB-CHEM-001", 2 + (day_offset % 3), usage_date)
        if day_offset % 2 == 0:
            manager.record_usage("LIB-BOOK-042", 1 + (day_offset % 2), usage_date)

    return manager


def main() -> None:
    manager = build_demo_manager()

    print("=== Usage Analytics ===")
    for item_id in manager.items:
        analytics = manager.usage_analytics(item_id, days=30)
        print(item_id, analytics)

    print("\n=== Predictive Restocking ===")
    for item_id in manager.items:
        prediction = manager.predict_restocking(item_id, forecast_days=30, lead_time_days=7)
        print(item_id, prediction)

    print("\n=== Automatic Procurement Suggestions (Budget: $1500) ===")
    for suggestion in manager.automatic_procurement_suggestions(budget_cap=1500):
        print(suggestion)


if __name__ == "__main__":
    main()
