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

        const $cityInfoPanel = $('#city_info_panel');

        const $cityInfoHeader = $('#city_info_header');

        const $cityDetailsName = $("<div>")
            .attr('id', 'city_details_name')
            .text('City Details');
        $cityInfoHeader.append($cityDetailsName);

        const $cityInfoExitButton = $("<div>")
            .attr('id', 'city_info_panel_exit')
            .click(() => {
                console.log('Close Info Panel');
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

        // new CityViewCitizenBox('abc', $cityInfoContent);
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

        // --- amenities -----

        const amenitiesHeader = $("<div></div>")
            .attr('id', 'amenitiesHeader')
            .cityViewSubHeader({title: 'Amenities'});
        $cityInfoContent.append(amenitiesHeader);
    }

    _showBreakdownContent() {
        const $cityInfoContent = $('#city_info_content');
        $cityInfoContent.empty(); // reset
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