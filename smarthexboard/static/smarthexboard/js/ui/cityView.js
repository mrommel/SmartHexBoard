class CityViewSubHeader {
    constructor(title, $parent) {
        const $sub_header = $("<div>")
            .attr('class', 'city_sub_header')
            .text(title);
        $parent.append($sub_header);
    }
}

class CityView {
    constructor() {
        this.cityDetailsTab = 'citizen'; // breakdown, loyalty

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

        this._showCitizenContent();
    }

    _showDetailsTab(tabName) {
        const $cityCitizenBtn = $('#city_citizen_btn');
        const $cityBreakdownBtn = $('#city_breakdown_btn');
        const $cityLoyaltyBtn = $('#city_loyalty_btn');

        // remove all classes
        $cityCitizenBtn.removeClass();
        $cityBreakdownBtn.removeClass();
        $cityLoyaltyBtn.removeClass();

        switch (tabName) {
            case 'citizen':
                $cityCitizenBtn.addClass('city_citizen_selected');
                $cityBreakdownBtn.addClass('city_breakdown_active');
                $cityLoyaltyBtn.addClass('city_loyalty_active');
                if (this.cityDetailsTab != tabName) {
                    this._showCitizenContent();
                }
                this.cityDetailsTab = tabName;
                break;
            case 'breakdown':
                $cityCitizenBtn.addClass('city_citizen_active');
                $cityBreakdownBtn.addClass('city_breakdown_selected');
                $cityLoyaltyBtn.addClass('city_loyalty_active');
                if (this.cityDetailsTab != tabName) {
                    this._showBreakdownContent();
                }
                this.cityDetailsTab = tabName;
                break;
            case 'loyalty':
                $cityCitizenBtn.addClass('city_citizen_active');
                $cityBreakdownBtn.addClass('city_breakdown_active');
                $cityLoyaltyBtn.addClass('city_loyalty_selected');
                if (this.cityDetailsTab != tabName) {
                    this._showLoyaltyContent();
                }
                this.cityDetailsTab = tabName;
                break;
        }
    }

    _showCitizenContent() {
        const $cityInfoContent = $('#city_info_content');
        $cityInfoContent.empty(); // reset

        new CityViewSubHeader('Citizen Growth', $cityInfoContent);

        new CityViewSubHeader('Amenities', $cityInfoContent);
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
        makeVisible('city_panel');
    }

    hide() {
        makeHidden('city_panel');
    }
}

export { CityView }