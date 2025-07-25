import azure.functions as func
import azure.durable_functions as df
import json
from datetime import datetime,timedelta


myApp = df.DFApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@myApp.route(route="orchestrators/process_order")
@myApp.durable_client_input(client_name="client")
async def http_start(req: func.HttpRequest, client):
    print("req.route_params:", req.route_params)
    input_data = req.get_json() if req.get_body() else None 
    print("input_data:", input_data)
    function_name = req.route_params.get('functionName')
    print(f"Starting orchestrator: {function_name}")
    instance_id = await client.start_new("process_order_orchestrator",None, input_data)
    return client.create_check_status_response(req, instance_id)

@myApp.orchestration_trigger(context_name="context")
def process_order_orchestrator(context):
    print("context:",context)
    order = context.get_input()
    # print("order:", order)
    if not context.is_replaying:
        print("order:", order)

    result = {}
    # Although the orchestrator function re-executes (replays) multiple times for reliability and consistency,
    # the context.call_activity() is not actually executed again
    valid = yield context.call_activity("validate_order", order)
    if not valid:
        return {"status": "Failed", "reason": "Invalid order"}

    # approval = yield context.wait_for_external_event("ApprovalEvent")
    # if not approval.get("approved"):
    #     return {"status": "Failed", "reason": "Manager rejected order"}
    #     curl -X POST \
    #       -H "Content-Type: application/json" \
    #       "http://localhost:7071/runtime/webhooks/durabletask/instances/<instanceId>/raiseEvent/ApprovalEvent" \
    #       -d '{"approved": true}'
    
    payment = yield context.call_activity("charge_payment", order)
    if not payment.get("success"):
        return payment

    # Simulate a delay for inventory check using a timer
    # This is to demonstrate that the orchestrator can wait for a certain condition before proceeding
    next_check_time = context.current_utc_datetime + timedelta(seconds=5)
    print("time @1", datetime.now())
    yield context.create_timer(next_check_time)

    print("time @2", datetime.now())
    in_stock = yield context.call_activity("check_inventory", order["product_id"])
    if not in_stock:
        return {"status": "Failed", "reason": "Out of stock"}

    yield context.call_activity("ship_order", order)
    return {"status": "Success", "message": "Order shipped"}


@myApp.activity_trigger(input_name="order")
def validate_order(order: dict):
    return bool(order.get("product_id") and order.get("amount", 0) > 0)

@myApp.activity_trigger(input_name="order")
def charge_payment(order: dict):
    # simulate charging
    return {"success": True, "message": "Charged successfully"}

@myApp.activity_trigger(input_name="product_id")
def check_inventory(product_id: str):
    # simulate inventory check
    return True

@myApp.activity_trigger(input_name="order")
def ship_order(order: dict):
    # simulate shipping
    return {"tracking_id": "XYZ123"}
