export default class Link {
    static generateId(sourceId, targetId) {
        return `${sourceId}_${targetId}`;
    }

    constructor(source, target) {
        this.source = source;
        this.target = target;
    }

    getId() {
        return Link.generateId(this.source.getId(), this.target.getId());
    }
}
