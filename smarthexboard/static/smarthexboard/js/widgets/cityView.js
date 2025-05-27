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

        const $cityInfoHeader = $('#city_info_header');

        const $cityDetailsName = $("<div>")
            .attr('id', 'city_details_name')
            .text('City Details');
        $cityInfoHeader.append($cityDetailsName);

        const $cityName = $("<div>")
            .attr('id', 'city_name')
            .text('##Name##');
        $cityInfoHeader.append($cityName);

        const $cityCitizenImg = $("<div>")
            .addClass('city_citizen_selected')
            .attr('id', 'city_citizen_btn')
            .click(() => {
                console.log('Clicked city citizen');
                this._showDetailsTab('citizen');
            });
        $cityInfoHeader.append($cityCitizenImg);

        const $cityBreakdownImg = $("<div>")
            .addClass('city_breakdown_active')
            .attr('id', 'city_breakdown_btn')
            .click(() => {
                console.log('Clicked city breakdown');
                this._showDetailsTab('breakdown');
            });
        $cityInfoHeader.append($cityBreakdownImg);

        const $cityLoyaltyImg = $("<div>")
            .addClass('city_loyalty_active')
            .attr('id', 'city_loyalty_btn')
            .click(() => {
                console.log('Clicked city loyalty');
                this._showDetailsTab('loyalty');
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
            .cityViewCitizenBox({title: 'Citizen Growth', text: 'abc', icon: 'icon.png'});
        $cityInfoContent.append(citizenBox);

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