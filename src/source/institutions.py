"""Module institutions.py"""
import logging
import os

import numpy as np
import pandas as pd

import config
import src.functions.streams
import src.source.api


class Institutions:
    """
    Notes<br>
    ------<br>

    This class
        <ul>
            <li>Retrieves and saves the latest raw institutions/hospitals data.</li>
            <li>Extracts and structures the relevant fields for modelling & analysis; subsequently saves.</li>
        </ul>
    """

    def __init__(self, url: str) -> None:
        """

        :param url: The uniform resource locator of the data
        """

        self.__url = url

        # Configurations
        self.__configurations = config.Config()

        # Renaming
        self.__rename = {'HospitalCode': 'hospital_code', 'HospitalName': 'hospital_name',
                         'AddressLine1': 'address_line_1', 'AddressLine2': 'address_line_2',
                         'AddressLine3': 'address_line_3', 'AddressLine4': 'address_line_4',
                         'Postcode': 'post_code', 'HealthBoard': 'health_board_code', 'HSCP': 'hscp_code',
                         'CouncilArea': 'council_area', 'IntermediateZone': 'intermediate_zone',
                         'DataZone': 'data_zone'}

    def __get_data(self) -> pd.DataFrame:
        """

        :return:
        """

        return src.source.api.API().__call__(url=self.__url + '&limit=1000')

    @staticmethod
    def __inspect(data: pd.DataFrame, field: str) -> None:
        """
        This function checks whether a specified field has distinct values.

        :param field: A field of interest
        :return:
        """

        tensor: np.ndarray = data[field].unique()

        assert tensor.shape[0] == data[field].shape[0], f'The {field} field values are not distinct.'

    def __get_key_fields(self, data: pd.DataFrame) -> pd.DataFrame:
        """

        :param data:
        :return:
        """

        frame = data.copy()[self.__rename.keys()]
        frame.rename(columns=self.__rename, inplace=True)

        return frame

    @staticmethod
    def __persist(blob: pd.DataFrame, path: str):
        """

        :param blob: The data being saved.
        :param path: The storage string of a data set.
        :return:
        """

        streams = src.functions.streams.Streams()

        return streams.write(blob=blob, path=path)

    def exc(self) -> None:
        """

        :return:
        """

        data = self.__get_data()

        # Assert
        self.__inspect(data=data.copy(), field='HospitalCode')

        # The critical data fields
        frame = self.__get_key_fields(data=data)

        # Persist
        message = self.__persist(blob=frame, path=os.path.join(self.__configurations.references_, 'institutions.csv'))
        logging.info(message)
