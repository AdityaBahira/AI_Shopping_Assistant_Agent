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

from app.agent import (
    DISCOUNT_CODES,
    LOYALTY_POINTS,
    award_loyalty_points,
    redeem_discount_code,
)


def test_redeem_discount_code() -> None:
    # Reset discount code state for testing
    DISCOUNT_CODES["WELCOME50"]["redeemed_by"] = None
    DISCOUNT_CODES["SUMMER20"]["redeemed_by"] = None

    # Test unregistered user ID
    res = redeem_discount_code("unknown_user", "WELCOME50")
    assert "not a registered user" in res

    # Test invalid code
    res = redeem_discount_code("user123", "INVALIDCODE")
    assert "is invalid" in res

    # Test successful redemption
    res = redeem_discount_code("user123", "WELCOME50")
    assert "Success" in res
    assert DISCOUNT_CODES["WELCOME50"]["redeemed_by"] == "user123"

    # Test double redemption of single-use code
    res2 = redeem_discount_code("user456", "WELCOME50")
    assert "already been redeemed" in res2


def test_award_loyalty_points() -> None:
    # Reset loyalty points balance for testing
    LOYALTY_POINTS["user123"] = 100

    # Test unregistered user ID
    res = award_loyalty_points("unknown_user", 50)
    assert "not a registered user" in res

    # Test validation failure: negative points
    res = award_loyalty_points("user123", -5)
    assert "Input validation failed" in res
    assert LOYALTY_POINTS["user123"] == 100

    # Test validation failure: zero points
    res = award_loyalty_points("user123", 0)
    assert "Input validation failed" in res
    assert LOYALTY_POINTS["user123"] == 100

    # Test validation failure: too many points (exceeding limit)
    res = award_loyalty_points("user123", 10001)
    assert "Input validation failed" in res
    assert LOYALTY_POINTS["user123"] == 100

    # Test successful award
    res = award_loyalty_points("user123", 150)
    assert "Success" in res
    assert LOYALTY_POINTS["user123"] == 250
