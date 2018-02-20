"""Data generator class for generating data for testing purposes."""
from __future__ import division, print_function
import random
import string
import time


class OPALDataGenerator(object):
    """Generate data as per OPAL formats for testing purposes.

    Args:
        num_antennas (int): Total number of antennas available.
        num_antennas_per_user (int): Total number of different antennas a user
            can connect to.
        num_records_per_user (int): Number of records generated for each user
            over the complete year.
        bandicoot_extended (bool): To use bandicoot extended format or
            old format.

    Todo:
        * Remove bandicoot extended once that library is fixed.

    """

    def __init__(self, num_antennas, num_antennas_per_user,
                 num_records_per_user, bandicoot_extended=True):
        """Initialize data generator class."""
        self.num_antennas = num_antennas
        self.num_antennas_per_user = num_antennas_per_user
        self.num_records_per_user = num_records_per_user
        self.__interactions = ["call", "text", "text", "text"]
        self.__directions = ["in", "out"]
        self.__country_codes = ["44", "33", "212", "19"]
        self.__levels = [
            "Diourbel,Dinguiraye", "Ziguinchor,Bignona", "Dakar,Dakar",
            "Ile-de-france,Paris", "Midi-pyrenee,Toulouse",
            "Aquitaine,Bordeaux", "Alsace,Strasbourg", "Oxfordshire,Oxford",
            "London,London", "Wales,Cardiff", "Scotland,Edinburg",
            "Lazzio,Roma", "Veneto,Venice", "Bruxelles,Bruxelles",
            "Flandesr,Brugges", "Maharashtra,Mumbai"]
        self.bandicoot_extended = bandicoot_extended

    def generate_data(self):
        """Generate data for a single user."""
        antennas = [str(random.randint(0, self.num_antennas - 1))
                    for i in range(self.num_antennas_per_user)]
        latitude = [str(round(random.random()*90, 6))
                    for i in antennas]
        longitude = [str(round(random.random()*180, 6))
                     for i in antennas]
        location = [self.__levels[random.randint(0, 15)]
                    for i in antennas]
        users = [random.choice(string.ascii_letters) + random.choice(
            string.ascii_letters) for j in range(20)]
        lines = []
        if self.bandicoot_extended:
            lines.append('interaction,direction,correspondent_id,datetime,'
                         'call_duration,antenna_id,latitude, longitude,'
                         'location_level_1,location_level_2')
        else:
            lines.append('interaction,direction,correspondent_id,datetime,'
                         'call_duration,antenna_id')
        date_props = [random.random() for i in range(
            self.num_records_per_user)]
        date_props.sort()
        for k in range(self.num_records_per_user):
            lines.append(self.__generate_single_line(
                antennas, users, date_props[k], latitude, longitude, location))
        return '\n'.join(lines) + '\n'

    def __generate_single_line(
            self, antennas, users, date_prop,
            latitude, longitude, location):
        """Generate a single call data record."""
        interaction = random.choice(self.__interactions)
        direction = random.choice(self.__directions)
        user = users[random.randint(0, 19)]
        date = self.__random_date(
            "2016-01-01 00:00:01", "2016-12-31 23:59:59", date_prop)
        call_length = ''
        if interaction == "call":
            call_length = str(
                random.randint(0, self.num_antennas - 1))
        antenna_index = random.randint(0, self.num_antennas_per_user - 1)
        antenna_id = antennas[antenna_index]
        line = ''
        if self.bandicoot_extended:
            line = ','.join([
                interaction, direction, user, date, call_length,
                antenna_id, latitude[antenna_index], longitude[antenna_index],
                location[antenna_index]])
        else:
            line = ','.join([
                interaction, direction, user, date, call_length,
                antenna_id])
        return line

    def __str_time_prop(self, start, end, format, prop):
        """Generate time as proportion between start time and end time."""
        stime = time.mktime(time.strptime(start, format))
        etime = time.mktime(time.strptime(end, format))
        ptime = stime + prop * (etime - stime)
        return time.strftime(format, time.localtime(ptime))

    def __random_date(self, start, end, prop):
        return self.__str_time_prop(start, end, '%Y-%m-%d %H:%M:%S', prop)
