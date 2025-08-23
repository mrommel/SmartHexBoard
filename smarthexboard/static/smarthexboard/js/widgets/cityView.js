import {Yields} from "../game/types.js";

class CityViewState {
    static none = new CityViewState('None');

    static citizen = new CityViewState('Citizen');
    static breakdown = new CityViewState('Breakdown');
    static loyalty = new CityViewState('Loyalty');

    constructor(name) {
        this.name = name;
    }

    toString() {
        return `CityViewState.${this.name}`;
    }
}

class CityView {
    constructor() {
        this.cityDetailsTab = CityViewState.none;

        // const $cityInfoPanel = $('#city_info_panel');

        const $cityInfoHeader = $('#city_info_header');

        const $cityDetailsName = $("<div>")
            .attr('id', 'city_details_name')
            .text('City Details');
        $cityInfoHeader.append($cityDetailsName);

        const $cityInfoExitButton = $("<div>")
            .attr('id', 'city_info_panel_exit')
            .click(() => {
                console.log('Close Info Panel');
                this.hide();
            });
        $cityInfoHeader.append($cityInfoExitButton);

        const $cityName = $("<div>")
            .attr('id', 'city_name')
            .text('##Name##');
        $cityInfoHeader.append($cityName);

        const $cityCitizenImg = $("<div>")
            .addClass('city_citizen_selected')
            .attr('id', 'city_citizen_btn')
            .click(() => {
                console.log('Clicked city citizen');
                this._showDetailsTab(CityViewState.citizen);
            });
        $cityInfoHeader.append($cityCitizenImg);

        const $cityBreakdownImg = $("<div>")
            .addClass('city_breakdown_active')
            .attr('id', 'city_breakdown_btn')
            .click(() => {
                console.log('Clicked city breakdown');
                this._showDetailsTab(CityViewState.breakdown);
            });
        $cityInfoHeader.append($cityBreakdownImg);

        const $cityLoyaltyImg = $("<div>")
            .addClass('city_loyalty_active')
            .attr('id', 'city_loyalty_btn')
            .click(() => {
                console.log('Clicked city loyalty');
                this._showDetailsTab(CityViewState.loyalty);
            });
        $cityInfoHeader.append($cityLoyaltyImg);

        this._showDetailsTab(CityViewState.citizen);
    }

    _showDetailsTab(viewState) {
        const $cityCitizenBtn = $('#city_citizen_btn');
        const $cityBreakdownBtn = $('#city_breakdown_btn');
        const $cityLoyaltyBtn = $('#city_loyalty_btn');

        // remove all classes
        $cityCitizenBtn.removeClass();
        $cityBreakdownBtn.removeClass();
        $cityLoyaltyBtn.removeClass();

        switch (viewState) {
            case CityViewState.citizen:
                $cityCitizenBtn.addClass('city_citizen_selected');
                $cityBreakdownBtn.addClass('city_breakdown_active');
                $cityLoyaltyBtn.addClass('city_loyalty_active');
                if (this.cityDetailsTab !== viewState) {
                    this._showCitizenContent();
                }
                this.cityDetailsTab = viewState;
                break;
            case CityViewState.breakdown:
                $cityCitizenBtn.addClass('city_citizen_active');
                $cityBreakdownBtn.addClass('city_breakdown_selected');
                $cityLoyaltyBtn.addClass('city_loyalty_active');
                if (this.cityDetailsTab !== viewState) {
                    this._showBreakdownContent();
                }
                this.cityDetailsTab = viewState;
                break;
            case CityViewState.loyalty:
                $cityCitizenBtn.addClass('city_citizen_active');
                $cityBreakdownBtn.addClass('city_breakdown_active');
                $cityLoyaltyBtn.addClass('city_loyalty_selected');
                if (this.cityDetailsTab !== viewState) {
                    this._showLoyaltyContent();
                }
                this.cityDetailsTab = viewState;
                break;
        }
    }

