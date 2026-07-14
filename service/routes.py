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

from flask import jsonify, abort, url_for, request, current_app as app

from service.models import Promotion, PromotionType, db
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


@app.route("/health", methods=["GET"])
def health():
    """Health endpoint for Kubernetes probes"""
    return jsonify(status="OK"), status.HTTP_200_OK


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

    location_url = url_for("get_promotion", promotion_id=promotion.id, _external=True)

    return (
        jsonify(promotion.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


@app.route("/promotions/<int:promotion_id>", methods=["DELETE"])
def delete_promotion(promotion_id):
    """
    Delete a Promotion

    This endpoint will delete a Promotion based on its ID.
    """
    app.logger.info("Request to delete Promotion with id: %s", promotion_id)
    promotion = Promotion.find(promotion_id)
    if promotion:
        promotion.delete()

    app.logger.info("Promotion with id %s delete complete", promotion_id)
    return "", status.HTTP_204_NO_CONTENT


@app.route("/promotions/<int:promotion_id>", methods=["GET"])
def get_promotion(promotion_id):
    """
    Retrieve a single Promotion

    This endpoint will return a Promotion based on its ID.
    """
    app.logger.info("Request to retrieve Promotion with id: %s", promotion_id)
    promotion = Promotion.find(promotion_id)
    if not promotion:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Promotion with id '{promotion_id}' was not found.",
        )

    app.logger.info("Returning Promotion: %s", promotion.name)
    return jsonify(promotion.serialize()), status.HTTP_200_OK


@app.route("/promotions", methods=["GET"])
def list_promotions():
    """Returns a list of all Promotions, optionally filtered by query params"""
    app.logger.info("Request for promotion list")

    name = request.args.get("name")
    promotion_type = request.args.get("promotion_type")

    if name:
        promotions = Promotion.find_by_name(name).all()
    elif promotion_type:
        try:
            promotion_type_enum = PromotionType[promotion_type.upper()]
            promotions = Promotion.find_by_type(promotion_type_enum).all()
        except KeyError:
            promotions = []
    else:
        promotions = Promotion.all()

    results = [promotion.serialize() for promotion in promotions]
    app.logger.info("Returning %d promotions", len(results))

    return jsonify(results), status.HTTP_200_OK


@app.route("/promotions/<int:promotion_id>", methods=["PUT"])
def update_promotion(promotion_id):
    """Updates an existing Promotion"""
    app.logger.info("Request to update Promotion with id [%s]", promotion_id)
    check_content_type("application/json")

    promotion = Promotion.find(promotion_id)
    if not promotion:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Promotion with id '{promotion_id}' was not found.",
        )

    promotion.deserialize(request.get_json())
    promotion.id = promotion_id  # the URL path id is authoritative
    promotion.update()

    app.logger.info("Promotion with id [%s] updated!", promotion.id)
    return jsonify(promotion.serialize()), status.HTTP_200_OK


@app.route("/promotions/<int:promotion_id>/deactivate", methods=["PUT"])
def deactivate_promotion(promotion_id):
    """Deactivate a Promotion"""
    app.logger.info("Request to deactivate Promotion with id: %s", promotion_id)

    promotion = Promotion.find(promotion_id)
    if not promotion:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Promotion with id '{promotion_id}' was not found.",
        )

    promotion.active = False
    promotion.update()

    app.logger.info("Promotion with id %s has been deactivated", promotion_id)
    return jsonify(promotion.serialize()), status.HTTP_200_OK


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


######################################################################
# RESET DATABASE (test use only)
######################################################################
@app.route("/promotions/reset", methods=["DELETE"])
def reset_promotions():
    """Resets the database for testing — should be disabled in production"""
    # if not app.config.get("TESTING"):
    #    abort(status.HTTP_404_NOT_FOUND)
    db.session.query(Promotion).delete()
    db.session.commit()
    return jsonify(message="database reset"), status.HTTP_200_OK
