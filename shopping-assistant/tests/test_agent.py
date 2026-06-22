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

from app.agent import DISCOUNT_CODES, redeem_discount_code


def test_redeem_discount_code_success() -> None:
    # Reset discount code state for testing
    DISCOUNT_CODES["WELCOME50"]["redeemed_by"] = None

    # Test successful redemption
    res = redeem_discount_code("user123", "WELCOME50")
    assert "Success" in res
    assert DISCOUNT_CODES["WELCOME50"]["redeemed_by"] == "user123"


def test_redeem_discount_code_unregistered_user() -> None:
    # Test unregistered user ID
    res = redeem_discount_code("unknown_user", "WELCOME50")
    assert "Error" in res
    assert "not a registered user" in res


def test_redeem_discount_code_invalid_code() -> None:
    # Test invalid code
    res = redeem_discount_code("user123", "INVALIDCODE")
    assert "Error" in res
    assert "is invalid" in res


def test_redeem_discount_code_already_redeemed() -> None:
    # Set code as already redeemed
    DISCOUNT_CODES["SUMMER20"]["redeemed_by"] = "user456"

    # Test double redemption of single-use code
    res = redeem_discount_code("user123", "SUMMER20")
    assert "Error" in res
    assert "already been redeemed" in res
