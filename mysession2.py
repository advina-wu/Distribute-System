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
# Create an API object to communicate with the hotel API
band  = reservationapi.ReservationApi(config['band']['url'],
                                       config['band']['key'],
                                       int(config['global']['retries']),
                                       float(config['global']['delay']))



hotel._headers()
band._headers()

slot_found = 0
available_id_for_both = 0
has_same_slot_as_booked = False
worse_slot = False
z = True
try:
    while (slot_found < 2):

        print("in while \n")

        # getting the held spot
        held_hotel = hotel.get_slots_held().json()
        held_band = band.get_slots_held().json()
        print(held_hotel)
        print(held_band)

        available_id_hotel = hotel.get_slots_available()
        available_id_band = band.get_slots_available()
        len_hotel_ava = len(available_id_hotel.json())
        len_band_ava = len(available_id_band.json())
        
        for x in range(len_hotel_ava):
            for y in range(len_band_ava):
                if (int(available_id_for_both) <= int(available_id_hotel.json()[x]["id"]) and int(available_id_for_both) != 0):
                    print("The slot they have is alreay better")
                    # has_same_slot_as_booked = True
                    worse_slot = True
                    # right now the problem is that the loop doesnt terminate even with this...
                    # if we want the program to run until it finds a better/ the best spot, then uncomment the below line
                    slot_found += 1
                    break

                elif (int(available_id_hotel.json()[x]["id"]) == int(available_id_band.json()[y]["id"])):
                    # print(str(y) +"band: " + available_id_band.json()[y]["id"])
                    available_id_for_both = available_id_hotel.json()[x]["id"]
                    print("Common slot available " + available_id_for_both)
                    break
                elif (int(available_id_hotel.json()[x]["id"]) < int(available_id_band.json()[y]["id"])):
                    # print(str(j) +  "band: " + available_id_band.json()[j]["id"])
                    # print("breaking\n")
                    break
            if (available_id_for_both != 0):
                break
            # if teh current best slot isnt as good as before then reloop
            if (worse_slot):
                break

        print(available_id_for_both)


        # getting the held spot
        held_hotel_before = hotel.get_slots_held().json()
        held_band_before = band.get_slots_held().json()

        for j in range(len(held_band_before)):
            # if these two are the same it means theres no better slot found then break the loop
            if (held_band_before[j] == available_id_for_both):
                slot_found += 1
                break

        # it means there is no reserved slot
        if (available_id_for_both != 0 ):
            # and len(held_band_before) != 0 
            print("in available_id_for_both != 0")
            # only reserver slot for band AND hotel when both has no slot booked
            if ( len(held_hotel_before) == len(held_band_before) and  len(held_hotel_before) < 2):

                # book slot
                hotel.reserve_slot(available_id_for_both)
                band.reserve_slot(available_id_for_both)

                # check if ther slot has been reserved for both
                held_hotel_after = hotel.get_slots_held().json()
                held_band_after = band.get_slots_held().json()

                # if none of them are empty, add the slot_found to 1 so it has one more go to see if theres any better slot
                if (len(held_hotel_after) == len(held_band_after) and len(held_band_after) - 1 == len(held_band_before)):
                    print("Good ! The slot " + available_id_for_both + " is booked for both!")
                    slot_found += 1

                    if (len(held_hotel_after) == 2):
                        # once it is successfully booked a better one, then release the previous one
                        hotel.release_slot(held_hotel_after[0]["id"])
                        band.release_slot(held_band_after[0]["id"])


                elif (len(held_hotel_after) == len(held_band_after) and len(held_band_after) == len(held_band_before)):
                    print("Both hotel and band failed to book the slot")
                # if band hasnt hold a slot but hotel doesnt, release band's slot
                elif (len(held_hotel_after) - len(held_band_after) == 1):
                    print("hotel empty but band not")
                    band.release_slot(held_hotel_after[0]["id"])

                # if hotel hasnt hold a slot but band doesnt, release hotel's slot
                elif (len(held_band_after) - len(held_hotel_after) == 1):
                    print("band empty but hotel not")
                    band.release_slot(held_band_after[0]["id"])
            else:
                print("Hotel and band dpes mpy has the same amount of booked slot")

                if (len(held_band_before) - len(held_hotel_before) == 1):
                    band.release_slot(held_band_before[0]["id"])
                elif (len(held_hotel_before) - len(held_band_before) == 1):
                    hotel.release_slot(held_hotel_before[0]["id"])

        else:
            print("No slot found")

except BadRequestError as e:
    print(f"bad Error message: {e}")
except SlotUnavailableError as e:
    print(f"slot un Error message: {e}")

    held_hotel = hotel.get_slots_held().json()
    held_band = band.get_slots_held().json()

    if (len(held_hotel) - len(held_band) == 1):
        print("hotel empty but band not")
        band.release_slot(held_hotel[0]["id"])

    # if hotel hasnt hold a slot but band doesnt, release hotel's slot
    elif (len(held_band) - len(held_hotel) == 1):
        print("band empty but hotel not")
        band.release_slot(held_band[0]["id"])
except Exception as e:
    # print(e)
    print(f"others un Error message: {e}")