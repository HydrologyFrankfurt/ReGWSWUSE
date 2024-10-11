# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================

"""GWSWUSE model equations for numpy arrays."""

import os
from numba import njit
import numpy as np
from model import time_unit_conversion as tc

# =================================================================
# Get module name and remove the .py extension
# Module name is passed to logger
# # ===============================================================
modname = os.path.basename(__file__)
modname = modname.split('.')[0]


# =========================================================================
#   model equations which are based on logic for every sector
# =========================================================================

#                  =================================
#                  ||     CALC GWSW WATER USE     ||
#                  =================================


@njit(cache=True)
def calc_gwsw_water_use(use_tot, fraction_gw_use):
    """
    Calculate sector-specific groundwater and surface water use.

    The function is used for the following sectors:
        - Irrigation (only cu)
        - Domestic
        - Manufacturing
        - Thermal Power
        - Livestock

    Parameters
    ----------
    use_tot : numpy.ndarray
        Sector-specific water use variable (consumptive use or abstraction)
        from total water resources.
    fraction_gw_use : numpy.ndarray
        Sector-specific relative fraction of groundwater use.

    Returns
    -------
    use_gw : numpy.ndarray
        Sector-specific consumptive use or abstraction from groundwater.
    use_sw : numpy.ndarray
       Sector-specific consumptive use or abstraction from surface water.

    """
    use_gw = fraction_gw_use * use_tot
    use_sw = use_tot - use_gw

    return use_gw, use_sw

#                  =================================
#                  ||      CALC RETURN FLOWS      ||
#                  =================================


@njit(cache=True)
def calc_return_flow_totgwsw(abstraction_tot,
                             consumptive_use_tot,
                             fraction_return_gw):
    """
    Calculate sector-specific return flows total and to gw and sw.

    The function is used for the following sectors:
        - Irrigation
        - Domestic
        - Manufacturing
        - Thermal Power
        - Livestock

    Parameters
    ----------
    abstraction_tot : numpy.ndarray
        Sector-specific water abstraction from total water resources.
    consumptive_use_tot : numpy.ndarray
        Sector-specific consumptive water use from total water resources.
    fraction_return_gw : numpy.ndarray or xarray
        Sector-specific relative fraction of return flow to groundwater.

    Returns
    -------
    return_flow_tot : numpy.ndarray
        Total return flow from the sector, calculated as the difference
        between withdrawal water use and consumptive water use.
     return_flow_gw : numpy.ndarray or xarray
         Sector-specific return flow to groundwater.
     return_flow_sw : numpy.ndarray
         Sector-specific return flow to surface water.
    """
    # calculation of total return flow
    return_flow_tot = abstraction_tot - consumptive_use_tot
    return_flow_gw = fraction_return_gw * return_flow_tot
    return_flow_sw = (1 - fraction_return_gw) * return_flow_tot

    return return_flow_tot, return_flow_gw, return_flow_sw

#                  =================================
#                  ||    CALC NET ABSTRACTIONS    ||
#                  =================================


@njit(cache=True)
def calc_net_abstraction_gwsw(abstraction_gw, return_flow_gw,
                              abstraction_sw, return_flow_sw):
    """
    Calculate sector-specific net abstraction from gw and sw.

    The function is used for the following sectors:
        - Irrigation
        - Domestic
        - Manufacturing
        - Thermal Power
        - Livestock

    Parameters
    ----------
    abstraction_gw : numpy.ndarray
        Sector-specific abstraction of groundwater.
    return_flow_gw : numpy.ndarray
        Sector-specific return flow to groundwater.
    abstraction_sw : numpy.ndarray
        Sector-specific abstraction of surface water.
    return_flow_sw : numpy.ndarray
        Sector-specific return flow to surface water.

    Returns
    -------
    net_abstraction_gw : numpy.ndarray
        Sector-specific net abstraction of groundwater.
    net_abstraction_sw : numpy.ndarray
        Sector-specific net abstraction of surface water.

    """
    # sector-specific net abstraction of groundwater
    net_abstraction_gw = \
        abstraction_gw - return_flow_gw
    # sector-specific net abstraction of surface water
    net_abstraction_sw = \
        abstraction_sw - return_flow_sw

    return net_abstraction_gw, net_abstraction_sw

