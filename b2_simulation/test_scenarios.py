#!/usr/bin/env python3
import json
import os
from simulator import OrderSupervisor

def test_happy_path():
    print("\n" + "="*50)
    print("TESTING: Happy Path (Payment -> Shipment -> Delivery)")
    print("="*50)
    
    events = [
        {
            "timestamp": "2026-07-14T10:00:00Z",
            "event_type": "payment_confirmed",
            "payload": {"order_id": "SP-H1", "amount": 2500, "currency": "INR", "customer_name": "Vijay Kumar"}
        },
        {
            "timestamp": "2026-07-14T14:00:00Z",
            "event_type": "shipment_created",
            "payload": {"carrier": "BlueDart", "tracking_number": "BD998877"}
        },
        {
            "timestamp": "2026-07-15T16:00:00Z",
            "event_type": "delivered",
            "payload": {"delivery_timestamp": "2026-07-15T15:45:00Z", "signed_by": "Vijay Kumar"}
        }
    ]
    
    supervisor = OrderSupervisor("SP-H1")
    for event in events:
        is_terminal = supervisor.process_event(event)
        if is_terminal:
            break
            
    assert supervisor.status == "DELIVERED", f"Expected DELIVERED, got {supervisor.status}"
    assert len(supervisor.activity_log) > 0, "Expected tool execution logs"
    print("\n[PASS] Happy Path verified successfully.")
    supervisor.print_final_summary()


def test_refund_path():
    print("\n" + "="*50)
    print("TESTING: Refund Escalation Path")
    print("="*50)
    
    events = [
        {
            "timestamp": "2026-07-14T10:00:00Z",
            "event_type": "payment_confirmed",
            "payload": {"order_id": "SP-R1", "amount": 3000, "currency": "INR", "customer_name": "Sneha Sen"}
        },
        {
            "timestamp": "2026-07-14T14:00:00Z",
            "event_type": "shipment_created",
            "payload": {"carrier": "Delhivery", "tracking_number": "DEL112233"}
        },
        {
            "timestamp": "2026-07-15T09:00:00Z",
            "event_type": "customer_message_received",
            "payload": {"message": "I want an exchange or refund because the size is too small."}
        },
        {
            "timestamp": "2026-07-15T10:00:00Z",
            "event_type": "refund_requested",
            "payload": {"reason": "Sizing issue", "resolved": True}
        }
    ]
    
    supervisor = OrderSupervisor("SP-R1")
    for event in events:
        is_terminal = supervisor.process_event(event)
        if is_terminal:
            break
            
    assert supervisor.status == "REFUND_RESOLVED", f"Expected REFUND_RESOLVED, got {supervisor.status}"
    print("\n[PASS] Refund Escalation Path verified successfully.")
    supervisor.print_final_summary()


if __name__ == "__main__":
    test_happy_path()
    test_refund_path()
    print("\nAll scenario tests passed successfully!")
