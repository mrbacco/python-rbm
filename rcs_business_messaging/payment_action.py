# Copyright 2018 Google Inc. All rights reserved.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Defines classes for creating a PaymentRequestAction."""

import uuid

# the LineItem type
TYPE_UNSPECIFIED = None
PRIMARY = 'PRIMARY'
SECONDARY = 'SECONDARY'

# constants for bill address format
BILLING_ADDRESS_FORMAT_UNSPECIFIED = None
MIN = 'MIN'
FULL = 'FULL'

class Money(object):
  """
  Represents an amount of money with its currency type.
  """

  def __init__(self, currency_code, units, nanos):
    """
    Constructor.

    Args:
      currency_code (str): The 3-letter currency code defined in ISO 4217.
      units (int): The whole units of the amount. For example if
          currencyCode is "USD", then 1 unit is one US dollar.
      nanos (long): Number of nano (10^-9) units of the amount.
    """
    self._currency_code = currency_code
    self._units = units
    self._nanos = nanos

  def get_object_as_json(self):
    return {
        'currencyCode': self._currency_code,
        'units': self._units,
        'nanos': self._nanos
    }

class LineItem(object):
  """
  A line item in a payment request.
  """

  def __init__(self, item_type, label, amount, sub_text=None):
    """
    Constructor.

    Args:
      item_type (str): The line item type.
      label (str): The text for a line item. For example, "Total due".
      sub_text (str): Text that is displayed in a smaller font below the line item label.
      amount (obj): The Money amount of the line item.
    """
    self._item_type = item_type
    self._label = label
    self._sub_text = sub_text
    self._amount = amount

  def get_object_as_json(self):
    line_item = {
        'label': self._label,
        'amount': self._amount.get_object_as_json()
    }

    if self._item_type:
        line_item['type'] = self._item_type

    if self._sub_text:
        line_item['subText'] = self._sub_text

    return line_item

class TokenizationData(object):
  """
  Tokenization information for the payment request.
  """

  def __init__(self, tokenization_type, parameters):
    """
    Constructor.

    Args:
      tokenization_type (str): The tokenization type for the payment processing provider.
      parameters (str): Tokenization parameters, such as the public key.
          An object containing a list of "key": value pairs.
          Example: { "name": "wrench", "mass": "1.3kg", "count": "3" }.
    """
    self._tokenization_type = tokenization_type
    self._parameters = parameters

  def get_object_as_json(self):
    return {
        'tokenizationType': self._tokenization_type,
        'parameters': self._parameters
    }

class Method(object):
  """
  Supported payment methods.
  """

  def __init__(self, payment_method, merchant_id, merchant_name,
      supported_card_networks, support_card_types, tokenization_data,
      allowed_country_codes, billing_address_required, billing_address_format):
    """
    Constructor.

    Args:
      payment_method (str): The payment method name.
          You must set this field to "https://paywith.google.com/pay".
      merchant_id (str): The merchant ID for the supported payment method.
      merchant_name (str): The merchant name.
      supported_card_networks (array): The supported card networks.
          For example, ["MASTERCARD", "VISA", "DISCOVER"].
      support_card_types (array): The supported card types.
          For example, ["DEBIT", "CREDIT"].
      tokenization_data (obj): Tokenization information for the payment request.
      allowed_country_codes (array): The countries that the payment request is
          valid in, as ISO-2 country codes. For example, ["US", "MX"].
      billing_address_required (boolean): Whether or not the user must
          provide a billing address.
      billing_address_format (str): The billing address format.
    """
    self._payment_method = payment_method
    self._merchant_id = merchant_id
    self._merchant_name = merchant_name
    self._supported_card_networks = supported_card_networks
    self._support_card_types = support_card_types
    self._tokenization_data = tokenization_data
    self._allowed_country_codes = allowed_country_codes
    self._billing_address_required = billing_address_required
    self._billing_address_format = billing_address_format

  def get_object_as_json(self):
    method = {
        'paymentMethod': self._payment_method,
        'merchantId': self._merchant_id,
        'merchantName': self._merchant_name,
        'supportedCardNetworks': self._supported_card_networks,
        'supportedCardTypes': self._support_card_types,
        'tokenizationData': self._tokenization_data.get_object_as_json(),
        'allowedCountryCodes': self._allowed_country_codes,
        'billingAddressRequired': self._billing_address_required
    }

    if self._billing_address_format:
        method['billingAddressFormat'] = self._billing_address_format

    return method

class PaymentRequestAction(object):
  """
  Payment request action.
  """

  def __init__(self, expired_message, completed_message,
      items, total, payment_methods, expire_time = None):
    """
    Constructor.

    Args:
      expired_message (str): Text that replaces the payment request
          text when the request is expired.
      completed_message (str): Text that replaces the payment request
          text when the transaction is complete.
      items (obj): Payment request line items, including regular items,
          taxes, sub-total, and shipping.
      total (obj): The total amount of the payment request. The value
          must be positive.
      payment_methods (obj): Supported payment methods.
      expire_time (str): A timestamp of when the payment request expires.
    """
    self._request_id = str(uuid.uuid4().int) + 'a'
    self._expired_message = expired_message
    self._completed_message = completed_message
    self._items = items
    self._total = total
    self._payment_methods = payment_methods
    self._expire_time = expire_time

  def get_object_as_json(self):
    line_items = []
    for item in self._items:
        line_items.append(item.get_object_as_json())

    payment_methods = []
    for method in self._payment_methods:
        payment_methods.append(method.get_object_as_json())

    request = {
        'requestId': self._request_id,
        'items': line_items,
        'total': self._total.get_object_as_json(),
        'paymentMethods': payment_methods,
        'expiredMessage': self._expired_message,
        'completedMessage': self._completed_message
    }

    if self._expire_time:
        request['expireTime'] = self._expire_time

    return request
