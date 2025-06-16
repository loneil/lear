# Copyright © 2024 Province of British Columbia
#
# Licensed under the BSD 3 Clause License, (the 'License');
# you may not use this file except in compliance with the License.
# The template for the license can be found here
#    https://opensource.org/license/bsd-3-clause/
#
# Redistribution and use in source and binary forms,
# with or without modification, are permitted provided that the
# following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS”
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
"""This Module processes simple cloud event messages for Digital Credentials.
"""
from http import HTTPStatus

import requests
from flask import Blueprint, current_app, request
from simple_cloudevent import SimpleCloudEvent

# TODO: copied from emailer to start out
from business_digital_credentials.exceptions import QueueException
from business_digital_credentials.services import flags, gcp_queue, verify_gcp_jwt
# from business_model.models import Filing, Furnishing

bp = Blueprint("worker", __name__)




@bp.route("/", methods=("POST",))
def worker():
    """Use endpoint to process Queue Msg objects."""
    try:
        if not request.data:
            return {}, HTTPStatus.OK

        if msg := verify_gcp_jwt(request):
            current_app.logger.info(msg)
            return {}, HTTPStatus.FORBIDDEN

        current_app.logger.info(f"Incoming raw msg: {request.data!s}")

        # 1. Get cloud event
        ce = gcp_queue.get_simple_cloud_event(request, wrapped=True)
        if not ce and not isinstance(ce, SimpleCloudEvent):
            # todo: verify this ? this is how it is done in other GCP pub sub consumers
            # Decision here is to return a 200,
            # so the event is removed from the Queue
            current_app.logger.debug(f"ignoring message, raw payload: {ce!s}")
            return {}, HTTPStatus.OK

        current_app.logger.info(f"received ce: {ce!s}")

        raise NotImplementedError("Digital Credentials feature is WIP.")

        # Process event
        # TODO implement
        return {}, HTTPStatus.OK

    # ruff: noqa: PGH004
    except QueueException as err:  # noqa B902; pylint: disable=W0703; :
        # Catch Exception so that any error is still caught and the message is removed from the queue
        current_app.logger.error("Queue Error: %s", ce, exc_info=True)
        return {}, HTTPStatus.BAD_REQUEST

