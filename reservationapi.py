""" Reservation API wrapper

This class implements a simple wrapper around the reservation API. It
provides automatic retries for server-side errors, delays to prevent
server overloading, and produces sensible exceptions for the different
types of client-side error that can be encountered.
"""

# This file contains areas that need to be filled in with your own
# implementation code. They are marked with "Your code goes here".
# Comments are included to provide hints about what you should do.

from ast import excepthandler
from lib2to3.pgen2 import token
import requests
import simplejson
import warnings
import time


from requests.exceptions import HTTPError
from exceptions import (
    BadRequestError, InvalidTokenError, BadSlotError, NotProcessedError,
    SlotUnavailableError,ReservationLimitError)

class ReservationApi:
    def __init__(self, base_url: str, token: str, retries: int, delay: float):
        """ Create a new ReservationApi to communicate with a reservation
        server.

        Args:
            base_url: The URL of the reservation API to communicate with.
            token: The user's API token obtained from the control panel.
            retries: The maximum number of attempts to make for each request.
            delay: A delay to apply to each request to prevent server overload.
        """
        self.base_url = base_url
        self.token    = token
        self.retries  = retries
        self.delay    = delay

    def _reason(self, req: requests.Response) -> str:
        """Obtain the reason associated with a response"""
        reason = ''

        # Try to get the JSON content, if possible, as that may contain a
        # more useful message than the status line reason
        try:
            json = req.json()
            reason = json['message']

        # A problem occurred while parsing the body - possibly no message
        # in the body (which can happen if the API really does 500,
        # rather than generating a "fake" 500), so fall back on the HTTP
        # status line reason
        except simplejson.errors.JSONDecodeError:
            if isinstance(req.reason, bytes):
                try:
                    reason = req.reason.decode('utf-8')
                except UnicodeDecodeError:
                    reason = req.reason.decode('iso-8859-1')
            else:
                reason = req.reason

        return reason


    def _headers(self) -> dict:
        """Create the authorization token header needed for API requests"""
        # Your code goes here
        header = {"Authorization": "Bearer " + self.token}
        return header



    def _send_request(self, method: str, endpoint: str) -> dict:
        """Send a request to the reservation API and convert errors to
           appropriate exceptions"""
        # Your code goes here

        # try:
            # Allow for multiple retries if needed
        for i in range(self.retries):
            # Perform the request.
            try:
                if (method == "POST"):
                    r = requests.post( endpoint, headers=self._headers())

                elif (method == "DELETE"):
                    r = requests.delete( endpoint, headers=self._headers())

                    # r = self.release_slot(endpoint)
                elif (method == "GET"):
                    r = requests.get( endpoint, headers=self._headers())

            # Delay before processing the response to avoid swamping server.
                time.sleep(self.delay)

            # 200 response indicates all is well - send back the json data.
                if (r.status_code == 200):
                    if (method == "POST"):
                        print("success! The slot has been booked")
                    elif (method == "DELETE"):
                        print("The reservation of the slot has been cancelled")
                    return r
            # 5xx responses indicate a server-side error, show a warning
            # (including the try number).
            
                elif (r.status_code >= 500 and r.status_code < 600):
                    print("Attempt: " + str(i))
                    # mes = "Service unavailable. The status code : "+ str(r.status_code)
                    warnings.warn(message = "Service unavailable. The status code : "+ str(r.status_code) )
                    # print(self._reason(r.status_code))

                elif (r.status_code == 400):
                    # print("400")
                    # print(self._reason(r))
                    raise BadRequestError(self._reason(r))
                    # return r
                elif (r.status_code == 401):
                    # print("401")
                    # print(self._reason(r))
                    raise InvalidTokenError(self._reason(r))
                elif (r.status_code == 403):
                    # print("403")
                    # print(self._reason(r))
                    raise BadSlotError(self._reason(r))
                elif (r.status_code == 404):
                    # print("404")
                    # print(self._reason(r))
                    raise NotProcessedError(self._reason(r))
                elif (r.status_code == 409):
                    # print("409")
                    # print(self._reason(r))
                    raise SlotUnavailableError(self._reason(r))
                elif (r.status_code == 451):
                    # print("451")
                    # print(self._reason(r))
                    raise ReservationLimitError(self._reason(r))
                else:
                    raise HTTPError(self._reason(r))

            # Anything else is unexpected and may need to kill the client.
            # Get here and retries have been exhausted, throw an appropriate exception.
            

            except BadRequestError as e:
                print("bad requestion BadRequestError")
                # print(f"Error message: {e}")
                # print(self._reason(e))

                raise e
                # pass

            except InvalidTokenError as e:
                # print("The API token was invalid or missing. InvalidTokenError")
                # print(f"inv Error message: {e}")
                # print(self._reason(e))
                # return r

                raise SystemExit(e)


            except BadSlotError as e:
                # print("SlotId does not exist. BadSlotError")
                print(f"bad Error message: {e}")
                # print(self._reason(e))
                # return r

                raise SystemExit(e)
                # raise e

            except NotProcessedError as e:
                # print("The request has not been proceed NotProcessedError")
                print(f"not Error message: {e}")
                # print(self._reason(e))


            except SlotUnavailableError as e:
                # print("Slot is not available SlotUnavailableError")
                print(f"slot Error message: {e}")
                # print(self._reason(e))
                # pass
                raise e



            except ReservationLimitError as e:
                # print("The client already holds the number of reservations ReservationLimitError")
                print(f"slot Error message: {e}")
                # pass
                # raise e
                return 0

            except HTTPError as e:
                # print("other exception")
                # print(f"Error message: {e}")
                print(self._reason(e))
                # raise SystemExit(e)

            # except requests.exceptions.RequestException as e:
            #     # print("other exception")
            #     # print(f"Error message: {e}")
            #     # print(self._reason(e))
            #     raise SystemExit(e)

        raise requests.exceptions.RequestException("Retries have been exhausted" )



    def get_slots_available(self):
        """Obtain the list of slots currently available in the system"""
        # Your code goes here
        # response = requests.get(self.base_url+ "/reservation/available", headers=self._headers())
        response = self._send_request("GET", self.base_url+ "/reservation/available")
        return response

    def get_slots_held(self):
        """Obtain the list of slots currently held by the client"""
        # Your code goes here
        # response = requests.get(self.base_url+ "/reservation", headers=self._headers())
        response = self._send_request("GET", self.base_url+ "/reservation")

        return response

    def release_slot(self, slot_id):
        """Release a slot currently held by the client"""
        # Your code goes here
        # response = requests.delete( self.base_url+ "/reservation/{}".format(slot_id), headers=self._headers())
        response = self._send_request("DELETE", self.base_url+ "/reservation/{}".format(slot_id))
        return response

    def reserve_slot(self, slot_id):
        """Attempt to reserve a slot for the client"""
        # Your code goes here
        # response = requests.post( self.base_url+ "/reservation/{}".format(slot_id), headers=self._headers())

        response = self._send_request("POST", self.base_url+ "/reservation/{}".format(slot_id))
        return response