// https://masteringjs.io/tutorials/fundamentals/enum
export class ActionState {
    static none = new ActionState('None');
    static selectMeleeTarget = new ActionState('SelectMeleeTarget');
    static selectRangedTarget = new ActionState('SelectRangedTarget');
    static selectEmbarkTarget = new ActionState('SelectEmbarkTarget');
    static inputCityName = new ActionState('InputCityName');
    static disbandUnit = new ActionState('DisbandUnit');

    constructor(name) {
        this.name = name;
    }

    toString() {
        return `ActionState.${this.name}`;
    }
}