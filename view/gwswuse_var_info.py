# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================
"""Variable Information."""

# This module contains dictionary with regwswuse variable definitions.

modelvars = {
    'consumptive_use_tot': {
        'total': {
            'standard_name': 'total_consumptive_use_tot',
            'isimip_name': 'ptotuse',
            'long_name': 'Monthly potential total consumptive water use',
            'unit': 'm3/month'
            },
        'irrigation': {
            'standard_name': 'irr_consumptive_use_tot',
            'isimip_name': 'pirruse',
            'long_name': 'Monthly potential irrigation consumptive water use',
            'unit': 'm3/month'
            },
        'domestic': {
            'standard_name': 'dom_consumptive_use_tot',
            'isimip_name': 'pdomuse',
            'long_name': 'Yearly potential domestic consumptive water use',
            'unit': 'm3/year'
            },
        'manufacturing': {
            'standard_name': 'man_consumptive_use_tot',
            'isimip_name': 'pmanuse',
            'long_name': (
                'Yearly potential manufacturing consumptive water use'),
            'unit': 'm3/year'
            },
        'thermal_power': {
            'standard_name': 'tp_consumptive_use_tot',
            'isimip_name': 'pelecuse',
            'long_name': (
                'Yearly potential thermal power consumptive water use'),
            'unit': 'm3/year'
            },
        'livestock': {
            'standard_name': 'liv_consumptive_use_tot',
            'isimip_name': 'plivuse',
            'long_name': 'Yearly potential livestock consumptive water use',
            'unit': 'm3/year'
            }
        },
    'consumptive_use_gw': {
        'total': {
            'standard_name': 'total_consumptive_use_gw',
            'isimip_name': 'ptotusegw',
            'long_name': 'Monthly potential total consumptive groundwater use',
            'unit': 'm3/month'
            },
        'irrigation': {
            'standard_name': 'irr_consumptive_use_gw',
            'isimip_name': 'pirrusegw',
            'long_name': (
                'Monthly potential irrigation consumptive groundwater use'),
            'unit': 'm3/month'
            },
        'domestic': {
            'standard_name': 'dom_consumptive_use_gw',
            'isimip_name': 'pdomusegw',
            'long_name': (
                'Yearly potential domestic consumptive groundwater use'),
            'unit': 'm3/year'
            },
        'manufacturing': {
            'standard_name': 'man_consumptive_use_gw',
            'isimip_name': 'pmanusegw',
            'long_name': (
                'Yearly potential manufacturing consumptive groundwater use'),
            'unit': 'm3/year'
            },
        'thermal_power': {
            'standard_name': 'tp_consumptive_use_gw',
            'isimip_name': 'pelecusegw',
            'long_name': (
                'Yearly potential thermal power consumptive groundwater use'),
            'unit': 'm3/year'
            },
        'livestock': {
            'standard_name': 'liv_consumptive_use_gw',
            'isimip_name': 'plivusegw',
            'long_name': (
                'Yearly potential livestock consumptive groundwater use'),
            'unit': 'm3/year'
            }
        },
    'consumptive_use_sw': {
        'total': {
            'standard_name': 'total_consumptive_use_sw',
            'isimip_name': 'ptotusesw',
            'long_name': (
                'Monthly potential total consumptive surface water use'),
            'unit': 'm3/month'
            },
        'irrigation': {
            'standard_name': 'irr_consumptive_use_sw',
            'isimip_name': 'pirrusesw',
            'long_name': (
                'Monthly potential irrigation consumptive surface water use'),
            'unit': 'm3/month'
            },
        'domestic': {
            'standard_name': 'dom_consumptive_use_sw',
            'isimip_name': 'pdomusesw',
            'long_name': (
                'Yearly potential domestic consumptive surface water use'),
            'unit': 'm3/year'
            },
        'manufacturing': {
            'standard_name': 'man_consumptive_use_sw',
            'isimip_name': 'pmanusesw',
            'long_name': (
                'Yearly potential manufacturing consumptive surface water use'
                ),
            'unit': 'm3/year'
            },
        'thermal_power': {
            'standard_name': 'tp_consumptive_use_sw',
            'isimip_name': 'pelecusesw',
            'long_name': (
                'Yearly potential thermal power consumptive surface water use'
                ),
            'unit': 'm3/year'
            },
        'livestock': {
            'standard_name': 'liv_consumptive_use_sw',
            'isimip_name': 'plivusesw',
            'long_name': (
                'Yearly potential livestock consumptive surface water use'),
            'unit': 'm3/year'
            }
        },
    'abstraction_tot': {
        'total': {
            'standard_name': 'total_abstraction_tot',
            'isimip_name': 'ptotww',
            'long_name': 'Monthly potential total water abstraction',
            'unit': 'm3/month'
            },
        'irrigation': {
            'standard_name': 'irr_abstraction_tot',
            'isimip_name': 'pirrww',
            'long_name': 'Monthly potential irrigation water abstraction',
            'unit': 'm3/month'
            },
        'domestic': {
            'standard_name': 'dom_abstraction_tot',
            'isimip_name': 'pdomww',
            'long_name': 'Yearly potential domestic water abstraction',
            'unit': 'm3/year'
            },
        'manufacturing': {
            'standard_name': 'man_abstraction_tot',
            'isimip_name': 'pmanww',
            'long_name': 'Yearly potential manufacturing water abstraction',
            'unit': 'm3/year'
            },
        'thermal_power': {
            'standard_name': 'tp_abstraction_tot',
            'isimip_name': 'pelecww',
            'long_name': 'Yearly potential thermal power water abstraction',
            'unit': 'm3/year'
            },
        'livestock': {
            'standard_name': 'liv_abstraction_tot',
            'isimip_name': 'plivww',
            'long_name': 'Yearly potential livestock water abstraction',
            'unit': 'm3/year'
            }
        },
    'abstraction_gw': {
        'total': {
            'standard_name': 'total_abstraction_gw',
            'isimip_name': 'ptotwwgw',
            'long_name': 'Monthly potential total groundwater abstraction',
            'unit': 'm3/month'
            },
        'irrigation': {
            'standard_name': 'irr_abstraction_gw',
            'isimip_name': 'pirrwwgw',
            'long_name': (
                'Monthly potential irrigation groundwater abstraction'),
            'unit': 'm3/month'
            },
        'domestic': {
            'standard_name': 'dom_abstraction_gw',
            'isimip_name': 'pdomwwgw',
            'long_name': 'Yearly potential domestic groundwater abstraction',
            'unit': 'm3/year'
            },
        'manufacturing': {
            'standard_name': 'man_abstraction_gw',
            'isimip_name': 'pmanwwgw',
            'long_name': (
                'Yearly potential manufacturing groundwater abstraction'),
            'unit': 'm3/year'
            },
        'thermal_power': {
            'standard_name': 'tp_abstraction_gw',
            'isimip_name': 'pelecwwgw',
            'long_name': (
                'Yearly potential thermal power groundwater abstraction'),
            'unit': 'm3/year'
            },
        'livestock': {
            'standard_name': 'liv_abstraction_gw',
            'isimip_name': 'plivwwgw',
            'long_name': 'Yearly potential livestock groundwater abstraction',
            'unit': 'm3/year'
            }
        },
    'abstraction_sw': {
        'total': {
            'standard_name': 'total_abstraction_sw',
            'isimip_name': 'ptotwwsw',
            'long_name': 'Monthly potential total surface water abstraction',
            'unit': 'm3/month'
            },
        'irrigation': {
            'standard_name': 'irr_abstraction_sw',
            'isimip_name': 'pirrwwsw',
            'long_name': (
                'Monthly potential irrigation surface water abstraction'),
            'unit': 'm3/month'
            },
        'domestic': {
            'standard_name': 'dom_abstraction_sw',
            'isimip_name': 'pdomwwsw',
            'long_name': 'Yearly potential domestic surface water abstraction',
            'unit': 'm3/year'
            },
        'manufacturing': {
            'standard_name': 'man_abstraction_sw',
            'isimip_name': 'pmanwwsw',
            'long_name': (
                'Yearly potential manufacturing surface water abstraction'),
            'unit': 'm3/year'
            },
        'thermal_power': {
            'standard_name': 'tp_abstraction_sw',
            'isimip_name': 'pelecwwsw',
            'long_name': (
                'Yearly potential thermal power surface water abstraction'),
            'unit': 'm3/year'
            },
        'livestock': {
            'standard_name': 'liv_abstraction_sw',
            'isimip_name': 'plivwwsw',
            'long_name': (
                'Yearly potential livestock surface water abstraction'),
            'unit': 'm3/year'
            }
        },
    'return_flow_tot': {
        'total': {
            'standard_name': 'total_return_flow_tot',
            'isimip_name': 'ptotrf',
            'long_name': 'Monthly potential total return flow',
            'unit': 'm3/month'
            },
        'irrigation': {
            'standard_name': 'irr_return_flow_tot',
            'isimip_name': 'pirrrf',
            'long_name': 'Monthly potential irrigation return flow',
            'unit': 'm3/month'
            },
        'domestic': {
            'standard_name': 'dom_return_flow_tot',
            'isimip_name': 'pdomrf',
            'long_name': 'Yearly potential domestic return flow',
            'unit': 'm3/year'
            },
        'manufacturing': {
            'standard_name': 'man_return_flow_tot',
            'isimip_name': 'pmanrf',
            'long_name': 'Yearly potential manufacturing return flow',
            'unit': 'm3/year'
            },
        'thermal_power': {
            'standard_name': 'tp_return_flow_tot',
            'isimip_name': 'pelecrf',
            'long_name': 'Yearly potential thermal power return flow',
            'unit': 'm3/year'
            },
        'livestock': {
            'standard_name': 'liv_return_flow_tot',
            'isimip_name': 'plivrf',
            'long_name': 'Yearly potential livestock return flow',
            'unit': 'm3/year'
            }
        },
    'return_flow_gw': {
        'total': {
            'standard_name': 'total_return_flow_gw',
            'isimip_name': 'ptotrfgw',
            'long_name': 'Monthly potential total return flow to groundwater',
            'unit': 'm3/month'
            },
        'irrigation': {
            'standard_name': 'irr_return_flow_gw',
            'isimip_name': 'pirrrfgw',
            'long_name': (
                'Monthly potential irrigation return flow to groundwater'),
            'unit': 'm3/month'
            },
        'domestic': {
            'standard_name': 'dom_return_flow_gw',
            'isimip_name': 'pdomrfgw',
            'long_name': (
                'Yearly potential domestic return flow to groundwater'),
            'unit': 'm3/year'
            },
        'manufacturing': {
            'standard_name': 'man_return_flow_gw',
            'isimip_name': 'pmanrfgw',
            'long_name': (
                'Yearly potential manufacturing return flow to groundwater'),
            'unit': 'm3/year'
            },
        'thermal_power': {
            'standard_name': 'tp_return_flow_gw',
            'isimip_name': 'pelecrfgw',
            'long_name': (
                'Yearly potential thermal power return flow to groundwater'),
            'unit': 'm3/year'
            },
        'livestock': {
            'standard_name': 'liv_return_flow_gw',
            'isimip_name': 'plivrfgw',
            'long_name': (
                'Yearly potential livestock return flow to groundwater'),
            'unit': 'm3/year'
            }
        },
    'return_flow_sw': {
        'total': {
            'standard_name': 'total_return_flow_sw',
            'isimip_name': 'ptotrfsw',
            'long_name': (
                'Monthly potential total return flow to surface water'),
            'unit': 'm3/month'
            },
        'irrigation': {
            'standard_name': 'irr_return_flow_sw',
            'isimip_name': 'pirrrfsw',
            'long_name': (
                'Monthly potential irrigation return flow to surface water'),
            'unit': 'm3/month'
            },
        'domestic': {
            'standard_name': 'dom_return_flow_sw',
            'isimip_name': 'pdomrfsw',
            'long_name': (
                'Yearly potential domestic return flow to surface water'),
            'unit': 'm3/year'
            },
        'manufacturing': {
            'standard_name': 'man_return_flow_sw',
            'isimip_name': 'pmanrfsw',
            'long_name': (
                'Yearly potential manufacturing return flow to surface water'),
            'unit': 'm3/year'
            },
        'thermal_power': {
            'standard_name': 'tp_return_flow_sw',
            'isimip_name': 'pelecrfsw',
            'long_name': (
                'Yearly potential thermal power return flow to surface water'),
            'unit': 'm3/year'
            },
        'livestock': {
            'standard_name': 'liv_return_flow_sw',
            'isimip_name': 'plivrfsw',
            'long_name': (
                'Yearly potential livestock return flow to surface water'),
            'unit': 'm3/year'
            }
        },
    'net_abstraction_gw': {
        'total': {
            'standard_name': 'total_net_abstraction_gw',
            'isimip_name': 'ptotnag',
            'long_name': 'Monthly potential total groundwater net abstraction',
            'unit': 'm3/month'
            },
        'irrigation': {
            'standard_name': 'irr_net_abstraction_gw',
            'isimip_name': 'pirrnag',
            'long_name': (
                'Monthly potential irrigation groundwater net abstraction'),
            'unit': 'm3/month'
            },
        'domestic': {
            'standard_name': 'dom_net_abstraction_gw',
            'isimip_name': 'pdomnag',
            'long_name': (
                'Yearly potential domestic groundwater net abstraction'),
            'unit': 'm3/year'
            },
        'manufacturing': {
            'standard_name': 'man_net_abstraction_gw',
            'isimip_name': 'pmannag',
            'long_name': (
                'Yearly potential manufacturing groundwater net abstraction'),
            'unit': 'm3/year'
            },
        'thermal_power': {
            'standard_name': 'tp_net_abstraction_gw',
            'isimip_name': 'pelecnag',
            'long_name': (
                'Yearly potential thermal power groundwater net abstraction'),
            'unit': 'm3/year'
            },
        'livestock': {
            'standard_name': 'liv_net_abstraction_gw',
            'isimip_name': 'plivnag',
            'long_name': (
                'Yearly potential livestock groundwater net abstraction'),
            'unit': 'm3/year'
            }
        },
    'net_abstraction_sw': {
        'total': {
            'standard_name': 'total_net_abstraction_sw',
            'isimip_name': 'ptotnas',
            'long_name': (
                'Monthly potential total surface water net abstraction'),
            'unit': 'm3/month'
            },
        'irrigation': {
            'standard_name': 'irr_net_abstraction_sw',
            'isimip_name': 'pirrnas',
            'long_name': (
                'Monthly potential irrigation surface water net abstraction'),
            'unit': 'm3/month'
            },
        'domestic': {
            'standard_name': 'dom_net_abstraction_sw',
            'isimip_name': 'pdomnas',
            'long_name': (
                'Yearly potential domestic surface water net abstraction'),
            'unit': 'm3/year'
            },
        'manufacturing': {
            'standard_name': 'man_net_abstraction_sw',
            'isimip_name': 'pmannas',
            'long_name': (
                'Yearly potential manufacturing surface water net abstraction'
                ),
            'unit': 'm3/year'
            },
        'thermal_power': {
            'standard_name': 'tp_net_abstraction_sw',
            'isimip_name': 'pelecnas',
            'long_name': (
                'Yearly potential thermal power surface water net abstraction'
                ),
            'unit': 'm3/year'
            },
        'livestock': {
            'standard_name': 'liv_net_abstraction_sw',
            'isimip_name': 'plivnas',
            'long_name': (
                'Yearly potential livestock surface water net abstraction'),
            'unit': 'm3/year'
            }
        },
    'fraction_gw_use': {
        'total': {
            'standard_name': 'total_fraction_gw_use',
            'long_name': 'Potential total fraction of groundwater use',
            'unit': '-'
            },
        'irrigation': {
            'standard_name': 'irr_fraction_gw_use',
            'long_name': 'Potential irrigation fraction of groundwater use',
            'unit': '-'
            },
        'domestic': {
            'standard_name': 'dom_fraction_gw_use',
            'long_name': 'Potential domestic fraction of groundwater use',
            'unit': '-'
            },
        'manufacturing': {
            'standard_name': 'man_fraction_gw_use',
            'long_name': 'Potential manufacturing fraction of groundwater use',
            'unit': '-'
            },
        'thermal_power': {
            'standard_name': 'tp_fraction_gw_use',
            'long_name': 'Potential thermal power fraction of groundwater use',
            'unit': '-'
            },
        'livestock': {
            'standard_name': 'liv_fraction_gw_use',
            'long_name': 'Potential livestock fraction of groundwater use',
            'unit': '-'
            }
        },
    'fraction_return_gw': {
        'total': {
            'standard_name': 'total_fraction_return_gw',
            'long_name': (
                'Potential total fraction of return flow to groundwater'),
            'unit': '-'
            },
        'irrigation': {
            'standard_name': 'irr_fraction_return_gw',
            'long_name': (
                'Potential irrigation fraction of return flow to groundwater'),
            'unit': '-'
            },
        'domestic': {
            'standard_name': 'dom_fraction_return_gw',
            'long_name': (
                'Potential domestic fraction of return flow to groundwater'),
            'unit': '-'
            },
        'manufacturing': {
            'standard_name': 'man_fraction_return_gw',
            'long_name': (
                'Potential manufacturing fraction of return flow to '
                'groundwater'),
            'unit': '-'
            },
        'thermal_power': {
            'standard_name': 'tp_fraction_return_gw',
            'long_name': (
                'Potential thermal power fraction of return flow to '
                'groundwater'),
            'unit': '-'
            },
        'livestock': {
            'standard_name': 'liv_fraction_return_gw',
            'long_name': (
                'Potential livestock fraction of return flow to groundwater'),
            'unit': '-'
            }
        },
    'irrigation_efficiency_gw': {
        'standard_name': 'irr_efficiency_gw',
        'long_name': (
            'Irrigation efficiency for groundwater abstraction '
            'infrastructure'),
        'unit': '-'
        },
    'irrigation_efficiency_sw': {
        'standard_name': 'irr_efficiency_sw',
        'long_name': (
            'Irrigation efficiency for surface water abstraction '
            'infrastructure'),
        'unit': '-'
        },
    'gwd_mask': {
        'standard_name': 'gwd5mm_mask',
        'long_name': (
            'Mask for groundwater depletion isolated through human water use '
            'is larger than 5 mm/yr in average for time period 1980 - 2009'
            ),
        'description': (
            'Mask: If grid cell = 1, then groundwater depletion isolated '
            'through human water use is larger than 5mm/yr. Mask based on Fig '
            '3a from Döll et al. (2014).'),
        'unit': 'boolean'
        },
    'abstraction_irr_part_mask': {
        'standard_name': 'irrwwpart5pct_mask',
        'long_name': ('Mask for irrigation part of water abstraction is larger'
                      ' than 5 % during the time period 1960 - 2000'),
        'description': (
            'Mask: If grid cell = 1, then ratio of water abstraction for '
            'irrigation over water abstraction for all sectors is larger than '
            '5 % during the time period 1960 - 2000.'
            'Mask based on Döll et al. (2014).'
            ),
        'unit': 'boolean'
        },
    'deficit_irrigation_location': {
        'standard_name': 'deficit_irrigation_location',
        'long_name': 'Factor for deficit irrigation location',
        'description': (
            'Potential irrigation consumptive use will decreased with deficit '
            'irrigation factor based on conditions mask for groundwater '
            'depletion and irrigation part of total water abstraction.'
            ),
        'unit': '-'
        },
    'fraction_aai_aei': {
        'standard name': 'fraction_aai_aei',
        'long_name': (
            'Fraction of areas actually irrigated to areas eqipped for '
            'irrgation'),
        'unit': '-'
        },
    'time_factor_aai': {
        'standard_name': 'time_factor_aai',
        'long_name': (
            'Temporal development factor of national areas actually irrigated '
            'for years 2016 till 2020 to reference year 2015.'
            ),
        'unit': '-'
        }
    }


def print_modelvars(model_vars):
    """Print dictionairy of gwswuse variables."""
    for var_name, var_data in model_vars.items():
        print(f"Variable: {var_name}")
        if isinstance(var_data, dict):
            # Check if sub-items are dictionaries or direct attributes
            for sub_key, sub_value in var_data.items():
                if isinstance(sub_value, dict):
                    print(f"  Sector: {sub_key}")
                    for attr_key, attr_value in sub_value.items():
                        print(f"    {attr_key}: {attr_value}")
                else:
                    # Handle case where there are no sectors
                    print(f"  {sub_key}: {sub_value}")
        else:
            print(f"  Value: {var_data}")
        print()  # Newline for better separation between variables


if __name__ == "__main__":
    print_modelvars(modelvars)
