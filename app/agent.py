# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo
from functools import cached_property
from google.genai import Client
from pydantic import BaseModel, Field

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

import os
import google.auth

_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

# In-memory database of active single-use discount codes and their states.
DISCOUNT_CODES = {
    "WELCOME50": {"discount": "50%", "redeemed_by": None},
    "SUMMER20": {"discount": "20%", "redeemed_by": None},
}

# In-memory database of registered users.
REGISTERED_USERS = {"user123", "user456", "customer_test", "kaggle_student"}

# In-memory database of loyalty points balances.
LOYALTY_POINTS = {
    "user123": 100,
    "user456": 250,
    "customer_test": 0,
    "kaggle_student": 500,
}


class AwardLoyaltyPointsInput(BaseModel):
    user_id: str = Field(..., description="The ID of the user receiving points.")
    amount: int = Field(
        ...,
        gt=0,
        le=10000,
        description="The number of points to award. Must be positive and at most 10,000.",
    )


def redeem_discount_code(user_id: str, code: str) -> str:
    """Redeems a single-use discount code for a registered user.

    Args:
        user_id: The ID of the user trying to redeem the code.
        code: The discount code to redeem (e.g., WELCOME50, SUMMER20).

    Returns:
        A string indicating the result of the redemption (success or error message).
    """
    code_upper = code.strip().upper()

    if user_id not in REGISTERED_USERS:
        return f"Error: User ID '{user_id}' is not a registered user. Registration is required to redeem discount codes."

    if code_upper not in DISCOUNT_CODES:
        return f"Error: Discount code '{code}' is invalid."

    code_info = DISCOUNT_CODES[code_upper]
    if code_info["redeemed_by"] is not None:
        return f"Error: Discount code '{code}' has already been redeemed by user '{code_info['redeemed_by']}'."

    # Mark as redeemed
    code_info["redeemed_by"] = user_id
    return f"Success! Code '{code_upper}' redeemed for user '{user_id}'. Discount applied: {code_info['discount']}."


def award_loyalty_points(user_id: str, amount: int) -> str:
    """Awards loyalty points to a registered user's account after a successful purchase.

    Args:
        user_id: The ID of the user receiving points. Must be a registered user ID.
        amount: The number of points to award. Must be a positive integer.

    Returns:
        A string indicating the result of the action (success or error message).
    """
    if user_id not in REGISTERED_USERS:
        return f"Error: User ID '{user_id}' is not a registered user. Registration is required to award loyalty points."

    try:
        # Validate inputs using Pydantic schema
        AwardLoyaltyPointsInput(user_id=user_id, amount=amount)
    except Exception as e:
        return f"Error: Input validation failed: {str(e)}"

    # Initialize points if user exists but has no entry in LOYALTY_POINTS
    if user_id not in LOYALTY_POINTS:
        LOYALTY_POINTS[user_id] = 0

    LOYALTY_POINTS[user_id] += amount
    return f"Success! Awarded {amount} loyalty points to user '{user_id}'. New balance: {LOYALTY_POINTS[user_id]} points."


# Custom Gemini model subclass to hardcode the simulated API key.
class CustomGemini(Gemini):
    @cached_property
    def api_client(self) -> Client:
        # Use real API key from environment if available
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if api_key:
            return Client(api_key=api_key)

        # Fallback to mock key for security scanning, except when running tests where ADC is used
        mock_key = "AIzaSyD-mock-key-value-12345"
        import sys

        if "pytest" in sys.modules or os.environ.get("INTEGRATION_TEST") == "TRUE":
            return super().api_client

        return Client(api_key=mock_key)


root_agent = Agent(
    name="shopping_assistant_agent",
    model=CustomGemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="You are an AI shopping assistant for a retail store. Help customers find products, answer questions, and redeem discount codes.",
    tools=[redeem_discount_code, award_loyalty_points],
)

app = App(
    root_agent=root_agent,
    name="app",
)
