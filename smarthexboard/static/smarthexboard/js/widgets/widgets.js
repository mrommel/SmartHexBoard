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
            titleValue = '...';
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
            .addClass('city_citizen_box_text');

        if (this.options.text.includes('\n')) {

        } else {
            spanText.text(this.options.text);
        }

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
                        if ($spanText.includes('\n')) {
                            const textLines = $spanText.split('\n');
                            $(innerElement).empty(); // Clear previous content
                            textLines.forEach(function(elem, idx, array) {
                                const lineSpan = $('<span>').text(elem);
                                $(innerElement).append(lineSpan);
                                if (idx !== textLines.length - 1) {
                                    $(innerElement).append('<br>'); // Add line break
                                }
                            });
                        } else {
                            $(innerElement).text($spanText);
                        }
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

$.widget("smarthexboard.normalButton", {
    // Default options.
    options: {
        title: "##title##",
        icon: "##icon##"
    },

    // The constructor.
    _create: function() {
        this.options.title = this._constrainTitle(this.options.title);

        this.element.addClass("button_normal");

        let imgIcon = $('<img>')
            .addClass('button_normal_icon')
            .attr('src', this.options.icon);
        this.element.append(imgIcon);

        let spanTitle = $('<span>')
            .addClass('button_normal_title')
            .text(this.options.title);
        this.element.append(spanTitle);

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
        let $spanTitle = this.options.title;
        let $imgIcon = this.options.icon;

        this.element.children().each(function (index, currentElement) {
            // console.info(currentElement);
            if (index === 0) {
                $(currentElement).attr('src', $imgIcon);
                if ($imgIcon === '##icon##') {
                    $(currentElement).hide();
                }
            } else if (index === 1) {
                $(currentElement).text($spanTitle);
            }
        });
    },

    _constrainTitle: function(titleValue) {
        if (titleValue.length > 30) {
            titleValue = '...';
        }
        if (titleValue.length === 0) {
            titleValue = '##title##';
        }
        return titleValue;
    }
});

$.widget("smarthexboard.highlightButton", {
    // Default options.
    options: {
        title: "##title##",
        icon: "##icon##"
    },

    // The constructor.
    _create: function() {
        this.options.title = this._constrainTitle(this.options.title);

        this.element.addClass("button_highlight");

        let imgIcon = $('<img>')
            .addClass('button_highlight_icon')
            .attr('src', this.options.icon);
        this.element.append(imgIcon);

        let spanTitle = $('<span>')
            .addClass('button_highlight_title')
            .text(this.options.title);
        this.element.append(spanTitle);

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
        let $spanTitle = this.options.title;
        let $imgIcon = this.options.icon;

        this.element.children().each(function (index, currentElement) {
            // console.info(currentElement);
            if (index === 0) {
                $(currentElement).attr('src', $imgIcon);
                if ($imgIcon === '##icon##') {
                    $(currentElement).hide();
                }
            } else if (index === 1) {
                $(currentElement).text($spanTitle);
            }
        });
    },

    _constrainTitle: function(titleValue) {
        if (titleValue.length > 30) {
            titleValue = '...';
        }
        if (titleValue.length === 0) {
            titleValue = '##title##';
        }
        return titleValue;
    }
});

$.widget("smarthexboard.keyValueRow", {
    // Default options.
    options: {
        key: "##key##",
        value: "##value##"
    },

    // The constructor.
    _create: function() {
        this.options.key = this._constrainKey(this.options.key);
        this.options.value = this._constrainValue(this.options.value);

        this.element.addClass("key_value_row");

        let spanKey = $('<span>')
            .addClass('key_title')
            .text(this.options.key);
        this.element.append(spanKey);

        let spanValue = $('<span>')
            .addClass('key_value')
            .text(this.options.value);
        this.element.append(spanValue);

        this.refresh();
    },

    _setOption: function(key, value) {
        if (key === "key") {
            value = this._constrainKey( value );
        }
        this._super( key, value );
    },

    _setOptions: function(options) {
        this._super(options);
        this.refresh();
    },

    refresh: function() {
        let $spanKey = this.options.key;
        let $spanValue = this.options.value;

        this.element.children().each(function (index, currentElement) {
            // console.info(currentElement);
            if (index === 0) {
                $(currentElement).text($spanKey);
            } else if (index === 1) {
                $(currentElement).text($spanValue);
            }
        });
    },

    _constrainKey: function(keyValue) {
        if (keyValue.length > 30) {
            keyValue = 100;
        }
        if (keyValue.length === 0) {
            keyValue = '##key##';
        }
        return keyValue;
    },

    _constrainValue: function(valueValue) {
        if (valueValue.length > 30) {
            valueValue = 100;
        }
        if (valueValue.length === 0) {
            valueValue = '##value##';
        }
        return valueValue;
    }
});

$.widget("smarthexboard.cityProgress", {
    // Default options.
    options: {
        key: "##key##",
        value: "##value##"
    },

    // The constructor.
    _create: function() {
        this.options.key = this._constrainKey(this.options.key);
        this.options.value = this._constrainValue(this.options.value);

        this.element.addClass("city_progress");

        let spanKey = $('<span>')
            .addClass('city_progress_title')
            .text(this.options.key);
        this.element.append(spanKey);

        let spanValue = $('<span>')
            .addClass('city_progres_value')
            .text(this.options.value);
        this.element.append(spanValue);

        this.refresh();
    },

    _setOption: function(key, value) {
        if (key === "key") {
            value = this._constrainKey( value );
        }
        this._super( key, value );
    },

    _setOptions: function(options) {
        this._super(options);
        this.refresh();
    },

    refresh: function() {
        let $spanKey = this.options.key;
        let $spanValue = this.options.value;

        this.element.children().each(function (index, currentElement) {
            // console.info(currentElement);
            if (index === 0) {
                $(currentElement).text($spanKey);
            } else if (index === 1) {
                $(currentElement).text($spanValue);
            }
        });
    },

    _constrainKey: function(keyValue) {
        if (keyValue.length > 30) {
            keyValue = 100;
        }
        if (keyValue.length === 0) {
            keyValue = '##key##';
        }
        return keyValue;
    },

    _constrainValue: function(valueValue) {
        if (valueValue.length > 30) {
            valueValue = 100;
        }
        if (valueValue.length === 0) {
            valueValue = '##value##';
        }
        return valueValue;
    }
});

$.widget("smarthexboard.districtHeader", {
    // Default options.
    options: {
        title: "##title##",
        icon: "##icon##"
    },

    // The constructor.
    _create: function() {
        this.options.title = this._constrainTitle(this.options.title);

        this.element.addClass("district_header");

        let imgIcon = $('<img>')
            .addClass('district_header_icon')
            .attr('src', this.options.icon);
        this.element.append(imgIcon);

        let spanTitle = $('<span>')
            .addClass('district_header_title')
            .text(this.options.title);
        this.element.append(spanTitle);

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
        let $spanTitle = this.options.title;
        let $imgIcon = this.options.icon;

        this.element.children().each(function (index, currentElement) {
            // console.info(currentElement);
            if (index === 0) {
                $(currentElement).attr('src', $imgIcon);
                if ($imgIcon === '##icon##') {
                    $(currentElement).hide();
                }
            } else if (index === 1) {
                $(currentElement).text($spanTitle);
            }
        });
    },

    _constrainTitle: function(titleValue) {
        if (titleValue.length > 30) {
            titleValue = '...';
        }
        if (titleValue.length === 0) {
            titleValue = '##title##';
        }
        return titleValue;
    }
});