# =============================================================================
#   model equations only for irrigation sector
# =============================================================================
#                  =================================
#                  || DEFICIT IRRIGATION LOCATION ||
#                  =================================


def set_irr_deficit_locations(gwd_mask,
                              abstraction_irr_part_mask,
                              deficit_irrigation_factor=0.7):
    """
    Create a deficit factor grid based on the deficit irrigation conditions.

    Create a NumPy array with a deficit irrigation factor based on the
    groundwater depletion (gwd_mask) larger than 5mm and the relative part
    of total water withdrawals by the irrigation sector larger than 5%.

    Parameters
    ----------
    gwd_mask : numpy.ndarray
        Grid mask for groundwater depletion larger than 5mm.
    abstraction_irr_part_mask : numpy.ndarray
        Grid mask for the relative part of total water withdrawals by the
        irrigation sector larger than 5%.
    deficit_irrigation_factor : float, optional
        Factor to set for cells that meet criteria for deficit irrigation based
        on gwd_mask and abstraction_irr_part_mask.
        Default is 0.7, based on WaterGAP 2.2d.

    Returns
    -------
    deficit_irrigation_location : numpy.ndarray
        Grid representing deficit irrigation conditions, where cells meeting
        criteria have the specified deficit irrigation factor.

    """
    # Initialize the result grid with NaN values
    deficit_irrigation_location = \
        np.full_like(gwd_mask, np.nan, dtype=float)

    # Set grid cell = deficit_irrigation_factor, if both masks have the value 1
    # and not NaN
    deficit_irrigation_location[
        (gwd_mask == 1) &
        (abstraction_irr_part_mask == 1) &
        ~np.isnan(gwd_mask) &
        ~np.isnan(abstraction_irr_part_mask)
        ] = \
        deficit_irrigation_factor

    # Set grid cell = 1, if one of the masks has a value not equal to 1 and
    # not NaN
    deficit_irrigation_location[((gwd_mask != 1) |
                                 (abstraction_irr_part_mask != 1)) &
                                ~(np.isnan(gwd_mask) |
                                  np.isnan(abstraction_irr_part_mask))
                                ] = 1

    return deficit_irrigation_location


# @njit(cache=True)
def calc_irr_deficit_consumptive_use_tot(irr_consumptive_use_tot,
                                         deficit_irrigation_location,
                                         deficit_irrigation_mode=True):
    """
    Calculate the total consumptive use adjusted for deficit irrigation.

    The function is used for the following sectors:
        - Irrigation

    This function adjusts the total consumptive water use based on the
    specified deficit irrigation locations. If `deficit_flag` is True, it
    applies a modification factor to the consumptive use, otherwise no
    adjustment is made.

    Parameters
    ----------
    irr_consumptive_use_tot : np.ndarray or xr.DataArray
        The total consumptive use in irrigation of water prior to adjustment.
    deficit_irrigation_location : np.ndarray or xr.DataArray
        A factor or array of factors that reduce the consumptive use based on
        deficit irrigation practices.
    deficit_flag : bool
        Flag to determine whether the adjustment should be applied.
        Defaults to True, based on WaterGAP 2.2d.

    Returns
    -------
    irr_deficit_consumptive_use_tot : np.ndarray or xr.DataArray
        The adjusted total consumptive use of water, in the same format as
        `cu_tot`.

    """
    if deficit_irrigation_mode:
        irr_deficit_consmptive_use_tot = \
            irr_consumptive_use_tot * deficit_irrigation_location
        return irr_deficit_consmptive_use_tot

    return irr_consumptive_use_tot  # No adjustment made

#                  =======================================
#                  ||  CORRECTION WITH QUOTIENT_AAI_AEI ||
#                  =======================================