    _showCitizenContent() {
        const $cityInfoContent = $('#city_info_content');
        $cityInfoContent.empty(); // reset

        const citizenGrowthHeader = $("<div></div>")
            .attr('id', 'citizenGrowthHeader')
            .cityViewSubHeader({title: 'Citizen Growth'});
        $cityInfoContent.append(citizenGrowthHeader);

        const citizenBox = $("<div></div>")
            .attr('id', 'citizenBox')
            .cityViewCitizenBox({
                title: 'Citizens',
                text: '17 turns until a new citizen is born',
                icon: '/static/smarthexboard/img/ui/city/citizen_icon_increase.png'
            });
        $cityInfoContent.append(citizenBox);

        // --- foodContainer -----

        const $foodContainer = $("<div></div>")
            .addClass('infoContainer');
        $cityInfoContent.append($foodContainer);

        const $foodPerTurnRow = $("<div></div>")
            .attr('id', 'foodPerTurnRow')
            .keyValueRow({key: 'Food per turn', value: '-5'});
        $foodContainer.append($foodPerTurnRow);

        const $foodConsumptionRow = $("<div></div>")
            .attr('id', 'foodConsumptionRow')
            .keyValueRow({key: 'Food consumption', value: '12%'});
        $foodContainer.append($foodConsumptionRow);

        const $line1 = $("<div></div>")
            .addClass('city_info_line');
        $foodContainer.append($line1);

        // --- growthContainer -----

        const $growthContainer = $("<div></div>")
            .addClass('infoContainer');
        $cityInfoContent.append($growthContainer);

        const $growthFoodPerTurnRow = $("<div></div>")
            .attr('id', 'growthFoodPerTurnRow')
            .keyValueRow({key: 'Growth food per turn', value: '-5'});
        $growthContainer.append($growthFoodPerTurnRow);

        const $amenitiesGrowthBonusRow = $("<div></div>")
            .attr('id', 'amenitiesGrowthBonusRow')
            .keyValueRow({key: 'Amenities growth bonus', value: '0%'});
        $growthContainer.append($amenitiesGrowthBonusRow);

        const $otherGrowthBonusesRow = $("<div></div>")
            .attr('id', 'otherGrowthBonusesRow')
            .keyValueRow({key: 'Other growth bonuses', value: '0%'});
        $growthContainer.append($otherGrowthBonusesRow);

        const $line2 = $("<div></div>")
            .addClass('city_info_line');
        $growthContainer.append($line2);

        // --- modifiedGrowthContainer -----

        const $modifiedGrowthContainer = $("<div></div>")
            .addClass('infoContainer');
        $cityInfoContent.append($modifiedGrowthContainer);

        const $modifiedGrowthPerTurnRow = $("<div></div>")
            .attr('id', 'modifiedGrowthPerTurnRow')
            .keyValueRow({key: 'Modified growth per turn', value: '+4'});
        $modifiedGrowthContainer.append($modifiedGrowthPerTurnRow);

        const $housingModifierRow = $("<div></div>")
            .attr('id', 'housingModifierRow')
            .keyValueRow({key: 'Housing modifier', value: '1'});
        $modifiedGrowthContainer.append($housingModifierRow);

        const $occupiedCityMultiplierRow = $("<div></div>")
            .attr('id', 'occupiedCityMultiplierRow')
            .keyValueRow({key: 'Occupied city multiplier', value: 'N/A'});
        $modifiedGrowthContainer.append($occupiedCityMultiplierRow);

        const $line3 = $("<div></div>")
            .addClass('city_info_line');
        $modifiedGrowthContainer.append($line3);

        const $totalFoodSurplusRow = $("<div></div>")
            .attr('id', 'totalFoodSurplusRow')
            .addClass('mb-2')
            .keyValueRow({key: 'Total food surplus', value: '+3.4'});
        $modifiedGrowthContainer.append($totalFoodSurplusRow);

        // --- city growth progress -----

        const $cityProgressRow = $("<div></div>")
            .attr('id', 'cityProgressRow')
            .addClass('mb-2')
            .cityProgress({key: 'Growth in', value: '11'});
        $cityInfoContent.append($cityProgressRow);

        // --- amenities -----

        const amenitiesHeader = $("<div></div>")
            .attr('id', 'amenitiesHeader')
            .cityViewSubHeader({title: 'Amenities'});
        $cityInfoContent.append(amenitiesHeader);

        // 27 amenities of 20 required
        // status: Ecstatic

        const citizenAmenitiesBox = $("<div></div>")
            .attr('id', 'citizenAmenitiesBox')
            .cityViewCitizenBox({
                title: ' ',
                text: '+20% Citizen growth\n+10% Non-food yields',
                icon: '/static/smarthexboard/img/ui/city/citizen_icon_increase.png'
            });
        $cityInfoContent.append(citizenAmenitiesBox);

        const $amenitiesContainer = $("<div></div>")
            .addClass('infoContainer');
        $cityInfoContent.append($amenitiesContainer);

        const $amenitiesFromLuxuriesRow = $("<div></div>")
            .attr('id', 'amenitiesFromLuxuriesRow')
            .keyValueRow({key: 'Amenities from Luxuries', value: '10'});
        $amenitiesContainer.append($amenitiesFromLuxuriesRow);

        const $amenitiesFromCivicsRow = $("<div></div>")
            .attr('id', 'amenitiesFromCivicsRow')
            .keyValueRow({key: 'Amenities from Civics', value: '2'});
        $amenitiesContainer.append($amenitiesFromCivicsRow);

        const $amenitiesFromEntertainmentRow = $("<div></div>")
            .attr('id', 'amenitiesFromEntertainmentRow')
            .keyValueRow({key: 'Amenities from Entertainment', value: '9'});
        $amenitiesContainer.append($amenitiesFromEntertainmentRow);

        const $amenitiesFromGreatPeopleRow = $("<div></div>")
            .attr('id', 'amenitiesFromGreatPeopleRow')
            .keyValueRow({key: 'Amenities from Great People', value: '2'});
        $amenitiesContainer.append($amenitiesFromGreatPeopleRow);

        const $amenitiesFromCityStatesRow = $("<div></div>")
            .attr('id', 'amenitiesFromCityStatesRow')
            .keyValueRow({key: 'Amenities from City-States', value: '5'});
        $amenitiesContainer.append($amenitiesFromCityStatesRow);

        const $amenitiesFromReligionRow = $("<div></div>")
            .attr('id', 'amenitiesFromReligionRow')
            .keyValueRow({key: 'Amenities from Religion', value: '3'});
        $amenitiesContainer.append($amenitiesFromReligionRow);

        const $amenitiesFromNationalParksRow = $("<div></div>")
            .attr('id', 'amenitiesFromNationalParksRow')
            .keyValueRow({key: 'Amenities from National Parks', value: '2'});
        $amenitiesContainer.append($amenitiesFromNationalParksRow);

        const $amenitiesFromWarWearinessRow = $("<div></div>")
            .attr('id', 'amenitiesFromWarWearinessRow')
            .keyValueRow({key: 'Amenities from War Weariness', value: '13'});
        $amenitiesContainer.append($amenitiesFromWarWearinessRow);

        const $amenitiesFromBankruptcyRow = $("<div></div>")
            .attr('id', 'amenitiesFromBankruptcyRow')
            .keyValueRow({key: 'Amenities from Bankruptcy', value: '0'});
        $amenitiesContainer.append($amenitiesFromBankruptcyRow);

        const $amenitiesFromGovernorsRow = $("<div></div>")
            .attr('id', 'amenitiesFromGovernorsRow')
            .keyValueRow({key: 'Amenities from Governors', value: '1'});
        $amenitiesContainer.append($amenitiesFromGovernorsRow);

        const $line4 = $("<div></div>")
            .addClass('city_info_line');
        $amenitiesContainer.append($line4);

        const $amenitiesTotalsRow = $("<div></div>")
            .attr('id', 'amenitiesTotalsRow')
            .keyValueRow({key: 'Total Amenities', value: '27'});
        $amenitiesContainer.append($amenitiesTotalsRow);
    }

