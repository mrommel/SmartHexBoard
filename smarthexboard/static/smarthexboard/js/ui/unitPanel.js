import { CircularProgressBar } from "./circularProgressBar.js";

class UnitPanel {
    constructor() {
        // createUnitPanel
        const $unitPanelIcon = $('#unit_panel_icon');

        const unitHealth = addTag('unit_panel_icon', 'div');
        unitHealth.id = 'unitHealth';

        this.progress = new CircularProgressBar(85, 85, 'unitHealth', {strokeSize: 6});
        this.progress.setBackgroundColor('darkcyan');
        this.progress.setStrokeColor('cyan');
        this.progress.showProgressNumber(false);
        $unitPanelIcon.append(this.progress);

        const $img = $("<img>")
            .attr('id', 'unit_panel_icon_img')
            .addClass('unit-icon')
            .attr("alt", '')
            .attr("src", '');

        $unitPanelIcon.append($img);

        console.log('created unit panel');
    }

    show(unit, actions, callback) {
        // console.log('unitPanel: ' +  unit + ' => ' + actions);
        // console.log('unitType: ' + unit.unitType.toString());
        // console.log('texture: ' + unit.unitType.texture);
        $('#unit_panel_title').text(unit.name);
        $('#unit_panel_icon_img').attr('src', unit.icon());
        $('#unit_panel_max_moves_text').text(unit.moves + ' / ' + unit.unitType.max_moves);
        $('#unit_panel_melee_strength_text').text(unit.meleeStrength);

        if (unit.rangedStrength === 0) {
            $('#unit_panel_ranged_strength').hide();
        } else {
            $('#unit_panel_ranged_strength_text').text(unit.rangedStrength);
            $('#unit_panel_ranged_strength').show();
        }

        if (unit.rangedRange === 0) {
            $('#unit_panel_ranged_range').hide();
        } else {
            $('#unit_panel_ranged_range_text').text(unit.rangedRange);
            $('#unit_panel_ranged_range').show();
        }

        let color = 'darkgreen';
        if (unit.health < 60) color = 'yellow';
        if (unit.health < 30) color = 'red';

        this.progress.setStrokeColor(color);
        this.progress.setProgress(unit.health);

        const $actionPanel = $('#unit_panel_actions');
        $actionPanel.empty();

        const actionImages = new Map([
            ['ACTION_ATTACK', '/static/smarthexboard/img/ui/commands/command_button_attack@3x.png'],
            ['ACTION_DISBAND', '/static/smarthexboard/img/ui/commands/command_button_disband@3x.png'],
            ['ACTION_FOUND_CITY', '/static/smarthexboard/img/ui/commands/command_button_found@3x.png'],
            ['ACTION_SKIP', '/static/smarthexboard/img/ui/commands/command_button_skip@3x.png'],
            ['ACTION_SLEEP', '/static/smarthexboard/img/ui/commands/command_button_sleep@3x.png']
        ]);

        actions.forEach((action, index) => {
            const actionImage = actionImages.get(action) || '/static/smarthexboard/img/ui/commands/command_button_default@3x.png';

            const $img = $("<img>")
                .addClass('unit-command')
                .attr("alt", action)
                .attr("src", actionImage)
                .attr("href", '#')
                .click(() => {
                    console.log('Clicked ' + action);
                    callback(action, index);
                });

            $actionPanel.append($img);
        });

        makeVisible('unit_panel');
    }

    hide() {
        makeHidden('unit_panel');
    }
}

export { UnitPanel }