# @njit(cache=True)
def calc_irr_consumptive_use_aai(
        irr_consumptive_use_tot_input,
        fraction_aai_aei,
        irrigation_input_based_on_aei):
    """
    Calc total consumptive use for area, actually irrigated.

    The function is used for the following sectors:
        - Irrigation

    Parameters
    ----------
    irr_consumptive_use_tot : numpy.ndarray
        Total consumptive water use for irrigation, which can be the output
        from `calc_irr_consumptive_use_aai`, representing the initial
        consumptive use values for the area actually irrigated (AAI).
    time_factor_aai : numpy.ndarray
        Represents the development of country-specific AAI (Area Actually
        Irrigated) from 2016 onwards, relative to the reference year 2015. This
        factor is used to adjust the consumptive use values to account for
        changes in irrigation practices or area actually irrigated over time.
    correct_irr_t_aai_mode : bool
        Flag indicating whether the irrigation consumptive use should be
        corrected with the time factor for AAI (True) or not (False).

    Returns
    -------
    irr_consumptive_use_tot_t_aai : numpy.ndarray
        Corrected total consumptive water use for the area actually irrigated
        if `correct_irr_t_aai_mode` is True; otherwise, returns the original
        `irr_consumptive_use_tot`.


    """
    if irrigation_input_based_on_aei:
        irr_consumptive_use_tot_aai = \
            irr_consumptive_use_tot_input * fraction_aai_aei
    else:
        irr_consumptive_use_tot_aai = irr_consumptive_use_tot_input
    return irr_consumptive_use_tot_aai

#                  =================================
#                  ||    CORRECTION WITH T_AAI    ||
#                  =================================


# @njit(cache=True)
def correct_irr_consumptive_use_by_t_aai(irr_consumptive_use_tot,
                                         time_factor_aai,
                                         correct_irr_t_aai_mode):
    """
    Correct irrigation consumptive use tot after 2016 with time factor for aai.

    The function is used for the following sectors:
        - Irrigation

    Parameters
    ----------
    irr_consumptive_use_tot : numpy.ndarray
        DESCRIPTION.
    time_factor_aai : numpy.ndarray
        DESCRIPTION.
    correct_with_t_aai_mode : bool
        DESCRIPTION.

    Returns
    -------
    irr_consumptive_use_tot_t_aai : numpy.ndarray
        DESCRIPTION.

    """
    if correct_irr_t_aai_mode is True:
        irr_consumptive_use_tot_correct_by_t_aai = \
            irr_consumptive_use_tot * time_factor_aai
        return irr_consumptive_use_tot_correct_by_t_aai
    return irr_consumptive_use_tot

#                  =================================
#                  || GWSW IRRIGATION EFFICIENCIES||
#                  =================================


def set_irr_efficiency_gw(efficiency_sw, threshold=0.7, mode="enforce"):
    """
    Set irr.-efficiency for groundwater based on surface water efficiency.

    This function adjusts the irrigation efficiency for groundwater irrigation
    systems based on given surface water efficiency, a threshold, and a
    specified method of adjustment.

    Parameters
    ----------
    efficiency_sw : np.ndarray
        The NumPy array of irrigation efficiency for surface water.
    threshold : float, optional
        The threshold at which groundwater irrigation efficiency will be
        adjusted. Default is 0.7..
    mode : str, optional
        Mode of operation, can be 'enforce' or 'adjust'.
        'enforce': sets efficiency to the threshold everywhere,
        'adjust': adjusts efficiency only where it is below the threshold,
        Default is "enforce".

    Returns
    -------
    efficiency_gw : np.ndarray
        The adjusted groundwater irrigation efficiency array, following the
        rules set by the selected method.

    """
    if mode == "enforce":
        # Set all non-NaN values to the threshold, preserve NaNs
        efficiency_gw = np.where(np.isnan(efficiency_sw),
                                 efficiency_sw,
                                 threshold)
    elif mode == "adjust":
        # Adjust all non-NaN values to at least the threshold or
        # higher if already greater
        efficiency_gw = np.where(np.isnan(efficiency_sw),
                                 efficiency_sw,
                                 np.maximum(efficiency_sw, threshold))

    return efficiency_gw

