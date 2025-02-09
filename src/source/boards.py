"""Module boards.py"""
import logging
import os

import numpy as np
import pandas as pd

import config
import src.functions.streams
import src.source.api


class Boards:
    """
    Notes<br>
    ------<br>

    This class
        <ul>
            <li>Retrieves and saves the latest raw boards data.</li>
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
        self.__rename = {'HB': 'health_board_code', 'HBName': 'health_board_name',
                         'HBDateEnacted': 'health_board_date_enacted'}

    def __get_data(self) -> pd.DataFrame:
        """

        :return:
        """

        return src.source.api.API()(url=self.__url + '&limit=100')

    @staticmethod
    def __inspect(blob: pd.DataFrame, field: str, expectation: int):
        """
        This function checks whether a specified field has the expected number of distinct values.

        :param blob:
        :param field: A field of interest
        :param expectation: The expected number of elements
        :return:
        """

        tensor: np.ndarray = blob[field].unique()

        assert tensor.shape[0] == expectation, f'The number of distinct {field} values is not equal to {expectation}.'

    def __get_key_fields(self, blob: pd.DataFrame):
        """

        :return:
        """

        frame = blob.copy()[self.__rename.keys()]
        frame.rename(columns=self.__rename, inplace=True)
        frame['health_board_date_enacted'] = pd.to_datetime(
            frame['health_board_date_enacted'].astype(dtype=str), errors='coerce', format='%Y%m%d')

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
        self.__inspect(blob=data.copy(), field='HB', expectation=data.shape[0])
        self.__inspect(blob=data.copy(), field='Country', expectation=1)

        # The critical data fields
        frame = self.__get_key_fields(blob=data)

        # Persist
        message = self.__persist(blob=frame, path=os.path.join(self.__configurations.references_, 'boards.csv'))
        logging.info(message)
