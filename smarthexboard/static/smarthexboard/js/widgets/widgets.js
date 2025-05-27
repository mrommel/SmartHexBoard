$.widget("smarthexboard.cityViewSubHeader", {

    // Default options.
    options: {
        title: "##title##"
    },

    // The constructor.
    _create: function() {
        this.options.title = this._constrainTitle(this.options.title);
        this.element.addClass("city_sub_header")
        this.refresh();
    },

    _setOption: function(key, value) {
        if (key === "title") {
            value = this._constrainTitle( value );
        }
        this._super( key, value );
    },

    _setOptions: function(options) {
        this._super(options);
        this.refresh();
    },

    refresh: function() {
        this.element.text(this.options.title);
    },

    _constrainTitle: function(titleValue) {
        if (titleValue.length > 30) {
            titleValue = 100;
        }
        if (titleValue.length === 0) {
            titleValue = '##title##';
        }
        return titleValue;
    }
});

$.widget("smarthexboard.cityViewCitizenBox", {

    // Default options.
    options: {
        title: "##title##",
        text: "##text##",
        icon: "##icon##"
    },

    // The constructor.
    _create: function() {
        this.options.title = this._constrainTitle(this.options.title);
        this.options.text = this._constrainText(this.options.text);

        this.element.addClass("city_citizen_box");

        let imgIcon = $('<img>')
            .addClass('city_citizen_box_icon')
            .attr('src', this.options.icon);
        this.element.append(imgIcon);

        let textContainer = $('<div>')
            .addClass('city_citizen_box_content');
        this.element.append(textContainer);

        let spanTitle = $('<h3>')
            .addClass('city_citizen_box_title')
            .text(this.options.title);
        textContainer.append(spanTitle);

        let spanText = $('<span>')
            .addClass('city_citizen_box_text')
            .text(this.options.text);
        textContainer.append(spanText);

        // <div class="text-content">

        this.refresh();
    },

    _setOption: function(key, value) {
        if (key === "title") {
            value = this._constrainTitle( value );
        }
        else if (key === "text") {
            value = this._constrainText( value );
        }
        this._super(key, value);
    },

    _setOptions: function(options) {
        this._super(options);
        this.refresh();
    },

    refresh: function() {
        let $spanTitle = this.options.title;
        let $spanText = this.options.text;
        let $imgIcon = this.options.icon;

        this.element.children().each(function (index, currentElement) {
            // console.info(currentElement);
            if (index === 0) {
                $(currentElement).attr('src', $imgIcon);
            } else if (index === 1) {
                $(currentElement).children().each(function (innerIndex, innerElement) {
                    // console.info(innerElement);
                    if (innerIndex === 0) {
                        $(innerElement).text($spanTitle);
                    } else if (innerIndex === 1) {
                        $(innerElement).text($spanText);
                    }
                });
            }
        });
    },

    _constrainTitle: function(titleValue) {
        if (titleValue.length > 30) {
            titleValue = titleValue.substring(0, 30);
        }
        if (titleValue.length === 0) {
            titleValue = '##title##';
        }
        return titleValue;
    },

    _constrainText: function(textValue) {
        if (textValue.length > 100) {
            textValue = textValue.substring(0, 100);
        }
        if (textValue.length === 0) {
            textValue = '##text##';
        }
        return textValue;
    }
});