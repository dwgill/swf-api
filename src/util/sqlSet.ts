import * as _ from 'lodash';

const sqlSet = (vals: string[]) => {
    const joined_vals = vals.join(',');
    return `(${joined_vals})`;
}

export default sqlSet;