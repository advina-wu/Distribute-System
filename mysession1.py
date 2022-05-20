#!/usr/bin/python3

import reservationapi
import configparser
from exceptions import (
    BadRequestError, InvalidTokenError, BadSlotError, NotProcessedError,
    SlotUnavailableError,ReservationLimitError)


# Load the configuration file containing the URLs and keys
config = configparser.ConfigParser()
config.read("api.ini")


# Create an API object to communicate with the hotel API
hotel  = reservationapi.ReservationApi(config['hotel']['url'],
                                       config['hotel']['key'],
                                       int(config['global']['retries']),
                                       float(config['global']['delay']))
# Create an API object to communicate with the band API
band  = reservationapi.ReservationApi(config['band']['url'],
                                       config['band']['key'],
                                       int(config['global']['retries']),
                                       float(config['global']['delay']))


loop = True
while loop:
    try:
        hotel._headers()
        band._headers()

        available_id_hotel = hotel.get_slots_available()
        r = hotel.reserve_slot(available_id_hotel.json()[0]["id"])

        available_id_band = band.get_slots_available()
        r = band.reserve_slot(available_id_band.json()[0]["id"])

        held_id_hotel = hotel.get_slots_held()
        print("the slots hotel client holds: ", held_id_hotel.json(), "\n")

        held_id_band = band.get_slots_held()
        print("the slots band client holds: ", held_id_band.json(), "\n")

        print("\nHotel client is trying to release the slot: ", held_id_hotel.json()[0]["id"])
        r = hotel.release_slot(held_id_hotel.json()[0]["id"])
 
        # releasing the first slot thats held by the client
        print("Band client is trying to cancel the slot: ", held_id_band.json()[0]["id"])
        r = band.release_slot(held_id_band.json()[0]["id"])

        held_id_hotel = hotel.get_slots_held()
        print("the slots hotel client end up holding: ", held_id_hotel.json())
        held_id_band = band.get_slots_held()
        print("the slots band client end up holding: ", held_id_band.json())

        loop = False


    except BadRequestError as e:
        print(f"bad Error message: {e}")
    except SlotUnavailableError as e:
        # print(e)
        print(f"slot un Error message: {e}")

    except Exception as e:
        print(f"others un Error message: {e}")