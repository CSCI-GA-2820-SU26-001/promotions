######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Promotion Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Promotion
"""

from flask import jsonify, abort, url_for
from flask import current_app as app  # Import Flask application
from service.models import Promotion
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/", methods=["GET"])
def index():
    """Root URL - returns service discovery information."""
    return (
        jsonify(
            service="Promotions Service",
            version="1.0.0",
            promotions_url=url_for("list_promotions", _external=True),
        ),
        200,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

@app.route("/promotions", methods=["POST"])
def create_promotion():
    """Create a new Promotion"""
    app.logger.info("Request to create a Promotion")
    check_content_type("application/json")

    promotion = Promotion()
    promotion.deserialize(request.get_json())
    promotion.create()

    location_url = f"/promotions/{promotion.id}"

    return (
        jsonify(promotion.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid content type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content type must be {media_type}",
    )