#                  =================================
#                  ||   IRRIGATION WITHDRAWALS    ||
#                  =================================


@njit(cache=True)
def calc_irr_abstraction_totgwsw(irr_consumptive_use_gw, irr_efficiency_gw,
                                 irr_consumptive_use_sw, irr_efficiency_sw):
    """
    Calculate irrigation-specific abstraction in total and from gw and sw.

    The function is used for the following sectors:
        - Irrigation

    Parameters
    ----------
    irr_consumptive_use_gw : numpy.ndarray
        Irrigation-specific consumptive use from groundwater.
    irr_efficiency_gw : numpy.ndarray or float
        Irrigation efficiency for groundwater.
    irr_consumptive_use_gw : numpy.ndarray
        Irrigation-specific consumptive water use from groundwater.
    irr_efficiency_gw : numpy.ndarray or float
        Irrigation efficiency for groundwater.
    Returns
    -------
    irr_abstraction_gw : numpy.ndarray
        Irrigation-specific abstraction from groundwater.
    irr_abstraction_sw : numpy.ndarray
        Irrigation-specific abstraction from surface water.
    irr_abstraction_tot : numpy.ndarray
        Irrigation-specific abstraction from total water resources.

    """
    irr_abstraction_gw = irr_consumptive_use_gw / irr_efficiency_gw
    irr_abstraction_sw = irr_consumptive_use_sw / irr_efficiency_sw

    irr_abstraction_tot = irr_abstraction_gw + irr_abstraction_sw
    return irr_abstraction_gw, irr_abstraction_sw, irr_abstraction_tot

# =============================================================================
#   model equation only for total sector
# =============================================================================
#            =======================================
#            || CROSS-SECTOR SIMULATION FUNCTIONS ||
#            =======================================


def sum_volume_per_time_variable(irr_monthly,
                                 dom_annual,
                                 man_annual,
                                 tp_annual,
                                 liv_annual):
    """
    Sum the volume per time variable for multiple sectors.

    This function calculates the total volume per time variable for multiple
    sectors by summing the monthly values of irrigation (m³/day), domestic,
    manufacturing, thermal power, and livestock sectors.

    The volume-per-time variables for which the function is intended are:
    - Consumptive use from groundwater (consumptive_use_gw), surface water
      (consumptive_use_sw) or both (consumptive_use_tot).
    - Water abstraction from groundwater (abstraction_gw), surface water
      (abstraction_sw) or both (abstraction_tot).
    - Return flow (rf) to groundwater (return_flow_gw), surface water
      (return_flow_sw) or both (return_flow_tot).
    - Net abstractions from groundwater (net_abstraction_gw) or surface water
      (net_abstraction_sw).

    Parameters
    ----------
    irr_monthly : numpy.ndarray
        Monthly irrigation data array (m³/day).
    dom_annual : numpy.ndarray
        Annual domestic data array (m³/day).
    man_annual : numpy.ndarray
        Annual manufacturing data array (m³/day).
    tp_annual : numpy.ndarray
        Annual thermal power data array (m³/day).
    liv_annual : numpy.ndarray
        Annual livestock data array (m³/day).

    Returns
    -------
    total_sectors_monthly : numpy.ndarray
        Total volume per time variable for all sectors combined, represented as
        a monthly data array (m³/day).

    """
    dom_man_tp_liv_sum_annual = \
        dom_annual + man_annual + tp_annual + liv_annual

    dom_man_tp_liv_sum_monthly = \
        tc.expand_array_size(dom_man_tp_liv_sum_annual)

    total_sectors_monthly = \
        irr_monthly + dom_man_tp_liv_sum_monthly

    return total_sectors_monthly


