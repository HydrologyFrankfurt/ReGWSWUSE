# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================
"""Variable Information."""

# This model returns dictionary with variable definitions.


modelvars = {
    'consumptive_use_tot': {
        'standard_name': 'p{sector_isimip}use',
        'long_name': 'Potential {sector_name} Consumptive Use',
        'wghm_code_name': 'potential_consumptive_use_tot{_sector}',
        'gwswuse_code_name': '{sector_watergap}.consumptive_use_tot',
        'description': (
            '{timestep} potential {sector_name_low} consumptive use of '
            'groundwater and surface water'
        )
    },
    'consumptive_use_gw': {
        'standard_name': 'p{sector_isimip}usegw',
        'long_name': (
            'Potential {sector_name} Consumptive Use From Groundwater'
            ),
        'wghm_code_name': 'potential_consumptive_use_gw{_sector}',
        'gwswuse_code_name': '{sector_watergap}.consumptive_use_gw',
        'description': (
            '{timestep} potential {sector_name_low} consumptive use of '
            'groundwater'
        )
    },
    'consumptive_use_sw': {
        'standard_name': 'p{sector_isimip}usesw',
        'long_name': (
            'Potential {sector_name} Consumptive Use From Surface Water'
            ),
        'wghm_code_name': 'potential_consumptive_use_sw{_sector}',
        'gwswuse_code_name': '{sector_watergap}.consumptive_use_sw',
        'description': (
            '{timestep} potential {sector_name_low} consumptive use of '
            'surface water'
        )
    },
    'abstraction_tot': {
        'standard_name': 'p{sector_isimip}ww',
        'long_name': 'Potential {sector_name} water abstraction',
        'wghm_code_name': 'potential_abstraction_tot{_sector}',
        'gwswuse_code_name': '{sector_watergap}.abstraction_tot',
        'description': (
            '{timestep} potential {sector_name_low} water abstractions from '
            'groundwater and surface water'
        )
    },
    'abstraction_gw': {
        'standard_name': 'p{sector_isimip}wwgw',
        'long_name': (
            'Potential {sector_name} Water Abstractions From Groundwater'
            ),
        'wghm_code_name': 'potential_withdrawals_tot{_sector}',
        'gwswuse_code_name': '{sector_watergap}.abstraction_gw',
        'description': (
            '{timestep} potential {sector_name_low} water abstractions from '
            'groundwater'
        )
    },
    'abstraction_sw': {
        'standard_name': 'p{sector_isimip}wwsw',
        'long_name': (
            'Potential {sector_name} Water Abstractions From Surface Water'
            ),
        'wghm_code_name': 'potential_abstraction_sw{_sector}',
        'gwswuse_code_name': '{sector_watergap}.abstraction_sw',
        'description': (
            '{timestep} potential {sector_name_low} water abstractions from '
            'surface water'
        )
    },
    'return_flow_tot': {
        'standard_name': 'p{sector_isimip}rf',
        'long_name': (
            'Potential Return Flow Of {sector_name} Water Abstraction'
            ),
        'wghm_code_name': 'potential_return_flow_tot{_sector}',
        'gwswuse_code_name': '{sector_watergap}.return_flow_tot',
        'description': (
            '{timestep} potential return flow of water abstraction in the '
            '{sector_name_low} sector.'
        )
    },
    'return_flow_gw': {
        'standard_name': 'p{sector_isimip}rfgw',
        'long_name': (
            'Potential Return Flow Of {sector_name} Water Abstraction into '
            'Groundwater'
            ),
        'wghm_code_name': 'potential_return_flow_gw{_sector}',
        'gwswuse_code_name': '{sector_watergap}.return_flow_gw',
        'description': (
            '{timestep} potential return flow to groundwater bodies in the '
            'event of water abstraction in the {sector_name_low} sectors.'
        )
    },
    'return_flow_sw': {
        'standard_name': 'p{sector_isimip}rfsw',
        'long_name': ('Potential Return Flow Of {sector_name} Water '
                      'Abstraction Into Surface Water'),
        'wghm_code_name': 'potential_return_flow_sw{_sector}',
        'gwswuse_code_name': '{sector_watergap}.return_flow_sw',
        'description': (
            '{timestep} potential return flow to surface water bodies in the '
            'event of water abstraction in the {sector_name_low} sectors.'
        )
    },
    'net_abstraction_gw': {
        'standard_name': 'p{sector_isimip}nag',
        'long_name': (
            'Potential net abstractions from groundwater in {sector_name}'
        ),
        'wghm_code_name': 'potential_net_abstraction{_sector}_gw',
        'gwswuse_code_name': '{sector_watergap}.net_abstraction_gw',
        'description': (
            '{timestep} simulated potential net abstractions from groundwater '
            'in {sector_name_low} sector.'
        )
    },
    'net_abstraction_sw': {
        'standard_name': 'p{sector_isimip}nas',
        'long_name': (
            'Potential net abstractions from surface water in {sector_name}'
        ),
        'wghm_code_name': 'potential_net_abstraction{_sector}_sw',
        'gwswuse_code_name': '{sector_watergap}.net_abstraction_sw',
        'description': (
            '{timestep} simulated potential net abstractions from surface '
            'water in {sector_name_low} sector.'
        )
    },
    'irr.fraction_gw_use': {
        'standard_name': 'pirrfractgwuse',
        'long_name': 'Potential Fraction of Groundwater Use in Irrigation',
        'gwswuse_code_name': 'irr.fraction_gw_use',
        'description': (
            'Time-constant groundwater use fractions in irrigation sector. '
            'Based on two sources: (1) "SS10" (zipped archive 2010-04-12, '
            'shapefiles from 2010-03-11), gridded; (2) Russia subnational '
            'basins, gridded.'
        )
    },
    'dom.fraction_gw_use': {
        'standard_name': 'pdomfractgwuse',
        'long_name': 'Potential Fraction of Groundwater Use in Domestic',
        'gwswuse_code_name': 'dom.fraction_gw_use',
        'description': (
            'Time-constant potential groundwater use fractions in '
            'domestic sector. '
            'Based on national and 10 subnational sources. Countries with '
            'subnational sources are Australia, Canada, China (incl. Taiwan & '
            'Province of China; Hong Kong & Macao not represented), Germany, '
            'India, Mexico, New Zealand, Russian Federation, Ukraine, United '
            'States.'
        )
    },
    'man.fraction_gw_use': {
        'standard_name': 'pmanfractgwuse',
        'long_name': 'Potential Fraction of Groundwater Use in Manufacturing',
        'wghm_code_name': 'potential_fraction_gw_use_man',
        'gwswuse_code_name': 'man.fraction_gw_use',
        'description': (
            'Time-constant potential groundwater use fractions in '
            'manufacturing sector. '
            'Based on national and 10 subnational sources. Countries with '
            'subnational sources are Australia, Canada, China (incl. Taiwan & '
            'Province of China; Hong Kong & Macao not represented), Germany, '
            'India, Mexico, New Zealand, Russian Federation, Ukraine, United '
            'States.'
        )
    },
    'fraction_return_gw': {
        'standard_name': 'p{sector_isimip}fractreturngw',
        'long_name': (
            'Fraction of return flow to groundwater of {sector_name} water '
            'use.'
            ),
        'gwswuse_code_name': '{sector_watergap}.fraction_return_gw',
        'description': (
            'Time-constant potential fraction of total return flow to '
            'groundwater of water use in {sector} sector.'
        )
    },
    'irr.fraction_return_gw': {
        'standard_name': 'p{sector_isimip}fractreturngw',
        'long_name': 'Potential {sector_name} Consumptive Use',
        'gwswuse_code_name': '{sector_watergap}.fraction_return_gw',
        'description': (
            'Time-constant potential fraction of total return flow to '
            'groundwater of water use in {sector} sector.  Derived using GMIA '
            'and adjustes Global Map of Irrigation Areas .'
        )
    },
    'gwd_mask': {
        'standard_name': 'gwd5mm_mask',
        'long_name': (
            'Mask for groundwater depletion isolated through human water use '
            'is larger than 5 mm/yr in average for time period 1980 - 2009'
            ),
        'gwswuse_code_name': 'irr.gwd_mask',
        'description': (
            'Mask: If grid cell = 1, then groundwater depletion isolated '
            'through human water use is larger than 5mm/yr. Mask based on Fig '
            '3a from Döll et al. (2014).'
        )
    },
    'abstraction_irr_part_mask': {
        'standard_name': 'irrwwpart5pct_mask',
        'long_name': ('Mask for ratio of water abstraction for irrigation '
                      'over water abstraction for all sectors is larger than '
                      '5 % during the time period 1960 - 2000'),
        'gwswuse_code_name': 'irr.abstraction_irr_part_mask',
        'description': (
            'Mask: If grid cell = 1, then ratio of water abstraction for '
            'irrigation over water abstraction for all sectors is larger than '
            '5 % during the time period 1960 - 2000.'
            'Mask based on Döll et al. (2014).'
        )
    },
    'deficit_irrigation_location': {
        'standard_name': 'deficit_irrigation_location',
        'long_name': 'Potential {sector_name} Consumptive Use',
        'gwswuse_code_name': '{sector_watergap}.consumptive_use_tot',
        'description': (
            '{timestep} potential {sector_name_low} consumptive use of '
            'groundwater and surface water'
        )
    },
    'irrigation_efficiency_gw': {
        'standard_name': 'irrefficiencygw',
        'long_name': 'Irrigation efficiency with groundwater infrastructure',
        'gwswuse_code_name': 'irr.efficiency_gw',
        'description': (
            'Time-constant irrigation efficiency with groundwater abstraction '
            'infrastructure used in this gwswuse simulation run.'
        )
    },
    'irrigation_efficiency_sw': {
        'standard_name': 'irrefficiencysw',
        'long_name': 'Irrigation efficiency with surface water infrastructure',
        'gwswuse_code_name': 'irr.efficiency_sw',
        'description': (
            'Time-constant irrigation efficiency with surface water '
            'abstraction infrastructure, synthesised PIK and Kulkarni '
            '(2010-05-12 from 2010-05-11 DOS-file)'
        )
    }
}
sector_metadata_dict = {
    'irrigation': {
        'sector_isimip': 'irr',
        'sector_watergap': 'irr',
        'sector_name': 'Irrigation',
        '_sector': '_irr',
        'timestep': 'Monthly'
        },
    'domestic': {
        'sector_isimip': 'dom',
        'sector_watergap': 'dom',
        'sector_name': 'Domestic',
        '_sector': '_dom',
        'timestep': 'Annual'
        },
    'manufacturing': {
        'sector_isimip': 'man',
        'sector_watergap': 'man',
        'sector_name': 'Manufacturing',
        '_sector': '_man',
        'timestep': 'Monthly'
        },
    'thermal_power': {
        'sector_isimip': 'elec',
        'sector_watergap': 'tp',
        'sector_name': 'Thermal Power',
        '_sector': '_tp',
        'timestep': 'Annual'
        },
    'livestock': {
        'sector_isimip': 'live',
        'sector_watergap': 'liv',
        'sector_name': 'Livestock',
        '_sector': '_liv',
        'timestep': 'Annual'
        },
    'total': {
        'sector_isimip': 'tot',
        'sector_watergap': 'tot',
        'sector_name': 'Total',
        '_sector': '',
        'timestep': 'Monthly'
        },
    }
