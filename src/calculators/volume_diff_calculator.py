import numpy as np
import scipy.stats as stats

from .analytics_calculator import AnalyticsCalculator


class VolumeDiffCalculator(AnalyticsCalculator):
    """
    Represents a class that calculates volume differences given volume data.
    """

    def __init__(self):
        """
        Initialises a new instance of this class.
        """
        super().__init__("volume_diff", "volume")

    def _calculate_analytics(self, fundamentals):
        """
        Calculate the analytics using the given fundamentals.

        Parameters
        ----------
        fundamentals : double[]
            An array of fundamentals.

        Returns
        -------
            An array of the calculated analytics.
        """
        volumes = list(filter(None, fundamentals))

        volume_diffs = np.diff(volumes)

        return volume_diffs

    def _calculate_latest_analytics(self, latest_fundamental, fundamentals, analytics):
        """
        Calculate the analytics using the given fundamentals but only for the latest tick.

        Parameters
        ----------
        latest_fundamental : double
            The latest tick price.
        fundamentals : double[]
            An array of fundamentals.
        analytics : double[
            An array of analytics values.

        Returns
        -------
            An array of the calculated analytics.
        """

        if len(fundamentals) < 2:
            raise Exception(
                "There are insufficient price data points to calculate a singular price difference value."
            )

        in_scope_volumes = (
            fundamentals[-2:]
            if latest_fundamental is None
            else [fundamentals[-2], latest_fundamental]
        )

        new_volume_diff = np.diff(in_scope_volumes)[-1]
        z_score = stats.zscore([*analytics[:-1], new_volume_diff])[-1]

        return {
            "time_series": None,
            f"last_{self.id}": new_volume_diff,
            "last_z_score": z_score,
        }