def calculate_cross_sector_totals(irr_monthly_m3_month,
                                  dom_annual_m3_year,
                                  man_annual_m3_year,
                                  tp_annual_m3_year,
                                  liv_annual_m3_year):
    """
    Sum the volume per time variable for multiple sectors.

    This function calculates the total volume per time variable for multiple
    sectors by summing the monthly values of irrigation (m³/month) and the
    annual values of domestic, manufacturing, thermal power, and livestock
    sectors (m³/year), converting the latter into monthly values.

    The volume-per-time variables for which the function is intended are:
    - Consumptive use from groundwater (consumptive_use_gw), surface water
      (consumptive_use_sw), or both (consumptive_use_tot).
    - Water abstraction from groundwater (abstraction_gw), surface water
      (abstraction_sw), or both (abstraction_tot).
    - Return flow (rf) to groundwater (return_flow_gw), surface water
      (return_flow_sw), or both (return_flow_tot).
    - Net abstractions from groundwater (net_abstraction_gw) or surface water
      (net_abstraction_sw).

    Parameters
    ----------
    irr_monthly_m3_month : numpy.ndarray
        Monthly irrigation data array (m³/month).
    dom_annual_m3_year : numpy.ndarray
        Annual domestic data array (m³/year).
    man_annual_m3_year : numpy.ndarray
        Annual manufacturing data array (m³/year).
    tp_annual_m3_year : numpy.ndarray
        Annual thermal power data array (m³/year).
    liv_annual_m3_year : numpy.ndarray
        Annual livestock data array (m³/year).

    Returns
    -------
    total_sectors_monthly_m3_month : numpy.ndarray
        Total volume per time variable for all sectors combined, represented as
        a monthly data array (m³/month).
    """
    dom_man_tp_liv_sum_annual_m3_year = \
        (dom_annual_m3_year + man_annual_m3_year + tp_annual_m3_year +
         liv_annual_m3_year)

    dom_man_tp_liv_sum_monthly_m3_month = \
        tc.convert_yearly_to_monthly(dom_man_tp_liv_sum_annual_m3_year)

    total_sectors_monthly_m3_month = \
        irr_monthly_m3_month + dom_man_tp_liv_sum_monthly_m3_month

    return total_sectors_monthly_m3_month


def calculate_fractions(consumptive_use_gw, consumptive_use_tot,
                        return_flow_gw, return_flow_tot):
    """
    Calculate the fractions of groundwater use and return flow to groundwater.

    Parameters
    ----------
    consumptive_use_gw : numpy.ndarray
        Consumptive water use from groundwater across all sectors.
    consumptive_use_tot : numpy.ndarray
        Consumptive water use from total water resources across all sectors.
    return_flow_gw : numpy.ndarray or xarray
        Return flow to groundwater across all sectors.
    return_flow_tot : numpy.ndarray
        Total return flow from all sectors.

    Returns
    -------
    fraction_gw_use : numpy.ndarray
        Fraction of groundwater use across all sectors.
    fraction_return_to_gw : numpy.ndarray
        Fraction of total return flow to groundwater across all sectors.
    """
    # Create masks to identify valid denominators (not NaN and not 0)
    valid_consumptive_use_tot = (~np.isnan(consumptive_use_tot)) & \
                                (consumptive_use_tot != 0)
    valid_return_flow_tot = (~np.isnan(return_flow_tot)) & \
                            (return_flow_tot != 0)

    # Initialize result arrays with NaN
    fraction_gw_use = np.full(consumptive_use_tot.shape, np.nan)
    fraction_return_to_gw = np.full(return_flow_tot.shape, np.nan)

    # Perform calculations only for valid elements
    fraction_gw_use[valid_consumptive_use_tot] = \
        consumptive_use_gw[valid_consumptive_use_tot] / \
        consumptive_use_tot[valid_consumptive_use_tot]
    fraction_return_to_gw[valid_return_flow_tot] = \
        return_flow_gw[valid_return_flow_tot] / \
        return_flow_tot[valid_return_flow_tot]

    return fraction_gw_use, fraction_return_to_gw