    _showBreakdownContent() {
        const $cityInfoContent = $('#city_info_content');
        $cityInfoContent.empty(); // reset

        const breakDownHeader = $("<div></div>")
            .attr('id', 'breakDownHeader')
            .cityViewSubHeader({title: 'City Breakdown'});
        $cityInfoContent.append(breakDownHeader);

        const $districtsContainer = $("<div></div>")
            .addClass('infoContainer');
        $cityInfoContent.append($districtsContainer);

        const $districtsConstructedRow = $("<div></div>")
            .attr('id', 'districtsConstructedRow')
            .keyValueRow({key: 'Districts Constructed', value: '3'});
        $districtsContainer.append($districtsConstructedRow);

        const $districtsPossibleRow = $("<div></div>")
            .attr('id', 'districtsPossibleRow')
            .keyValueRow({key: 'of Districts Possible', value: '3'});
        $districtsContainer.append($districtsPossibleRow);

        // Buildings and Districts
        const buildingsAndDistrictsHeader = $("<div></div>")
            .attr('id', 'buildingsAndDistrictsHeader')
            .cityViewSubHeader({title: 'Buildings and Districts'});
        $cityInfoContent.append(buildingsAndDistrictsHeader);

        const cityCenterDistrictHeader = $("<div></div>")
            .attr('id', 'cityCenterDistrictHeader')
            .districtHeader({title: 'City Center', icon: '/static/smarthexboard/img/districts/district_cityCenter@3x.png'});
        $cityInfoContent.append(cityCenterDistrictHeader);

        // Monument
        const monumentYields = new Yields(1, 0, 0, 0, 0, 0);
        const monumentBuildingItem = $("<div></div>")
            .attr('id', 'monumentBuildingRow')
            .buildingItem({title: 'Monument', icon: '/static/smarthexboard/img/buildings/Monument.png', yields: monumentYields });
        $cityInfoContent.append(monumentBuildingItem);

        // Wonders
        const wondersHeader = $("<div></div>")
            .attr('id', 'wondersHeader')
            .cityViewSubHeader({title: 'Wonders'});
        $cityInfoContent.append(wondersHeader);

        // Trading Posts
        const tradingPostHeader = $("<div></div>")
            .attr('id', 'tradingPostHeader')
            .cityViewSubHeader({title: 'Trading Posts'});
        $cityInfoContent.append(tradingPostHeader);
    }

    _showLoyaltyContent() {
        const $cityInfoContent = $('#city_info_content');
        $cityInfoContent.empty(); // reset
    }

    show(city, city_info, callback) {
        $('#city_name').text(city.name);

        makeVisible('city_panel');
    }

    hide() {
        makeHidden('city_panel');
    }
}

export { CityView }